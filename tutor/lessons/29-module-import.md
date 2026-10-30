## Ce este

Un **modul** e un fișier `.py` al cărui cod (funcții, variabile, clase) poate fi folosit din alt fișier. Instrucțiunea **`import`** încarcă un modul și îți dă acces la ce conține:

```python
import math

print(math.sqrt(81))
print(math.pi)
```

```text
9.0
3.141592653589793
```

`math` e un modul din **biblioteca standard**, colecția de module care vine cu Python. Dar orice fișier `.py` scris de tine e tot un modul. Un **pachet** (în engleză „package”) e un folder care grupează mai multe module.

## De ce contează

Până acum, fiecare program stătea într-un singur fișier. Jurnalul de cheltuieli din lecția 28 avea deja patru părți: încărcare, adăugare, salvare și raport. Pe măsură ce programul crește, un singur fișier devine greu de citit, iar codul nu poate fi refolosit: dacă vrei aceeași funcție de încărcare a jurnalului într-un alt program, trebuie s-o copiezi.

Modulele rezolvă ambele probleme:
- **organizare**: fiecare fișier are o singură responsabilitate, cu un nume care spune ce face;
- **refolosire**: o funcție scrisă o dată se importă oriunde e nevoie;
- **acces la cod scris de alții**: biblioteca standard (lecția 31) și pachetele instalate cu `pip` (lecția 30).

Un proiect Django e, de fapt, o colecție de module și pachete (`settings.py`, `urls.py`, `models.py`, `views.py`), care se importă unele pe altele. Fără `import`, Django nu ar exista.

## Cum funcționează

### Formele lui import

```python
import math                      # tot modulul; folosești math.ceil(...)
from math import sqrt, pi        # doar anumite nume; le folosești direct
import statistics as st          # modul cu un nume mai scurt (alias)
from math import floor as rotunjeste_in_jos

print(math.ceil(4.2))
print(sqrt(16), round(pi, 2))
print(st.mean([9, 7, 10]))
print(rotunjeste_in_jos(4.8))
```

```text
5
4.0 3.14
8.666666666666666
4
```

Cum alegi:
- **`import modul`** e varianta cea mai clară: când citești `math.sqrt(...)`, știi imediat de unde vine `sqrt`. Folosește-o implicit;
- **`from modul import nume`** e comodă pentru nume folosite des, al căror rost e evident (`from pathlib import Path`, pe care l-ai văzut la lecția 27);
- **`as`** dă un alias, util pentru nume lungi sau prin convenție (`import numpy as np` e scris așa de toată lumea).

Există și `from modul import *`, care aduce toate numele dintr-un modul. **Evit-o**: nu mai știi de unde vine un nume, iar numele importate pot acoperi fără niciun avertisment variabilele tale.

Importurile se pun **la începutul fișierului**, câte unul pe rând: întâi modulele din biblioteca standard, apoi cele instalate, apoi cele ale tale.

### Primul tău modul

Împărțim jurnalul de cheltuieli. Funcțiile care lucrează cu fișierul JSON merg într-un modul separat, `jurnal_fisier.py`:

<!-- fisier: jurnal_fisier.py -->
```python
"""Încărcarea și salvarea jurnalului de cheltuieli în format JSON."""
import json
from pathlib import Path

CALE_IMPLICITA = Path("cheltuieli.json")


def incarca(cale=CALE_IMPLICITA):
    """Întoarce jurnalul din fișier sau un jurnal nou, dacă fișierul nu există."""
    if not cale.exists():
        return {"cheltuieli": []}
    with open(cale, encoding="utf-8") as fisier:
        return json.load(fisier)


def salveaza(jurnal, cale=CALE_IMPLICITA):
    with open(cale, "w", encoding="utf-8") as fisier:
        json.dump(jurnal, fisier, ensure_ascii=False, indent=2)


def total_pe_categorii(jurnal):
    totaluri = {}
    for c in jurnal["cheltuieli"]:
        totaluri[c["categorie"]] = totaluri.get(c["categorie"], 0) + c["suma"]
    return totaluri
```

Programul principal, `aplicatie.py`, aflat în **același folder**, îl importă și îl folosește:

<!-- fisier: aplicatie.py -->
```python
import jurnal_fisier

jurnal = jurnal_fisier.incarca()
jurnal["cheltuieli"].append({"data": "2026-10-29", "categorie": "cafea", "suma": 14.5})
jurnal["cheltuieli"].append({"data": "2026-10-30", "categorie": "cinema", "suma": 45})
jurnal_fisier.salveaza(jurnal)

for categorie, total in jurnal_fisier.total_pe_categorii(jurnal).items():
    print(f"{categorie:<8}{total:>7.2f}")
print("Fișierul implicit:", jurnal_fisier.CALE_IMPLICITA)
```

