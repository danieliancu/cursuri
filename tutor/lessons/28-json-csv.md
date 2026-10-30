## Ce este

**JSON** și **CSV** sunt două formate de text pentru date, folosite peste tot:
- **JSON** („JavaScript Object Notation”) păstrează date **structurate**, cu dicționare și liste unele în altele. Arată aproape exact ca un dicționar Python;
- **CSV** („Comma-Separated Values”) păstrează **tabele**: fiecare rând e o înregistrare, iar valorile sunt separate prin virgulă (sau punct și virgulă). Excel și Google Sheets îl deschid direct.

Python are câte un modul pentru fiecare, `json` și `csv`, în biblioteca standard:

```python
import json

cheltuiala = {"data": "2026-10-29", "categorie": "cafea", "suma": 14.5, "platit_cu_cardul": True}
text = json.dumps(cheltuiala, ensure_ascii=False)
print(text)
print(type(text))
inapoi = json.loads(text)
print(inapoi["suma"] + 1)
```

```text
{"data": "2026-10-29", "categorie": "cafea", "suma": 14.5, "platit_cu_cardul": true}
<class 'str'>
15.5
```

`import json` face disponibil modulul `json`, la fel cum `from pathlib import Path` făcea disponibil `Path` la lecția 27. Ce înseamnă exact `import` vei vedea la lecția 29.

## De ce contează

În lecția 27, jurnalul de cheltuieli avea un format inventat (`data;categorie;suma`), pe care îl spărgeai de mână cu `split(";")`. Merge pentru date simple, dar se strică repede: ce faci dacă o categorie conține `;`? Cum salvezi o listă de etichete pentru fiecare cheltuială? Cum îi spui altui program ce înseamnă fiecare coloană?

JSON și CSV sunt formate **standard**, cu reguli clare și cu biblioteci în toate limbajele. Le vei întâlni mereu:
- **JSON**: fișiere de configurare, răspunsurile oricărui API web (inclusiv API-ul pe care îl vei construi cu Django REST Framework, lecția 60), date schimbate între programe;
- **CSV**: exporturi din Excel, din bănci, din aplicații de contabilitate, rapoarte pe care le deschide oricine.

## Cum funcționează

### JSON: tipurile de date

JSON are puține tipuri, fiecare cu un corespondent în Python:

| JSON | Python |
|---|---|
| obiect `{"cheie": ...}` | `dict` |
| tablou `[...]` | `list` |
| text `"..."` (doar ghilimele duble) | `str` |
| număr `14.5`, `32` | `float`, `int` |
| `true`, `false` | `True`, `False` |
| `null` | `None` |

Cheile unui obiect JSON sunt **mereu** texte. Tuplurile devin liste, iar seturile nu au corespondent (vezi greșelile frecvente).

### JSON: patru funcții

- `json.dumps(obiect)` transformă date Python în **text** JSON („dump string”);
- `json.loads(text)` transformă text JSON în date Python („load string”);
- `json.dump(obiect, fisier)` scrie direct într-un **fișier** deschis;
- `json.load(fisier)` citește direct dintr-un fișier.

Regula de memorare: cu `s` la final lucrezi cu un string, fără `s` lucrezi cu un fișier.

```python
import json

jurnal = {
    "proprietar": "Ana Popescu",
    "moneda": "lei",
    "cheltuieli": [
        {"data": "2026-10-27", "categorie": "cafea", "suma": 32, "etichete": ["dimineață"]},
        {"data": "2026-10-28", "categorie": "benzină", "suma": 250, "etichete": []},
    ],
}

with open("jurnal.json", "w", encoding="utf-8") as fisier:
    json.dump(jurnal, fisier, ensure_ascii=False, indent=2)

with open("jurnal.json", encoding="utf-8") as fisier:
    print(fisier.read())
```

```text
{
  "proprietar": "Ana Popescu",
  "moneda": "lei",
  "cheltuieli": [
    {
      "data": "2026-10-27",
      "categorie": "cafea",
      "suma": 32,
      "etichete": [
        "dimineață"
      ]
    },
    {
      "data": "2026-10-28",
      "categorie": "benzină",
      "suma": 250,
      "etichete": []
    }
  ]
}
```

Cele două opțiuni:
- `indent=2` așază textul pe mai multe rânduri, cu indentare, ca să poată fi citit de un om. Fără el, totul stă pe un singur rând;
- `ensure_ascii=False` păstrează diacriticele așa cum sunt. Fără el, `ț` ar apărea ca `\u021b` (tot corect, dar greu de citit).

Citirea înapoi dă exact structura de dinainte:

```python
import json

with open("jurnal.json", encoding="utf-8") as fisier:
    jurnal = json.load(fisier)

print(jurnal["proprietar"])
total = sum(c["suma"] for c in jurnal["cheltuieli"])
print(f"{len(jurnal['cheltuieli'])} cheltuieli, {total} {jurnal['moneda']}")
print(jurnal["cheltuieli"][0]["etichete"])
```

```text
Ana Popescu
2 cheltuieli, 282 lei
['dimineață']
```

Tiparul **„încarc, modific, salvez”** e cel mai des întâlnit: citești tot fișierul într-o structură Python, o modifici cu tot ce ai învățat la colecții (lecțiile 12–17), apoi o scrii înapoi.

### CSV: scriere

```python
import csv

cheltuieli = [
    ["data", "categorie", "suma"],
    ["2026-10-27", "cafea", 32],
    ["2026-10-28", "benzină", 250],
    ["2026-10-29", "cărți; reviste", 89],
]

with open("cheltuieli.csv", "w", encoding="utf-8", newline="") as fisier:
    scriitor = csv.writer(fisier)
    scriitor.writerows(cheltuieli)

with open("cheltuieli.csv", encoding="utf-8") as fisier:
    print(fisier.read())
```

```text
data,categorie,suma
2026-10-27,cafea,32
2026-10-28,benzină,250
2026-10-29,cărți; reviste,89

```

- `csv.writer(fisier)` creează un obiect care scrie rânduri; `writerow(lista)` scrie un rând, `writerows(liste)` scrie mai multe;
- numerele sunt transformate automat în text;
- **`newline=""`** la `open()` e obligatoriu pentru CSV: modulul `csv` pune singur sfârșiturile de rând, iar fără opțiunea asta, pe Windows apar rânduri goale între înregistrări.

Dacă o valoare conține chiar separatorul, `csv` o pune automat între ghilimele. Cu separatorul `;`, folosit de Excel în română:

```python
import csv

with open("excel.csv", "w", encoding="utf-8", newline="") as fisier:
    scriitor = csv.writer(fisier, delimiter=";")
    scriitor.writerow(["categorie", "suma"])
    scriitor.writerow(["cărți; reviste", "89,50"])

with open("excel.csv", encoding="utf-8") as fisier:
    print(fisier.read())
```

```text
categorie;suma
"cărți; reviste";89,50

```

Așa se rezolvă problema „ce faci dacă textul conține separatorul”, pe care formatul făcut de mână din lecția 27 nu o putea rezolva.

### CSV: citire

`csv.reader` dă fiecare rând ca listă de stringuri. Mai comod e **`csv.DictReader`**, care folosește primul rând drept nume de coloane și dă fiecare înregistrare ca dicționar:

```python
import csv

with open("cheltuieli.csv", encoding="utf-8", newline="") as fisier:
    for rand in csv.DictReader(fisier):
        print(rand)

with open("cheltuieli.csv", encoding="utf-8", newline="") as fisier:
    total = sum(float(rand["suma"]) for rand in csv.DictReader(fisier))
print(f"Total: {total:.2f}")
```

```text
{'data': '2026-10-27', 'categorie': 'cafea', 'suma': '32'}
{'data': '2026-10-28', 'categorie': 'benzină', 'suma': '250'}
{'data': '2026-10-29', 'categorie': 'cărți; reviste', 'suma': '89'}
Total: 371.00
```

Atenție: în CSV **totul e text**. Valoarea `'32'` e un string, deci o convertești cu `float()` sau `int()` (lecția 6). JSON, în schimb, păstrează tipurile.

Pentru scriere există perechea **`csv.DictWriter`**, căreia îi spui numele coloanelor:

```python
import csv

cheltuieli = [
    {"data": "2026-10-30", "categorie": "cinema", "suma": 45},
    {"data": "2026-10-31", "categorie": "cafea", "suma": 14.5},
]
with open("noi.csv", "w", encoding="utf-8", newline="") as fisier:
    scriitor = csv.DictWriter(fisier, fieldnames=["data", "categorie", "suma"])
    scriitor.writeheader()
    scriitor.writerows(cheltuieli)

with open("noi.csv", encoding="utf-8") as fisier:
    print(fisier.read())
```

```text
data,categorie,suma
2026-10-30,cinema,45
2026-10-31,cafea,14.5

```

### JSON sau CSV?

- **CSV**, când datele sunt un **tabel** simplu (fiecare înregistrare are aceleași câmpuri, fără liste sau structuri în interior) și cineva le va deschide în Excel;
- **JSON**, când datele au **structură** (liste în înregistrări, obiecte în obiecte), când contează tipurile sau când le schimbi cu alt program ori cu un API.

### Ce se întâmplă „pe dedesubt”: JSON e doar text

