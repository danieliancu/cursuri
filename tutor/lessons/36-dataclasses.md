## Ce este

Un **dataclass** e o clasă pentru care Python scrie singur metodele plictisitoare. Pui decoratorul `@dataclass` deasupra clasei și enumeri câmpurile cu tipurile lor (type hints, lecția 22). Python generează automat `__init__`, `__repr__` și `__eq__` (lecțiile 32 și 35).

```python
from dataclasses import dataclass


@dataclass
class Carte:
    titlu: str
    autor: str
    an: int


ion = Carte("Ion", "Liviu Rebreanu", 1920)
print(ion)
print(ion.titlu, ion.an)
print(ion == Carte("Ion", "Liviu Rebreanu", 1920))
```

```text
Carte(titlu='Ion', autor='Liviu Rebreanu', an=1920)
Ion 1920
True
```

Patru rânduri de clasă, dar obiectul are deja un `__init__` cu trei parametri, se afișează lizibil și se compară după conținut.

## De ce contează

Multe clase sunt în primul rând **containere de date**: o carte, un membru, un împrumut, un punct pe hartă, un rând dintr-un fișier CSV. Pentru ele, ai scrie mereu același cod: `__init__` cu `self.x = x` pentru fiecare câmp, un `__repr__` care le enumeră, un `__eq__` care le compară. E mult cod repetitiv, în care e ușor să uiți un câmp când adaugi unul nou.

Cu `@dataclass`, câmpurile apar **o singură dată**, la începutul clasei, ca o listă clară a datelor. Restul e generat și rămâne sincronizat automat. Metodele tale (comportamentul) rămân la fel ca înainte.

Ideea „descrii câmpurile, iar framework-ul generează restul” e exact cea a modelelor Django (lecția 50): `titlu = models.CharField(...)`. Dacă înțelegi dataclass-urile, modelele vor părea familiare.

## Cum funcționează

### Câmpuri și valori implicite

Fiecare câmp e scris ca `nume: tip`, opțional cu o valoare implicită. Câmpurile **fără** valoare implicită trebuie să vină **înaintea** celor care au, ca la parametrii unei funcții (lecția 19).

```python
from dataclasses import dataclass


@dataclass
class Membru:
    nume: str
    varsta: int
    oras: str = "Cluj"
    activ: bool = True


ana = Membru("Ana Popescu", 25)
mihai = Membru("Mihai Ionescu", 31, oras="Iași")
print(ana)
print(mihai)
```

```text
Membru(nume='Ana Popescu', varsta=25, oras='Cluj', activ=True)
Membru(nume='Mihai Ionescu', varsta=31, oras='Iași', activ=True)
```

`__init__`-ul generat e exact cel pe care l-ai fi scris de mână: `def __init__(self, nume, varsta, oras="Cluj", activ=True)`.

Tipurile **nu sunt verificate** la rulare: `Membru("Ana", "douăzeci")` funcționează fără eroare. Ele documentează intenția și ajută editorul și uneltele de verificare (lecția 22). Pentru o verificare reală, vezi `__post_init__` mai jos.

### Liste și dicționare: field(default_factory=...)

O valoare implicită mutabilă, cum e `[]`, ar fi **comună** tuturor obiectelor, exact capcana de la lecțiile 19 și 33. Dataclass-urile te opresc (vezi greșelile frecvente) și îți cer `field(default_factory=list)`: o funcție apelată pentru **fiecare** obiect nou, ca să-i creeze lista lui.

```python
from dataclasses import dataclass, field


@dataclass
class Membru:
    nume: str
    carti: list[str] = field(default_factory=list)


ana = Membru("Ana Popescu")
mihai = Membru("Mihai Ionescu")
ana.carti.append("Ion")
print(ana.carti, mihai.carti)
```

```text
['Ion'] []
```

### Metode, ca la orice clasă

Un dataclass e o clasă normală, deci îi poți adăuga metode, property-uri (lecția 33) și metode speciale. Cele scrise de tine au prioritate față de cele generate.

```python
from dataclasses import dataclass, field


@dataclass
class Membru:
    nume: str
    limita: int = 3
    carti: list[str] = field(default_factory=list)

    @property
    def poate_imprumuta(self):
        return len(self.carti) < self.limita

    def __str__(self):
        return f"{self.nume} ({len(self.carti)}/{self.limita} cărți)"


ana = Membru("Ana Popescu", limita=2)
ana.carti += ["Ion", "Maitreyi"]
print(ana)
print(ana.poate_imprumuta)
print(repr(ana))
```