```text
cafea     14.50
cinema    45.00
Fișierul implicit: cheltuieli.json
```

Numele modulului e numele fișierului **fără** `.py`. Tot ce e definit la nivelul de sus al modulului (funcții, constante ca `CALE_IMPLICITA`) e accesibil cu `jurnal_fisier.nume`. `aplicatie.py` nu mai știe nimic despre JSON: doar cere „încarcă” și „salvează”. Dacă mâine jurnalul trece în CSV, modifici doar `jurnal_fisier.py`.

Șirul de caractere de la începutul modulului (`"""..."""`) e **docstring-ul** modulului: spune pe scurt ce conține, la fel ca docstring-urile funcțiilor (lecția 22).

### `if __name__ == "__main__":`

Când Python încarcă un modul, **execută tot codul de la nivelul de sus** al fișierului. Definițiile de funcții doar creează funcțiile, dar un `print()` sau un `input()` aflat acolo chiar rulează, și asta se întâmplă și la import.

Fiecare modul are o variabilă specială, `__name__`:
- când fișierul e **rulat direct** (`python fisier.py`), `__name__` e `"__main__"`;
- când fișierul e **importat**, `__name__` e numele modulului.

Pe asta se bazează tiparul care separă „cod de folosit din alte fișiere” de „cod care rulează doar când pornești fișierul”. Modulul `unitati.py`, rulat direct cu `python unitati.py`:

<!-- fisier: unitati.py -->
```python
"""Conversii de unități."""


def km_in_mile(km):
    return km * 0.621371


print(f"Modulul unitati se încarcă; __name__ = {__name__!r}")

if __name__ == "__main__":
    # rulează doar la `python unitati.py`, nu și la import
    print("Test rapid:", round(km_in_mile(100), 1), "mile")
```

```text
Modulul unitati se încarcă; __name__ = '__main__'
Test rapid: 62.1 mile
```

Importat din alt fișier:

<!-- fisier: drum.py -->
```python
import unitati
import unitati  # al doilea import nu mai execută nimic

print(f"Cluj–Iași: {unitati.km_in_mile(390):.0f} mile")
```

```text
Modulul unitati se încarcă; __name__ = 'unitati'
Cluj–Iași: 242 mile
```

Două lucruri de reținut:
- la import, testul din `if __name__ == "__main__":` **nu** a rulat;
- modulul s-a încărcat **o singură dată**, deși a fost importat de două ori. Python ține minte modulele deja încărcate și, la un import repetat, îl dă pe cel existent.

În practică, nu pune `print()` la nivelul de sus al unui modul: importul ar trebui să nu facă nimic vizibil. Codul care „face ceva” stă în funcții sau sub `if __name__ == "__main__":`.

### Pachete: foldere de module

Când ai multe module, le grupezi într-un **pachet**: un folder cu un fișier `__init__.py` (poate fi gol), care îi spune lui Python că folderul e un pachet. Structura jurnalului, organizată ca pachet:

```text
proiect/
├── aplicatie.py
└── jurnal/
    ├── __init__.py
    ├── fisier.py
    └── rapoarte.py
```

În editor, creezi folderele și fișierele cu butoanele din Explorer. Aici le creăm din Python, cu ce ai învățat la lecția 27:

```python
from pathlib import Path

pachet = Path("jurnal")
pachet.mkdir(exist_ok=True)
(pachet / "__init__.py").write_text('"""Jurnalul de cheltuieli."""\n', encoding="utf-8")
(pachet / "rapoarte.py").write_text(
    "def linie(categorie, suma):\n"
    "    return f'{categorie:<8}{suma:>7.2f} lei'\n",
    encoding="utf-8",
)
print(sorted(p.name for p in pachet.iterdir()))
```

```text
['__init__.py', 'rapoarte.py']
```

Modulele din pachet se importă cu punct între nume:

```python
from jurnal import rapoarte
import jurnal.rapoarte

print(rapoarte.linie("cafea", 14.5))
print(jurnal.rapoarte.linie("cinema", 45))
```

```text
cafea     14.50 lei
cinema    45.00 lei
```

Exact așa arată importurile în Django: `from django.db import models` înseamnă „din pachetul `django`, subpachetul `db`, ia modulul `models`”.

### Biblioteca standard: un exemplu promis

La lecția 12 am spus că o copie completă a unei liste imbricate se face cu `copy.deepcopy()`. Acum poți s-o folosești:

```python
import copy

catalog = [["Ana", 9, 10], ["Mihai", 7, 6]]
superficial = catalog.copy()
complet = copy.deepcopy(catalog)

catalog[0].append(8)
print(superficial[0])
print(complet[0])
```

```text
['Ana', 9, 10, 8]
['Ana', 9, 10]
```

