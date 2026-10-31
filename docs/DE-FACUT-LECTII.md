# Ce mai e de făcut — lecțiile PyTutor

**Actualizat:** 2026-10-31. Pașii pentru lecții sunt făcuți; rămâne verificarea de mână în aplicație. Ce urmează
pentru verificarea fără AI și costuri e în secțiunea [Verificare fără AI și cost redus](#verificare-fără-ai-și-cost-redus-2026-10-30).
Planurile de bază: [PLAN-LECTII.md](PLAN-LECTII.md) (stare pe lecție) și
[PLAN-CONSTRUCTIE-LECTII.md](PLAN-CONSTRUCTIE-LECTII.md) (cum se construiesc și se verifică).

## Unde suntem

| Lecții | Scrise | Verificate automat | Recenzie independentă | În aplicație |
|---|---|---|---|---|
| 01–44 (Python, calitate, web) | ✅ | ✅ | ✅ (2 recenzii + claritate) | ✅ încărcate, marcate ✅ |
| 45–61 (Django) | ✅ | ✅ (2026-10-30, toate 61 „OK”) | ✅ | ✅ încărcate 2026-10-30, marcate ✅ |

Proiectul de referință al blogului: `tutor/lessons/_blog/45` … `61` (+ `date/`, `README.md`), verificat cu
`tools/verifica_blog.py`. După ultimele corecturi (comentariul despre `SECRET_KEY`, HSTS mai prudent la 61,
`form.as_div` la 58–61) a fost reverificat integral (pasul 2).

## Pașii rămași, în ordine

1. ~~**Recenzia 50–54**~~ — făcută 2026-10-30: corecturi în 51–54 (`search_fields` nu e verificat de `check`,
   „Acțiuni recente” = doar ale tale, `contains` pe SQLite, exerciții reluabile) și explicația formatului
   „ | ” mutată la prima apariție (lecția 46). Output-urile din 54 erau deja în formatul nou.
2. ~~**Verificarea copiilor proiectului**~~ — făcut 2026-10-29 17:05, după toate corecturile: toate 17 „OK”
   (`MSYS_NO_PATHCONV=1 PYTHONUTF8=1 .venv/Scripts/python tools/verifica_blog.py`).
3. ~~**Verificarea tuturor lecțiilor**~~ — 2026-10-30: toate 61 „OK” (diferențele de la 47, 52, 58 dispăruseră).
4. ~~**Verificarea afișării**~~ — 2026-10-30, automat: Markdown-ul randat cu `marked` 12.0.2 (ca în pagină):
   toate au 7 secțiuni `##`, nicio directivă vizibilă, `<details>` din lecția 45 conține codul.
   Verificat apoi și în browser, pe `/progres/`, după încărcare: 45–61 au 7 secțiuni, nicio directivă, `<details>`
   din 45 se deschide cu codul colorat, iar corecturile din 2026-10-30 apar în pagină.
5. ~~**Încărcarea**~~ — 2026-10-30: 17 încărcate (45–61, inclusiv 59 în locul celei AI); `manage.py test tutor`: 10 OK.
6. ~~**Marcarea**~~ — 45–61 pe ✅ în `PLAN-LECTII.md`, starea generală „gata”.

## De verificat de mână în aplicație (nu se pot verifica automat)

- **Tutorele** (prompt schimbat 2026-10-29; modelul e `gpt-4.1`). Testat parțial 2026-10-30, oprit de
  creditul OpenAI epuizat (`credit_balance_exhausted`):
  - ✅ după „Rulează și verifică” primește rezultatul automat și îl comentează (exercițiul de la Liste);
  - ✅ nu repetă în panou ce a pus în baloane (2026-10-30: 2 baloane pe if/else, în panou o singură propoziție);
  - ✅ încheierea mesajelor: după regula adăugată și în „Amintire” (`_context_block` din `ai.py`) încheie cu
    „…apoi apasă **Rulează și verifică**” / „…apoi apasă **Următorul pas**” (comenzi în terminal);
  - ✅ la lecțiile Django: după corectarea promptului (excepția Django de la punctul 6 din `ai.py`) trimite la
    proiectul `blog` și dă corect `django-admin startproject blog_proiect .`, cu explicația punctului.
    Descrierea ecranului din prompt e actualizată: acum spune „terminalul de sub editor”;
  - ✅ ordinea lecțiilor e doar o recomandare (decis 2026-10-30): elevul poate sări direct la ce cere; lipsurile
    se explică pe loc sau se oferă o recapitulare, fără obligație. Testat: „vreau direct Django” → pornește imediat;
  - ✅ după „învățat”, rezultatul lui `record_progress` îi spune tutorelui care e pasul următor din sumar
    (`_next_active_note`); din 2026-10-30 editorul nu se mai mută singur: elevul trece la lecție când vrea, cu
    „Următorul pas” sau din sumar.
- ✅ **Folderul capitolului la Django:** `chapters.has_folder` — subiectele din modulele `django-*` nu mai primesc
  `capitole/NN-slug/` (2026-10-30; folderele goale `45-django-proiect` existente au fost șterse).
- **Lecțiile Django în PyTutor** — ✅ verificate 2026-10-30 (utilizatorul u4, proiectul `blog`):
  - proiectul nou `blog` (are doar `main.py`), `django-admin startproject blog_proiect .` → cod 0;
    ✅ explorerul se reîmprospătează singur la finalul fiecărei comenzi din terminal (și la 2,5 s după start);
  - `python manage.py runserver 0.0.0.0:8000` → bara arată `server: localhost:9004`, pagina de bun venit merge;
  - lecția 46, `DJANGO_DEBUG=0` cu `settings.py` din `_blog/46`: `/nimic/` și `/` dau „Not Found” simplu
    (nu 400, deci `ALLOWED_HOSTS` e în regulă prin container);
  - la `127.0.0.1:8000` rulează PyTutor, cum spune lecția 45.
- ✅ **Interfața** (2026-10-30): „Rulează și verifică” se luminează după o modificare de cod, fereastra
  „Nivelul tău” se deschide din meniul contului, codul e fără ligaturi (`font-variant-ligatures: none`).

## Mărunțișuri cunoscute (opționale)

- Butonul „Ieși” din meniul blogului (lecțiile 57–61) n-are stil propriu (`.iesire` lipsește din `stil.css`):
  cosmetic; s-ar schimba în copiile `_blog/57`–`61` și în lecțiile care arată `stil.css`.
- Admin-ul Django afișează lunile cu majusculă („20 Octombrie 2026”) — e localizarea Django, lăsată așa.
- Lecțiile 23, 26, 28, 36 conțin numere de rând din fișierele interne ale lui Python 3.12.16; la o imagine sandbox
  cu altă versiune 3.12.x, `verifica_lectie.py` le semnalează și se actualizează textul.
- Lecțiile 40–42 și cele Django sunt mai lungi decât restul (2.000–3.400 de cuvinte cu cod), mai ales din cauza
  fișierelor complete cerute de comparația cu proiectul de referință.
- `tools/construieste_blog.py` reface copiile `_blog/` de la zero: corecturile făcute ulterior direct în copii
  (form.as_div, comentariul SECRET_KEY, HSTS, „create”) **nu** sunt în el — dacă îl rulezi, reaplică-le.

## Verificare fără AI și cost redus (2026-10-30)

**Făcut** (detalii în `README.md`, „Verificare fără AI”):
- **Exerciții fixe pentru lecțiile 1–11** (`tutor/exercitii/NN-slug.toml`): teste pe output, verificări de structură,
  pyflakes, 3 indicii în trepte, soluție de referință și **exemplu de început** (`inceput`: primul pas scris ca model,
  apoi „scrii așa: …” la fiecare pas). Se scriu în fișierul capitolului; verdictul îl dă codul, modelul mic doar
  formulează fraza. Plasa de siguranță din balon: „Nu lucrez la exercițiul lecției”. Validare:
  `python tools/verifica_exercitii.py`.
- **Erorile Python explicate în română fără AI** (`tutor/erori.py`, aproximativ 60 de reguli), ca balon pe rândul greșit.
- **„Rulează și verifică” și „Verifică-mi codul”** fără exercițiu fix: modelul mic, cu context redus.
- **„Următorul pas” și „Exercițiu nou”** răspund din curriculum, fără AI, când se poate.
- **Lecția curentă** = ultima deschisă de elev; un click doar ca să te uiți nu mai marchează „în lucru”.
- **Fișierele capitolelor 12–44** au enunțul lecției ca antet (cele 1–11 au în locul lui exemplul de început).
- **Raportul de cost:** `python manage.py raport_cost` (doar citește).

**Făcut 2026-10-31** (commit-ul de bază: `7436bd4`, apoi cel cu lucrurile de mai jos):
1. ~~Commit și push~~ — tot ce era doar pe disc e pe GitHub.
2. ~~Serverele~~ — versiunea veche (`C:\_work\pyth`) nu mai rulează; aplicația nouă e pe 8000.
3. ~~Testele din browser~~ — 9 teste (erau 4): plus balonul unei erori cunoscute, exercițiul fix (greșit → indiciu
   → corect → „învățat”), „Următorul pas” fără AI și linkul la secțiunea din lecție. Un test vechi presupunea că
   la pornire nu se creează niciun folder `capitole/` (acum se creează cel al lecției curente) — corectat.
4. ~~Verificare gratuită pentru fișierele fără cod~~ — „Verifică-mi codul” pe un fișier doar cu comentarii /
   docstring-uri răspunde fără AI (`ai._empty_file_reply`, `verificare.fara_cod`).
5. ~~Modelul mic nu schimbă lecții~~ — la verificare, `record_progress` merge doar cu „învățat” și doar pe lecția
   verificată (fișierul capitolului, altfel lecția curentă); plasa de siguranță `_progress_check` e limitată la fel.
6. ~~Exerciții fixe pentru lecțiile 12–22~~ — 11 fișiere TOML noi, cu date fixe în exemplul de început (orașe,
   contacte, texte, elevi) ca testele să știe rezultatul. Verificări de structură noi în `verificare.py`
   (liste, dicționare, seturi, comprehension-uri, lambda, `*args`, parametri după `*`, docstring-uri, type hints,
   alias de tip; `global` și valorile implicite mutabile pot fi interzise).
7. ~~Indicii specifice fiecărui test~~ — `indiciu` la fiecare `[[test]]` (1–22, cerut de validator): un test nou
   picat → indiciul lui; același test din nou → indiciile generale 2 și 3 (`ExerciseAttempt.last_test`, migrarea 0016).
8. ~~Exemple de început la 23–44~~ — `tutor/exercitii/inceput/NN-slug.py`, sub enunțul din antet (fără teste).
9. ~~Linkuri la secțiune~~ — titlurile din lecții au `id` (`md.js`, `PTMarkdown.anchor`), balonul trimite la
   `/progres/#slug:s-titlu`, pagina derulează și evidențiază secțiunea. Un test verifică pentru fiecare regulă din
   `erori.py` că secțiunea există exact în lecție.
10. **Raportul de cost** rulat 2026-10-31: £1.147 plătit în total, £1.038 în sistemul nou (10%; 27% pe cererile
    identificate). Verificarea unui exercițiu fix: £0.0221 → £0.0003 pe tură. Majoritatea datelor sunt dinainte de
    sistemul nou și 65% vin din conversații șterse, deci economia reală se vede abia după câteva zile de folosire.

Validare: `python tools/verifica_exercitii.py` — toate 44 OK (22 exerciții, 22 exemple de început);
`python manage.py test tutor` — 67 OK.

**De făcut, în ordinea propusă:**
1. **Încercat de mână exercițiile 12–22 în aplicație**, cu un elev nou: textul din lecție spune uneori „alege tu
   datele” (orașe, elevi), iar testele folosesc datele din exemplul de început; dacă încurcă, se aliniază lecțiile
   (atunci `verifica_lectie.py` + `load_lessons` pentru lecțiile schimbate).
2. **Raportul de cost din nou** peste câteva zile de folosire reală (`python manage.py raport_cost`).
3. **Exerciții fixe și la 23–44**, acolo unde output-ul se poate testa (excepții, fișiere, clase); la git, pip,
   HTML rămâne tutorele.
4. **Indicii pentru verificările de structură** (acum doar testele au indiciu propriu; „lipsește un `for`” primește
   indiciul general).
5. Creditul OpenAI (oprit 2026-10-30) — de verificat înainte de testarea cu elevi.

## După lecții (idei, nu cerute încă)

- Testarea cu un elev real pe primele module și ajustarea pe baza întrebărilor lui.
- Un model mai bun pentru tutore decât `gpt-4.1`, dacă regulile din prompt continuă să fie ignorate.
