# Plan de construcție: lecțiile scrise în proiect

Pașii concreți pentru [PLAN-LECTII.md](PLAN-LECTII.md): ce cod se scrie o singură dată, cum arată un fișier de lecție, cum se verifică și în ce ordine se scriu cele 61 de lecții.

**Stare:** etapa 0 gata (2026-10-29); modulele 1–10 scrise, așteaptă recitirea; urmează Django (45–61).

---

## Etapa 0 — Infrastructura (o singură dată, înainte de modulul 1)

### 0.1 Constanta „manual”
- `tutor/models.py`: `LESSON_MANUAL = "manual"` lângă `STATUS_*`.
- `Topic`: docstring-ul și `help_text` la `lesson` spun acum „Gol = AI-ul o scrie”; se schimbă în „Lecțiile din `tutor/lessons/` au prioritate; AI-ul scrie doar lecțiile fără fișier.”
- Schema nu se schimbă (`lesson_model` e deja `CharField`), dar Django cere o migrare mică pentru noul `help_text`; o generăm, ca să nu rămână pending.

### 0.2 Comanda `load_lessons`
Fișier nou: `tutor/management/commands/load_lessons.py`.

Ce face, pentru fiecare `tutor/lessons/NN-slug.md`:
1. Găsește `Topic` după slug. Dacă nu există → eroare.
2. Verifică că `NN` e poziția subiectului în curriculum (aceeași numerotare ca `chapters.folder_for`). Dacă nu → eroare (prinde fișierele numerotate greșit).
3. Verifică structura: începe cu `## Ce este` și are cele 7 titluri de nivel 2, în ordine, fără altele în plus.
4. Dacă textul diferă de `Topic.lesson` → scrie `lesson`, `lesson_model = "manual"`, `lesson_updated_at = now()`. Dacă e identic → nu atinge nimic (data rămâne cea reală).

Opțiuni:
- `--check` — doar validează, nu scrie (folosit în timpul scrierii).
- `--only NN|slug` — o singură lecție.

La final afișează: încărcate / neschimbate / erori, plus subiectele care nu au încă fișier.
Un fișier șters nu golește lecția din baza de date; comanda doar avertizează („lecție manuală fără fișier”).

Ignoră fișierele și folderele care încep cu `_` (vezi proiectul de referință Django, 0.6).

### 0.3 Regula „manual nu se suprascrie”
- `tutor/ai.py` → `generate_lesson`: înainte de `topic.save(...)`, `topic.refresh_from_db(fields=["lesson_model"])`; dacă e `manual`, nu salvează. Acoperă cazul rar în care `load_lessons` rulează cât AI-ul încă scrie.
- `tutor/views.py` → `topic_lesson` rămâne cum e: generează doar când `lesson` e gol.

### 0.4 Admin
`TopicAdmin`:
- `clear_lesson` exclude lecțiile manuale (`queryset.exclude(lesson_model=LESSON_MANUAL)`) și spune câte a sărit: „3 lecții vor fi rescrise; 2 sunt scrise în proiect și se editează în `tutor/lessons/`.”
- `get_readonly_fields`: la o lecție manuală, câmpul `lesson` e read-only (o editare din admin s-ar pierde la următorul `load_lessons`).
- `list_filter` primește `lesson_model`, ca să vezi rapid ce e manual / AI / gol.

### 0.5 Pornire și deploy
- `start.bat`: după `migrate`, `manage.py load_lessons`.
- `curriculum.py`: docstring-ul spune că lecțiile sunt în `tutor/lessons/`.
- `README.md`: o secțiune scurtă „Lecții”.

### 0.6 Scriptul de verificare a codului
Fișier nou: `tools/verifica_lectie.py` (unealtă de autor, nu parte din aplicație).

Convenția din Markdown, pe care o citește scriptul:

| În lecție | Ce face scriptul |
|---|---|
| ```` ```python ```` urmat imediat de ```` ```text ```` | program complet: îl rulează și compară output-ul exact cu blocul `text` |
| ```` ```python ```` urmat de ```` ```text ```` care conține `Traceback` | rulează și compară **ultima linie** (tipul și mesajul erorii) |
| ```` ```python ```` fără bloc `text` după | fragment: doar `compile()`, ca să prindă greșeli de sintaxă |
| `<!-- stdin: Ana\n25 -->` înaintea blocului | trimite textul la `input()` |
| `<!-- nu-rula -->` înaintea blocului | sărit (ex. fragmente care depind de altele, cod Django) |

Comentariile HTML nu se văd la elev (`marked` le lasă invizibile).

Rularea: `docker run --rm -i --network none pytutor-sandbox:2 ...` — Python 3.12, la fel ca elevii.

Comenzi de terminal (`pytest`, `git`, `ruff`...): `<!-- ruleaza -->` înaintea unui bloc ```` ```bash ```` urmat de ```` ```text ````; output-ul se compară după ce duratele și hash-urile de commit sunt normalizate.
Raport: OK / diferă (cu diff) / eroare neașteptată, pe fiecare bloc.

### 0.7 Teste
`tutor/tests.py` (nu există încă), minim:
- `load_lessons` încarcă un fișier valid și pune `manual`;
- respinge număr greșit, slug inexistent, secțiuni lipsă;
- `clear_lesson` nu atinge lecțiile manuale.

**Gata când:** `load_lessons --check` rulează pe folderul gol, testele trec, acțiunea din admin se comportă corect.

---

## Cum se scrie o lecție (fluxul pe fiecare fișier)

1. Recitesc `summary` din `curriculum.py` și lecțiile dinainte din același modul (continuitate, ce s-a predat deja).
2. Scriu `tutor/lessons/NN-slug.md` cu cele 7 secțiuni.
3. La `## Exercițiu`, numele fișierului e cel dat de `chapters.main_name`, nu mereu `<slug>.py`:
   - cratimele devin `_`: `f-strings` → `f_strings.py`;
   - 4 excepții primesc `_exercitii`: **09** `while_exercitii.py`, **23** `traceback_exercitii.py`, **36** `dataclasses_exercitii.py`, **43** `http_exercitii.py`.
4. `python tools/verifica_lectie.py tutor/lessons/NN-slug.md` până iese totul OK.
5. `manage.py load_lessons --check --only NN`.

## Cum se închide un modul

1. Toate lecțiile modulului trec verificarea.
2. Le recitesc cap-coadă: fără trimiteri la lucruri nepredate, personaje/date consecvente.
3. `manage.py load_lessons`, apoi `/progres/` în browser: randare, blocuri de cod, tabele.
4. Tu citești și ceri modificări.
5. Bifez ✅ în tabelul din `PLAN-LECTII.md`.

---

## Ordinea și firul fiecărui modul

Firul roșu e contextul comun al exemplelor dintr-un modul (regula de continuitate). E o propunere; se poate schimba la începutul fiecărui modul.

| Etapa | Modul | Lecții | Fir roșu propus | De avut în vedere |
|---|---|---|---|---|
| 1 | Bazele Python | 01–07 | fișa unei persoane: `nume`, `varsta`, `oras` | 06 are nevoie de `<!-- stdin -->`; înlocuiește 6 lecții AI |
| 2 | Controlul fluxului | 08–11 | jocul „ghicește numărul”, construit pe rând | `while`/`input` → stdin în verificare |
| 3 | Colecții | 12–17 | lista de cumpărături și notele unei clase | înlocuiește lecția AI 12 |
| 4 | Funcții | 18–22 | refac exemplele din modulul 3 în funcții | 19: capcana listei mutabile, output real; înlocuiește 18 |
| 5 | Erori | 23–26 | un calculator care validează ce primește | 26: `pdb` rulat cu comenzi pe stdin |
| 6 | Fișiere, module | 27–31 | jurnal de cheltuieli salvat în JSON/CSV | 30 (`pip`, `venv`) nu se poate rula cu `--network none` → doar `bash` comentat |
| 7 | OOP | 32–36 | o bibliotecă: `Carte`, `Membru`, `Imprumut` | |
| 8 | Python intermediar | 37–39 | continuă biblioteca (generator de cărți, decorator de log) | |
| 9 | Cod de calitate | 40–42 | testează funcțiile din modulul 4 | 41 cere `pytest`, 42 cere `git` — **nu sunt în imaginea sandbox** |
| 10 | Web | 43–44 | pagina blogului, scrisă de mână | 43 se verifică cu `http.server` + `urllib` în container |
| 11 | Django: fundamente | 45–49 | **proiectul blog** începe | vezi mai jos |
| 12 | Django: date | 50–54 | blogul primește modele | |
| 13 | Django: interactiv | 55–58 | comentarii, formulare, login | |
| 14 | Django: mai departe | 59–61 | teste, API, publicare | 60 cere `djangorestframework`; 61 se verifică cu `check --deploy`; înlocuiește 59 |

### Blogul din lecțiile Django

Un proiect de referință, `tutor/lessons/_blog/`, ține starea codului **după ultima lecție scrisă**. Fiecare lecție adaugă la el, și fiecare exemplu din lecție vine din el, deci codul arătat chiar funcționează împreună.