```text
Ana Popescu (2/2 cărți)
False
Membru(nume='Ana Popescu', limita=2, carti=['Ion', 'Maitreyi'])
```

`print()` folosește `__str__`-ul tău, iar `repr()` pe cel generat.

### __post_init__: verificări după creare

`__init__`-ul e generat, deci nu poți scrie verificări în el. Pentru asta există `__post_init__`, apelată automat **imediat după** `__init__`:

```python
from dataclasses import dataclass


@dataclass
class Carte:
    titlu: str
    pagini: int

    def __post_init__(self):
        self.titlu = self.titlu.strip()
        if self.pagini <= 0:
            raise ValueError(f"Număr de pagini invalid: {self.pagini}")


print(Carte("  Ion ", 480))
try:
    Carte("Maitreyi", -1)
except ValueError as eroare:
    print(eroare)
```

```text
Carte(titlu='Ion', pagini=480)
Număr de pagini invalid: -1
```

### frozen=True: obiecte care nu se pot modifica

`@dataclass(frozen=True)` creează obiecte **imutabile**, ca tuplurile (lecția 13): orice atribuire după creare dă eroare. Fiind imutabile, primesc automat și `__hash__`, deci pot fi puse în seturi și folosite drept chei de dicționar.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Isbn:
    cod: str


exemplare = {Isbn("978-1"): 3, Isbn("978-2"): 1}
print(exemplare[Isbn("978-1")])
```

```text
3
```

E alegerea potrivită pentru valori care identifică ceva și nu au de ce să se schimbe: un cod, o dată, o pereche de coordonate.

### order=True: sortare după câmpuri

`@dataclass(order=True)` generează `<`, `<=`, `>` și `>=`, care compară obiectele **câmp cu câmp, în ordinea în care sunt scrise**, ca pe tupluri:

```python
from dataclasses import dataclass


@dataclass(order=True)
class Carte:
    an: int
    titlu: str


carti = [Carte(1933, "Maitreyi"), Carte(1920, "Ion"), Carte(1920, "Pădurea spânzuraților")]
for carte in sorted(carti):
    print(carte)
```

```text
Carte(an=1920, titlu='Ion')
Carte(an=1920, titlu='Pădurea spânzuraților')
Carte(an=1933, titlu='Maitreyi')
```

Ordinea câmpurilor contează: aici anul e primul, deci sortarea e după an, iar la egalitate după titlu. Când ordinea dorită nu se potrivește cu ordinea câmpurilor, scrie tu `__lt__` sau folosește `key=`.

### Clasă obișnuită sau dataclass?

- **dataclass**: când obiectul e în primul rând un grup de date, cu câteva metode în jurul lor (o carte, un membru, un rând dintr-un raport);
- **clasă obișnuită**: când constructorul face mai mult decât să salveze argumentele (deschide fișiere, calculează lucruri complicate) sau când obiectul e mai ales comportament (o conexiune, o bibliotecă cu reguli de împrumut).

### Ce se întâmplă „pe dedesubt”: decoratorul scrie cod pentru tine

`@dataclass` e o funcție care primește clasa, citește adnotările ei (`Carte.__annotations__`) și **adaugă** metode în clasă. Rezultatul e o clasă obișnuită, cu metode obișnuite:

```python
from dataclasses import dataclass, fields


@dataclass
class Carte:
    titlu: str
    an: int = 1900


print(Carte.__annotations__)
print([f.name for f in fields(Carte)])
print("__init__" in Carte.__dict__, "__repr__" in Carte.__dict__)
```

```text
{'titlu': <class 'str'>, 'an': <class 'int'>}
['titlu', 'an']
True True
```

Doar atributele **cu adnotare de tip** devin câmpuri. Un atribut fără adnotare rămâne un atribut de clasă obișnuit (lecția 33). La lecția 38 vei vedea cum funcționează decoratorii; `@dataclass` e un decorator aplicat unei clase.

## Exemplu complet

Versiunea finală a bibliotecii din acest modul: datele sunt dataclass-uri, iar regulile stau într-o clasă obișnuită.

<!-- fisier: biblioteca.py -->
```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Carte:
    isbn: str
    titlu: str
    autor: str


@dataclass
class Membru:
    nume: str
    limita: int = 3
    imprumuturi: list["Imprumut"] = field(default_factory=list)


@dataclass
class Imprumut:
    carte: Carte
    membru: Membru
    zi: int
    returnat: bool = False

    def intarziere(self, zi_curenta, zile_permise=14):
        return max(zi_curenta - self.zi - zile_permise, 0)


