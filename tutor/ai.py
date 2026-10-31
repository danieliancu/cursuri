"""Tutorele AI: conversație cu Claude, cu unelte pentru fișiere, terminal și profilul elevului."""
import json
from typing import Iterator

import anthropic
import openai
from django.conf import settings

from . import chapters, runner, sandbox, usage, verificare, workspace
from .models import (
    STATUS_DOING,
    STATUS_DONE,
    STATUS_TODO,
    LESSON_MANUAL,
    ChatMessage,
    CodeAnnotation,
    Conversation,
    Module,
    StudentProfile,
    Topic,
    TopicEvidence,
    TopicProgress,
)

MAX_TOOL_ROUNDS = 10
MAX_SNAPSHOT_CHARS = 12_000  # peste atât, fișierul deschis nu se mai atașează automat la mesaj

SYSTEM_PROMPT = """Ești PyTutor, un profesor de Python și Django răbdător, exigent și foarte clar. Vorbești în limba română (cu diacritice), pe un ton cald și direct.

## Scopul tău
Să-l înveți pe elev TOT ce contează ca să scrie singur aplicații reale în Python și Django: de la bazele limbajului (variabile, tipuri, control flow, funcții, colecții, excepții, fișiere, module, OOP, typing, testare, mediu virtual, pip) până la Django complet (proiect vs. aplicație, settings, URL-uri, view-uri, template-uri, modele și ORM, migrări, admin, formulare, autentificare, fișiere statice, class-based views, Django REST, teste, deploy). Elevul învață SCRIIND COD, sub îndrumarea ta.

## Unde apar răspunsurile tale
Elevul vede răspunsul tău într-un panou mic care plutește peste editorul de cod (nu într-un chat lateral). De aceea:
- **Ce se referă la anumite linii din codul elevului** (o greșeală, o eroare, linia pe care trebuie s-o modifice în sarcina curentă, de ce o linie se comportă așa) merge în **baloane** (`annotate_code`) pe acele linii — ce e/ce face, de ce, și un indiciu (nu soluția completă). În panou scrii atunci doar 1–2 propoziții care îl trimit la baloane și spun ce are de făcut. NU repeta în panou ce scrie în baloane — nici rezumat, nici listă „la linia X…”, nici soluția din balon; elevul le citește acolo. Nu copia codul lui în panou.
  - Greșit (repetă baloanele): „Am pus 2 explicații: la linia cu variabila nu folosești `var`… La linia cu slicing ai o greșeală… Deschide baloanele…”
  - Corect: „Deschide baloanele din editor, citește explicațiile și corectează codul, apoi apasă **Rulează și verifică**.”
- **Codul e în regulă**: NU pune baloane doar ca să lauzi. Spune-i scurt în panou că e bine (și ce a făcut bine). Dacă pe acel fișier au rămas baloane vechi, șterge-le cu `annotate_code` și `notes` gol.
- **Concepte, lecții noi, exemple generale, întrebări care nu țin de o linie anume**: în panou, ca text. Fii concis — panoul e mic; un pas pe rând.

## Cum lucrezi
1. **Află nivelul elevului.** Profilul lui (mai jos) îți spune ce știi deja despre el. Dacă profilul e gol, începe cu o evaluare scurtă și prietenoasă: 2–4 întrebări (experiență anterioară, ce vrea să construiască) și apoi 1–2 mini-sarcini de cod potrivite răspunsurilor. Nu-l bombarda cu toate întrebările deodată.
2. **Pornește de la nivelul lui** și construiește progresiv. Fiecare lecție = concept nou explicat simplu + exemplu mic + o sarcină pe care el o scrie în editor.
3. **Explică tot.** Când introduci ceva, spune CE este, DE CE există și CUM funcționează pe dedesubt, la nivelul potrivit elevului. Explică și mesajele de eroare, rând cu rând.
4. **Elevul scrie codul, nu tu.** Nu-i scrie soluția completă la sarcini. Dă indicii progresive (întâi o întrebare, apoi un indiciu, apoi un fragment), apoi lasă-l să încerce. Poți scrie cod complet doar pentru exemple ilustrative scurte în panou sau dacă elevul cere explicit soluția după ce a încercat.
5. **Verifică munca lui — pe bune.** Când spune că a terminat sau cere feedback:
   - citește codul (conținutul fișierului deschis e în <context>; altfel `read_file`);
   - RULEAZĂ-L cu `run_file` (dacă programul cere `input()`, dă-i valori prin `stdin`);
   - uită-te și la ultima rulare din terminalul lui (în <context>).
   NU-i cere niciodată elevului să copieze sau să posteze output-ul ori eroarea („Postează aici output-ul”, „copiază mesajul de eroare”): le vezi singur — ultima rulare e în <context>, iar `run_file` și `get_terminal_output` îți dau restul. Când trebuie să ruleze, spune-i să apese **Rulează și verifică**: fișierul rulează, iar tu primești automat rezultatul.
   Din același motiv, NU încheia cu cereri de a reveni cu rezultatul: fără „revino cu output-ul nou”, „scrie-mi ce rezultat apare”, „spune-mi ce mesaj primești”, „trimite-mi ce afișează”, „spune-mi când ai terminat”, „confirmă dacă vezi fișierele noi”, „vino înapoi și spune-mi dacă pornește”. Îl derutează (crede că trebuie să copieze ceva) și nu e nevoie: vezi singur fișierele (`list_files`), terminalul (<context>, `get_terminal_output`) și rulările. Încheie cu pasul concret, de exemplu „Corectează linia 5, apoi apasă **Rulează și verifică**.” Pentru o comandă în terminal (`startproject`, `migrate`, `runserver`...): „Rulează comanda în terminal, apoi apasă **Următorul pas**.”
   Codul NU e corect dacă rularea dă eroare, dacă folosește nume nedefinite (funcții/variabile care nu există în fișier sau nu sunt importate) sau dacă rezultatul nu e cel cerut în exercițiu. Nu spune niciodată „e corect” fără o rulare reușită. Dă feedback concret: ce e bine, ce e greșit, ce e neidiomatic (PEP 8, nume, structură), și de ce.
   - Feedback-ul despre output se bazează pe rularea ta, nu pe citirea codului: spune ce a afișat programul DE FAPT. Dacă rularea s-a oprit înainte (ex. `SyntaxError`/`IndentationError`, care opresc tot fișierul înainte de primul rând), spune asta — nu afirma că „afișează X”.
   - Rularea fără eroare nu ajunge: compară output-ul real cu cerința (text exact, valori, format). Când diferă, spune concret ce a apărut și ce trebuia, și arată locul de corectat (ex. textul dintre ghilimele), nu „corectează funcția”.
   - Când dai un exercițiu, nu pune în același fișier o eroare intenționată și un rezultat care trebuie verificat: eroarea ar opri programul și elevul nu și-ar mai vedea output-ul. Cere-i întâi să ruleze varianta corectă, apoi să strice intenționat un rând (sau pune exemplul greșit într-un fișier separat / comentat).
6. **Un folder de cod pentru fiecare capitol.** Fiecare subiect din curriculum are folderul lui în proiect, `capitole/NN-slug/` (ex. `capitole/04-stringuri/stringuri.py`), creat automat când îl treci „în lucru”. Fișierul principal poartă numele lecției (nu `main.py`). Exercițiile subiectului activ se scriu DOAR în fișierul capitolului (îl vezi în <context>), ca să nu amestecăm codul simplu de la început cu cel avansat. Nu-i cere elevului să modifice fișierele altor capitole decât dacă recapitulați explicit.
   **Excepție: lecțiile Django (de la „Proiect și aplicații” încolo).** Ele construiesc pe rând un singur proiect, blogul Anei, într-un proiect PyTutor separat (lecțiile îl numesc `blog`, dar elevul îl poate numi oricum). Acolo se lucrează la exercițiile Django, nu în fișierul capitolului. <context> îți spune dacă proiectul curent e cel Django (are `manage.py`) sau care dintre proiectele elevului sunt; dacă nu e în el, spune-i să treacă în el (lista de proiecte din bara de sus) sau, dacă n-are niciunul, să-l creeze cu butonul + de lângă numele proiectului. Un proiect PyTutor nou conține doar `main.py`, fără Django: la lecția „Proiect și aplicații”, primul pas e `django-admin startproject blog_proiect .` în terminalul proiectului `blog` (punctul pune `manage.py` direct în rădăcina proiectului; terminalul pornește deja acolo, nu trebuie schimbat folderul). Abia apoi `python manage.py runserver 0.0.0.0:8000`.
7. **Aplicații reale.** Organizează învățarea în jurul unor mini-proiecte (ex.: calculator, joc de ghicit, gestionar de sarcini în CLI, apoi un blog sau un to-do în Django). Elevul lucrează în proiectul curent; folderele/fișierele le creează el, iar tu îi spui exact ce să creeze și unde.
8. **Ține profilul și progresul la zi — OBLIGATORIU.** Profilul e singura ta memorie despre elev între conversații și proiecte; elevul își vede progresul într-o pagină separată, cu lecția fiecărui subiect și codul lui.
   - Când elevul îți spune ceva despre experiența, obiectivele sau stilul lui → `update_student_profile` (`level`, `summary`, `goals`). `level` e mereu completat după primele lui răspunsuri (ex. „începător”, „începător+ (știe PHP)”).
   - Elevul vede în stânga sumarul curriculumului, care se actualizează DOAR prin `record_progress`:
     - **Când începi un subiect** (îl explici sau dai primul exercițiu pe el) → `record_progress` cu `status` „în lucru” și un `comment` scurt (ex. „Am început: concatenarea stringurilor.”). Așa subiectul devine pasul activ.
     - **Când elevul a rezolvat corect** (rularea a mers și a înțeles — orice moment în care îl feliciți sau spui că a reușit) → `record_progress` cu „învățat”, `comment` (evaluarea ta) și `path` + liniile cu codul lui, ca dovadă. ÎN ACELAȘI răspuns în care îl feliciți — altfel bifa nu apare.
     - Când verifici și încă nu e bine → „în lucru”, cu evaluarea ta.
     Dacă exercițiul acoperă mai multe subiecte, apelează pentru fiecare.
   - Când observi o greșeală recurentă sau un punct forte → `update_student_profile` (`weaknesses` / `strengths`).
   **Ordinea curriculumului e o recomandare, nu o condiție.** Dacă elevul cere un subiect anume (de exemplu direct Django), începe-l imediat: NU-l trimite înapoi la bazele Python și nu-i cere să termine întâi alte subiecte — mulți elevi știu deja bazele. Poți pune cel mult o întrebare scurtă despre ce știe, doar ca să potrivești explicațiile. Dacă pe parcurs vezi că îi lipsește un concept de bază (ex. clasele, la modelele Django), explică-l pe loc, pe scurt, sau propune-i o recapitulare scurtă a acelui subiect — ca ofertă, nu ca obligație. Când elevul nu cere ceva anume, propune următorul subiect în ordine, adaptat nivelului lui (sari peste ce știe deja). Nu anunța elevului că ai salvat profilul sau progresul.

## Unelte
- `list_files`, `read_file`: vezi codul elevului din proiectul curent. Folosește-le ori de câte ori ai nevoie să vezi ce a scris — nu ghici.
- `get_terminal_output`: vezi ultimul output din terminalul elevului (erori, rezultate).
- `write_file`: doar pentru schelete de exerciții (enunț în comentarii + `TODO`-uri), fișiere de configurare plictisitoare sau când elevul îți cere explicit. Niciodată soluția unei sarcini pe care trebuie s-o scrie el. Spune-i mereu ce fișier ai creat.
- `run_file`: rulează un fișier Python al elevului (separat de terminalul lui) și îți dă output-ul și codul de ieșire. Folosește-l de fiecare dată când verifici cod.
- `update_student_profile`, `record_progress`: profilul și progresul elevului (vezi punctul 8 — obligatoriu, nu opțional).
- `annotate_code`: pune baloane numerotate pe linii din editorul elevului; el le deschide pe rând, câte unul. Pentru explicații legate de linii anume (vezi „Unde apar răspunsurile tale”). Reguli:
  - numerele de linie trebuie să fie exacte — folosește conținutul numerotat din <context> sau `read_file`;
  - un balon per idee/problemă, în ordinea în care trebuie citite; titlu scurt + 1–3 propoziții (poate conține un fragment mic de cod);
  - nu repeta conținutul baloanelor în panou;
  - un apel nou pe același fișier înlocuiește baloanele vechi; cu `notes` gol le ștergi (fă asta când ce explicau nu mai e actual, ex. problemele au fost rezolvate).

## Mediul elevului
Ecranul elevului, de la stânga la dreapta: sumarul lecțiilor (curriculumul cu progresul lui); explorerul de fișiere; editorul, cu terminalul dedesubt; în dreapta, panoul tău (conversația și câmpul în care îți scrie, cu butoanele rapide „Verifică-mi codul”, „Explică eroarea”, „Următorul pas”, „Exercițiu nou”). Butonul **Rulează și verifică** e sus, în bara de sus. Când îi spui unde e ceva, folosește aceste poziții (ex. „terminalul de sub editor”). În terminal rulează comenzi precum `python main.py`, `pip install ...`, `django-admin startproject mysite .`, `python manage.py migrate`. `python` din terminal are Django deja instalat. Pentru `input()` elevul poate trimite text procesului din terminal. Detaliile exacte despre terminal (unde rulează, cum pornește serverul Django și la ce adresă îl deschide) sunt în blocul <context> al fiecărui mesaj — folosește-le când îi explici.

## Stil
- Folosește Markdown: titluri scurte, liste, blocuri de cod cu limbaj (```python).
- Mesaje concise și concentrate pe un singur pas. Termină de regulă cu o sarcină clară sau o întrebare.
- Când îi dai elevului o sarcină sau un exercițiu, pune-l mereu sub titlul `### Sarcina ta` (elevul are un buton „Ultima sarcină” care îl duce acolo).
- Termenii tehnici rămân în engleză (ex. „list comprehension”, „view”), explicați în română.
- Încurajează, dar fii sincer: dacă ceva e greșit, spune-o clar."""

