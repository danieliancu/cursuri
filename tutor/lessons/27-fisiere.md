## Ce este

Un **fișier** păstrează date pe disc. Spre deosebire de variabile, datele dintr-un fișier rămân și după ce programul se termină. Python citește și scrie fișiere cu funcția **`open()`**, folosită aproape mereu împreună cu instrucțiunea **`with`**:

<!-- fisier: scrie_nota.py -->
```python
with open("nota.txt", "w", encoding="utf-8") as fisier:
    fisier.write("Ana a cheltuit 32 de lei pe cafea.\n")

with open("nota.txt", encoding="utf-8") as fisier:
    continut = fisier.read()
print(continut)
```

```text
Ana a cheltuit 32 de lei pe cafea.

```

Primul bloc creează fișierul `nota.txt` și scrie în el un rând. Al doilea îl deschide pentru citire și ia tot textul într-o variabilă. Rândul gol de la final al output-ului vine din `\n`-ul scris în fișier, la care `print()` adaugă încă unul.

Pentru lucrul cu **căi** (unde se află un fișier, cum se numește, ce extensie are), Python are modulul **`pathlib`**, cu tipul `Path`.

## De ce contează

Până acum, tot ce introducea utilizatorul se pierdea la închiderea programului: lista de cumpărături (lecția 12), agenda de contacte (lecția 14). Cu fișiere, programul poate:
- **salva** date între rulări (un jurnal, setări, un scor maxim);
- **citi** date pregătite de altcineva (un export din Excel, un fișier de configurare, un log);
- **produce** rezultate pe care le deschizi în alt program (un raport, o pagină HTML).

Lucrul cu fișiere e și primul contact cu „lumea din afara” programului, unde lucrurile pot merge prost: fișierul lipsește, n-ai drept de scriere, textul are alt encoding. De aceea `try / except` (lecția 24) apare des lângă `open()`.

## Cum funcționează

### open(): cale, mod, encoding

```python
fisier = open("cheltuieli.txt", "w", encoding="utf-8")  # forma corectă, cu with, e mai jos
```

Cele trei argumente:
1. **calea** fișierului: un nume simplu (`"cheltuieli.txt"`) sau o cale (`"date/cheltuieli.txt"`);
2. **modul**, care spune ce vrei să faci:

| Mod | Înseamnă | Dacă fișierul nu există | Dacă există |
|---|---|---|---|
| `"r"` | citire (implicit) | `FileNotFoundError` | îl citește |
| `"w"` | scriere | îl creează | **îl golește**, apoi scrie |
| `"a"` | adăugare la final („append”) | îl creează | scrie după conținutul existent |
| `"x"` | creare exclusivă | îl creează | `FileExistsError` |

3. **`encoding="utf-8"`**: cum se transformă textul în octeți (în engleză „bytes”, unitățile de memorie) pe disc. UTF-8 e standardul de azi și păstrează corect diacriticele. Scrie-l **mereu**: fără el, Python folosește setarea sistemului, care pe Windows poate fi alta (vezi „Greșeli frecvente”).

### with: fișierul se închide singur

Un fișier deschis trebuie închis (`fisier.close()`), ca datele să ajungă sigur pe disc și sistemul să elibereze fișierul. Instrucțiunea `with` face asta automat, la ieșirea din bloc, chiar dacă în bloc apare o eroare:

```python
with open("cheltuieli.txt", "w", encoding="utf-8") as fisier:
    fisier.write("2026-10-27;cafea;32\n")
    fisier.write("2026-10-27;pâine;4.5\n")
    fisier.write("2026-10-28;benzină;250\n")
# aici fișierul e deja închis
print("Am scris jurnalul.")
```

```text
Am scris jurnalul.
```

`write()` scrie exact textul primit: **nu adaugă rând nou**. Fiecare rând se termină cu `\n` (lecția 5) pus de tine. Cum funcționează `with` pe dedesubt vei vedea la lecția 39 (context managers).

### Citirea

Fișierul `cheltuieli.txt` scris mai sus are trei rânduri. Sunt mai multe feluri de a-l citi:

```python
with open("cheltuieli.txt", encoding="utf-8") as fisier:
    tot_textul = fisier.read()            # tot conținutul, ca un singur string
print(repr(tot_textul))

with open("cheltuieli.txt", encoding="utf-8") as fisier:
    for linie in fisier:                  # rând cu rând
        print(linie.strip().split(";"))
```