Un fișier `.json` nu are nimic special: e un fișier text, cu reguli de scriere stricte. `json.dumps` face exact ce ai face de mână (pune ghilimele, virgule, acolade), dar fără greșeli, iar `json.loads` citește textul caracter cu caracter și construiește dicționare și liste.

Din același motiv, un JSON scris greșit (de exemplu, cu ghilimele simple, cum scrie Python dicționarele) nu poate fi citit:

<!-- fisier: json_gresit.py -->
```python
import json

text = "{'nume': 'Ana'}"   # ghilimele simple: e Python, nu JSON
date = json.loads(text)
```

```text
Traceback (most recent call last):
  File "json_gresit.py", line 4, in <module>
    date = json.loads(text)
           ^^^^^^^^^^^^^^^^
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

(Am scurtat tracebackul: în realitate, între rândurile de mai sus apar încă trei perechi `File "/usr/local/lib/python3.12/json/..."`, din interiorul modulului `json`.) Ultimul rând e cel care contează: „Expecting property name enclosed in double quotes”, adică JSON vrea ghilimele **duble**. Mesajul spune și unde a găsit problema: rândul 1, coloana 2. Cum citești un traceback lung ca acesta ai văzut la lecția 23.

## Exemplu complet

Jurnalul de cheltuieli al Anei, salvat în JSON: la fiecare rulare, programul încarcă jurnalul (sau pornește unul nou), adaugă cheltuieli, salvează și exportă un raport CSV pe categorii, pe care Ana îl poate deschide în Excel.

<!-- fisier: jurnal_json.py -->
<!-- stdin: 2026-10-29\ncafea\n14,5\n2026-10-30\ncinema\n45\n\n -->
```python
import csv
import json
from pathlib import Path

JURNAL = Path("cheltuieli.json")
RAPORT = Path("raport.csv")

# 1. Încarcă jurnalul sau pornește unul nou
if JURNAL.exists():
    with open(JURNAL, encoding="utf-8") as fisier:
        jurnal = json.load(fisier)
else:
    jurnal = {"proprietar": "Ana Popescu", "cheltuieli": []}
    print("Jurnal nou.")

# 2. Adaugă cheltuieli
while True:
    data = input("Data (gol = gata): ").strip()
    if not data:
        break
    categorie = input("Categorie: ").strip().lower()
    suma = float(input("Suma: ").replace(",", "."))
    jurnal["cheltuieli"].append({"data": data, "categorie": categorie, "suma": suma})

# 3. Salvează jurnalul
with open(JURNAL, "w", encoding="utf-8") as fisier:
    json.dump(jurnal, fisier, ensure_ascii=False, indent=2)

# 4. Raport pe categorii, în CSV pentru Excel (separator ; și virgulă zecimală)
pe_categorii = {}
for c in jurnal["cheltuieli"]:
    pe_categorii[c["categorie"]] = pe_categorii.get(c["categorie"], 0) + c["suma"]

with open(RAPORT, "w", encoding="utf-8", newline="") as fisier:
    scriitor = csv.writer(fisier, delimiter=";")
    scriitor.writerow(["categorie", "total"])
    for categorie, total in sorted(pe_categorii.items()):
        scriitor.writerow([categorie, f"{total:.2f}".replace(".", ",")])

print(f"\nJurnal: {len(jurnal['cheltuieli'])} cheltuieli salvate în {JURNAL}")
print(f"Raport ({RAPORT}):")
print(RAPORT.read_text(encoding="utf-8"), end="")
```

```text
Jurnal nou.
Data (gol = gata): 2026-10-29
Categorie: cafea
Suma: 14,5
Data (gol = gata): 2026-10-30
Categorie: cinema
Suma: 45
Data (gol = gata): 

Jurnal: 2 cheltuieli salvate în cheltuieli.json
Raport (raport.csv):
categorie;total
cafea;14,50
cinema;45,00
```

La rularea următoare, jurnalul existent se încarcă, iar cheltuielile noi se adaugă la cele vechi. Un singur fișier JSON păstrează tot, iar CSV-ul e doar un export, refăcut de fiecare dată.

## Greșeli frecvente

### 1. Un set (sau alt tip) care nu are corespondent în JSON

<!-- fisier: salveaza.py -->
```python
import json

cheltuiala = {"categorie": "cafea", "etichete": {"dimineață", "birou"}}
print(json.dumps(cheltuiala))
```

```text
Traceback (most recent call last):
  File "salveaza.py", line 4, in <module>
    print(json.dumps(cheltuiala))
          ^^^^^^^^^^^^^^^^^^^^^^