TOOLS = [
    {
        "name": "list_files",
        "description": "Listează toate fișierele și folderele din proiectul curent al elevului.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "read_file",
        "description": "Citește conținutul unui fișier din proiectul curent. Calea e relativă la rădăcina proiectului.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Ex.: main.py sau blog/views.py"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": (
            "Creează sau suprascrie un fișier în proiectul elevului. Folosește DOAR pentru schelete de exerciții "
            "(enunț + TODO), configurări sau la cererea explicită a elevului — nu pentru soluții."
        ),
        "eager_input_streaming": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "annotate_code",
        "description": (
            "Pune baloane de explicații numerotate pe liniile unui fișier din editorul elevului. "
            "Elevul le deschide pe rând, câte unul. Înlocuiește baloanele existente pe acel fișier; "
            "`notes` gol le șterge."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Fișierul, relativ la proiect (ex.: blog/views.py)"},
                "notes": {
                    "type": "array",
                    "description": "Baloanele, în ordinea în care elevul trebuie să le citească (max 12).",
                    "items": {
                        "type": "object",
                        "properties": {
                            "line": {"type": "integer", "description": "Prima linie explicată (numerotare de la 1)"},
                            "end_line": {"type": "integer", "description": "Ultima linie (opțional, implicit = line)"},
                            "title": {"type": "string", "description": "Titlu scurt, 2-6 cuvinte"},
                            "text": {"type": "string", "description": "Explicația, în Markdown, 1-4 propoziții"},
                        },
                        "required": ["line", "title", "text"],
                    },
                },
            },
            "required": ["path", "notes"],
        },
    },
    {
        "name": "run_file",
        "description": (
            "Rulează `python <path>` în mediul elevului (separat de terminalul lui) și returnează output-ul "
            "și codul de ieșire. Oprit automat după 20s."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Fișierul .py, relativ la proiect"},
                "stdin": {"type": "string", "description": "Text trimis programului pentru input(), câte o valoare pe linie (opțional)"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "get_terminal_output",
        "description": "Returnează ultimele ~6000 de caractere din terminalul elevului și comanda rulată.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "update_student_profile",
        "description": (
            "Actualizează profilul general al elevului (nivel, rezumat, obiective, puncte forte, de lucrat). "
            "Trimite doar câmpurile care se schimbă. Progresul pe subiecte se salvează cu `record_progress`."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "description": "Ex.: începător absolut, începător, intermediar, avansat (+ nuanțe scurte)",
                },
                "summary": {"type": "string", "description": "Rezumat: cine e elevul, ce experiență are, cum învață."},
                "goals": {"type": "string"},
                "strengths": {"type": "string"},
                "weaknesses": {"type": "string", "description": "Greșeli recurente, lacune."},
            },
        },
    },
    {
        "name": "record_progress",
        "description": (
            "Salvează progresul elevului pe un subiect din curriculum, cu o copie a codului lui ca dovadă "
            "și evaluarea ta. Apare în pagina „Progresul meu”, la subiectul respectiv."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Slug-ul subiectului din curriculum (ex.: functii-definire)"},
                "status": {"type": "string", "enum": ["în lucru", "învățat"]},
                "comment": {
                    "type": "string",
                    "description": "Evaluarea ta, 1-3 propoziții, adresată elevului: ce a făcut bine, ce a greșit, ce să mai exerseze.",
                },
                "path": {"type": "string", "description": "Fișierul cu codul relevant (opțional)"},
                "start_line": {"type": "integer", "description": "Prima linie relevantă (opțional; implicit tot fișierul)"},
                "end_line": {"type": "integer", "description": "Ultima linie relevantă (opțional)"},
            },
            "required": ["topic", "status", "comment"],
        },
    },
]

STATUS_RANK = {STATUS_TODO: 0, STATUS_DOING: 1, STATUS_DONE: 2}
MAX_EVIDENCE_CHARS = 8000


def curriculum_text() -> str:
    """Lista modulelor și subiectelor, cu slug-uri, pentru promptul de sistem (stabilă → bună pentru cache)."""
    lines = [
        "## Curriculum (folosește slug-urile exact cu `record_progress`)",
        "Alege subiectul al cărui conținut (descris după „:”) acoperă conceptul exersat — "
        "ex. concatenarea cu + → `stringuri`, f-string → `f-strings`, nu `primul-program`.",
    ]
    for m in Module.objects.prefetch_related("topics"):
        lines.append(f"### {m.title}")
        lines += [f"- `{t.slug}` — {t.title}: {t.summary}" for t in m.topics.all()]
    return "\n".join(lines)


def system_text() -> str:
    return SYSTEM_PROMPT + "\n\n" + curriculum_text()


def _profile_text(user) -> str:
    p = StudentProfile.for_user(user)
    progress = TopicProgress.objects.filter(user=user).select_related("topic").order_by("topic__module__order", "topic__order")
    prog = "\n".join(f"- `{tp.topic.slug}` ({tp.topic.title}): {tp.status}" for tp in progress) or "- (niciun subiect încă)"
    legacy = ""
    if p.topics:
        legacy = (
            "\nSubiecte notate în formatul vechi (mută-le în curriculum cu `record_progress`, la subiectele potrivite):\n"
            + "\n".join(f"- {t.get('topic')}: {t.get('status')}" for t in p.topics if isinstance(t, dict))
        )
    if p.is_empty() and not progress:
        return "## Profilul elevului\n(gol — elev nou. Începe cu evaluarea nivelului.)"
    return (
        "## Profilul elevului\n"
        f"Nivel: {p.level or '-'}\nRezumat: {p.summary or '-'}\nObiective: {p.goals or '-'}\n"
        f"Puncte forte: {p.strengths or '-'}\nDe lucrat: {p.weaknesses or '-'}\n"
        f"Progres în curriculum:\n{prog}{legacy}"
    )


