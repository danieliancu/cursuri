## Ce este

Două feluri de a documenta o funcție direct în cod:
- un **docstring** este un text între ghilimele triple, pus pe primul rând din corpul funcției, care explică **ce face** funcția;
- **type hints** (adnotări de tip) sunt indicații despre **tipul** parametrilor și al rezultatului.

```python
def media(note: list[float]) -> float:
    """Întoarce media aritmetică a notelor."""
    return sum(note) / len(note)

print(media([9, 10, 8]))
print(media.__doc__)
```

```text
9.0
Întoarce media aritmetică a notelor.
```

`note: list[float]` se citește „`note` e o listă de numere `float`”, iar `-> float` înseamnă „funcția întoarce un `float`”. Ai văzut deja docstring-uri în lecțiile 18–20; acum afli regulile lor.

## De ce contează

Codul se citește mult mai des decât se scrie: de tine peste o lună, de colegi, de tutorele tău. Când vezi apelul `calculeaza(d, 7, True)`, nu știi ce înseamnă argumentele. Cu un docstring și cu tipuri, afli din definiție, fără să citești tot corpul funcției:
- **ce face** funcția și ce întoarce;
- **ce fel de valori** primește: o listă? un text? poate fi `None`?

Mai e un câștig: editoarele și unelte ca **mypy** citesc type hints și te avertizează **înainte** să rulezi codul, de exemplu când dai un `str` unei funcții care vrea un `int`. Multe biblioteci moderne sunt scrise cu type hints (pentru Django există pachetul separat `django-stubs`), iar editorul îți arată tipurile când le folosești.

## Cum funcționează

### Docstring-uri

Un docstring e **primul** lucru din corpul unei funcții: un string, de obicei între `"""`. Convențiile (PEP 257):
- primul rând e un rezumat scurt, ca o comandă: „Întoarce media…”, „Citește un număr…”;
- dacă e nevoie de mai mult, urmează un rând gol și apoi detaliile: ce înseamnă parametrii, ce întoarce funcția, ce cazuri speciale există.

```python
def pret_final(pret, tva=0.21, reducere=0):
    """Calculează prețul de plată, rotunjit la bani.

    pret: prețul fără TVA, în lei.
    tva: cota TVA, ca fracție (0.21 înseamnă 21%).
    reducere: reducerea, ca fracție din prețul cu TVA.
    Întoarce prețul final, rotunjit la 2 zecimale.
    """
    return round(pret * (1 + tva) * (1 - reducere), 2)

print(pret_final(100, reducere=0.1))
```

```text
108.9
```

Diferența față de un comentariu `#`: docstring-ul e păstrat de Python în funcție, în atributul `__doc__`, iar alte unelte îl pot citi. Funcția `help()` îl afișează frumos, împreună cu parametrii:

```python
def media(note):
    """Întoarce media aritmetică a notelor."""
    return sum(note) / len(note)

help(media)
```

```text
Help on function media in module __main__:

media(note)
    Întoarce media aritmetică a notelor.

```

Când vrei să afli ce face o funcție a lui Python, încearcă `help()`: `help(len)`, `help(str.split)`.

Ce scrii într-un docstring: **ce** face funcția și **cum se folosește**, nu **cum** e implementată pe dinăuntru. Pentru o funcție evidentă, un rând ajunge.

### Type hints pentru parametri și rezultat

Sintaxa: `parametru: tip` și `-> tip` înainte de `:` final. Pentru un parametru cu valoare implicită, tipul vine înaintea lui `=`:

```python
def prezinta(nume: str, varsta: int, oras: str = "Cluj") -> str:
    return f"{nume}, {varsta} de ani, din {oras}"

def este_major(varsta: int) -> bool:
    return varsta >= 18

def afiseaza_linie(latime: int = 20) -> None:
    print("-" * latime)

print(prezinta("Ana Popescu", 25))
print(este_major(17))
afiseaza_linie(10)
```

```text
Ana Popescu, 25 de ani, din Cluj
False
----------
```

