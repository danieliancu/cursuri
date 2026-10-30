## Ce este

Până acum, excepțiile apăreau „singure”: Python le ridica atunci când ceva nu mergea. Cu **`raise`** ridici tu o excepție, în mod intenționat, când codul tău descoperă o situație pe care nu o poate trata:

<!-- fisier: nota.py -->
```python
def valideaza_nota(nota: float) -> float:
    if not 1 <= nota <= 10:
        raise ValueError(f"nota trebuie să fie între 1 și 10, nu {nota}")
    return nota


print(valideaza_nota(9.5))
print(valideaza_nota(11))
```

```text
9.5
Traceback (most recent call last):
  File "nota.py", line 8, in <module>
    print(valideaza_nota(11))
          ^^^^^^^^^^^^^^^^^^
  File "nota.py", line 3, in valideaza_nota
    raise ValueError(f"nota trebuie să fie între 1 și 10, nu {nota}")
ValueError: nota trebuie să fie între 1 și 10, nu 11
```

`raise` oprește imediat funcția, exact ca o eroare apărută natural, iar excepția urcă prin stiva de apeluri (lecția 23) până o prinde un `try / except` (lecția 24) sau până oprește programul.

## De ce contează

O funcție are un rol clar: „calculează media”, „retrage bani din cont”, „salvează utilizatorul”. Când primește date cu care nu-și poate face treaba, are trei variante:
- să întoarcă o valoare „specială” (`None`, `-1`), pe care apelantul o poate ignora din greșeală;
- să afișeze un mesaj, ceea ce amestecă logica cu afișarea și nu-i spune nimic codului care a apelat-o;
- să **ridice o excepție**, care nu poate fi ignorată: fie e tratată, fie oprește programul cu un mesaj clar.

A treia variantă e cea folosită de Python și de Django. Când ceri din baza de date un articol care nu există, Django ridică `Articol.DoesNotExist` (lecția 52). Când un formular e invalid, validarea ridică `ValidationError` (lecția 55). Funcțiile tale ar trebui să se comporte la fel.

## Cum funcționează

### raise cu un tip potrivit

Forma de bază e `raise TipEroare("mesaj")`. Alege tipul care descrie problema; de cele mai multe ori, unul dintre cele existente e suficient:

| Tip | Când îl ridici |
|---|---|
| `ValueError` | tipul e bun, dar valoarea nu are sens: notă 11, vârstă negativă, text gol |
| `TypeError` | s-a primit un tip nepotrivit: listă în loc de număr |
| `KeyError` | o cheie căutată nu există |
| `ZeroDivisionError`, `IndexError` etc. | rar ridicate de mână; apar singure |

Mesajul e pentru omul care va citi tracebackul: spune **ce** era greșit și, dacă se poate, **ce valoare** a venit.

```python
def imparte_nota(total: float, persoane: int) -> float:
    if not isinstance(persoane, int):
        raise TypeError(f"persoane trebuie să fie int, nu {type(persoane).__name__}")
    if persoane <= 0:
        raise ValueError(f"persoane trebuie să fie pozitiv, nu {persoane}")
    return total / persoane


for persoane in [4, 0, "4"]:
    try:
        print(f"{imparte_nota(347.5, persoane):.2f}")
    except (TypeError, ValueError) as eroare:
        print(f"Eroare: {eroare}")
```

```text
86.88
Eroare: persoane trebuie să fie pozitiv, nu 0
Eroare: persoane trebuie să fie int, nu str
```

`isinstance(valoare, tip)` întoarce `True` dacă valoarea e de tipul respectiv. E forma preferată față de `type(x) == int`.

### Verifică devreme

Validarea se face **la începutul** funcției, înainte de orice altă muncă. Dacă datele sunt greșite, funcția se oprește imediat, cu un mesaj despre cauza reală, nu trei funcții mai târziu cu un `TypeError` misterios. Principiul se numește „eșuează repede” (în engleză „fail fast”).

### Retransmiterea: raise fără argument

Uneori vrei să faci ceva când apare o eroare (s-o notezi, să afișezi un mesaj), dar fără s-o „înghiți”. Un `raise` simplu, în interiorul unui `except`, ridică din nou **aceeași** excepție:

<!-- fisier: salvare.py -->
```python
def salveaza_nota(catalog, elev, nota):
    try:
        catalog[elev].append(nota)
    except KeyError:
        print(f"[jurnal] încercare de a nota un elev inexistent: {elev}")
        raise


catalog = {"Ana": [9]}
salveaza_nota(catalog, "Ana", 10)
salveaza_nota(catalog, "Radu", 8)
```

```text
[jurnal] încercare de a nota un elev inexistent: Radu
Traceback (most recent call last):
  File "salvare.py", line 11, in <module>
    salveaza_nota(catalog, "Radu", 8)
  File "salvare.py", line 3, in salveaza_nota
    catalog[elev].append(nota)
    ~~~~~~~^^^^^^
KeyError: 'Radu'
```

### Înlănțuirea: raise ... from

Când traduci o eroare tehnică într-una cu sens pentru programul tău, păstrează legătura cu cauza folosind `from`:

<!-- fisier: setari.py -->
```python
def citeste_varsta(text: str) -> int:
    try:
        return int(text)
    except ValueError as eroare:
        raise ValueError(f"vârsta „{text}” nu e un număr întreg") from eroare


citeste_varsta("douăzeci")
```

```text
Traceback (most recent call last):
  File "setari.py", line 3, in citeste_varsta
    return int(text)
           ^^^^^^^^^
ValueError: invalid literal for int() with base 10: 'douăzeci'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "setari.py", line 8, in <module>
    citeste_varsta("douăzeci")
  File "setari.py", line 5, in citeste_varsta
    raise ValueError(f"vârsta „{text}” nu e un număr întreg") from eroare
ValueError: vârsta „douăzeci” nu e un număr întreg
```

Tracebackul are acum două părți: eroarea originală și, după rândul „The above exception was the direct cause...”, eroarea nouă. Citește-l tot de jos în sus. Partea de jos îți spune ce problemă vede programul tău, iar cea de sus de unde a pornit.

### Excepții proprii

Pentru situațiile specifice programului tău, poți crea propriile tipuri de excepții. Forma minimă e o **clasă** derivată din `Exception`:

```python
class SoldInsuficient(Exception):
    pass


def retrage(sold: float, suma: float) -> float:
    if suma > sold:
        raise SoldInsuficient(f"ai {sold:.2f} lei, nu poți retrage {suma:.2f}")
    return sold - suma


try:
    sold = retrage(100, 250)
except SoldInsuficient as eroare:
    print(f"Tranzacție refuzată: {eroare}")
```

```text
Tranzacție refuzată: ai 100.00 lei, nu poți retrage 250.00
```

Deocamdată, reține doar tiparul: `class NumeEroare(Exception):` pe un rând și `pass` pe următorul (lecția 11). Ce înseamnă `class` și ce înseamnă `(Exception)` vei afla la lecțiile 32 (clase) și 34 (moștenire). Prin convenție, numele unei excepții se scrie cu literă mare la fiecare cuvânt (`SoldInsuficient`), nu în snake_case.

Avantajul față de un `ValueError` generic: apelantul poate trata **exact** situația asta, fără să prindă din greșeală alte erori de valoare.

### Ce se întâmplă „pe dedesubt”: excepțiile formează o ierarhie

Fiecare tip de excepție e „un fel de” alt tip, mai general. `ZeroDivisionError` e un fel de `ArithmeticError`, care e un fel de `Exception`. Funcția `issubclass(A, B)` întreabă exact asta: e tipul `A` un fel de `B`? (Detalii la lecția 34.)

```python
print(issubclass(ZeroDivisionError, ArithmeticError))
print(issubclass(ZeroDivisionError, Exception))
print(issubclass(KeyboardInterrupt, Exception))
```

```text
True
True
False
```

Un `except` prinde tipul scris **și toate tipurile derivate din el**. De aceea `except Exception:` prinde aproape orice, dar nu și Ctrl+C (`KeyboardInterrupt` derivă direct din `BaseException`, tocmai ca să nu fie prins din greșeală). Poți folosi asta și pentru excepțiile tale: o excepție de bază pentru tot programul și câteva mai specifice, derivate din ea.

```python
class EroareBancara(Exception):
    pass


class SoldInsuficient(EroareBancara):
    pass


class ContBlocat(EroareBancara):
    pass


for eroare in [SoldInsuficient("sold prea mic"), ContBlocat("cont blocat")]:
    try:
        raise eroare
    except EroareBancara as e:
        print(f"{type(e).__name__}: {e}")
```