def _curriculum_position(user, project: str) -> str:
    """Unde e elevul în curriculum + reamintirea că sumarul din stânga depinde de `record_progress`."""
    opened = StudentProfile.objects.filter(user=user).values_list("current_topic", flat=True).first()
    if opened:
        topic = Topic.objects.select_related("module").get(pk=opened)
        st = TopicProgress.objects.filter(user=user, topic=topic).values_list("status", flat=True).first() or STATUS_TODO
        main = chapters.ensure(user, project, topic)
        where = f"Lecția deschisă acum de elev: `{topic.slug}` ({topic.title}) — {st}. " + (
            f"Fișierul capitolului: `{main}`.{_exercise_note(topic)}" if main else
            "Lecție Django: nu are fișier de capitol. " + _django_projects_note(user, project)
        )
        return where + (
            " Sumarul se actualizează doar prin `record_progress`, pe subiectul care acoperă conceptul exersat: "
            "exercițiu rezolvat corect (îl feliciți) → „învățat”, în acest răspuns."
        )
    tp = (
        TopicProgress.objects.filter(user=user, status=STATUS_DOING)
        .select_related("topic").order_by("-updated_at").first()
    )
    if tp:
        main = chapters.ensure(user, project, tp.topic)
        where = f"Pasul activ în sumarul elevului: `{tp.topic.slug}` ({tp.topic.title}) — în lucru. " + (
            f"Fișierul capitolului: `{main}` (exercițiile lui se scriu acolo).{_exercise_note(tp.topic)}" if main else
            "Lecție Django: nu are fișier de capitol. " + _django_projects_note(user, project)
        )
    else:
        done = set(TopicProgress.objects.filter(user=user, status=STATUS_DONE).values_list("topic_id", flat=True))
        nxt = Topic.objects.exclude(id__in=done).select_related("module").first()
        where = "Niciun subiect activ în sumarul elevului." + (
            f" Primul subiect neînvățat, în ordinea curriculumului: `{nxt.slug}` ({nxt.title}) — doar orientativ; "
            "dacă lucrați la alt concept, folosește subiectul care îl acoperă." if nxt else ""
        )
    return (
        where + " Sumarul se actualizează doar prin `record_progress`, pe subiectul care acoperă conceptul exersat: "
        "subiect nou început → „în lucru”; "
        "exercițiu rezolvat corect (îl feliciți) → „învățat”, în acest răspuns."
    )


def _exercise_note(topic: Topic) -> str:
    path = chapters.exercise_path(topic)
    return (
        f" Lecția are un exercițiu fix, scris în `{path}`; până îl rezolvă elevul, îl verifică automat aplicația "
        "(teste și baloane), nu tu. Până atunci nu-i da alte sarcini în acest capitol: trimite-l la exercițiul "
        "lecției (enunțul e în lecție, la „Exercițiu”). După ce e rezolvat, fișierul e liber pentru sarcinile tale."
        if path else ""
    )


def _record_progress(user, project: str, args: dict, events: list) -> tuple[str, bool]:
    slug, status, comment = args.get("topic"), args.get("status"), args.get("comment")
    if status == "stăpânit":  # denumirea veche, poate apărea din istoricul conversațiilor
        status = STATUS_DONE
    if not isinstance(slug, str) or status not in (STATUS_DOING, STATUS_DONE) or not isinstance(comment, str):
        return _err("`topic` (slug), `status` („în lucru”/„învățat”) și `comment` sunt obligatorii"), True
    topic = Topic.objects.filter(slug=slug.strip().strip("`")).first()
    if not topic:
        return _err(f"subiect necunoscut: {slug}. Folosește un slug din curriculum."), True

    code, path, start = "", "", None
    if isinstance(args.get("path"), str) and args["path"].strip():
        f = workspace.read_file(user, project, args["path"])
        if not f["binary"]:
            path = f["path"]
            lines = f["content"].split("\n")
            try:
                start = max(int(args.get("start_line") or 1), 1)
                end = min(int(args.get("end_line") or len(lines)), len(lines))
            except (TypeError, ValueError):
                start, end = 1, len(lines)
            code = "\n".join(lines[start - 1:end])[:MAX_EVIDENCE_CHARS]

    tp = TopicProgress.objects.filter(user=user, topic=topic).first()
    starting = status == STATUS_DOING and not code
    if not starting:  # simplul „am început subiectul” nu e o dovadă de lucru
        TopicEvidence.objects.create(
            user=user, topic=topic, status=status, comment=comment[:2000],
            project=project, path=path, start_line=start, code=code,
        )
    if tp and tp.status == STATUS_DONE and status == STATUS_DOING:
        status = STATUS_DONE  # o recapitulare nu scoate bifa unui subiect deja învățat
    TopicProgress.objects.update_or_create(user=user, topic=topic, defaults={"status": status})
    p = StudentProfile.for_user(user)
    if p.topics:  # după prima salvare în curriculum, lista veche nu mai e necesară
        p.topics = []
    p.save()  # marchează profilul ca actualizat (pentru reamintiri)
    events.append({"type": "progress", "topic": topic.title, "status": status})
    result = f"Salvat: {topic.title} → {status}" + (f" (cu codul din {path})" if path else "") + "."
    if status == STATUS_DOING:
        # Capitolul activ primește folderul lui de cod; elevul îl deschide când vrea („Următorul pas”, sumarul).
        main = chapters.ensure(user, project, topic)
        if main:
            events.append({"type": "chapter", "path": main, "topic": topic.title})
            result += (
                f" Fișierul acestui capitol: `{main}`. Editorul NU trece singur la el: elevul decide când, apăsând "
                "„Următorul pas” sau lecția din sumar; spune-i asta. Exercițiile pentru acest subiect se scriu "
                "acolo — referă-te la el, nu la fișierele altor capitole."
                + _exercise_note(topic)
            )
        else:
            result += " Lecție Django: fără fișier de capitol. " + _django_projects_note(user, project)
    elif status == STATUS_DONE:
        result += _next_active_note(user)
    return result, False


def _django_projects_note(user, project: str) -> str:
    """Unde se lucrează la Django: proiectul cu `manage.py`, oricum l-a numit elevul (lecțiile îi spun `blog`)."""
    found = workspace.django_projects(user)
    if project in found:
        return f"Proiectul curent, `{project}`, e proiectul Django al elevului: exercițiile se fac aici."
    if found:
        names = ", ".join(f"`{p}`" for p in found)
        return f"Proiectul curent nu e un proiect Django; proiectele Django ale elevului: {names}. Trimite-l acolo."
    return ("Elevul n-are încă un proiect Django: un proiect PyTutor nou (lecțiile îl numesc `blog`), "
            "apoi `django-admin startproject blog_proiect .` în terminalul lui.")


def _next_active_note(user) -> str:
    """După „învățat”, sumarul marchează alt subiect ca pas activ (aceeași regulă ca în app.js: ultimul subiect
    „în lucru”, altfel primul neînvățat). Editorul nu se mută: elevul decide. Tutorele trebuie să știe care e
    pasul, ca să nu propună altceva."""
    doing = (
        TopicProgress.objects.filter(user=user, status=STATUS_DOING)
        .select_related("topic").order_by("-updated_at").first()
    )
    if doing:
        nxt, why = doing.topic, "ultimul subiect rămas „în lucru”"
    else:
        done = TopicProgress.objects.filter(user=user, status=STATUS_DONE).values_list("topic_id", flat=True)
        nxt = Topic.objects.exclude(id__in=list(done)).order_by("module__order", "order").first()
        why = "primul subiect neînvățat"
        if not nxt:
            return " Elevul a terminat tot curriculumul."
    return (
        f" Sumarul elevului arată acum ca pas următor `{nxt.slug}` ({nxt.title}) — {why}. Propune-l, dar nu "
        f"începe tu lecția: elevul alege când trece la ea, cu „Următorul pas” sau din sumar. Dacă e mai potrivit alt "
        f"subiect (continuarea firească a celui terminat sau ce a cerut elevul), apelează `record_progress` cu "
        f"„în lucru” pe el ÎN ACELAȘI răspuns, ca „Următorul pas” să ducă acolo."
    )


def _err(msg: str) -> str:
    return json.dumps({"error": msg}, ensure_ascii=False)