class EroareBiblioteca(Exception):
    pass


class Biblioteca:
    def __init__(self):
        self.carti = {}        # isbn -> Carte
        self.imprumuturi = []

    def adauga(self, carte):
        self.carti[carte.isbn] = carte

    def disponibila(self, carte):
        return all(i.returnat or i.carte != carte for i in self.imprumuturi)

    def imprumuta(self, isbn, membru, zi):
        carte = self.carti[isbn]
        active = [i for i in membru.imprumuturi if not i.returnat]
        if len(active) >= membru.limita:
            raise EroareBiblioteca(f"{membru.nume} a atins limita de {membru.limita}.")
        if not self.disponibila(carte):
            raise EroareBiblioteca(f"„{carte.titlu}” nu e disponibilă.")
        imprumut = Imprumut(carte, membru, zi)
        self.imprumuturi.append(imprumut)
        membru.imprumuturi.append(imprumut)
        return imprumut


biblioteca = Biblioteca()
for carte in [
    Carte("978-1", "Ion", "Liviu Rebreanu"),
    Carte("978-2", "Maitreyi", "Mircea Eliade"),
    Carte("978-3", "Baltagul", "Mihail Sadoveanu"),
]:
    biblioteca.adauga(carte)

ana = Membru("Ana Popescu", limita=2)
mihai = Membru("Mihai Ionescu")

operatii = [
    ("978-1", ana, 1),
    ("978-2", ana, 3),
    ("978-3", ana, 4),
    ("978-1", mihai, 5),
    ("978-3", mihai, 6),
]
for isbn, membru, zi in operatii:
    try:
        imprumut = biblioteca.imprumuta(isbn, membru, zi)
        print(f"Ziua {zi}: {membru.nume} a luat „{imprumut.carte.titlu}”.")
    except EroareBiblioteca as eroare:
        print(f"Ziua {zi}: refuzat - {eroare}")

zi_curenta = 20
print(f"\nÎntârzieri în ziua {zi_curenta}:")
for imprumut in biblioteca.imprumuturi:
    zile = imprumut.intarziere(zi_curenta)
    if zile:
        print(f"  {imprumut.membru.nume}: „{imprumut.carte.titlu}”, {zile} zile")
print(biblioteca.carti["978-2"])
```

```text
Ziua 1: Ana Popescu a luat „Ion”.
Ziua 3: Ana Popescu a luat „Maitreyi”.
Ziua 4: refuzat - Ana Popescu a atins limita de 2.
Ziua 5: refuzat - „Ion” nu e disponibilă.
Ziua 6: Mihai Ionescu a luat „Baltagul”.

Întârzieri în ziua 20:
  Ana Popescu: „Ion”, 5 zile
  Ana Popescu: „Maitreyi”, 3 zile
Carte(isbn='978-2', titlu='Maitreyi', autor='Mircea Eliade')
```

Observă:
- `Carte` e `frozen`, deci are `__hash__` și poate fi pusă în seturi sau folosită drept cheie de dicționar, iar nimeni nu-i poate schimba ISBN-ul din greșeală;
- `Membru` are o listă creată cu `default_factory`, deci fiecare membru are lista lui;
- `list["Imprumut"]` folosește numele clasei între ghilimele, pentru că `Imprumut` e definit mai jos în fișier; adnotările de tip acceptă și forma asta;
- `i.carte != carte` compară cărțile cu `__eq__`-ul generat, câmp cu câmp.

## Greșeli frecvente

### 1. Listă ca valoare implicită

<!-- fisier: date.py -->
```python
from dataclasses import dataclass


@dataclass
class Membru:
    nume: str
    carti: list = []
```

```text
Traceback (most recent call last):
  File "date.py", line 4, in <module>
    @dataclass
     ^^^^^^^^^
  File "/usr/local/lib/python3.12/dataclasses.py", line 1275, in dataclass
    return wrap(cls)
           ^^^^^^^^^
ValueError: mutable default <class 'list'> for field carti is not allowed: use default_factory
```

Spre deosebire de o clasă obișnuită (greșeala 2 de la lecția 33), dataclass-ul te oprește înainte să creezi vreun obiect. Mesajul îți spune și soluția: `carti: list = field(default_factory=list)`.

### 2. Câmp fără valoare implicită după unul cu valoare

<!-- fisier: date.py -->
```python
from dataclasses import dataclass