`-> None` spune explicit că funcția nu întoarce nimic: ea **face** ceva, nu calculează.

### Tipuri pentru colecții

Pentru colecții, scrii între paranteze pătrate și tipul elementelor:

| Adnotare | Înseamnă |
|---|---|
| `list[int]` | listă de numere întregi |
| `dict[str, float]` | dicționar cu chei `str` și valori `float` |
| `set[str]` | set de stringuri |
| `tuple[str, int]` | tuplu cu exact două elemente: un `str`, apoi un `int` |
| `tuple[int, ...]` | tuplu de oricâte `int` |

```python
def citeste_linie(linie: str) -> tuple[str, list[int]]:
    """Transformă "ana popescu: 9, 10, 8" în ("Ana Popescu", [9, 10, 8])."""
    nume, note_text = linie.split(":")
    return nume.strip().title(), [int(n) for n in note_text.split(",")]

def medii(catalog: dict[str, list[int]]) -> dict[str, float]:
    return {nume: sum(note) / len(note) for nume, note in catalog.items()}

nume, note = citeste_linie("ana popescu: 9, 10, 8")
print(medii({nume: note, "Mihai Ionescu": [7, 6, 9]}))
```

```text
{'Ana Popescu': 9.0, 'Mihai Ionescu': 7.333333333333333}
```

Doar din semnătura `medii(catalog: dict[str, list[int]]) -> dict[str, float]` înțelegi ce primește funcția și ce dă înapoi, fără să-i citești corpul.

### Valori care pot lipsi: `| None` și Optional

Multe funcții întorc `None` în anumite cazuri, ca `cauta_nota()` din lecția 18 sau `joaca()` din jocul refăcut acolo. Tipul se scrie cu `|` („sau”):

```python
def cauta_elev(catalog: dict[str, list[int]], nume: str) -> list[int] | None:
    """Întoarce notele elevului sau None dacă nu există."""
    return catalog.get(nume.title())

catalog = {"Ana": [9, 10], "Mihai": [7, 6]}
print(cauta_elev(catalog, "ana"))
print(cauta_elev(catalog, "Ioana"))
```

```text
[9, 10]
None
```

`list[int] | None` avertizează pe oricine folosește funcția: rezultatul poate lipsi, deci verifică-l cu `is None` înainte să-l folosești.

În cod mai vechi vei vedea aceeași idee scrisă `Optional[list[int]]`. Pentru ea e nevoie de rândul `from typing import Optional` la începutul fișierului (despre `import`, la lecția 29). Cele două scrieri înseamnă exact același lucru. În Python modern, preferă `| None`.

### Adnotarea variabilelor

Poți adnota și o variabilă, util mai ales pentru colecțiile care pornesc goale, unde tipul nu se vede din valoare:

```python
cos: list[str] = []
preturi: dict[str, float] = {}
cos.append("pâine")
preturi["pâine"] = 4.5
print(cos, preturi)
```

```text
['pâine'] {'pâine': 4.5}
```

Nu adnota totul: `varsta: int = 25` nu spune nimic în plus față de `varsta = 25`. Adnotările își merită locul în semnăturile funcțiilor și la colecțiile goale.

### Ce se întâmplă „pe dedesubt”: Python nu verifică tipurile

Type hints sunt **doar informații**. Python le păstrează (în atributul `__annotations__`), dar **nu le verifică** la rulare. O funcție adnotată cu `int` acceptă fără protest și un `str`:

```python
def dublu(x: int) -> int:
    return x * 2

print(dublu(21))
print(dublu("ha"))
print(dublu.__annotations__)
```

```text
42
haha
{'x': <class 'int'>, 'return': <class 'int'>}
```

`dublu("ha")` a mers, pentru că `"ha" * 2` are sens pentru stringuri (lecția 4). Rezultatul e însă greșit față de ce promite semnătura.

Verificarea o fac **uneltele**: editorul subliniază apelul greșit, iar programe ca **mypy** verifică tot proiectul fără să-l ruleze. Așa găsești greșelile de tip înainte să ajungă la utilizatori. Despre unelte care verifică automat codul vei afla mai multe la lecția 40.

