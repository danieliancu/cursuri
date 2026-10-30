## Ce este

Biblioteca standard (o vei explora la lecția 31) acoperă multe, dar nu tot. Pentru restul există sute de mii de **pachete** scrise de alți programatori și publicate pe **PyPI** (Python Package Index, [pypi.org](https://pypi.org)): Django, pentru aplicații web; `requests`, pentru cereri HTTP; `pytest`, pentru teste; și multe altele.

- **`pip`** e programul care instalează pachete de pe PyPI;
- un **mediu virtual** (în engleză „virtual environment”, prescurtat „venv”) e un folder cu propriul `python` (legat de Python-ul instalat pe calculator) și cu propriile pachete, ale unui singur proiect.

```bash
python -m venv .venv               # creează mediul virtual în folderul .venv
source .venv/bin/activate          # îl activează (Linux / macOS)
pip install requests               # instalează un pachet în el
```

## De ce contează

Fără medii virtuale, toate pachetele s-ar instala într-un singur loc, comun tuturor proiectelor de pe calculator. Apar repede probleme:
- proiectul A are nevoie de Django 4.2, proiectul B de Django 5.2, dar într-un loc comun poate exista o singură versiune;
- nu mai știi de ce pachete are nevoie fiecare proiect, așa că un coleg (sau serverul pe care publici aplicația, lecția 61) nu poate reface mediul;
- un pachet instalat „pentru încercare” rămâne acolo și poate strica alt proiect.

Un mediu virtual per proiect, plus un fișier `requirements.txt` cu lista pachetelor, le rezolvă pe toate trei. E felul standard de lucru în Python, iar orice proiect Django începe așa.

## Cum funcționează

### Crearea și activarea unui mediu virtual

În folderul proiectului:

```bash
python -m venv .venv
```

Comanda creează folderul `.venv`, cu propriul `python` (o legătură spre Python-ul instalat, nu o copie completă) și un folder `site-packages` gol, în care vor ajunge pachetele. Numele `.venv` e doar o convenție, dar e cea mai folosită: multe editoare îl recunosc automat.

Mediul se **activează** în terminal, cu o comandă care diferă după sistem:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows, Command Prompt
.venv\Scripts\activate

# Windows, PowerShell
.venv\Scripts\Activate.ps1
```

După activare, numele mediului apare în fața promptului, iar `python` și `pip` din terminal sunt cele din `.venv`:

```bash
(.venv) ana@laptop:~/jurnal$ python --version
Python 3.12.7
```

Comanda `deactivate` te scoate din mediu. Activarea ține doar cât terminalul e deschis: într-un terminal nou, activezi din nou.

### Instalarea pachetelor

```bash
pip install requests                # ultima versiune
pip install "django>=5.2,<6"        # o versiune din intervalul dat
pip install requests==2.32.3        # exact această versiune
pip install --upgrade requests      # actualizare
pip uninstall requests              # dezinstalare
pip list                            # ce e instalat
pip show requests                   # detalii despre un pachet
```

`pip install` descarcă pachetul de pe PyPI, împreună cu **dependențele** lui, adică alte pachete de care are nevoie. De exemplu, `pip install "django>=5.2,<6"` instalează și `asgiref` și `sqlparse`. Output-ul arată cam așa (versiunile diferă în timp):

```text
Collecting django<6,>=5.2
  Downloading Django-5.2.18-py3-none-any.whl (8.3 MB)
Collecting asgiref>=3.8.1 (from django)
  Downloading asgiref-3.13.0-py3-none-any.whl (24 kB)
Collecting sqlparse>=0.3.1 (from django)
  Downloading sqlparse-0.6.0-py3-none-any.whl (44 kB)
Installing collected packages: sqlparse, asgiref, django
Successfully installed asgiref-3.13.0 django-5.2.18 sqlparse-0.6.0
```

Ghilimelele din `"django>=5.2,<6"` sunt necesare pentru că `>` și `<` au un sens special în terminal (redirecționare).

O variantă mai sigură decât `pip install ...` e **`python -m pip install ...`**: pornește `pip` cu exact interpretorul `python` pe care îl folosești. Așa nu instalezi din greșeală în alt Python decât cel cu care rulezi programul (greșeala 2).

### requirements.txt: lista pachetelor proiectului

Fișierul `requirements.txt` din rădăcina proiectului enumeră pachetele de care are nevoie proiectul, câte unul pe rând:

```text
Django>=5.2,<6
requests==2.32.3
```

Cu el, oricine reface mediul cu o singură comandă:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Fișierul îl poți scrie de mână, cu pachetele pe care le folosești direct (varianta recomandată pentru început), sau îl poți genera cu `pip freeze`, care listează **tot** ce e instalat în mediu, inclusiv dependențele, cu versiuni exacte:

```bash
pip freeze > requirements.txt
```

```text
asgiref==3.13.0
Django==5.2.18
sqlparse==0.6.0
```

`>` trimite output-ul comenzii într-un fișier, în loc de ecran.

### Ce intră în Git și ce nu

Folderul `.venv` **nu se copiază și nu se pune în Git** (lecția 42): e mare, conține căi specifice calculatorului tău și se reface oricând din `requirements.txt`. În fișierul `.gitignore` al proiectului se scrie:

```text
.venv/
__pycache__/
```

În Git intră doar `requirements.txt`.

### Mediul tău din PyTutor

Terminalul din PyTutor rulează deja **într-un mediu virtual**, pregătit pentru tine, cu pachetele de care ai nevoie în curs: Django, Django REST Framework, pytest, black, ruff și mypy (le vei folosi în lecțiile următoare). Poți verifica din Python dacă rulezi într-un mediu virtual: într-un venv, `sys.prefix` (folderul mediului) diferă de `sys.base_prefix` (folderul Python-ului de bază).

```python
import sys

in_venv = sys.prefix != sys.base_prefix
print("Mediu virtual activ:", in_venv)
```

```text
Mediu virtual activ: True
```

Ce instalezi cu `pip install` în terminalul PyTutor ajunge în mediul tău și e disponibil în toate proiectele tale, până când mediul e refăcut de la zero (de exemplu, când PyTutor își actualizează mediul). De aceea, și aici merită să notezi pachetele într-un `requirements.txt`. Când vei lucra pe calculatorul tău, vei crea câte un `.venv` pentru fiecare proiect, ca mai sus.

### Ce se întâmplă „pe dedesubt”: activarea doar schimbă PATH

Un mediu virtual nu e o mașină virtuală și nici un container: e doar un folder. Înăuntru are:
- `bin/` (pe Windows `Scripts\`): `python`, `pip` și scriptul de activare;
- `lib/python3.12/site-packages/`: pachetele instalate;
- `pyvenv.cfg`: un fișier mic, care spune ce Python de bază a fost folosit.

Când scrii `python` în terminal, sistemul caută programul în folderele din variabila de mediu **`PATH`**, în ordine. Activarea face un singur lucru important: pune `.venv/bin` **la începutul** lui `PATH`. De aceea `python` și `pip` devin cele din mediu. La `import`, Python caută pachetele în `site-packages`-ul mediului (al treilea loc din lista de căutare a modulelor, lecția 29).

De aici rezultă că nici nu e nevoie de activare dacă apelezi direct interpretorul mediului: `.venv/bin/python program.py` (pe Windows `.venv\Scripts\python program.py`) rulează programul cu pachetele din `.venv`.

## Exemplu complet

Pornirea unui proiect nou, pas cu pas: jurnalul de cheltuieli primește un raport frumos în terminal cu pachetul `rich`, care colorează și formatează textul.

```bash
mkdir jurnal-cheltuieli
cd jurnal-cheltuieli

# 1. Mediul virtual
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate

# 2. Pachetul
python -m pip install rich

# 3. Lista pachetelor, scrisă de mână
echo "rich>=13" > requirements.txt

# 4. Git ignoră mediul
echo ".venv/" > .gitignore
```

Programul `raport.py`:

<!-- nu-rula -->
```python
from rich.console import Console
from rich.table import Table

cheltuieli = [("cafea", 46.5), ("benzină", 250.0), ("cărți", 89.0)]

tabel = Table(title="Cheltuielile Anei")
tabel.add_column("Categorie")
tabel.add_column("Suma (lei)", justify="right")
for categorie, suma in cheltuieli:
    tabel.add_row(categorie, f"{suma:.2f}")

Console().print(tabel)
```

```bash
python raport.py
```

Rezultatul e un tabel desenat cu chenare, în culori. Un coleg care primește proiectul (fără `.venv`) rulează:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python raport.py
```

și obține exact același rezultat.

## Greșeli frecvente

### 1. Pachetul nu e instalat

<!-- fisier: cerere.py -->
```python
import requests

raspuns = requests.get("https://pypi.org")
```

```text
Traceback (most recent call last):
  File "cerere.py", line 1, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'
```

Aceeași eroare ca la un modul propriu negăsit (lecția 29). Pentru un pachet de pe PyPI, înseamnă de obicei că nu l-ai instalat **în mediul din care rulezi**. Instalează-l cu `python -m pip install requests`.

### 2. Instalat în alt mediu decât cel care rulează

```bash
pip install requests
python cerere.py
```

```text
ModuleNotFoundError: No module named 'requests'
```

Pachetul s-a instalat, dar programul tot nu-l găsește. Cel mai probabil, `pip` și `python` aparțin unor medii diferite: ai uitat să activezi mediul, l-ai activat în alt terminal, sau pe calculator sunt mai multe versiuni de Python. Verifică:

```bash
python -c "import sys; print(sys.executable)"
python -m pip --version
```

Primul arată ce interpretor rulează, al doilea în ce mediu instalează `pip`. Cu `python -m pip install ...`, cele două sunt mereu aceleași.

### 3. Numele pachetului diferă de numele modulului

```bash
pip install PIL
```

```text
ERROR: Could not find a version that satisfies the requirement PIL (from versions: none)
ERROR: No matching distribution found for PIL
```

Unele pachete au alt nume pe PyPI decât la `import`. Biblioteca pentru imagini se instalează cu `pip install Pillow` și se importă cu `import PIL`. La fel, `pip install beautifulsoup4` se importă cu `import bs4`. Caută pachetul pe [pypi.org](https://pypi.org): pagina lui arată comanda exactă de instalare.

### 4. Mediul virtual copiat sau pus în Git

Folderul `.venv` copiat pe alt calculator (sau mutat în alt folder) de obicei nu funcționează: scripturile din el conțin căile absolute de pe calculatorul original, iar unele pachete sunt compilate pentru sistemul acela. Mediul nu se copiază, **se reface**: `python -m venv .venv`, apoi `pip install -r requirements.txt`. Pune `.venv/` în `.gitignore`.

### 5. requirements.txt uitat sau neactualizat

Instalezi un pachet nou, programul merge la tine, dar colegul primește `ModuleNotFoundError`. Lista din `requirements.txt` nu se actualizează singură. Regula: **orice `pip install` pentru proiect e urmat de o modificare în `requirements.txt`**. Verifică periodic, într-un mediu nou și gol, că `pip install -r requirements.txt` e suficient ca proiectul să ruleze.

## Exercițiu

În terminalul PyTutor, în proiectul tău:

1. verifică în ce mediu rulezi: `python -c "import sys; print(sys.executable)"` și `python -m pip --version`;
2. vezi ce pachete sunt instalate (`pip list`) și detaliile lui Django (`pip show django`): ce versiune are și de ce pachete depinde (rândul `Requires`);
3. instalează pachetul `rich` cu `python -m pip install rich` și scrie în `capitole/30-pip-venv/pip_venv.py` un program care afișează, cu un tabel `rich`, cheltuielile pe categorii din jurnalul de la lecția 28 (sau dintr-o listă scrisă în cod);
4. creează în rădăcina proiectului un `requirements.txt` scris de mână, cu pachetele pe care le folosește proiectul tău, și un `.gitignore` care exclude `.venv/` și `__pycache__/`;
5. în fișierul capitolului, adaugă la început un test care afișează „Rulezi într-un mediu virtual” sau „Atenție: nu rulezi într-un mediu virtual”, folosind `sys.prefix` și `sys.base_prefix`.

## Pe scurt

- Pachetele de pe PyPI se instalează cu `pip`; varianta sigură e `python -m pip install nume`.
- Un mediu virtual (`python -m venv .venv`) ține pachetele unui singur proiect, separat de restul.
- Activarea (`source .venv/bin/activate` sau `.venv\Scripts\activate`) pune `python` și `pip` din mediu pe primul loc în `PATH`.
- `requirements.txt` listează pachetele proiectului; `pip install -r requirements.txt` reface mediul, iar `pip freeze` arată tot ce e instalat.
- `.venv/` nu se copiază și nu intră în Git: se reface din `requirements.txt`.
- `ModuleNotFoundError` pentru un pachet înseamnă de obicei „neinstalat în mediul din care rulezi”.
