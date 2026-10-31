# PyTutor

Aplicație Django care te învață Python și Django scriind cod:
- **stânga** — tutorele AI, care îți evaluează nivelul, explică tot și îți verifică codul;
- **dreapta** — explorer de fișiere + editor + terminal.

Temă întunecată implicit (Sistem / Luminos / Întunecat). Funcționează pe desktop, tabletă și mobil.

## Conturi
- **Elevi** — își fac singuri cont la `/signup/` (dacă `PYTUTOR_ALLOW_SIGNUP=1`) sau le creează adminul.
  Fiecare elev are profilul, proiectele și conversațiile lui.
- **Superadmin** — se creează din terminal:
  ```
  .venv\Scripts\python manage.py createsuperuser
  ```
  Panoul de administrare: http://127.0.0.1:8000/admin/ (elevi, profiluri, conversații, conturi).

## Izolare (Docker)
Cu `PYTUTOR_SANDBOX=docker`, terminalul fiecărui elev rulează în containerul lui (`pytutor-u<id>`),
cu limite de memorie/CPU și acces doar la propriile proiecte. Imaginea (`sandbox/Dockerfile`) se
construiește automat la prima comandă. Serverul Django pornit de elev cu
`python manage.py runserver 0.0.0.0:8000` se deschide la `http://localhost:<9000 + id elev>`
(adresa apare în bara terminalului).

## Lecții
Lecțiile sunt fișiere Markdown în `tutor/lessons/NN-slug.md` (planul: `docs/PLAN-LECTII.md`).
- `python manage.py load_lessons` le încarcă în baza de date (rulează automat din `start.bat`);
  `--check` doar le verifică, `--only 04` sau `--only stringuri` ia o singură lecție.
- Lecțiile încărcate așa nu sunt suprascrise de AI; AI-ul scrie doar lecțiile care nu au încă fișier.
- `python tools/verifica_lectie.py tutor/lessons/04-stringuri.md` rulează codul din lecție în
  containerul sandbox și compară output-ul cu cel scris în lecție (convențiile sunt în script).

## Verificare fără AI (cost redus)
„Rulează și verifică” și „Verifică-mi codul” aleg, în ordine, varianta cea mai ieftină:
1. **Exercițiu fix** (`tutor/exercitii/NN-slug.toml`, acum lecțiile 1–22), scris în fișierul capitolului
   (`capitole/NN-slug/<lecție>.py`, care începe cu un exemplu de început: primul pas scris ca model, apoi
   „scrii așa: …” la fiecare pas, `inceput` în TOML) și verificat așa până e rezolvat; după aceea
   fișierul e liber pentru sarcinile tutorelui. Plasa de siguranță: linkul „Nu lucrez la exercițiul lecției”
   din balon trece fișierul la tutore (modelul mic) până la „Exercițiu nou”. Verdictul îl dă codul
   (`tutor/verificare.py`: teste pe output, structură prin AST, pyflakes, indicii în 3 trepte);
   modelul mic doar îl formulează într-o frază, iar fără AI rămâne un șablon.
   Fiecare test are `indiciu`-ul lui: când pică un test nou, primul indiciu e despre exact ce a greșit
   elevul; dacă pică iar același test, urmează indiciile generale ale exercițiului.
   Lecțiile 23–44 n-au teste, dar au exemplu de început (`tutor/exercitii/inceput/NN-slug.py`), sub enunțul
   din antet; acolo verifică modelul mic.
   „Verifică-mi codul” pe un fișier fără cod (doar comentarii) răspunde fără AI. La verificare, modelul mic
   poate doar bifa „învățat” lecția verificată, nu începe sau schimbă alte lecții.
2. **Eroare cunoscută**: `tutor/erori.py` o explică în română într-o casetă sub terminal, cu link spre
   secțiunea din lecție (`/progres/#slug:s-titlu`); tutorele AI e doar la butonul „Întreabă AI”.
3. Altfel, **modelul mic** (`PYTUTOR_OPENAI_CHECK_MODEL` / `PYTUTOR_CHECK_MODEL`) cu context redus.
   Întrebările libere rămân la modelul mare.
„Următorul pas” și „Exercițiu nou” răspund fără AI când se poate: pasul următor din curriculum (lecția activă,
altfel prima neînvățată) și exercițiul ei fix, dacă nu e rezolvat. Altfel întreabă tutorele AI.
- `python tools/verifica_exercitii.py` verifică exercițiile (soluția de referință trece, un fișier gol și exemplul de
  început nu, fiecare test are `indiciu`) și exemplele de început fără teste (Python valid, pași „scrii așa”).
- `python manage.py raport_cost` compară costul AI plătit cu cel estimat în sistemul nou (doar citește).

## Pornire
1. În `.env`: `PYTUTOR_PROVIDER=anthropic` sau `openai` și cheia corespunzătoare.
2. Docker Desktop pornit (dacă folosești sandbox-ul).
3. Dublu-click pe `start.bat` → http://127.0.0.1:8000

## Teste
- `python manage.py test tutor` rulează toate testele: cele de server (`tutor/tests.py`) și cele din browser
  (`tutor/tests_browser.py`), care folosesc interfața într-un Chrome fără fereastră.
- Testele din browser cer `pip install -r requirements-dev.txt` și Chrome instalat (nu și `playwright install`),
  plus internet pentru bibliotecile din pagină (cdnjs); fără Playwright sunt sărite.
- Doar cele de server: `python manage.py test tutor.tests`.