## Exemplu complet

Funcțiile magazinului din lecția 14, documentate și adnotate. Citește doar semnăturile și docstring-urile, fără corpul funcțiilor, și vezi cât de mult afli.

<!-- fisier: magazin.py -->
```python
Magazin = dict[str, dict[str, float]]  # alias de tip: produs -> {"pret": ..., "stoc": ...}


def pret_produs(magazin: Magazin, produs: str) -> float | None:
    """Întoarce prețul produsului sau None dacă magazinul nu-l are."""
    date = magazin.get(produs)
    return date["pret"] if date else None


def adauga_in_cos(magazin: Magazin, cos: dict[str, int], produs: str, cantitate: int = 1) -> bool:
    """Adaugă produsul în coș dacă e destul stoc.

    Modifică dicționarul `cos` primit. Întoarce False dacă produsul nu există
    sau dacă stocul rămas nu ajunge.
    """
    if produs not in magazin:
        return False
    disponibil = magazin[produs]["stoc"] - cos.get(produs, 0)
    if cantitate > disponibil:
        return False
    cos[produs] = cos.get(produs, 0) + cantitate
    return True


def total_cos(magazin: Magazin, cos: dict[str, int]) -> float:
    """Întoarce valoarea coșului, rotunjită la bani."""
    return round(sum(magazin[p]["pret"] * cant for p, cant in cos.items()), 2)


magazin: Magazin = {
    "pâine": {"pret": 4.5, "stoc": 20},
    "lapte": {"pret": 8.99, "stoc": 5},
    "cafea": {"pret": 32.0, "stoc": 3},
}
cos: dict[str, int] = {}

for produs, cantitate in [("cafea", 2), ("lapte", 10), ("ceai", 1), ("pâine", 3)]:
    rezultat = "adăugat" if adauga_in_cos(magazin, cos, produs, cantitate) else "respins"
    print(f"{produs} x{cantitate}: {rezultat}")

print("Coș:", cos)
print("Total:", total_cos(magazin, cos))
print("Preț ceai:", pret_produs(magazin, "ceai"))
help(total_cos)
```

```text
cafea x2: adăugat
lapte x10: respins
ceai x1: respins
pâine x3: adăugat
Coș: {'cafea': 2, 'pâine': 3}
Total: 77.5
Preț ceai: None
Help on function total_cos in module __main__:

total_cos(magazin: dict[str, dict[str, float]], cos: dict[str, int]) -> float
    Întoarce valoarea coșului, rotunjită la bani.

```

Observă:
- `Magazin = dict[str, dict[str, float]]` dă un **nume** unui tip lung (se numește „alias de tip”), ca semnăturile să rămână scurte;
- docstring-ul lui `adauga_in_cos` spune explicit că modifică `cos`: e exact genul de efect pe care lecția 20 cerea să-l faci vizibil;
- `help()` afișează semnătura completă, cu tipuri, și docstring-ul. Așa arată documentația funcțiilor tale pentru oricine le folosește.

## Greșeli frecvente

### 1. Comentariu în loc de docstring

```python
# Întoarce media notelor.
def media(note):
    return sum(note) / len(note)

print(media.__doc__)
```

```text
None
```

Un comentariu `#` deasupra funcției nu e docstring: Python îl ignoră complet, iar `help()` nu-l arată. Docstring-ul trebuie să fie **primul rând din corp**, sub `def`, ca string.

### 2. Paranteze rotunde în loc de pătrate la tip

<!-- fisier: tipuri.py -->
```python
def media(note: list(float)) -> float:
    return sum(note) / len(note)
```

```text
Traceback (most recent call last):
  File "tipuri.py", line 1, in <module>
    def media(note: list(float)) -> float:
                    ^^^^^^^^^^^
TypeError: 'type' object is not iterable
```

Adnotarea e evaluată când rulează rândul cu `def`. `list(float)` înseamnă „construiește o listă din `float`”, ceea ce nu are sens. Tipul elementelor se scrie între paranteze **pătrate**: `list[float]`.

