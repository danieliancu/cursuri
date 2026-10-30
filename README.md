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