@dataclass
class Carte:
    titlu: str
    an: int = 1900
    autor: str
```

```text
Traceback (most recent call last):
  File "date.py", line 4, in <module>
    @dataclass
     ^^^^^^^^^
TypeError: non-default argument 'autor' follows default argument
```

Câmpurile devin parametrii lui `__init__`, iar un parametru obligatoriu nu poate veni după unul opțional (lecția 19). Mută câmpurile cu valori implicite la final.

### 3. Modificarea unui obiect frozen

<!-- fisier: date.py -->
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Carte:
    titlu: str
    an: int


ion = Carte("Ion", 1920)
ion.an = 1921
```

```text
Traceback (most recent call last):
  File "date.py", line 11, in <module>
    ion.an = 1921
    ^^^^^^
  File "<string>", line 4, in __setattr__
dataclasses.FrozenInstanceError: cannot assign to field 'an'
```

`File "<string>"` apare pentru că metoda care te-a oprit a fost generată de `@dataclass`, nu scrisă într-un fișier. Un obiect frozen nu se modifică, ci se înlocuiește cu unul nou. Funcția `dataclasses.replace(ion, an=1921)` creează o copie cu un câmp schimbat.

### 4. Câmp fără adnotare de tip

<!-- fisier: date.py -->
```python
from dataclasses import dataclass


@dataclass
class Membru:
    nume: str
    limita = 3


ana = Membru("Ana Popescu", limita=5)
```

```text
Traceback (most recent call last):
  File "date.py", line 10, in <module>
    ana = Membru("Ana Popescu", limita=5)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: Membru.__init__() got an unexpected keyword argument 'limita'
```

Fără `: int`, `limita` nu e câmp, ci un atribut de clasă obișnuit, deci nu apare în `__init__` (vezi „pe dedesubt”). Scrie `limita: int = 3`.

### 5. Încrederea că tipurile sunt verificate

```python
from dataclasses import dataclass


@dataclass
class Carte:
    titlu: str
    an: int


carte = Carte("Ion", "o mie nouă sute douăzeci")
print(carte.an + 1)
```

Fără nicio eroare la creare, obiectul are un `an` care e text, iar eroarea apare abia mai târziu, departe de cauză, la `carte.an + 1` (`TypeError: can only concatenate str (not "int") to str`). Adnotările de tip nu sunt verificate la rulare. Când datele vin din afară (input, fișiere, formulare), verifică-le în `__post_init__`: `if not isinstance(self.an, int): raise TypeError(...)`.

## Exercițiu

În `capitole/36-dataclasses/dataclasses_exercitii.py` (fișierul nu se numește `dataclasses.py`, pentru că ar ascunde modulul `dataclasses` din biblioteca standard și importul de la începutul fișierului n-ar mai funcționa), rescrie cu dataclass-uri catalogul de cărți al bibliotecii:

1. `Autor(nume: str, an_nastere: int)` cu `frozen=True`;
2. `Carte(titlu: str, autor: Autor, an: int, pagini: int, genuri: list[str])`, unde `genuri` pornește ca listă goală, prin `default_factory`; în `__post_init__`, ridică `ValueError` dacă anul e înainte de nașterea autorului sau dacă numărul de pagini nu e pozitiv;
3. un property `varsta_autorului_la_publicare`;
4. o listă de cel puțin 5 cărți, de la 2–3 autori; afișează-le sortate după an (cu `key=`, ca să nu depinzi de ordinea câmpurilor), apoi grupează-le într-un dicționar `Autor -> listă de titluri` (merge, pentru că `Autor` e frozen) și afișează-l;
5. încearcă să creezi o carte publicată înainte de nașterea autorului și prinde eroarea;
6. încearcă să modifici numele unui autor și explică, într-un comentariu, eroarea primită.

## Pe scurt

- `@dataclass` generează `__init__`, `__repr__` și `__eq__` din câmpurile scrise ca `nume: tip = valoare_implicita`.
- Câmpurile fără valoare implicită vin primele; listele și dicționarele implicite se scriu cu `field(default_factory=list)`.
- Tipurile nu sunt verificate la rulare; verificările se fac în `__post_init__`.
- `frozen=True` face obiectele imutabile (și le dă `__hash__`); `order=True` le compară câmp cu câmp, în ordinea scrierii.
- Doar atributele cu adnotare devin câmpuri; restul sunt atribute de clasă.
- Folosește dataclass pentru obiectele care sunt mai ales date și clase obișnuite pentru cele care sunt mai ales comportament.