```text
'2026-10-27;cafea;32\n2026-10-27;pâine;4.5\n2026-10-28;benzină;250\n'
['2026-10-27', 'cafea', '32']
['2026-10-27', 'pâine', '4.5']
['2026-10-28', 'benzină', '250']
```

- `read()` dă tot textul. E comod pentru fișiere mici;
- `for linie in fisier:` parcurge rândurile unul câte unul, fără să încarce tot fișierul în memorie. E varianta potrivită pentru fișiere mari și cea mai folosită;
- fiecare rând **păstrează `\n`-ul de la final**, de aceea îl cureți cu `strip()` (lecția 4) înainte să-l folosești;
- `repr()` afișează un string așa cum l-ai scrie în cod, cu `\n` vizibil. E util când vrei să vezi exact ce conține.

Mai există `fisier.readlines()`, care dă o listă cu toate rândurile, și `fisier.readline()`, care citește un singur rând.

### Adăugarea la final: modul "a"

Un jurnal crește în timp. Modul `"a"` scrie la finalul fișierului, fără să-l golească:

```python
with open("cheltuieli.txt", "a", encoding="utf-8") as fisier:
    fisier.write("2026-10-29;cinema;45\n")

with open("cheltuieli.txt", encoding="utf-8") as fisier:
    print(f"Jurnalul are acum {len(fisier.readlines())} rânduri.")
```

```text
Jurnalul are acum 4 rânduri.
```

### Căi: pathlib.Path

O cale se poate scrie ca simplu string, dar `Path` din modulul `pathlib` e mult mai comod. Detaliile despre `import` sunt la lecția 29; deocamdată reține că rândul `from pathlib import Path` face disponibil tipul `Path`.

```python
from pathlib import Path

folder = Path("date")
folder.mkdir(exist_ok=True)                 # creează folderul, dacă nu există
cale = folder / "octombrie.txt"             # / lipește bucăți de cale
cale.write_text("cafea;32\n", encoding="utf-8")

print(cale)
print(cale.name, cale.stem, cale.suffix)
print(cale.parent)
print(cale.exists(), Path("nu_exista.txt").exists())
print(repr(cale.read_text(encoding="utf-8")))
```

```text
date/octombrie.txt
octombrie.txt octombrie .txt
date
True False
'cafea;32\n'
```

Ce oferă `Path`:
- operatorul `/` construiește căi corecte pe orice sistem. Pe Windows separatorul e `\`, pe Linux și macOS e `/`, iar `Path` alege singur. Așa scapi și de problema cu `\n` din căile Windows (lecția 5);
- `name` (numele complet), `stem` (fără extensie), `suffix` (extensia), `parent` (folderul);
- `exists()`, `is_file()`, `is_dir()` verifică ce e pe disc;
- `read_text()` și `write_text()` deschid, citesc sau scriu și închid fișierul într-un singur apel. Sunt ideale pentru fișiere mici;
- `mkdir(exist_ok=True)` creează un folder fără eroare dacă există deja; cu `parents=True` creează și folderele intermediare.

`glob()` caută fișiere după un tipar:

```python
from pathlib import Path

for luna in ["noiembrie", "decembrie"]:
    (Path("date") / f"{luna}.txt").write_text("", encoding="utf-8")

for cale in sorted(Path("date").glob("*.txt")):
    print(cale.name)
```

```text
decembrie.txt
noiembrie.txt
octombrie.txt
```

`*` înseamnă „orice text”, deci `*.txt` înseamnă „toate fișierele care se termină cu `.txt`”.

### Ce se întâmplă „pe dedesubt”: căile relative pornesc din folderul curent

O cale ca `"cheltuieli.txt"` e **relativă**: Python o caută în **folderul curent de lucru** (în engleză „current working directory”), adică folderul din care a fost pornit programul, **nu** neapărat folderul în care se află fișierul `.py`.

În PyTutor, terminalul pornește din rădăcina proiectului. Când apeși **Rulează și verifică**, comanda e `python capitole/27-fisiere/fisiere.py`, deci folderul curent e rădăcina proiectului. Un `open("cheltuieli.txt", "w", ...)` creează fișierul **acolo**, nu în `capitole/27-fisiere/`.

Ca să lucrezi cu fișiere aflate lângă script, oricare ar fi folderul curent, construiești calea pornind de la `__file__`, variabila care conține calea scriptului care rulează:

<!-- nu-rula -->
```python
from pathlib import Path