Copia făcută cu `copy()` împarte listele interioare cu originalul, așa că nota nouă a Anei apare și în ea. `deepcopy()` copiază totul, pe toate nivelurile. Lecția 31 îți prezintă cele mai folosite module din biblioteca standard.

### Ce se întâmplă „pe dedesubt”: unde caută Python modulele

La `import jurnal_fisier`, Python caută un fișier `jurnal_fisier.py` (sau un folder-pachet `jurnal_fisier/`) într-o listă de foldere, în ordine:
1. **folderul scriptului pe care l-ai pornit**;
2. folderele bibliotecii standard;
3. folderul `site-packages`, unde ajung pachetele instalate cu `pip` (lecția 30).

Prima potrivire câștigă. Lista e în `sys.path`:

<!-- nu-rula -->
```python
import sys

for folder in sys.path:
    print(folder)
```

Atenție la diferența față de lecția 27: fișierele deschise cu `open()` se caută pornind din **folderul curent** (de unde ai pornit programul), dar modulele se caută pornind din **folderul scriptului**. De aceea, în PyTutor, `python capitole/29-module-import/module_import.py` poate importa un modul aflat lângă el, în `capitole/29-module-import/`, chiar dacă terminalul e în rădăcina proiectului.

Pentru că folderul scriptului e primul în listă, un fișier al tău cu același nume ca un modul din biblioteca standard îl **ascunde** pe cel real (greșeala 5 de mai jos). Din același motiv, fișierul capitolului de la lecția 36 se numește `dataclasses_exercitii.py`, nu `dataclasses.py`. (La lecția 9, `while_exercitii.py` are alt motiv: `while` e cuvânt rezervat, deci `while.py` n-ar putea fi importat.)

## Exemplu complet

Aplicația jurnalului de cheltuieli, împărțită în module, cu un meniu care le folosește. Modulele `jurnal_fisier.py` (de mai sus) și `jurnal/rapoarte.py` există deja în folder.

<!-- fisier: meniu_jurnal.py -->
<!-- stdin: 1\n2026-10-31\ncărți\n89\n2\n0 -->
```python
"""Aplicația jurnalului de cheltuieli: meniul principal."""
import jurnal_fisier
from jurnal import rapoarte


def adauga(jurnal):
    data = input("Data: ").strip()
    categorie = input("Categorie: ").strip().lower()
    suma = float(input("Suma: ").replace(",", "."))
    jurnal["cheltuieli"].append({"data": data, "categorie": categorie, "suma": suma})
    jurnal_fisier.salveaza(jurnal)
    print("Salvat.")


def raport(jurnal):
    totaluri = jurnal_fisier.total_pe_categorii(jurnal)
    for categorie, suma in sorted(totaluri.items()):
        print(rapoarte.linie(categorie, suma))
    print(rapoarte.linie("TOTAL", sum(totaluri.values())))


def main():
    jurnal = jurnal_fisier.incarca()
    while True:
        optiune = input("1 = adaugă, 2 = raport, 0 = ieșire: ").strip()
        if optiune == "0":
            break
        elif optiune == "1":
            adauga(jurnal)
        elif optiune == "2":
            raport(jurnal)


if __name__ == "__main__":
    main()
```

```text
1 = adaugă, 2 = raport, 0 = ieșire: 1
Data: 2026-10-31
Categorie: cărți
Suma: 89
Salvat.
1 = adaugă, 2 = raport, 0 = ieșire: 2
cafea     14.50 lei
cinema    45.00 lei
cărți     89.00 lei
TOTAL    148.50 lei
1 = adaugă, 2 = raport, 0 = ieșire: 0
```

Structura e cea pe care o vei întâlni peste tot:
- fiecare modul are o singură treabă: `jurnal_fisier` știe de fișiere, `jurnal.rapoarte` știe de afișare, iar `meniu_jurnal` leagă totul și vorbește cu utilizatorul;
- programul principal are o funcție `main()`, apelată doar sub `if __name__ == "__main__":`. Așa, și `meniu_jurnal.py` poate fi importat (de exemplu, de teste, la lecția 41) fără să pornească meniul;
- cheltuielile adăugate la rularea anterioară (cafea, cinema) au fost încărcate din `cheltuieli.json`.

## Greșeli frecvente

### 1. Modulul nu e găsit

<!-- fisier: greseala.py -->
```python
import jurnal_fisiere
```

```text
Traceback (most recent call last):
  File "greseala.py", line 1, in <module>
    import jurnal_fisiere
ModuleNotFoundError: No module named 'jurnal_fisiere'
```

Cauze, în ordinea frecvenței: numele e scris greșit (aici `fisiere` în loc de `fisier`); modulul e în alt folder decât scriptul pornit (vezi „pe dedesubt”); e un pachet de pe internet care nu e instalat (lecția 30). Nu scrie `.py` în `import`: `import jurnal_fisier.py` caută un modul `py` în pachetul `jurnal_fisier`.