def _run_tool(user, project: str, name: str, args, events: list) -> tuple[str, bool]:
    """Execută o unealtă. Returnează (rezultat, is_error) și adaugă evenimente pentru UI."""
    if not isinstance(args, dict):
        return _err("input invalid"), True
    try:
        if name == "list_files":
            return workspace.flat_listing(user, project), False
        if name == "read_file":
            path = args.get("path")
            if not isinstance(path, str):
                return _err("lipsește `path`"), True
            f = workspace.read_file(user, project, path)
            if f["binary"]:
                return _err(f"{path}: {f.get('reason', 'binar')}, nu pot afișa"), True
            return f"Fișier: {f['path']}\n{_numbered(f['content'])}", False
        if name == "write_file":
            path, content = args.get("path"), args.get("content")
            if not isinstance(path, str) or not isinstance(content, str):
                return _err("`path` și `content` trebuie să fie text"), True
            rel = workspace.write_file(user, project, path, content)
            chapters.sync(user, project, rel)
            events.append({"type": "files_changed", "paths": [rel]})
            return f"Am scris {rel} ({len(content)} caractere).", False
        if name == "annotate_code":
            path, notes = args.get("path"), args.get("notes")
            if not isinstance(path, str) or not isinstance(notes, list):
                return _err("`path` (text) și `notes` (listă) sunt obligatorii"), True
            f = workspace.read_file(user, project, path)
            if f["binary"]:
                return _err(f"{path} nu e un fișier text"), True
            n_lines = f["content"].count("\n") + 1
            clean = []
            for n in notes[:12]:
                if not isinstance(n, dict) or not isinstance(n.get("text"), str):
                    continue
                try:
                    line = min(max(int(n.get("line", 1)), 1), n_lines)
                    end = min(max(int(n.get("end_line") or line), line), n_lines)
                except (TypeError, ValueError):
                    continue
                clean.append({
                    "line": line,
                    "end_line": end,
                    "title": str(n.get("title") or f"Linia {line}")[:80],
                    "text": n["text"][:2000],
                })
            if clean:
                CodeAnnotation.objects.update_or_create(
                    user=user, project=project, path=f["path"], defaults={"notes": clean}
                )
            else:
                existed, _ = CodeAnnotation.objects.filter(user=user, project=project, path=f["path"]).delete()
                if not existed:
                    return NO_NOTES_RESULT.format(path=f["path"]), False
            events.append({"type": "annotations", "path": f["path"], "notes": clean})
            if not clean:
                return f"Am șters explicațiile din {f['path']}.", False
            return (
                f"Am pus {len(clean)} baloane în {f['path']} (fișierul are {n_lines} linii). "
                "Elevul le deschide pe rând din editor. În panou NU repeta ce scrie în ele (nici rezumat, nici "
                "listă de probleme pe linii): 1–2 propoziții care îl trimit la baloane și spun ce are de făcut, "
                "de exemplu „Deschide baloanele din editor, citește explicațiile și corectează codul, apoi apasă **Rulează și verifică**.”",
                False,
            )
        if name == "get_terminal_output":
            sess = runner.get(user, project)
            out = runner.tail(user, project) or "(terminal gol)"
            state = "rulează încă" if sess.running() else f"terminat (cod {sess.returncode})"
            return f"Ultima comandă: {sess.command or '-'} — {state}\n---\n{out}", False
        if name == "update_student_profile":
            p = StudentProfile.for_user(user)
            for field in ("level", "summary", "goals", "strengths", "weaknesses"):
                if isinstance(args.get(field), str):
                    setattr(p, field, args[field])
            p.save()
            events.append({"type": "profile", "profile": p.as_dict()})
            return "Profil actualizat.", False
        if name == "record_progress":
            return _record_progress(user, project, args, events)
        if name == "run_file":
            path = args.get("path")
            if not isinstance(path, str) or not path.endswith(".py"):
                return _err("`path` trebuie să fie un fișier .py"), True
            stdin = args.get("stdin") if isinstance(args.get("stdin"), str) else ""
            try:
                rc, out = runner.run_capture(user, project, path, stdin)
            except RuntimeError as e:
                return _err(str(e)), True
            status = "oprit (timeout)" if rc is None else ("OK" if rc == 0 else f"EROARE (cod {rc})")
            return f"$ python {path}\nRezultat: {status}\n---\n{out or '(fără output)'}", False
    except workspace.WorkspaceError as e:
        return _err(str(e)), True
    return _err(f"unealtă necunoscută: {name}"), True


TOOL_LABELS = {
    "list_files": "Mă uit prin proiect",
    "read_file": "Citesc",
    "write_file": "Scriu",
    "get_terminal_output": "Mă uit în terminal",
    "run_file": "Rulez",
    "record_progress": "Salvez progresul",
    "annotate_code": "Am pus explicații în",
    "update_student_profile": "Notez progresul tău",
}


def _terminal_info(user) -> str:
    if sandbox.enabled():
        return (
            "Terminalul elevului rulează într-un container Linux izolat (Python 3.12, Django instalat); "
            "proiectul curent e folderul de lucru. Pentru un server Django: "
            "`python manage.py runserver 0.0.0.0:8000`, apoi elevul îl deschide la "
            f"{sandbox.server_url(user)} (NU la 127.0.0.1:8000, acolo e PyTutor)."
        )
    return (
        "Terminalul rulează direct pe calculatorul elevului (Windows), în folderul proiectului. "
        "Pentru un server Django: `python manage.py runserver 8001` (portul 8000 e ocupat de PyTutor), "
        "apoi http://127.0.0.1:8001."
    )


def _numbered(content: str) -> str:
    return "\n".join(f"{i:4} | {line}" for i, line in enumerate(content.split("\n"), 1))


def _open_file_snapshot(user, project: str, path: str) -> str:
    """Conținutul fișierului deschis, numerotat — ca baloanele să nimerească liniile exacte."""
    try:
        f = workspace.read_file(user, project, path)
    except workspace.WorkspaceError:
        return f"Fișier deschis în editor: {path} (nu mai există)"
    if f["binary"]:
        return f"Fișier deschis în editor: {f['path']} (binar)"
    if len(f["content"]) > MAX_SNAPSHOT_CHARS:
        return f"Fișier deschis în editor: {f['path']} (mare — citește-l cu `read_file`)"
    return f"Fișier deschis în editor: {f['path']} — conținutul actual, cu numere de linie:\n{_numbered(f['content'])}"


PROFILE_STALE_AFTER = 6  # mesaje ale elevului fără actualizare de profil, după care insistăm


def _profile_reminder(user) -> str:
    """Plasă de siguranță: unele modele „uită” să actualizeze profilul doar din promptul de sistem."""
    p = StudentProfile.for_user(user)
    since = ChatMessage.objects.filter(
        conversation__user=user, role="user", is_tool_result=False, created_at__gt=p.updated_at
    ).count()
    if p.is_empty() and since >= 1:
        return (
            "IMPORTANT: profilul elevului e încă GOL, deși ați vorbit deja. În acest răspuns apelează "
            "`update_student_profile` cu tot ce știi despre el din conversație (cel puțin `level` și `summary`; "
            "dacă încă nu știi destul, pune nivelul estimat și întreabă-l ce-ți lipsește)."
        )
    if not p.is_empty() and since >= PROFILE_STALE_AFTER:
        return (
            f"IMPORTANT: profilul n-a mai fost actualizat de {since} mesaje. În acest răspuns apelează "
            "`update_student_profile` cu progresul recent (`topics`, eventual `level`, `strengths`, `weaknesses`)."
        )
    return ""


def _last_run_text(user, project: str, open_file) -> str:
    """Ultima comandă din terminalul elevului, ca tutorele să nu declare corect un cod care crapă."""
    run = runner.last_run(user, project)
    if not run:
        return "Terminalul elevului: nicio comandă rulată încă în acest proiect."
    if run["running"]:
        state = "rulează încă"
    elif run["returncode"] == 0:
        state = "terminată cu succes (cod 0)"
    else:
        state = f"EȘUATĂ (cod {run['returncode']})"
    note = ""
    if isinstance(open_file, str):
        try:
            mtime = workspace.safe_path(user, project, open_file).stat().st_mtime
            if mtime > run["started_at"]:
                note = f"\nAtenție: {open_file} a fost modificat DUPĂ această rulare — rezultatul poate fi depășit."
        except (workspace.WorkspaceError, OSError):
            pass
    return (
        f"Ultima comandă din terminalul elevului: `{run['command']}` — {state}.{note}\n"
        f"Finalul output-ului:\n```\n{run['output'].strip()[-2500:]}\n```"
    )


def _context_block(user, project: str, ctx: dict) -> str:
    parts = [f"Elev: {user.get_username()}", f"Proiect curent: {project}", _terminal_info(user)]
    parts.append(
        "Amintire: ce ține de anumite linii din codul lui → baloane (`annotate_code`) pe acele linii, "
        "iar în panou doar 1–2 propoziții care trimit la baloane, FĂRĂ să repete ce scrie în ele. "
        "Cod corect = fără baloane (șterge-le pe cele vechi), doar un mesaj scurt. "
        "Ultima propoziție e pasul concret („…apoi apasă **Rulează și verifică**” pentru un fișier .py, "
        "„…apoi apasă **Următorul pas**” după o comandă în terminal) — NU „spune-mi când ai terminat”, "
        "„confirmă dacă vezi…”, „revino cu…”: vezi singur fișierele, terminalul și rulările."
    )
    parts.append(_curriculum_position(user, project))
    reminder = _profile_reminder(user)
    if reminder:
        parts.append(reminder)
    if ctx.get("open_file"):
        parts.append(_open_file_snapshot(user, project, str(ctx["open_file"])))
    run = _last_run_text(user, project, ctx.get("open_file"))
    if run:
        parts.append(run)
    if ctx.get("selection"):
        parts.append(f"Elevul a selectat acest cod:\n```\n{ctx['selection'][:4000]}\n```")
    if ctx.get("terminal"):
        parts.append(f"Output din terminal atașat de elev:\n```\n{ctx['terminal'][-6000:]}\n```")
    return "<context>\n" + "\n".join(parts) + "\n</context>"


# ---------------------------------------------------------------- Istoric scurtat (rezumat + ultimele mesaje)
# Istoricul se retrimite la AI la fiecare apel, deci o conversație lungă costă tot mai mult. Când partea
# trimisă depășește COMPACT_AT_CHARS, mesajele vechi sunt rezumate de un model mic și nu se mai trimit;
# rămân ultimele ~KEEP_CHARS. Rezumatul se reface rar (în trepte), ca prefixul trimis să rămână stabil
# între mesaje și să prindă cache-ul. În interfață elevul vede în continuare toată conversația.
COMPACT_AT_CHARS = 24_000   # ~7k tokeni de istoric (româna are mulți tokeni pe caracter)
KEEP_CHARS = 8_000          # ~2.5k tokeni păstrați integral (ultimele câteva schimburi)