### 3. Așteptarea ca Python să verifice tipurile

<!-- fisier: tipuri.py -->
<!-- stdin: 25 -->
```python
def peste_ani(varsta: int, ani: int) -> int:
    return varsta + ani

varsta = input("Vârsta: ")
print(peste_ani(varsta, 5))
```

```text
Vârsta: 25
Traceback (most recent call last):
  File "tipuri.py", line 5, in <module>
    print(peste_ani(varsta, 5))
          ^^^^^^^^^^^^^^^^^^^^
  File "tipuri.py", line 2, in peste_ani
    return varsta + ani
           ~~~~~~~^~~~~
TypeError: can only concatenate str (not "int") to str
```

Adnotarea `int` nu a convertit nimic și nici n-a oprit apelul: eroarea apare abia în corpul funcției. Conversia rămâne treaba ta (`int(input(...))`, lecția 6). Un editor cu verificare de tipuri ar fi subliniat însă apelul înainte să rulezi programul.

### 4. Tipul spune un lucru, funcția face altul

```python
def eticheta(produs: str, pret: float) -> str:
    print(f"{produs.upper()} — {pret:.2f} lei")

text = eticheta("pâine", 4.5)
print(repr(text))
```

```text
PÂINE — 4.50 lei
None
```

Semnătura promite un `str`, dar funcția afișează și întoarce `None` (greșeala `print` vs `return` din lecția 18). Python nu observă contradicția, dar cine citește semnătura e indus în eroare. Ține adnotările sincronizate cu codul: aici, fie `return f"..."`, fie `-> None`. (`repr()` afișează valoarea așa cum ar fi scrisă în cod, ca să se vadă clar `None`.)

### 5. Valoare implicită None fără `| None` în tip

```python
def saluta(nume: str = None) -> str:
    return f"Salut, {nume or 'vizitatorule'}!"

print(saluta())
```

```text
Salut, vizitatorule!
```

Merge, dar tipul minte: `nume` poate fi și `None`, nu doar `str`, iar mypy semnalează asta ca greșeală. Scrie `nume: str | None = None`, ca oricine citește să știe că valoarea poate lipsi.

## Exercițiu

În `capitole/22-docstrings-type-hints/docstrings_type_hints.py`, copiază funcțiile scrise la exercițiul lecției 19 (catalogul clasei) sau la cel al lecției 18 (calculatorul de reducere) și:

1. adaugă fiecărei funcții un docstring: un rând de rezumat și, unde e util, ce înseamnă parametrii și ce întoarce funcția;
2. adaugă type hints la toți parametrii și la rezultat, inclusiv `-> None` pentru funcțiile care doar afișează și `| None` unde funcția poate întoarce `None`;
3. definește un alias de tip pentru structura catalogului (de exemplu `Catalog = dict[str, list[float]]`) și folosește-l în semnături;
4. la finalul fișierului, apelează `help()` pentru două dintre funcții și verifică dacă documentația afișată îi ajunge cuiva care n-a văzut niciodată codul;
5. găsește intenționat un loc unde tipul și comportamentul nu se potrivesc (sau creează unul) și explică într-un comentariu de ce Python nu dă eroare.

## Pe scurt

- Docstring-ul e primul string din corpul funcției: un rând de rezumat, apoi detalii; îl citesc `__doc__` și `help()`.
- Type hints: `def f(x: int, nume: str = "Ana") -> bool:`; `-> None` pentru funcțiile fără rezultat.
- Colecții: `list[int]`, `dict[str, float]`, `set[str]`, `tuple[str, int]`, cu paranteze pătrate.
- O valoare care poate lipsi se scrie `tip | None` (sau `Optional[tip]` din modulul `typing`, în cod mai vechi).
- Un alias de tip (`Catalog = dict[str, list[float]]`) scurtează semnăturile lungi.
- Python nu verifică tipurile la rulare; o fac editorul și unelte ca mypy. Ține adnotările sincronizate cu codul.