### 2. Un nume care nu există în modul

<!-- fisier: greseala.py -->
```python
from jurnal_fisier import incarca, sterge
```

```text
Traceback (most recent call last):
  File "greseala.py", line 1, in <module>
    from jurnal_fisier import incarca, sterge
ImportError: cannot import name 'sterge' from 'jurnal_fisier' (jurnal_fisier.py)
```

Modulul a fost găsit, dar nu conține o funcție `sterge`. Verifică numele în fișierul modulului. Mesajul arată și ce fișier a fost încărcat, ceea ce te ajută când Python a găsit alt fișier decât te așteptai.

### 3. Uitarea prefixului modulului

<!-- fisier: greseala.py -->
```python
import math

print(sqrt(16))
```

```text
Traceback (most recent call last):
  File "greseala.py", line 3, in <module>
    print(sqrt(16))
          ^^^^
NameError: name 'sqrt' is not defined
```

`import math` aduce doar numele `math`. Funcțiile lui se scriu cu prefix: `math.sqrt(16)`. Sau importă exact funcția: `from math import sqrt`.

### 4. Cod care rulează la import

<!-- fisier: setari.py -->
```python
nume = input("Numele tău: ")


def salut():
    return f"Salut, {nume}!"
```

<!-- fisier: foloseste_setari.py -->
<!-- stdin: Ana -->
```python
print("Pornesc aplicația...")
import setari

print(setari.salut())
```

```text
Pornesc aplicația...
Numele tău: Ana
Salut, Ana!
```

`input()` de la nivelul de sus al lui `setari.py` a rulat **în momentul importului**, nu când te așteptai. Pune codul care „face ceva” în funcții sau sub `if __name__ == "__main__":`; importul unui modul trebuie doar să definească lucruri. (Și importurile se pun la începutul fișierului, nu după alte instrucțiuni, ca aici.)

### 5. Un fișier propriu cu numele unui modul standard

Ana își numește fișierul de test `random.py`, apoi, în alt program din același folder, vrea să folosească modulul standard `random` (lecția 31):

<!-- fisier: random.py -->
```python
# testele Anei cu numere aleatoare
numar = 4
```

<!-- fisier: zar.py -->
```python
import random

print(random.randint(1, 6))
```

```text
Traceback (most recent call last):
  File "zar.py", line 3, in <module>
    print(random.randint(1, 6))
          ^^^^^^^^^^^^^^
AttributeError: module 'random' has no attribute 'randint'
```

Python a găsit **întâi** fișierul Anei, din folderul scriptului (vezi „pe dedesubt”), și l-a importat pe acela în locul modulului standard. Redenumește fișierul (de exemplu `teste_random.py`); folderul `__pycache__` rămas nu mai contează. Evită pentru fișierele tale numele modulelor standard: `random`, `math`, `json`, `csv`, `copy`, `string`, `email`, `test`.

## Exercițiu

În folderul `capitole/29-module-import/`, transformă **agenda de contacte** (lecțiile 14 și 28) într-un mic proiect cu module:

1. `agenda_fisier.py`: funcțiile `incarca(cale)` și `salveaza(agenda, cale)` pentru JSON (un fișier care lipsește înseamnă agendă goală);
2. `agenda_cautare.py`: funcțiile `cauta(agenda, text)` (contactele al căror nume conține textul, fără să conteze literele mari) și `pe_orase(agenda)` (dicționar `oras -> număr de contacte`);
3. `module_import.py`, fișierul capitolului: importă cele două module (o dată cu `import modul`, o dată cu `from modul import ...`) și face un meniu cu `main()`, apelat sub `if __name__ == "__main__":`;
4. în `agenda_cautare.py`, adaugă sub `if __name__ == "__main__":` un test rapid care creează o agendă mică în cod și afișează rezultatul lui `cauta()`; rulează fișierul direct, apoi verifică faptul că, la rularea lui `module_import.py`, testul **nu** apare;
5. calea fișierului JSON se construiește cu `Path(__file__).parent` (lecția 27), ca agenda să stea lângă cod, oricare ar fi folderul curent.

## Pe scurt

- Un modul e un fișier `.py`; un pachet e un folder de module cu `__init__.py`.
- `import modul` (cu prefix: `modul.nume`), `from modul import nume` (fără prefix), `import modul as alias`; evită `from modul import *`.
- La primul import, Python execută tot codul de sus al modulului, o singură dată; codul care „face ceva” stă în funcții sau sub `if __name__ == "__main__":`.
- `__name__` e `"__main__"` când fișierul e rulat direct și numele modulului când e importat.
- Modulele se caută întâi în folderul scriptului pornit, apoi în biblioteca standard și în pachetele instalate (`sys.path`).
- Nu-ți numi fișierele ca modulele standard (`random.py`, `json.py`): le ascund pe cele reale.