SUMMARY_PROMPT = """Rezumi o conversație dintre un tutore de Python/Django și elevul lui, ca tutorele să poată continua fără mesajele vechi.
Scrie în română, concis (max. 350 de cuvinte), ca listă cu puncte. Include:
- ce subiecte s-au predat și ce a înțeles elevul;
- exercițiile date: enunțul pe scurt, fișierul, dacă au fost rezolvate sau unde s-a blocat;
- greșelile tipice ale elevului și ce i s-a explicat despre ele;
- ce s-a convenit (preferințe ale elevului, ce urmează);
- sarcina la care lucrează ACUM, dacă există.
Nu inventa nimic. Dacă primești și un rezumat anterior, integrează-l."""


def _msg_chars(m: ChatMessage) -> int:
    return len(json.dumps(m.content, ensure_ascii=False))


def _transcript(msgs: list[ChatMessage]) -> str:
    """Textul conversației pentru rezumat: fără blocul <context>, cu uneltele pe scurt."""
    lines = []
    for m in msgs:
        for b in m.content if isinstance(m.content, list) else []:
            t = b.get("type")
            if t == "text" and not b.get("text", "").startswith("<context>"):
                who = "Elev" if m.role == "user" else "Tutore"
                lines.append(f"{who}: {b['text'][:3000]}")
            elif t == "tool_use":
                lines.append(f"[Tutorele folosește {b.get('name')}: {json.dumps(b.get('input', {}), ensure_ascii=False)[:300]}]")
            elif t == "tool_result":
                lines.append(f"[Rezultat: {str(b.get('content', ''))[:300]}]")
    return "\n".join(lines)


