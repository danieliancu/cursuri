## Ce este

**PEP 8** este ghidul oficial de stil pentru codul Python: un document care spune cum se numesc variabilele, cum se pun spațiile, cât de lung poate fi un rând, cum se ordonează importurile. „PEP” vine de la „Python Enhancement Proposal” (propunere de îmbunătățire a lui Python); PEP 8 e propunerea cu numărul 8, scrisă în 2001 de Guido van Rossum, autorul limbajului, împreună cu alți doi programatori.

Pe lângă ghid, vei folosi trei **unelte** care îl aplică automat:
- **black** **formatează** codul: rescrie spațiile, rândurile goale și parantezele după reguli fixe;
- **ruff** **verifică** codul și semnalează probleme: importuri nefolosite, nume nepotrivite, comparații greșite;
- **mypy** **verifică tipurile**, pe baza type hints-urilor din lecția 22.

În terminalul din PyTutor, toate trei sunt deja instalate.

## De ce contează

Codul se citește mult mai des decât se scrie. Când tot codul unui proiect arată la fel, îl citești repede, fără să te împiedici de stiluri diferite, și vezi direct ce face. Asta contează și când lucrezi singur (tu, peste o lună, ești „altcineva”), și mai ales într-o echipă.

Uneltele mai rezolvă o problemă: discuțiile despre stil. Nimeni nu mai pierde timpul cu „pune un spațiu aici”, pentru că black hotărăște pentru toți. Iar ruff și mypy găsesc greșeli reale **înainte** să rulezi programul: o variabilă scrisă greșit, un import uitat, un `None` folosit ca număr. Proiectele serioase, inclusiv Django, își verifică automat codul cu astfel de unelte la fiecare modificare.

## Cum funcționează

### Nume

| Ce numești | Stil | Exemplu |
|---|---|---|
| variabile, funcții, metode, module | `snake_case` | `pret_total`, `citeste_linie()`, `jurnal.py` |
| clase (lecția 32) | `PascalCase` | `Carte`, `MembruStudent` |
| constante | `MAJUSCULE_CU_UNDERSCORE` | `TVA`, `MAX_INCERCARI` |
| „intern, nu folosi din afară” | începe cu `_` | `_calculeaza_taxa()` |

O **constantă** e o valoare care nu se schimbă în timpul programului. Python nu te oprește s-o modifici; numele cu majuscule e doar un semnal pentru cititor. Constantele înlocuiesc „numerele magice” din cod:

```python
TVA = 0.21
PRAG_TRANSPORT_GRATUIT = 100


def total_cu_tva(valoare):
    return round(valoare * (1 + TVA), 2)


print(total_cu_tva(50))
print(total_cu_tva(50) >= PRAG_TRANSPORT_GRATUIT)
```

```text
60.5
False
```

Evită numele de o singură literă (cu excepția contoarelor scurte, ca `i`, și a lui `_`). Mai ales `l`, `O` și `I` nu se folosesc niciodată singure ca nume, pentru că se confundă cu `1` și `0`.

### Spații și rânduri goale

Regulile pe care le-ai respectat deja, din obișnuință, în tot cursul:
- indentare de **4 spații**, niciodată tab-uri amestecate cu spații;
- câte un spațiu în jurul operatorilor de atribuire și comparație (`x = 1`, `a == b`) și după virgulă (`f(a, b)`);
- fără spații în interiorul parantezelor (`f(a)`, nu `f( a )`) și nici înainte de `:` sau de paranteza unui apel;
- **două** rânduri goale înainte și după funcțiile și clasele de la nivelul de sus al fișierului, **unul** între metodele unei clase;
- excepție: la argumentele keyword nu se pun spații în jurul lui `=`: `sorted(note, reverse=True)`.

### Lungimea rândurilor

PEP 8 recomandă cel mult **79 de caractere** pe rând. black folosește implicit **88**, iar multe proiecte au adoptat această limită. Un rând prea lung se rupe în interiorul parantezelor, unde Python permite continuarea pe rândul următor:

```python
cheltuieli = {"mâncare": 412.5, "transport": 180.0, "chirie": 1500.0, "distracție": 220.0}
total = (
    cheltuieli["mâncare"]
    + cheltuieli["transport"]
    + cheltuieli["chirie"]
)
print(total)
```

```text
2092.5
```

### Importuri

Importurile (lecția 29) stau la începutul fișierului, câte unul pe rând, în trei grupuri separate de un rând gol: biblioteca standard, pachete instalate cu pip, modulele proiectului tău.

```python
import json
from pathlib import Path

import django

from jurnal import incarca
```

Importurile nefolosite se șterg: doar încarcă degeaba module și îl încurcă pe cititor.

### Comparații și condiții

```python
nota = None
note = [9, 10]
este_activ = True

if nota is None:            # nu: nota == None
    print("fără notă")
if note:                    # nu: if len(note) > 0
    print("are note")
if este_activ:              # nu: if este_activ == True
    print("activ")
```

```text
fără notă
are note
activ
```

`is None` verifică dacă e **chiar** obiectul `None` (lecția 12 a arătat diferența dintre `is` și `==`). Truthiness (lecția 7) face condițiile scurte și clare.

### lambda cu nume

La lecția 21 ai văzut că poți da un nume unei funcții `lambda`, dar că nu e o idee bună. PEP 8 o spune explicit: o funcție cu nume se scrie cu `def`. `lambda` e pentru funcții scurte, date direct ca argument (de exemplu la `key=`). Cu `def`, funcția are un nume real în tracebackuri și poate primi un docstring.

```python
# Nu: dublu = lambda x: x * 2
def dublu(x):
    return x * 2


preturi = {"pâine": 4.5, "cafea": 32.0, "lapte": 8.99}
print(dublu(21))
print(sorted(preturi, key=lambda produs: preturi[produs]))
```

```text
42
['pâine', 'lapte', 'cafea']
```

ruff (prezentat mai jos) semnalează varianta cu nume ca problemă de stil, cu codul `E731`:

<!-- fisier: lambda_nume.py -->
```python
dublu = lambda x: x * 2
```

<!-- ruleaza -->
```bash
ruff check --select E,F,W,I,N --output-format concise lambda_nume.py
```

```text
lambda_nume.py:1:1: E731 Do not assign a `lambda` expression, use a `def`
Found 1 error.
1 unsafe fix available with `--fix --unsafe-fixes`.
```

### black: formatare automată

Un fișier scris în grabă, fără grijă la stil:

<!-- fisier: note.py -->
```python
import os
def Media( Note ):
    total=0
    for n in Note : total+=n
    if total == None:
        return 0
    return total/len(Note)
print(Media([9,10,8]))
```

`black --check` spune doar dacă fișierul ar fi reformatat, fără să-l modifice:

<!-- ruleaza -->
```bash
black --check note.py
```

```text
would reformat note.py

Oh no! 💥 💔 💥
1 file would be reformatted.
```

Fără `--check`, black rescrie fișierul:

<!-- ruleaza -->
```bash
black note.py
cat note.py
```

```text
reformatted note.py

All done! ✨ 🍰 ✨
1 file reformatted.
import os


def Media(Note):
    total = 0
    for n in Note:
        total += n
    if total == None:
        return 0
    return total / len(Note)


print(Media([9, 10, 8]))
```

(`cat` afișează conținutul unui fișier în terminal.) black a reparat spațiile, rândurile goale și bucla scrisă pe un singur rând. **Nu** a schimbat însă nimic din ce ține de sens: numele `Media` și `Note`, importul nefolosit, `== None`. Pentru acestea e nevoie de ruff.

### ruff: verificare

Fără configurare, versiunea de ruff din PyTutor verifică un set larg de reguli, unele fără legătură cu un începător (de exemplu `EXE002`, care apare doar din cauza felului în care PyTutor îți păstrează fișierele). Le alegi explicit cu `--select`: `E` și `W` (stilul din PEP 8), `F` (greșeli reale, ca nume nedefinite), `I` (ordinea importurilor) și `N` (numele). `--output-format concise` scrie câte o problemă pe rând.