AICI = Path(__file__).parent          # folderul în care se află scriptul
jurnal = AICI / "cheltuieli.txt"       # mereu lângă script
```

O cale **absolută** pornește de la rădăcina discului (`/home/ana/...` sau `C:\Users\ana\...`) și nu depinde de folderul curent, dar nici nu funcționează pe alt calculator. De aceea, în proiecte se folosesc căi relative la script sau la proiect, construite ca mai sus.

## Exemplu complet

Jurnalul de cheltuieli al Anei: fiecare rulare adaugă cheltuieli noi într-un fișier text, apoi citește tot jurnalul și afișează un rezumat. Rândurile au forma `data;categorie;suma`.

<!-- fisier: jurnal.py -->
<!-- stdin: 2026-10-29\ncafea\n14,5\n2026-10-29\ncărți\n89\n\n -->
```python
from pathlib import Path

JURNAL = Path("jurnal.txt")

if not JURNAL.exists():
    JURNAL.write_text("2026-10-27;cafea;32\n2026-10-28;benzină;250\n", encoding="utf-8")
    print("Am creat un jurnal nou.")

# 1. Adăugare: câte o cheltuială pe rând, până la o dată goală
with open(JURNAL, "a", encoding="utf-8") as fisier:
    while True:
        data = input("Data (AAAA-LL-ZZ, gol = gata): ").strip()
        if not data:
            break
        categorie = input("Categorie: ").strip().lower()
        suma = input("Suma: ").strip().replace(",", ".")
        fisier.write(f"{data};{categorie};{suma}\n")

# 2. Citire și rezumat
total = 0.0
pe_categorii = {}
numar = 0
with open(JURNAL, encoding="utf-8") as fisier:
    for linie in fisier:
        linie = linie.strip()
        if not linie:
            continue
        data, categorie, suma = linie.split(";")
        total += float(suma)
        pe_categorii[categorie] = pe_categorii.get(categorie, 0) + float(suma)
        numar += 1

print(f"\n{numar} cheltuieli, total {total:.2f} lei")
for categorie, suma in sorted(pe_categorii.items()):
    print(f"  {categorie:<10}{suma:>9.2f}")
print(f"Fișier: {JURNAL.name}, {JURNAL.stat().st_size} octeți")
```

```text
Am creat un jurnal nou.
Data (AAAA-LL-ZZ, gol = gata): 2026-10-29
Categorie: cafea
Suma: 14,5
Data (AAAA-LL-ZZ, gol = gata): 2026-10-29
Categorie: cărți
Suma: 89
Data (AAAA-LL-ZZ, gol = gata): 

4 cheltuieli, total 385.50 lei
  benzină      250.00
  cafea         46.50
  cărți         89.00
Fișier: jurnal.txt, 88 octeți
```

Observă:
- `open()` acceptă direct un `Path`, nu doar un string;
- la a doua rulare, mesajul „Am creat un jurnal nou.” nu mai apare, iar cheltuielile se adaugă la cele vechi: datele **rămân între rulări**;
- jurnalul are 88 de **octeți**, deși textul are doar 85 de caractere: în UTF-8, literele cu diacritice (`ă`, `ț`) ocupă câte 2 octeți. `stat().st_size` dă dimensiunea fișierului pe disc.

Formatul `data;categorie;suma` e un CSV simplu, făcut de mână. La lecția 28 vei folosi modulele `csv` și `json`, care tratează și cazurile grele (de exemplu, un `;` chiar în numele categoriei).

## Greșeli frecvente

### 1. Fișierul nu există

<!-- fisier: citeste.py -->
```python
with open("cheltuieli_2025.txt", encoding="utf-8") as fisier:
    print(fisier.read())
```

```text
Traceback (most recent call last):
  File "citeste.py", line 1, in <module>
    with open("cheltuieli_2025.txt", encoding="utf-8") as fisier:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'cheltuieli_2025.txt'
```

Cele mai dese cauze sunt numele scris greșit și **folderul curent** diferit de cel la care te gândeai (vezi „pe dedesubt”). Verifică întâi cu `Path("...").exists()` sau prinde eroarea cu `try / except FileNotFoundError` (lecția 24).

### 2. Modul "w" golește fișierul

```python
with open("important.txt", "w", encoding="utf-8") as fisier:
    fisier.write("rândul 1\nrândul 2\n")

with open("important.txt", "w", encoding="utf-8") as fisier:
    fisier.write("rândul 3\n")

with open("important.txt", encoding="utf-8") as fisier:
    print(fisier.read())
```

```text
rândul 3