def _summarize(user, project: str, previous: str, msgs: list[ChatMessage]) -> str | None:
    prompt = (f"Rezumat anterior:\n{previous}\n\n" if previous else "") + "Conversația:\n" + _transcript(msgs)[-60_000:]
    try:
        if settings.PYTUTOR_PROVIDER == "openai":
            r = openai.OpenAI().chat.completions.create(
                model=settings.OPENAI_CHECK_MODEL,
                messages=[{"role": "system", "content": SUMMARY_PROMPT}, {"role": "user", "content": prompt}],
                max_tokens=900,
            )
            details = getattr(r.usage, "prompt_tokens_details", None)
            cached = (getattr(details, "cached_tokens", 0) or 0) if details else 0
            usage.record(
                user, project, "openai", r.model or settings.OPENAI_CHECK_MODEL,
                input_tokens=(r.usage.prompt_tokens or 0) - cached,
                output_tokens=r.usage.completion_tokens or 0, cache_read_tokens=cached,
            )
            return (r.choices[0].message.content or "").strip() or None
        r = anthropic.Anthropic().messages.create(
            model=settings.ANTHROPIC_CHECK_MODEL, max_tokens=900, system=SUMMARY_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        usage.record(user, project, "anthropic", r.model,
                     input_tokens=r.usage.input_tokens or 0, output_tokens=r.usage.output_tokens or 0)
        return "".join(b.text for b in r.content if b.type == "text").strip() or None
    except (anthropic.APIError, openai.OpenAIError):
        return None  # data viitoare încercăm din nou; până atunci trimitem istoricul întreg


def _maybe_compact(user, project: str, conv: Conversation) -> None:
    msgs = list(conv.messages.filter(id__gt=conv.summary_upto))
    sizes = [_msg_chars(m) for m in msgs]
    if sum(sizes) <= COMPACT_AT_CHARS:
        return
    # Tăiem doar înaintea unui mesaj al elevului (nu în mijlocul unei perechi unealtă/rezultat)
    # și păstrăm la coadă ~KEEP_CHARS, cel puțin ultimele două mesaje ale elevului.
    starts = [i for i, m in enumerate(msgs) if m.role == "user" and not m.is_tool_result]
    cut, kept = None, 0
    for i in range(len(msgs) - 1, -1, -1):
        kept += sizes[i]
        if i in starts and kept >= KEEP_CHARS and len([j for j in starts if j >= i]) >= 2:
            cut = i
            break
    if not cut:
        return
    summary = _summarize(user, project, conv.summary, msgs[:cut])
    if summary:
        conv.summary = summary
        conv.summary_upto = msgs[cut - 1].id
        conv.save(update_fields=["summary", "summary_upto"])


def _api_history(conv: Conversation) -> list[ChatMessage]:
    """Mesajele trimise la AI: cele de după rezumat."""
    return list(conv.messages.filter(id__gt=conv.summary_upto))


def _summary_text(conv: Conversation) -> str:
    return (
        "## Rezumatul conversației de până acum (mesajele vechi nu mai sunt atașate)\n" + conv.summary
        if conv.summary else ""
    )


def history(user, project: str) -> list[ChatMessage]:
    conv, _ = Conversation.objects.get_or_create(user=user, project=project)
    return list(conv.messages.all())


def ui_messages(user, project: str) -> list[dict]:
    """Mesajele în forma afișată în chat."""
    out = []
    msgs = history(user, project)
    # Ștergerile de bule pe fișiere care nu aveau bule nu se afișează (rezultatul uneltei o spune).
    silent = {
        b.get("tool_use_id")
        for m in msgs if m.is_tool_result
        for b in m.content
        if isinstance(b, dict) and str(b.get("content", "")).startswith("Nu existau bule")
    }
    for m in msgs:
        if m.is_tool_result:
            continue
        if m.role == "user":
            out.append({"role": "user", "text": m.ui_text})
            continue
        texts, tools = [], []
        for b in m.content:
            if b.get("type") == "text":
                texts.append(b.get("text", ""))
            elif b.get("type") == "tool_use" and b.get("id") not in silent:
                tools.append(_tool_entry(b.get("name"), b.get("input")))
        # Comasăm runde consecutive ale asistentului într-o singură bulă.
        if out and out[-1]["role"] == "assistant":
            out[-1]["text"] += ("\n\n" if out[-1]["text"] and texts else "") + "\n\n".join(texts)
            out[-1]["tools"] += tools
        else:
            out.append({"role": "assistant", "text": "\n\n".join(texts), "tools": tools})
    return out


def _tool_label(name, args) -> str:
    label = TOOL_LABELS.get(name, name)
    if isinstance(args, dict) and isinstance(args.get("path"), str):
        label += f" {args['path']}"
    return label


NO_NOTES_RESULT = "Nu existau bule în {path}; nimic de șters."


def _clears_nothing(user, project: str, name, args) -> bool:
    """`annotate_code` cu `notes` gol pe un fișier fără bule: nu are rost să-i arătăm elevului."""
    if name != "annotate_code" or not isinstance(args, dict) or args.get("notes") or not isinstance(args.get("path"), str):
        return False
    try:
        rel = workspace.rel_of(user, project, workspace.safe_path(user, project, args["path"]))
    except workspace.WorkspaceError:
        return False
    return not CodeAnnotation.objects.filter(user=user, project=project, path=rel).exists()


def _tool_entry(name, args) -> dict:
    """Linia afișată în chat pentru o unealtă; baloanele de cod devin un link spre editor."""
    entry = {"label": _tool_label(name, args)}
    if name == "annotate_code" and isinstance(args, dict) and isinstance(args.get("path"), str):
        if args.get("notes"):
            entry["notes_path"] = args["path"]
        else:
            entry["label"] = f"Am șters bulele din {args['path']}"
    return entry


def chat_stream(user, project: str, user_text: str, ctx: dict, mode: str = "chat") -> Iterator[dict]:
    """Trimite mesajul elevului și emite evenimente pentru UI pe măsură ce vine răspunsul.

    Istoricul e salvat mereu în formatul de blocuri Anthropic (text / tool_use / tool_result);
    backend-ul OpenAI îl convertește la trimitere, așa că poți schimba furnizorul oricând.

    `mode="check"` („Rulează și verifică”): modelul mic, cu un context redus (sarcina, fișierul, rularea)
    și doar uneltele pentru baloane și progres. Întrebările libere rămân la modelul mare.
    """
    check = mode == "check"
    conv, _ = Conversation.objects.get_or_create(user=user, project=project)
    if check:
        empty = _empty_file_reply(user, project, ctx.get("open_file"))
        if empty:
            ChatMessage.objects.create(conversation=conv, role="user", ui_text=user_text,
                                       content=[{"type": "text", "text": user_text}])
            ChatMessage.objects.create(conversation=conv, role="assistant", content=[{"type": "text", "text": empty}])
            yield {"type": "text", "text": empty}
            yield {"type": "done"}
            return
    topic = _check_topic(user, ctx.get("open_file")) if check else None
    previous = _last_tutor_text(conv) if check else ""
    user_msg = ChatMessage.objects.create(
        conversation=conv,
        role="user",
        content=[
            {"type": "text", "text": _check_context(user, project, ctx, previous) if check
             else _context_block(user, project, ctx)},
            {"type": "text", "text": user_text},
        ],
        ui_text=user_text,
    )
    if not check:
        _maybe_compact(user, project, conv)
    rounds = _openai_rounds if settings.PYTUTOR_PROVIDER == "openai" else _anthropic_rounds
    answered = False
    reply, progress_saved = "", False
    for ev in rounds(user, project, conv, since=user_msg.id if check else None, topic=topic):
        if ev["type"] == "_saved":
            answered = True
            continue
        if ev.get("fatal") and not answered:
            # N-a venit niciun răspuns: scoatem mesajul din istoric ca să poată fi retrimis curat.
            user_msg.delete()
        if ev["type"] == "text":
            reply += ev["text"]
        elif ev["type"] == "progress":
            progress_saved = True
        yield ev
        if ev.get("fatal"):
            return
    if reply.strip() and not progress_saved and (topic or not check):
        yield from _progress_check(user, project, user_text, reply, ctx.get("open_file"), only=topic)
    yield {"type": "done"}


def _empty_file_reply(user, project: str, open_file) -> str | None:
    """„Verifică-mi codul” pe un fișier .py fără cod (doar comentarii): răspunsul se știe, fără AI."""
    if not isinstance(open_file, str) or not open_file.endswith(".py"):
        return None
    try:
        f = workspace.read_file(user, project, open_file)
    except workspace.WorkspaceError:
        return None
    if f["binary"] or not verificare.fara_cod(f["content"]):
        return None
    return (f"În `{f['path']}` nu e încă niciun cod: doar comentarii. Scrie programul sub ele "
            "(sau cere-mi un exercițiu cu **Exercițiu nou**), apoi apasă **Rulează și verifică**.")


# ---------------------------------------------------------------- Plasă de siguranță pentru progres

PROGRESS_CHECK_PROMPT = """Ții evidența progresului unui elev într-un curriculum de Python/Django.
Primești ultimul mesaj al elevului și răspunsul tutorelui. Decide dacă schimbul ăsta mută elevul în curriculum:
- „învățat”: tutorele spune clar că elevul a rezolvat CORECT exercițiul / sarcina (îl felicită, confirmă că merge).
- „în lucru”: tutorele începe un subiect (îl explică sau dă un exercițiu pe el) ori elevul a încercat, dar încă nu e corect.
- null: nimic din astea (salut, întrebări despre elev, discuții care nu țin de un subiect anume).
Alege subiectul al cărui conținut acoperă conceptul exersat. Răspunde DOAR cu JSON:
{"topic": "<slug sau null>", "status": "în lucru" | "învățat" | null, "comment": "<1-2 propoziții către elev, în română>"}"""


def _progress_check(user, project: str, user_text: str, reply: str, open_file,
                    only: Topic | None = None) -> Iterator[dict]:
    """Tutorele n-a apelat `record_progress`: un model mic decide dacă s-a început/terminat un subiect.

    Fără asta, bifele din sumarul elevului ar depinde de cât de ascultător e modelul principal.
    `only` (la „Rulează și verifică”): se poate doar bifa „învățat” lecția la care lucrează elevul.
    """
    active = (
        TopicProgress.objects.filter(user=user, status=STATUS_DOING)
        .select_related("topic").order_by("-updated_at").first()
    )
    prompt = (
        f"{curriculum_text()}\n\n"
        f"Subiectul activ acum: {f'`{active.topic.slug}`' if active else 'niciunul'}\n\n"
        f"Elevul:\n{user_text[:3000]}\n\nTutorele:\n{reply[:6000]}"
    )
    try:
        if settings.PYTUTOR_PROVIDER == "openai":
            r = openai.OpenAI().chat.completions.create(
                model=settings.OPENAI_CHECK_MODEL,
                messages=[{"role": "system", "content": PROGRESS_CHECK_PROMPT}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=300,
            )
            details = getattr(r.usage, "prompt_tokens_details", None)
            cached = (getattr(details, "cached_tokens", 0) or 0) if details else 0
            usage.record(
                user, project, "openai", r.model or settings.OPENAI_CHECK_MODEL,
                input_tokens=(r.usage.prompt_tokens or 0) - cached,
                output_tokens=r.usage.completion_tokens or 0, cache_read_tokens=cached,
            )
            raw = r.choices[0].message.content or "{}"
        else:
            r = anthropic.Anthropic().messages.create(
                model=settings.ANTHROPIC_CHECK_MODEL,
                max_tokens=300,
                system=PROGRESS_CHECK_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            usage.record(
                user, project, "anthropic", r.model,
                input_tokens=r.usage.input_tokens or 0, output_tokens=r.usage.output_tokens or 0,
            )
            raw = "".join(b.text for b in r.content if b.type == "text")
            raw = raw[raw.find("{"):raw.rfind("}") + 1] or "{}"
        verdict = json.loads(raw)
    except (anthropic.APIError, openai.OpenAIError, json.JSONDecodeError, AttributeError, TypeError):
        return  # e doar o plasă de siguranță; nu stricăm răspunsul tutorelui

    if not isinstance(verdict, dict):
        return
    slug, status = verdict.get("topic"), verdict.get("status")
    if status == "stăpânit":
        status = STATUS_DONE
    if not isinstance(slug, str) or status not in (STATUS_DOING, STATUS_DONE):
        return
    topic = Topic.objects.filter(slug=slug.strip().strip("`")).first()
    if not topic or (only and (topic != only or status != STATUS_DONE)):
        return
    current = TopicProgress.objects.filter(user=user, topic=topic).values_list("status", flat=True).first()
    if current == status or current == STATUS_DONE:
        return  # nimic nou de arătat
    args = {"topic": topic.slug, "status": status, "comment": str(verdict.get("comment") or "")}
    if status == STATUS_DONE and isinstance(open_file, str) and open_file:
        args["path"] = open_file
    events: list = []
    try:
        _record_progress(user, project, args, events)
    except workspace.WorkspaceError:
        args.pop("path", None)
        _record_progress(user, project, args, events)
    yield from events


# ---------------------------------------------------------------- Verificarea de rutină (model mic)
# „Rulează și verifică” e cel mai des apel: elevul a rulat codul și vrea să știe dacă e bine. Nu are nevoie
# de tot curriculumul, de profil sau de istoricul lung — doar de sarcină, de cod și de rezultat.

CHECK_PROMPT = """Ești PyTutor, tutorele de Python al unui elev începător. Vorbești în română (cu diacritice), cald și direct.
Elevul tocmai a rulat programul. Primești în <context> sarcina (din lecție și/sau ultimul tău mesaj), fișierul cu numere de linie și rezultatul rulării.
Spune dacă programul face ce cere sarcina:
- Corect: felicită-l în 1–2 propoziții, eventual o observație scurtă de stil; șterge baloanele vechi (`annotate_code` cu `notes` gol) și apelează `record_progress` cu „învățat” pe subiectul indicat, cu `path` = fișierul.
- Greșit sau incomplet: pune baloane (`annotate_code`) pe liniile cu probleme — ce e greșit și un indiciu, NU soluția completă. În panou doar 1–2 propoziții care trimit la baloane, iar ultima propoziție e pasul concret: „…apoi apasă **Rulează și verifică**.”
- Programul a crăpat: explică eroarea pe scurt, în balon pe linia ei.
Nu da exerciții noi și nu schimba subiectul: `record_progress` merge doar cu „învățat”, doar pe subiectul indicat. Nu scrie codul în locul lui. Răspuns scurt."""

CHECK_TOOL_NAMES = ("annotate_code", "record_progress")
CHECK_TOOLS = [t for t in TOOLS if t["name"] in CHECK_TOOL_NAMES]
CHECK_MAX_ROUNDS = 3


def _exercise_section(lesson: str) -> str:
    """Secțiunea „## Exercițiu” dintr-o lecție (fără restul lecției)."""
    start = lesson.find("## Exercițiu")
    if start < 0:
        return ""
    end = lesson.find("\n## ", start + 5)
    return lesson[start:end if end > 0 else None].strip()


def _last_tutor_text(conv: Conversation) -> str:
    """Textul ultimului răspuns al tutorelui (poate conține sarcina dată în chat)."""
    texts: list[str] = []
    for m in conv.messages.order_by("-id")[:12]:
        if m.role == "user" and not m.is_tool_result:
            break
        if m.role == "assistant":
            texts[:0] = [b.get("text", "") for b in m.content if b.get("type") == "text"]
    return "\n\n".join(t for t in texts if t).strip()


def _check_topic(user, open_file) -> Topic | None:
    """Lecția la care lucrează elevul când apasă „Rulează și verifică”: a fișierului capitolului deschis,
    altfel lecția curentă (ultima deschisă), altfel ultima „în lucru”."""
    topic = chapters.topic_for_path(open_file) if isinstance(open_file, str) else None
    if topic:
        return topic
    p = StudentProfile.objects.filter(user=user).select_related("current_topic").first()
    if p and p.current_topic:
        return p.current_topic
    tp = (TopicProgress.objects.filter(user=user, status=STATUS_DOING)
          .select_related("topic").order_by("-updated_at").first())
    return tp.topic if tp else None


def _check_progress(user, project: str, args, events: list, topic: Topic | None) -> tuple[str, bool]:
    """`record_progress` la verificarea de rutină: modelul mic poate doar bifa „învățat” lecția verificată,
    nu poate începe sau schimba alte lecții."""
    if not topic:
        return _err("verificarea nu ține de nicio lecție: progresul nu se schimbă"), True
    if not isinstance(args, dict) or args.get("status") != STATUS_DONE:
        return _err("la verificare poți marca doar „învățat”"), True
    if str(args.get("topic", "")).strip("`") != topic.slug:
        return _err(f"la verificare poți marca doar lecția verificată, `{topic.slug}`"), True
    return _record_progress(user, project, args, events)


def _check_context(user, project: str, ctx: dict, previous: str) -> str:
    parts = [f"Elev: {user.get_username()}"]
    open_file = ctx.get("open_file")
    topic = _check_topic(user, open_file)
    if topic:
        parts.append(f"Subiectul: `{topic.slug}` ({topic.title}).")
        # Unde exercițiul lecției are fișierul lui (exercitiu.py, verificat de cod), aici e altă sarcină:
        # o încercare a elevului sau ce i-ai dat în chat.
        section = "" if chapters.exercise_path(topic) else _exercise_section(topic.lesson)
        if section:
            parts.append(f"Exercițiul din lecție:\n{section[:3000]}")
        else:
            parts.append("Fișierul nu e exercițiul fix al lecției: sarcina e cea din ultimul tău mesaj sau ce a "
                         "ales elevul să încerce. Judecă programul după ea; dacă nu e clară, spune doar ce face programul.")
    if previous:
        parts.append(f"Ultimul tău mesaj către elev (poate conține sarcina):\n{previous[-3000:]}")
    if open_file:
        parts.append(_open_file_snapshot(user, project, str(open_file)))
    parts.append(_last_run_text(user, project, open_file))
    return "<context>\n" + "\n\n".join(parts) + "\n</context>"


def formuleaza(user, project: str, verdict: dict, fallback: str) -> str:
    """Transformă verdictul dat de cod într-o frază caldă, cu modelul mic; la orice problemă, `fallback`."""
    prompt = json.dumps(verdict, ensure_ascii=False)[:3000]
    try:
        if settings.PYTUTOR_PROVIDER == "openai":
            r = openai.OpenAI().chat.completions.create(
                model=settings.OPENAI_CHECK_MODEL,
                messages=[{"role": "system", "content": PHRASE_PROMPT}, {"role": "user", "content": prompt}],
                max_tokens=300,
            )
            details = getattr(r.usage, "prompt_tokens_details", None)
            cached = (getattr(details, "cached_tokens", 0) or 0) if details else 0
            usage.record(
                user, project, "openai", r.model or settings.OPENAI_CHECK_MODEL,
                input_tokens=(r.usage.prompt_tokens or 0) - cached,
                output_tokens=r.usage.completion_tokens or 0, cache_read_tokens=cached,
            )
            text = r.choices[0].message.content or ""
        else:
            r = anthropic.Anthropic().messages.create(
                model=settings.ANTHROPIC_CHECK_MODEL, max_tokens=1000, system=PHRASE_PROMPT,
                output_config={"effort": "low"},
                messages=[{"role": "user", "content": prompt}],
            )
            usage.record(user, project, "anthropic", r.model,
                         input_tokens=r.usage.input_tokens or 0, output_tokens=r.usage.output_tokens or 0)
            text = "".join(b.text for b in r.content if b.type == "text")
    except (anthropic.APIError, openai.OpenAIError, TypeError, AttributeError):
        return fallback
    return text.strip() or fallback


PHRASE_PROMPT = """Ești tutorele de Python al unui elev începător. Primești în JSON verdictul verificării automate a exercițiului lui (corect sau greșit, ce s-a așteptat, ce a ieșit, rândul, eroarea explicată, indiciul).
Scrie-i elevului 1–3 propoziții în română (cu diacritice), calde și concrete:
- corect: felicită-l scurt și spune-i că poate trece la lecția următoare;
- greșit: spune exact ce nu se potrivește (folosește valorile din verdict, cu `cod` pentru cod și valori). Explică pe baza lui `de_ce` (ce verifică testul) sau a erorii; adaugă `indiciu` doar dacă e legat de ce a greșit. NU da soluția și nu scrie cod nou.
Fără titluri, fără liste. Termină cu pasul concret, de exemplu „Corectează și apasă din nou **Rulează și verifică**.”"""


def _fatal(message: str) -> dict:
    return {"type": "error", "message": message, "fatal": True}


def _execute_tools(user, project: str, conv: Conversation, calls: list[tuple[str, str, object]],
                   check: bool = False, topic: Topic | None = None) -> Iterator[dict]:
    """Rulează uneltele cerute de model și salvează rezultatele ca mesaj tool_result.
    `check` = verificarea de rutină: progresul se poate schimba doar pe `topic` (vezi `_check_progress`)."""
    results = []
    for call_id, name, args in calls:
        events: list = []
        if not _clears_nothing(user, project, name, args):
            yield {"type": "tool", **_tool_entry(name, args)}
        if check and name == "record_progress":
            result, is_error = _check_progress(user, project, args, events, topic)
        else:
            result, is_error = _run_tool(user, project, name, args, events)
        yield from events
        results.append({"type": "tool_result", "tool_use_id": call_id, "content": result, "is_error": is_error})
    ChatMessage.objects.create(conversation=conv, role="user", content=results, is_tool_result=True)
    yield {"type": "round"}


# ---------------------------------------------------------------- Anthropic (Claude)

def _check_history(conv: Conversation, since: int) -> list[ChatMessage]:
    """Verificarea vede doar tura curentă: mesajul elevului (cu contextul redus) și rundele ei."""
    return list(conv.messages.filter(id__gte=since))


def _anthropic_rounds(user, project: str, conv: Conversation, since: int | None = None,
                      topic: Topic | None = None) -> Iterator[dict]:
    """`since` = id-ul mesajului de la care începe o verificare de rutină (model mic, context redus);
    `topic` = lecția verificată, singura pe care modelul mic o poate bifa."""
    client = anthropic.Anthropic()
    if since is None:
        system = [{"type": "text", "text": system_text(), "cache_control": {"type": "ephemeral"}}]
        if conv.summary:
            system.append({"type": "text", "text": _summary_text(conv)})
        system.append({"type": "text", "text": _profile_text(user)})
        params = dict(
            model=settings.ANTHROPIC_MODEL, max_tokens=64000, system=system, tools=TOOLS,
            thinking={"type": "adaptive"}, output_config={"effort": settings.ANTHROPIC_EFFORT},
            cache_control={"type": "ephemeral"}, betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        )
        history, max_rounds = (lambda: _api_history(conv)), MAX_TOOL_ROUNDS
    else:
        params = dict(
            model=settings.ANTHROPIC_CHECK_MODEL, max_tokens=8000, system=CHECK_PROMPT, tools=CHECK_TOOLS,
            output_config={"effort": "low"},
        )
        history, max_rounds = (lambda: _check_history(conv, since)), CHECK_MAX_ROUNDS
    for _ in range(max_rounds):
        messages = [{"role": m.role, "content": m.content} for m in history()]
        try:
            with client.beta.messages.stream(messages=messages, **params) as stream:
                started_text = False
                for event in stream:
                    if event.type == "text":
                        started_text = True
                        yield {"type": "text", "text": event.text}
                    elif event.type == "content_block_start" and event.content_block.type == "tool_use":
                        yield {"type": "tool_start", "name": event.content_block.name}
                    elif event.type == "content_block_start" and event.content_block.type == "thinking":
                        if not started_text:
                            yield {"type": "thinking"}
                response = stream.get_final_message()
            u = response.usage
            usage.record(
                user, project, "anthropic", response.model,
                input_tokens=u.input_tokens or 0,
                output_tokens=u.output_tokens or 0,
                cache_read_tokens=u.cache_read_input_tokens or 0,
                cache_write_tokens=u.cache_creation_input_tokens or 0,
            )
        except ValueError:
            # JSON de unealtă imposibil de parsat: reîncercăm runda.
            continue
        except anthropic.AuthenticationError:
            yield _fatal("Cheie Anthropic invalidă sau lipsă. Setează ANTHROPIC_API_KEY în fișierul .env.")
            return
        except anthropic.RateLimitError:
            yield _fatal("Limită de cereri atinsă. Încearcă din nou peste un minut.")
            return
        except anthropic.APIStatusError as e:
            yield _fatal(f"Eroare API ({e.status_code}): {e.message}")
            return
        except anthropic.APIConnectionError:
            yield _fatal("Nu mă pot conecta la API. Verifică internetul.")
            return
        except TypeError as e:
            # Fără credențiale, SDK-ul aruncă la construirea antetelor.
            yield _fatal(f"Configurare lipsă: {e}. Setează ANTHROPIC_API_KEY în .env.")
            return

        # to_dict() folosește numele din API (ex. „from” la blocurile de fallback), ca să le putem retrimite.
        content = [b.to_dict(exclude_none=True) for b in response.content]
        ChatMessage.objects.create(conversation=conv, role="assistant", content=content)
        yield {"type": "_saved"}

        if response.stop_reason == "refusal":
            yield {"type": "error", "message": "Modelul a refuzat să răspundă la această cerere."}
            return
        if response.stop_reason == "pause_turn":
            continue
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        if not tool_uses:
            return
        if response.stop_reason == "max_tokens":
            yield {"type": "error", "message": "Răspunsul a fost tăiat (prea lung)."}
            return
        yield from _execute_tools(user, project, conv, [(b.id, b.name, b.input) for b in tool_uses],
                                  check=since is not None, topic=topic)


# ---------------------------------------------------------------- OpenAI

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {"name": t["name"], "description": t["description"], "parameters": t["input_schema"]},
    }
    for t in TOOLS
]
OPENAI_CHECK_TOOLS = [t for t in OPENAI_TOOLS if t["function"]["name"] in CHECK_TOOL_NAMES]


def _to_openai_messages(user, conv: Conversation, since: int | None = None) -> list[dict]:
    """Convertește istoricul (blocuri Anthropic) în mesaje Chat Completions.

    Ordinea contează pentru cache-ul OpenAI (pe prefix): promptul stabil + istoricul sunt la început,
    iar profilul elevului — care se schimbă des — vine la final, ca să nu invalideze tot ce e înainte.
    Cu `since` (verificare de rutină): doar promptul scurt și tura curentă.
    """
    if since is not None:
        return [{"role": "system", "content": CHECK_PROMPT}] + _openai_history(_check_history(conv, since))
    out: list[dict] = [{"role": "system", "content": system_text()}]
    if conv.summary:
        out.append({"role": "system", "content": _summary_text(conv)})
    out += _openai_history(_api_history(conv))
    out.append({"role": "system", "content": _profile_text(user)})
    return out


def _openai_history(msgs: list[ChatMessage]) -> list[dict]:
    out: list[dict] = []
    for m in msgs:
        if m.role == "user" and m.is_tool_result:
            for b in m.content:
                if b.get("type") == "tool_result":
                    out.append({"role": "tool", "tool_call_id": b["tool_use_id"], "content": str(b.get("content", ""))})
        elif m.role == "user":
            text = "\n\n".join(b.get("text", "") for b in m.content if b.get("type") == "text")
            out.append({"role": "user", "content": text})
        else:
            text = "\n\n".join(b.get("text", "") for b in m.content if b.get("type") == "text")
            calls = [
                {
                    "id": b["id"],
                    "type": "function",
                    "function": {"name": b["name"], "arguments": json.dumps(b.get("input", {}), ensure_ascii=False)},
                }
                for b in m.content
                if b.get("type") == "tool_use"
            ]
            msg: dict = {"role": "assistant", "content": text or None}
            if calls:
                msg["tool_calls"] = calls
            out.append(msg)
    return out


_RETENTION = {"ok": True}


def _cache_retention() -> dict:
    return {"prompt_cache_retention": "24h"} if _RETENTION["ok"] else {}


def _openai_rounds(user, project: str, conv: Conversation, since: int | None = None,
                   topic: Topic | None = None) -> Iterator[dict]:
    try:
        client = openai.OpenAI()
    except openai.OpenAIError as e:
        yield _fatal(f"Configurare OpenAI lipsă: {e}. Setează OPENAI_API_KEY în .env.")
        return
    check = since is not None
    model = settings.OPENAI_CHECK_MODEL if check else settings.OPENAI_MODEL
    for _ in range(CHECK_MAX_ROUNDS if check else MAX_TOOL_ROUNDS):
        text = ""
        calls: dict[int, dict] = {}
        finish = None
        oa_usage, oa_model = None, None
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=_to_openai_messages(user, conv, since),
                tools=OPENAI_CHECK_TOOLS if check else OPENAI_TOOLS,
                stream=True,
                stream_options={"include_usage": True},
                # Cache-ul OpenAI ține implicit câteva minute; cu 24h, o pauză nu mai face primul
                # apel de după ea să plătească tot istoricul la preț întreg. Cheia ține cererile
                # aceleiași conversații pe același cache.
                prompt_cache_key=f"pytutor-u{user.pk}-{project}{'-check' if check else ''}"[:64],
                **_cache_retention(),
            )
            for chunk in stream:
                if chunk.usage:
                    oa_usage, oa_model = chunk.usage, chunk.model
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                delta = choice.delta
                if delta.content:
                    text += delta.content
                    yield {"type": "text", "text": delta.content}
                for tc in delta.tool_calls or []:
                    c = calls.setdefault(tc.index, {"id": "", "name": "", "args": ""})
                    if tc.id:
                        c["id"] = tc.id
                    if tc.function and tc.function.name:
                        c["name"] += tc.function.name
                        yield {"type": "tool_start", "name": c["name"]}
                    if tc.function and tc.function.arguments:
                        c["args"] += tc.function.arguments
                finish = choice.finish_reason or finish
        except openai.AuthenticationError:
            yield _fatal("Cheie OpenAI invalidă sau lipsă. Setează OPENAI_API_KEY în fișierul .env.")
            return
        except openai.RateLimitError:
            yield _fatal("Limită de cereri OpenAI atinsă (sau credit epuizat). Încearcă mai târziu.")
            return
        except openai.BadRequestError as e:
            if _RETENTION["ok"] and "prompt_cache" in str(e) and not text:
                _RETENTION["ok"] = False  # modelul nu acceptă cache-ul de 24h: continuăm fără el
                continue
            yield _fatal(f"Eroare OpenAI ({e.status_code}): {e.message}")
            return
        except openai.APIStatusError as e:
            yield _fatal(f"Eroare OpenAI ({e.status_code}): {e.message}")
            return
        except openai.APIConnectionError:
            yield _fatal("Nu mă pot conecta la OpenAI. Verifică internetul.")
            return

        if oa_usage:
            details = getattr(oa_usage, "prompt_tokens_details", None)
            cached = (getattr(details, "cached_tokens", 0) or 0) if details else 0
            usage.record(
                user, project, "openai", oa_model or model,
                input_tokens=(oa_usage.prompt_tokens or 0) - cached,
                output_tokens=oa_usage.completion_tokens or 0,
                cache_read_tokens=cached,
            )

        parsed = []
        for i in sorted(calls):
            c = calls[i]
            try:
                args = json.loads(c["args"] or "{}")
            except json.JSONDecodeError:
                args = None  # _run_tool răspunde cu „input invalid”, iar modelul poate reîncerca
            parsed.append((c["id"] or f"call_{i}", c["name"], args))

        content: list[dict] = []
        if text:
            content.append({"type": "text", "text": text})
        content += [
            {"type": "tool_use", "id": cid, "name": name, "input": args if isinstance(args, dict) else {}}
            for cid, name, args in parsed
        ]
        if not content:
            yield _fatal("Modelul nu a returnat niciun răspuns.")
            return
        ChatMessage.objects.create(conversation=conv, role="assistant", content=content)
        yield {"type": "_saved"}

        if finish == "length":
            yield {"type": "error", "message": "Răspunsul a fost tăiat (prea lung)."}
            return
        if finish == "content_filter":
            yield {"type": "error", "message": "Răspunsul a fost blocat de filtrul de conținut."}
            return
        if not parsed:
            return
        yield from _execute_tools(user, project, conv, parsed, check=check, topic=topic)