```text
SoldInsuficient: sold prea mic
ContBlocat: cont blocat
```

Un singur `except EroareBancara` le prinde pe amândouă.

## Exemplu complet

Contul bancar al Anei, cu funcții care validează tot și ridică excepții, plus o buclă care le tratează și explică problema utilizatorului.

<!-- fisier: cont.py -->
<!-- stdin: depune 500\nretrage 2000\nretrage -50\ntransfer 10\nretrage abc\nretrage 300\nstop -->
```python
class EroareBancara(Exception):
    pass


class SoldInsuficient(EroareBancara):
    pass


class LimitaDepasita(EroareBancara):
    pass


LIMITA_RETRAGERE = 1000


def verifica_suma(suma: float) -> None:
    if suma <= 0:
        raise ValueError(f"suma trebuie să fie pozitivă, nu {suma:g}")


def depune(sold: float, suma: float) -> float:
    verifica_suma(suma)
    return sold + suma


def retrage(sold: float, suma: float) -> float:
    verifica_suma(suma)
    if suma > LIMITA_RETRAGERE:
        raise LimitaDepasita(f"poți retrage cel mult {LIMITA_RETRAGERE} lei odată")
    if suma > sold:
        raise SoldInsuficient(f"sold {sold:.2f} lei, ai cerut {suma:.2f}")
    return sold - suma


sold = 200.0
operatii = {"depune": depune, "retrage": retrage}
print("Comenzi: depune SUMA, retrage SUMA, stop")
while True:
    comanda = input("> ").strip().split()
    if comanda == ["stop"]:
        break
    try:
        nume_operatie, text_suma = comanda
        operatie = operatii[nume_operatie]
        sold = operatie(sold, float(text_suma))
    except KeyError:
        print("  Comandă necunoscută.")
    except ValueError as eroare:
        print(f"  Date greșite: {eroare}")
    except EroareBancara as eroare:
        print(f"  Refuzat ({type(eroare).__name__}): {eroare}")
    else:
        print(f"  Sold nou: {sold:.2f} lei")
print(f"Sold final: {sold:.2f} lei")
```

```text
Comenzi: depune SUMA, retrage SUMA, stop
> depune 500
  Sold nou: 700.00 lei
> retrage 2000
  Refuzat (LimitaDepasita): poți retrage cel mult 1000 lei odată
> retrage -50
  Date greșite: suma trebuie să fie pozitivă, nu -50
> transfer 10
  Comandă necunoscută.
> retrage abc
  Date greșite: could not convert string to float: 'abc'
> retrage 300
  Sold nou: 400.00 lei
> stop
Sold final: 400.00 lei
```

Observă împărțirea rolurilor:
- funcțiile `depune` și `retrage` **nu afișează nimic**: doar calculează sau ridică excepții. Le-ai putea folosi la fel într-o aplicație web;
- bucla de jos **decide ce vede utilizatorul**, prinzând fiecare categorie de erori o singură dată;
- `operatii` e un dicționar care asociază numele comenzii cu funcția: funcțiile sunt valori ca oricare altele (lecția 21).

## Greșeli frecvente

### 1. raise cu un text

<!-- fisier: eroare.py -->
```python
def retrage(sold, suma):
    if suma > sold:
        raise "Sold insuficient"
    return sold - suma


retrage(100, 250)
```

```text
Traceback (most recent call last):
  File "eroare.py", line 7, in <module>
    retrage(100, 250)
  File "eroare.py", line 3, in retrage
    raise "Sold insuficient"
TypeError: exceptions must derive from BaseException
```

`raise` primește o **excepție**, nu un text. Textul e mesajul ei: `raise ValueError("Sold insuficient")`.

### 2. Valoare „specială” în loc de excepție

```python
def medie(note):
    if not note:
        return -1  # „semnal” că nu sunt note
    return sum(note) / len(note)


medii = [medie([9, 10]), medie([]), medie([7, 8])]
print(f"Media clasei: {sum(medii) / len(medii):.2f}")
```

```text
Media clasei: 5.33
```

Rezultatul e greșit (media corectă a celor doi elevi cu note e 8.50), iar nimic nu te avertizează: `-1` a intrat în calcul ca o notă oarecare. Cu o excepție, problema nu poate trece neobservată:

<!-- fisier: eroare.py -->
```python
def medie(note):
    if not note:
        raise ValueError("nu se poate calcula media unei liste goale")
    return sum(note) / len(note)


medii = [medie([9, 10]), medie([]), medie([7, 8])]
```

```text
Traceback (most recent call last):
  File "eroare.py", line 7, in <module>
    medii = [medie([9, 10]), medie([]), medie([7, 8])]
                             ^^^^^^^^^
  File "eroare.py", line 3, in medie
    raise ValueError("nu se poate calcula media unei liste goale")
ValueError: nu se poate calcula media unei liste goale
```

Acum codul care apelează trebuie să decidă explicit ce face cu elevii fără note.

### 3. Ordinea except-urilor, de la general la specific

```python
class EroareBancara(Exception):
    pass


class SoldInsuficient(EroareBancara):
    pass


try:
    raise SoldInsuficient("sold prea mic")
except EroareBancara:
    print("Eroare bancară generală.")
except SoldInsuficient:
    print("Nu ai destui bani.")
```

```text
Eroare bancară generală.
```

Python verifică `except`-urile de sus în jos și îl alege pe **primul** care se potrivește. `SoldInsuficient` e un fel de `EroareBancara`, deci primul bloc a câștigat, iar al doilea nu va rula niciodată. Pune întâi tipurile **specifice**, apoi pe cele generale.

### 4. Excepții prea generale

<!-- nu-rula -->
```python
def retrage(sold, suma):
    if suma > sold:
        raise Exception("sold insuficient")
    return sold - suma
```

Ca să trateze situația, apelantul trebuie să scrie `except Exception:`, care prinde și orice altă greșeală (un `NameError`, un `TypeError`), cu problemele din lecția 24. Ridică un tip specific: unul existent (`ValueError`) sau unul propriu (`SoldInsuficient`).

### 5. Mesaj care nu spune nimic

<!-- fisier: eroare.py -->
```python
def seteaza_varsta(varsta):
    if varsta < 0:
        raise ValueError
    return varsta


seteaza_varsta(-3)
```

```text
Traceback (most recent call last):
  File "eroare.py", line 7, in <module>
    seteaza_varsta(-3)
  File "eroare.py", line 3, in seteaza_varsta
    raise ValueError
ValueError
```

Ultimul rând din traceback nu spune nimic. Scrie mesajul și include valoarea primită: `raise ValueError(f"vârsta nu poate fi negativă: {varsta}")`. Tu, peste o lună, îți vei mulțumi.

## Exercițiu

În `capitole/25-raise-exceptii/raise_exceptii.py`, scrie un **catalog cu validare**:

1. o excepție de bază `EroareCatalog(Exception)` și două derivate din ea: `ElevInexistent` și `NotaInvalida`;
2. funcția `adauga_nota(catalog, elev, nota)`, care ridică `ElevInexistent` dacă elevul nu e în catalog, `NotaInvalida` dacă nota (primită ca text) nu se poate converti în număr sau nu e între 1 și 10 (inclusiv), iar altfel adaugă nota; mesajele includ valorile primite;
3. funcția `medie(catalog, elev)`, care ridică `ElevInexistent` pentru un elev necunoscut și `ValueError` dacă elevul nu are note;
4. o buclă care citește comenzi de forma `nota Ana 9` și `medie Ana` (rând gol = gata) și tratează **toate** erorile, inclusiv comenzile scrise greșit, cu mesaje clare; folosește un singur `except EroareCatalog` pentru cele două erori proprii, afișând și tipul lor (`type(eroare).__name__`);
5. testează fiecare ramură de eroare cel puțin o dată.

## Pe scurt

- `raise TipEroare("mesaj")` ridică o excepție: funcția se oprește, iar excepția urcă până e prinsă.
- Validează argumentele la începutul funcției („eșuează repede”) și ridică un tip potrivit (`ValueError`, `TypeError`) cu un mesaj care include valoarea greșită.
- O excepție nu poate fi ignorată din greșeală, spre deosebire de valorile „speciale” ca `-1` sau `None`.
- `raise` simplu, într-un `except`, retransmite excepția; `raise Noua(...) from eroare` păstrează cauza originală.
- Excepțiile proprii: `class NumeEroare(Exception): pass`; `except` prinde și tipurile derivate, deci pune `except`-urile specifice înaintea celor generale.
- Funcțiile cu logică ridică excepții; codul care vorbește cu utilizatorul le prinde și le explică.