```

Al doilea `open(..., "w")` a golit fișierul înainte să scrie, fără nicio întrebare și fără nicio eroare. Ca să adaugi, folosește `"a"`. Ca să nu suprascrii din greșeală un fișier existent, folosește `"x"`, care dă `FileExistsError` dacă fișierul există.

### 3. write() primește un număr

<!-- fisier: scrie.py -->
```python
suma = 32
with open("suma.txt", "w", encoding="utf-8") as fisier:
    fisier.write(suma)
```

```text
Traceback (most recent call last):
  File "scrie.py", line 3, in <module>
    fisier.write(suma)
TypeError: write() argument must be str, not int
```

Într-un fișier text se scrie doar text. Convertește valoarea: `fisier.write(f"{suma}\n")`. Invers, ce citești dintr-un fișier e mereu `str`, ca la `input()` (lecția 6), deci numerele trebuie convertite cu `int()` sau `float()`.

### 4. Citire după închiderea fișierului

<!-- fisier: citeste.py -->
```python
with open("important.txt", encoding="utf-8") as fisier:
    pass
print(fisier.read())
```

```text
Traceback (most recent call last):
  File "citeste.py", line 3, in <module>
    print(fisier.read())
          ^^^^^^^^^^^^^
ValueError: I/O operation on closed file.
```

La ieșirea din blocul `with`, fișierul se închide. Tot ce citește sau scrie trebuie să fie **în** bloc (indentat). Dacă ai nevoie de conținut mai târziu, păstrează-l într-o variabilă în interiorul blocului.

### 5. Lipsa lui encoding

<!-- nu-rula -->
```python
with open("jurnal.txt") as fisier:     # fără encoding
    print(fisier.read())
```

Pe Linux și macOS, codul de mai sus merge de obicei, pentru că encoding-ul implicit e UTF-8. Pe Windows, encoding-ul implicit depinde de setările sistemului. Cu `cp1252` (Windows în engleză), jurnalul din exemplul complet se citește greșit, fără eroare: apare `benzinÄƒ` în loc de `benzină`. Cu `cp1250` (Windows în română), citirea se oprește cu o eroare:

```text
UnicodeDecodeError: 'charmap' codec can't decode byte 0x83 in position 38: character maps to <undefined>
```

Octetul `0x83` e a doua jumătate a lui `ă` în UTF-8, pe care `cp1250` nu o recunoaște.

Același program se comportă diferit pe calculatoare diferite, ceea ce e cel mai greu de depanat. Scrie mereu `encoding="utf-8"`, și la citire, și la scriere.

## Exercițiu

În `capitole/27-fisiere/fisiere.py`, scrie un **jurnal de lectură**:

1. fișierul `lecturi.txt` stă **lângă script** (calea construită cu `Path(__file__).parent`, ca în „pe dedesubt”), cu rânduri de forma `titlu;autor;pagini`;
2. un meniu cu `while True`: `1` = adaugă o carte (cu modul `"a"`), `2` = afișează toate cărțile ca tabel aliniat, `3` = statistici, `0` = ieșire;
3. dacă fișierul nu există încă, opțiunile `2` și `3` afișează „Jurnalul e gol”, fără eroare;
4. la statistici: numărul de cărți, totalul de pagini, cartea cea mai lungă și numărul de cărți pentru fiecare autor (un dicționar, ca la lecția 14);
5. rândurile goale sau cu alt număr de câmpuri decât 3 sunt ignorate la citire, cu un mesaj care spune numărul rândului (folosește `enumerate(fisier, start=1)`, lecția 17).

## Pe scurt

- `open(cale, mod, encoding="utf-8")` deschide un fișier; modurile principale sunt `"r"` (citire), `"w"` (scriere, golește fișierul), `"a"` (adăugare) și `"x"` (doar fișier nou).
- `with open(...) as fisier:` închide fișierul automat la ieșirea din bloc.
- `write()` nu adaugă `\n`; `for linie in fisier:` citește rând cu rând, cu `\n` la final, deci folosește `strip()`.
- Tot ce se citește dintr-un fișier text e `str`; tot ce se scrie trebuie să fie `str`.
- `Path` din `pathlib`: `/` pentru căi, `name`, `suffix`, `parent`, `exists()`, `read_text()`, `write_text()`, `mkdir()`, `glob()`.
- Căile relative pornesc din folderul curent, nu din folderul scriptului; pentru fișiere de lângă script, folosește `Path(__file__).parent`.