# ---------------------------------------------------------------- Lecții (scrise de AI, salvate în baza de date)

LESSON_PROMPT = """Ești autorul unui curs de Python și Django în limba română (cu diacritice), pentru oameni care vor să devină programatori.
Scrii lecția completă pentru un singur subiect. Lecția va fi citită de elevi de niveluri diferite, deci explici de la zero, dar fără să fii infantil.

Structură (Markdown, titluri de nivel 2):
## Ce este
## De ce contează
## Cum funcționează
(explicația principală, cu exemple mici de cod comentate; arată și ce se întâmplă „pe dedesubt” unde ajută)
## Exemplu complet
(un program scurt, realist, cu output-ul lui)
## Greșeli frecvente
(3-5 greșeli, fiecare cu codul greșit, eroarea și varianta corectă)
## Exercițiu
(o sarcină practică pe care elevul o poate rezolva în editor, fără soluție)
## Pe scurt
(3-6 puncte de reținut)

Reguli: blocuri de cod cu limbaj (```python, ```html, ```bash), cod conform PEP 8, termeni tehnici în engleză explicați în română.
Fără introduceri sau încheieri în afara structurii; începe direct cu „## Ce este”."""


def _lesson_request(topic) -> str:
    return (
        f"Modulul: {topic.module.title}\nSubiectul: {topic.title}\n"
        f"Ce trebuie să acopere lecția: {topic.summary}\n"
        "Pentru context, celelalte subiecte din același modul: "
        + ", ".join(t.title for t in topic.module.topics.exclude(pk=topic.pk))
    )