<!-- ruleaza -->
```bash
ruff check --select E,F,W,I,N --output-format concise note.py
```

```text
note.py:1:8: F401 [*] `os` imported but unused
note.py:4:5: N802 Function name `Media` should be lowercase
note.py:4:11: N803 Argument name `Note` should be lowercase
note.py:8:17: E711 Comparison to `None` should be `cond is None`
Found 4 errors.
[*] 1 fixable with `--fix` (1 unsafe fix available with `--fix --unsafe-fixes`).
```

Fiecare rând are forma `fișier:rând:coloană: COD mesaj`. Codul (`F401`, `N802`) îl poți căuta în documentația lui ruff ca să afli detalii. Problemele marcate `[*]` le poate repara ruff singur, cu `--fix`. Celelalte, ca numele, le repari tu.

Ca să nu scrii `--select` de fiecare dată, regulile se pun în fișierul `pyproject.toml` din rădăcina proiectului, iar apoi ajunge `ruff check`:

```toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "N"]
```

ruff are și o comandă de formatare, `ruff format`, care face aproape exact ce face black. Un proiect folosește de obicei una dintre ele, nu pe amândouă.

### mypy: verificarea tipurilor

La lecția 22 ai învățat că type hints nu sunt verificate de Python la rulare. mypy le verifică **fără să ruleze** programul:

<!-- fisier: tipuri.py -->
```python
def media(note: list[float]) -> float:
    return sum(note) / len(note)


print(media([9, 10, 8]))
print(media("9 10 8"))
```

<!-- ruleaza -->
```bash
mypy tipuri.py
```

```text
tipuri.py:6: error: Argument 1 to "media" has incompatible type "str"; expected "list[float]"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

Python ar fi rulat primul `print` și abia la al doilea s-ar fi oprit cu un `TypeError`. mypy a găsit problema citind doar codul. Pe un proiect mare, unde unele funcții se apelează rar, diferența e uriașă.

### Ce se întâmplă „pe dedesubt”: black nu poate strica programul

black nu caută și înlocuiește text. Citește codul și îl transformă într-un **arbore de sintaxă** (în engleză „abstract syntax tree”, AST), adică structura programului: „o funcție cu un parametru, care conține o buclă, care conține o atribuire”. Apoi scrie din nou codul din acest arbore, după regulile lui. La final verifică dacă noul cod produce **același arbore** ca cel vechi; dacă nu, renunță și raportează o eroare. De aceea black poate schimba aspectul codului, dar nu și ce face.

ruff citește codul tot ca arbore de sintaxă, așa că înțelege, de exemplu, că `os` e importat și nefolosit. E scris în limbajul Rust și e foarte rapid, chiar și pe proiecte cu mii de fișiere.

## Exemplu complet

Funcțiile jurnalului de cheltuieli (lecțiile 27–31), scrise în grabă:

<!-- fisier: jurnal_rapid.py -->
```python
import json, sys
from pathlib import Path
CALE=Path("jurnal.json")
def Total(jurnal, Categorie = None):
    s=0
    for c in jurnal :
        if Categorie == None or c["categorie"]==Categorie: s+=c["suma"]
    return s
def categorii(jurnal) :
    return sorted(set( c["categorie"] for c in jurnal ))