TypeError: Object of type set is not JSON serializable
```

(Și aici am scos rândurile din interiorul modulului `json`.) JSON știe doar tipurile din tabel. Transformă setul în listă înainte de salvare: `sorted(etichete)`. Același mesaj apare pentru date calendaristice (lecția 31) și pentru obiectele claselor tale (lecția 32).

### 2. Cheile numerice devin texte

```python
import json

camere = {101: "Ana", 102: "Mihai"}
inapoi = json.loads(json.dumps(camere))
print(inapoi)
print(101 in inapoi, "101" in inapoi)
```

```text
{'101': 'Ana', '102': 'Mihai'}
False True
```

În JSON, cheile sunt mereu texte, așa că după o salvare și o încărcare `inapoi[101]` dă `KeyError` (lecția 14). Fie folosești de la început chei text, fie convertești la încărcare: `{int(k): v for k, v in inapoi.items()}` (lecția 16).

### 3. load() în loc de loads() (sau invers)

<!-- fisier: incarca.py -->
```python
import json

text = '{"nume": "Ana"}'
date = json.load(text)
```

```text
Traceback (most recent call last):
  File "incarca.py", line 4, in <module>
    date = json.load(text)
           ^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/json/__init__.py", line 293, in load
    return loads(fp.read(),
                 ^^^^^^^
AttributeError: 'str' object has no attribute 'read'
```

`json.load()` așteaptă un **fișier** deschis, pe care apelează `read()`. Pentru un string, folosește `json.loads()`. Ține minte: `s` de la final vine de la „string”.

### 4. Calcule cu valorile din CSV

<!-- fisier: incarca.py -->
```python
import csv

with open("cheltuieli.csv", encoding="utf-8", newline="") as fisier:
    sume = [rand["suma"] for rand in csv.DictReader(fisier)]
print(sum(sume))
```

```text
Traceback (most recent call last):
  File "incarca.py", line 5, in <module>
    print(sum(sume))
          ^^^^^^^^^
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

Valorile citite din CSV sunt stringuri (`'32'`, `'250'`), iar `sum()` pornește de la 0 și nu poate aduna un număr cu un text (lecția 17). Convertește-le: `float(rand["suma"])`.

### 5. CSV citit cu separatorul greșit

```python
import csv

with open("excel.csv", encoding="utf-8", newline="") as fisier:
    for rand in csv.reader(fisier):
        print(rand)
```

```text
['categorie;suma']
['cărți; reviste;89', '50']
```

Fișierul folosește `;`, dar `csv.reader` caută implicit `,`. Primul rând a devenit o singură valoare, iar al doilea a fost tăiat la virgula din `89,50`. Spune-i separatorul: `csv.reader(fisier, delimiter=";")`. Când primești un CSV, uită-te întâi la primul rând ca să vezi ce separator are.

## Exercițiu

În `capitole/28-json-csv/json_csv.py`, scrie un **convertor pentru agenda de contacte** din lecția 14:

1. pornește de la un dicționar `nume -> {"telefon": ..., "oras": ..., "etichete": [...]}` cu 3–4 contacte, salvat în `agenda.json` (cu `indent=2` și `ensure_ascii=False`) doar dacă fișierul nu există;
2. încarcă agenda din `agenda.json` și cere un contact nou (nume, telefon, oraș, etichete separate prin virgulă); adaugă-l și salvează agenda înapoi;
3. exportă agenda în `agenda.csv` cu `csv.DictWriter`, cu coloanele `nume`, `telefon`, `oras`, `etichete` și separatorul `;`; etichetele se scriu ca un singur text, lipite cu `", "`;
4. citește înapoi `agenda.csv` cu `csv.DictReader` (nu uita `delimiter=";"`, greșeala 5) și afișează numărul de contacte din fiecare oraș;
5. verifică, la final, că numele din CSV sunt exact numele din JSON (compară două seturi, lecția 15) și afișează rezultatul.

## Pe scurt

- JSON păstrează date structurate (dicționare, liste, texte, numere, `true`/`false`/`null`); CSV păstrează tabele.
- `json.dump(obiect, fisier)` / `json.load(fisier)` lucrează cu fișiere; `json.dumps()` / `json.loads()` cu stringuri.
- Pentru JSON lizibil, cu diacritice: `indent=2, ensure_ascii=False`. Cheile JSON sunt mereu texte, iar seturile trebuie transformate în liste.
- Fișierele CSV se deschid cu `newline=""`; `csv.writer`/`csv.reader` lucrează cu liste, `DictWriter`/`DictReader` cu dicționare.
- În CSV totul e text: convertește numerele; separatorul se alege cu `delimiter=";"`.
- Tiparul obișnuit: încarci, modifici structura în Python, salvezi înapoi.