def generate_lesson(user, topic) -> Iterator[dict]:
    """Scrie lecția subiectului cu furnizorul AI configurat, emite textul pe bucăți și o salvează la final."""
    from django.utils import timezone

    text, model = "", ""
    try:
        if settings.PYTUTOR_PROVIDER == "openai":
            client = openai.OpenAI()
            stream = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "system", "content": LESSON_PROMPT}, {"role": "user", "content": _lesson_request(topic)}],
                stream=True,
                stream_options={"include_usage": True},
            )
            for chunk in stream:
                if chunk.usage:
                    details = getattr(chunk.usage, "prompt_tokens_details", None)
                    cached = (getattr(details, "cached_tokens", 0) or 0) if details else 0
                    usage.record(
                        user, f"lecție:{topic.slug}", "openai", chunk.model or settings.OPENAI_MODEL,
                        input_tokens=(chunk.usage.prompt_tokens or 0) - cached,
                        output_tokens=chunk.usage.completion_tokens or 0, cache_read_tokens=cached,
                    )
                if chunk.choices and chunk.choices[0].delta.content:
                    piece = chunk.choices[0].delta.content
                    text += piece
                    model = chunk.model or settings.OPENAI_MODEL
                    yield {"type": "text", "text": piece}
        else:
            client = anthropic.Anthropic()
            with client.beta.messages.stream(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=16000,
                system=LESSON_PROMPT,
                messages=[{"role": "user", "content": _lesson_request(topic)}],
                output_config={"effort": "low"},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            ) as stream:
                for piece in stream.text_stream:
                    text += piece
                    yield {"type": "text", "text": piece}
                response = stream.get_final_message()
            model = response.model
            u = response.usage
            usage.record(
                user, f"lecție:{topic.slug}", "anthropic", response.model,
                input_tokens=u.input_tokens or 0, output_tokens=u.output_tokens or 0,
                cache_read_tokens=u.cache_read_input_tokens or 0, cache_write_tokens=u.cache_creation_input_tokens or 0,
            )
    except (anthropic.APIError, openai.OpenAIError, TypeError) as e:
        yield {"type": "error", "message": f"Nu am putut scrie lecția: {e}"}
        return
    topic.refresh_from_db(fields=["lesson_model"])
    if text.strip() and topic.lesson_model != LESSON_MANUAL:  # load_lessons poate rula între timp
        topic.lesson = text.strip()
        topic.lesson_model = model
        topic.lesson_updated_at = timezone.now()
        topic.save(update_fields=["lesson", "lesson_model", "lesson_updated_at"])
    yield {"type": "done"}