```

Pasul 1: ruff găsește problemele.

<!-- ruleaza -->
```bash
ruff check --select E,F,W,I,N --output-format concise jurnal_rapid.py
```

```text
jurnal_rapid.py:1:1: E401 [*] Multiple imports on one line
jurnal_rapid.py:1:1: I001 [*] Import block is un-sorted or un-formatted
jurnal_rapid.py:1:8: F401 [*] `json` imported but unused
jurnal_rapid.py:1:14: F401 [*] `sys` imported but unused
jurnal_rapid.py:4:5: N802 Function name `Total` should be lowercase
jurnal_rapid.py:4:19: N803 Argument name `Categorie` should be lowercase
jurnal_rapid.py:7:25: E711 Comparison to `None` should be `cond is None`
jurnal_rapid.py:7:58: E701 Multiple statements on one line (colon)
Found 8 errors.
[*] 4 fixable with `--fix` (1 unsafe fix available with `--fix --unsafe-fixes`).
```

Pasul 2: repari numele și comparația cu mâna, ruff șterge importurile nefolosite (`--fix`), black așază restul, iar pe parcurs adaugi type hints. Rezultatul:

<!-- fisier: jurnal_rapid.py -->
```python
from pathlib import Path

CALE = Path("jurnal.json")


def total(jurnal: list[dict], categorie: str | None = None) -> float:
    """Suma cheltuielilor, eventual doar dintr-o categorie."""
    suma = 0.0
    for cheltuiala in jurnal:
        if categorie is None or cheltuiala["categorie"] == categorie:
            suma += cheltuiala["suma"]
    return suma


def categorii(jurnal: list[dict]) -> list[str]:
    """Categoriile distincte, sortate."""
    return sorted({cheltuiala["categorie"] for cheltuiala in jurnal})
```

Pasul 3: toate cele trei unelte sunt mulțumite.

<!-- ruleaza -->
```bash
ruff check --select E,F,W,I,N jurnal_rapid.py
black --check jurnal_rapid.py
mypy jurnal_rapid.py
```

```text
All checks passed!
All done! ✨ 🍰 ✨
1 file would be left unchanged.
Success: no issues found in 1 source file
```

Observă și schimbările pe care nu le-a cerut nicio unealtă, dar care fac codul mai clar: `s` a devenit `suma`, `c` a devenit `cheltuiala`, iar `sorted(set(...))` a devenit un set comprehension (lecția 16). Uneltele prind ce e mecanic; numele bune rămân treaba ta.

## Greșeli frecvente

### 1. Tab-uri amestecate cu spații

Editoarele de cod pun spații la Tab, dar un fișier copiat de pe internet poate conține tab-uri reale. Pentru ochi arată la fel; pentru Python, nu:

<!-- fisier: tab.py -->
```python
def media(note):
    total = sum(note)
	return total / len(note)
```

```text
  File "tab.py", line 3
    return total / len(note)
TabError: inconsistent use of tabs and spaces in indentation
```

Rândul 2 e indentat cu 4 spații, rândul 3 cu un tab. Nici black nu te ajută aici: un fișier pe care Python nu-l poate citi nu poate fi nici formatat, iar black se oprește cu o eroare. Înlocuiește tab-ul cu 4 spații în editor (multe editoare au o comandă „convert indentation to spaces”) și folosește de acum doar spații.

### 2. Așteptarea ca black să repare tot

black nu redenumește nimic și nu șterge cod. Un fișier poate fi perfect formatat și totuși plin de probleme:

<!-- fisier: formatat.py -->
```python
import os


def Media(Note):
    if Note == None:
        return 0
    return sum(Note) / len(Note)
```

<!-- ruleaza -->
```bash
black --check formatat.py
ruff check --select E,F,W,I,N --output-format concise formatat.py
```

```text
All done! ✨ 🍰 ✨
1 file would be left unchanged.
formatat.py:1:8: F401 [*] `os` imported but unused
formatat.py:4:5: N802 Function name `Media` should be lowercase
formatat.py:4:11: N803 Argument name `Note` should be lowercase
formatat.py:5:16: E711 Comparison to `None` should be `cond is None`
Found 4 errors.
[*] 1 fixable with `--fix` (1 unsafe fix available with `--fix --unsafe-fixes`).
```

Folosește-le pe amândouă: black pentru aspect, ruff pentru conținut.

### 3. Ignorarea lui mypy pentru că „programul merge”

O funcție care poate întoarce `None` (lecția 18) merge în toate testele tale, până când datele sunt altele:

<!-- fisier: cauta.py -->
```python
def pret(produse: dict[str, float], nume: str) -> float | None:
    return produse.get(nume)