**Fixat deja în lecțiile 43–44 (de păstrat în Django):**
- „Blogul Anei”, al Anei Popescu din Cluj; Mihai e cel care comentează.
- Articole: 1 „Primul meu program în Python” (14.09.2026, Programare), 2 „De ce am ales Django” (02.10.2026, Programare), 3 „O plimbare prin Cluj” (20.10.2026, Călătorii).
- Articol: `titlu`, `continut`, data, `categorie`, comentarii; comentariu: `autor`, `text`, dată.
- URL-uri: `/` (listă), `/articol/<nr>/`, `POST /articol/<nr>/comentariu/` → redirect înapoi la articol; câmpurile formularului: `autor`, `text`.
- Pagini: `index.html`, `articol.html` (cu `#comentarii`), `despre.html`, `stil.css`; clase CSS: `.antet`, `.sigla`, `.articol`, `.meta`, `.categorie`, `.comentarii`, `.comentariu`, `.formular-comentariu`, `.subsol`.
- Promisiuni: 45 `runserver`; 47 `urls.py` și `/articol/1/`; 48 `{{ }}`, `{% extends %}`, escaparea automată (antetul/subsolul repetat); 49 CSS ca fișier static; 55 `{% csrf_token %}` și POST-redirect-GET; 56 salvarea comentariilor; 57 cookie-uri, sesiuni, login prin POST; 61 HTTPS.
- În terminalul PyTutor, `cd` nu rămâne de la o comandă la alta (fiecare rulează din rădăcina proiectului): lecțiile dau căi relative la proiect.

| # | Ce adaugă |
|---|---|
| 45 | `startproject blog_proiect`, `startapp articole`, `INSTALLED_APPS`, `runserver` |
| 46 | `SECRET_KEY` și `DEBUG` din variabile de mediu, `LANGUAGE_CODE = "ro"` |
| 47 | `/` (lista) și `/articol/<int:id>/` cu date dintr-o listă Python |
| 48 | `base.html`, `lista.html`, `detaliu.html` |
| 49 | `static/articole/stil.css` |
| 50–51 | modelul `Articol`, prima migrare |
| 52 | interogări în `manage.py shell`, view-urile trec de la listă la ORM |
| 53 | `Categorie` (ForeignKey), `Eticheta` (ManyToMany), `Comentariu` |
| 54 | admin pentru toate |
| 55 | formular de contact (`forms.Form`) |
| 56 | adăugare comentariu (`ModelForm`), POST-redirect-GET |
| 57 | login/logout, doar autorii logați scriu articole |
| 58 | view-urile rescrise ca `ListView` / `DetailView` / `CreateView` |
| 59 | `tests.py` pentru modele și view-uri |
| 60 | `/api/articole/` cu DRF |
| 61 | setări de producție, `collectstatic`, `gunicorn` |

Verificarea pe lecție: `migrate`, `manage.py check`, `manage.py test` (de la 59 încolo, testele se păstrează), plus cereri cu clientul de test pentru paginile noi.

---

## De hotărât înainte de etapele respective

1. ~~Imaginea sandbox~~ — rezolvat (2026-10-29): `pytutor-sandbox:2` are `git`, `pytest`, `black`, `ruff`, `mypy` și `djangorestframework`; containerele elevilor create din imaginea veche se refac automat.
2. ~~Tabelul de stare din PLAN-LECTII.md~~ — corectat (erau 9 lecții AI, nu 8).
3. **Firul roșu** al fiecărui modul: confirmat sau schimbat la începutul modulului.

## Promisiuni de ținut în lecțiile încă nescrise

Lecțiile scrise trimit înainte la aceste lucruri; lecția respectivă trebuie să le conțină.

- **40 (PEP 8):** `mypy` și verificarea tipurilor (trimis din 22); `lambda` cu nume nerecomandat de PEP 8 (din 21); black, ruff.
- **41 (testare):** teste care importă `main` dintr-un modul (din 29).
- **42 (git):** `.gitignore`, inclusiv `.venv/` și `__pycache__/` (din 30).
- **46 (settings):** constante și variabile de mediu (din 22, 31).
- **47, 52, 55, 57:** view-uri cu `path()`; `Articol.DoesNotExist`; `ValidationError`; `@login_required` (din 18, 24, 38).
- **Sandbox:** lecțiile 23, 26, 28 și 36 conțin numere de rând din fișierele interne ale lui Python 3.12 (de ex. `json/decoder.py`). La reconstruirea imaginii cu altă versiune 3.12.x, `verifica_lectie.py` le poate semnala; se actualizează textul, nu verificarea.

## Estimare

- Etapa 0: o sesiune.
- Modulele 1–10 (44 de lecții): câte o sesiune pe modul.
- Modulele Django (17 lecții): câte o sesiune pe modul, mai lungi din cauza proiectului de referință.

Aproximativ **15 sesiuni** în total, fiecare încheiată cu o recitire de partea ta.