preturi = {"pâine": 4.5, "lapte": 8.99}
print(pret(preturi, "pâine") * 2)
```

<!-- ruleaza -->
```bash
python cauta.py
mypy cauta.py
```

```text
9.0
cauta.py:6: error: Unsupported operand types for * ("None" and "int")  [operator]
cauta.py:6: note: Left operand is of type "float | None"
Found 1 error in 1 file (checked 1 source file)
```

Programul a rulat, pentru că „pâine” există. Cu un produs care lipsește, `None * 2` ar fi dat `TypeError`. mypy a văzut riscul din tipul `float | None` și cere să tratezi cazul `None` înainte să faci calcule: salvezi rezultatul într-o variabilă (`pret_paine = pret(preturi, "pâine")`) și verifici întâi `if pret_paine is None:`.

### 4. Rânduri prea lungi

Rândurile peste limită sunt greu de citit, mai ales când compari două fișiere unul lângă altul:

<!-- fisier: lung.py -->
```python
mesaj = "Bună ziua, " + "Ana Popescu" + "! Comanda ta a fost trimisă în Cluj și va ajunge mâine."
```

<!-- ruleaza -->
```bash
ruff check --select E,F,W,I,N --output-format concise --line-length 79 lung.py
```

```text
lung.py:1:80: E501 Line too long (97 > 79)
Found 1 error.
```

`--line-length 79` aplică limita din PEP 8 (implicit, ruff folosește 88, ca black). Rândul se rupe în paranteze, ca în secțiunea despre lungimea rândurilor. Evită continuarea cu `\` la final de rând: e fragilă, pentru că un singur spațiu după backslash strică totul.

```python
mesaj = (
    "Bună ziua, "
    + "Ana Popescu"
    + "! Comanda ta a fost trimisă în Cluj și va ajunge mâine."
)
```

## Exercițiu

În `capitole/40-pep8-stil/pep8_stil.py`, copiază codul de mai jos, apoi adu-l la standard:

```python
import math, random
def CalculeazaReducere( Valoare,Cod ):
  if Cod==None : return 0
  if Cod.upper()=="STUDENT": return Valoare*0.1
  elif Cod.upper()=="VARA2026" and Valoare>=150 : return 20
  else : return 0
Rezultat=CalculeazaReducere(200,"vara2026")
print( Rezultat )
```

1. rulează `ruff check --select E,F,W,I,N --output-format concise capitole/40-pep8-stil/pep8_stil.py` și notează ce probleme raportează;
2. repară-le: nume în `snake_case`, `is None`, fără importuri nefolosite, câte o instrucțiune pe rând;
3. înlocuiește numerele „magice” (`0.1`, `150`, `20`) cu constante cu nume clare;
4. adaugă type hints și un docstring funcției (lecția 22);
5. rulează `black`, apoi verifică din nou: `ruff check ...`, `black --check ...` și `mypy ...` trebuie să nu raporteze nimic;
6. rulează programul și verifică dacă rezultatul e același ca înainte (`20`).

## Pe scurt

- PEP 8 e ghidul de stil Python: `snake_case` pentru variabile și funcții, `PascalCase` pentru clase, `MAJUSCULE` pentru constante, 4 spații, două rânduri goale între funcții.
- Importurile stau sus, grupate (standard, instalate, ale tale); comparația cu `None` se face cu `is`, iar `lambda` nu primește nume.
- **black** formatează automat (`black --check` doar verifică) și nu schimbă ce face programul.
- **ruff** găsește probleme de stil și greșeli reale; alege regulile cu `--select` sau în `pyproject.toml`; `--fix` repară o parte.
- **mypy** verifică type hints fără să ruleze codul și prinde, de exemplu, un `None` folosit ca număr.
- Uneltele prind ce e mecanic; numele clare și funcțiile scurte rămân treaba ta.
