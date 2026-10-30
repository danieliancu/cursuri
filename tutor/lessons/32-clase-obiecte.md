## Ce este

O **clasă** este un șablon după care creezi obiecte. Ea descrie **ce date** are un lucru (atributele) și **ce poate face** (metodele). Un **obiect**, numit și **instanță**, e un exemplar concret creat după acel șablon.

```python
class Carte:
    def __init__(self, titlu, autor, pagini):
        self.titlu = titlu
        self.autor = autor
        self.pagini = pagini

    def descriere(self):
        return f"„{self.titlu}” de {self.autor}, {self.pagini} de pagini"


ion = Carte("Ion", "Liviu Rebreanu", 480)
enigma = Carte("Enigma Otiliei", "George Călinescu", 420)
print(ion.descriere())
print(enigma.titlu)
```

```text
„Ion” de Liviu Rebreanu, 480 de pagini
Enigma Otiliei
```

`Carte` e clasa. `ion` și `enigma` sunt două obiecte diferite, fiecare cu datele lui, dar amândouă au aceeași structură și aceleași metode.

De fapt, folosești obiecte din prima lecție: `"Ana"` e un obiect al clasei `str`, iar `[1, 2]` unul al clasei `list`. `type()` (lecția 2) îți arăta exact clasa: `<class 'str'>`. Acum înveți să-ți creezi propriile clase.

## De ce contează

Până acum ai ținut datele în dicționare și liste, iar operațiile în funcții separate (lecțiile 14 și 18). Pentru o carte, asta înseamnă un dicționar `{"titlu": ..., "autor": ...}` și funcții care primesc dicționarul. Merge, dar nimic nu te oprește să scrii greșit o cheie (`"titlul"`), iar funcțiile care lucrează cu cărți sunt împrăștiate prin program.

O clasă **pune datele și operațiile împreună**, sub un nume care spune ce reprezintă. Codul devine mai ușor de citit („cartea se împrumută”, nu „funcția primește un dicționar”) și mai ușor de extins.

Clasele sunt și baza lui Django. Un model din baza de date (lecția 50), un formular (lecția 55) și un view bazat pe clasă (lecția 58) sunt toate clase pe care le scrii tu.

## Cum funcționează

### Definirea unei clase

```python
class Membru:
    pass


ana = Membru()
print(type(ana))
```

```text
<class '__main__.Membru'>
```

- `class Membru:` definește clasa. Prin convenție, numele claselor se scriu cu **literă mare la fiecare cuvânt**, fără `_` (stilul „CamelCase”): `Carte`, `Membru`, `ImprumutCarte`. Variabilele și funcțiile rămân în snake_case;
- `pass` (lecția 11) ține locul corpului, care deocamdată e gol;
- `Membru()`, cu paranteze, **creează un obiect nou**. Operația se numește **instanțiere**;
- `__main__` din rezultat e numele modulului în care e definită clasa: fișierul pe care l-ai rulat direct (lecția 29).

### __init__: pregătirea obiectului nou

Metoda cu numele special `__init__` (două underscore-uri de fiecare parte) e apelată **automat** când creezi un obiect. Rolul ei e să-i dea obiectului datele de pornire.

```python
class Membru:
    def __init__(self, nume, varsta, oras):
        self.nume = nume
        self.varsta = varsta
        self.oras = oras


ana = Membru("Ana Popescu", 25, "Cluj")
mihai = Membru("Mihai Ionescu", 31, "Iași")
print(ana.nume, ana.varsta)
print(mihai.oras)
```

```text
Ana Popescu 25
Iași
```

Argumentele din `Membru("Ana Popescu", 25, "Cluj")` ajung la parametrii lui `__init__`, în ordine: `nume`, `varsta`, `oras`. Funcționează exact ca la funcții (lecțiile 18 și 19), inclusiv valorile implicite și argumentele cu nume:

```python
class Membru:
    def __init__(self, nume, varsta, oras="Cluj"):
        self.nume = nume
        self.varsta = varsta
        self.oras = oras


ioana = Membru(nume="Ioana Marin", varsta=19)
print(ioana.nume, ioana.oras)
```

```text
Ioana Marin Cluj
```

### self: obiectul curent

Primul parametru al oricărei metode e **obiectul pe care se lucrează**. Prin convenție se numește `self` („însuși”). Când scrii `Membru("Ana Popescu", 25, "Cluj")`, Python creează un obiect gol și apelează `__init__` cu acel obiect ca `self`. Rândul `self.nume = nume` înseamnă „pune în obiectul ăsta un atribut `nume`, cu valoarea primită”.

`self` nu se transmite de mână: Python îl completează singur. De aceea `__init__` are 4 parametri (`self`, `nume`, `varsta`, `oras`), dar tu dai doar 3 argumente.

### Atribute de instanță

Datele unui obiect se numesc **atribute** și se accesează cu punct: `obiect.atribut`. Fiecare obiect are atributele lui, independente de ale celorlalte:

```python
class Membru:
    def __init__(self, nume, varsta):
        self.nume = nume
        self.varsta = varsta


ana = Membru("Ana Popescu", 25)
mihai = Membru("Mihai Ionescu", 31)
ana.varsta += 1                 # Ana își serbează ziua
print(ana.varsta, mihai.varsta)
ana.email = "ana@exemplu.ro"    # atribut nou, doar pentru Ana
print(ana.email)
```

```text
26 31
ana@exemplu.ro
```

Poți adăuga oricând un atribut nou unui obiect, cum am făcut cu `email`, dar e o practică proastă. Cine citește clasa nu află din `__init__` că unele obiecte au și `email`, iar `mihai.email` ar da eroare. Regula: **toate atributele se creează în `__init__`**, chiar și cele care pornesc de la o valoare goală (`self.email = ""`).

### Metode: funcții care aparțin clasei

O **metodă** e o funcție definită în interiorul clasei. Primește obiectul ca `self`, deci are acces la toate datele lui:

```python
class Carte:
    def __init__(self, titlu, autor, pagini):
        self.titlu = titlu
        self.autor = autor
        self.pagini = pagini
        self.pagina_curenta = 0

    def citeste(self, numar_pagini):
        self.pagina_curenta = min(self.pagina_curenta + numar_pagini, self.pagini)

    def progres(self):
        return self.pagina_curenta / self.pagini

    def terminata(self):
        return self.pagina_curenta == self.pagini


ion = Carte("Ion", "Liviu Rebreanu", 480)
ion.citeste(120)
ion.citeste(60)
print(f"{ion.pagina_curenta} pagini citite ({ion.progres():.0%})")
print(ion.terminata())
ion.citeste(1000)
print(ion.pagina_curenta, ion.terminata())
```

```text
180 pagini citite (38%)
False
480 True
```

Observă cele două feluri de metode:
- `citeste()` **schimbă starea** obiectului (avansează pagina curentă) și nu întoarce nimic;
- `progres()` și `terminata()` **calculează** ceva din starea obiectului și întorc rezultatul.

`ion.citeste(120)` se citește natural: „din cartea `ion` se citesc 120 de pagini”. Metoda știe pe ce carte lucrează, prin `self`, fără să-i dai cartea ca argument.

### Ce se întâmplă „pe dedesubt”: obiect.metoda() e Clasa.metoda(obiect)

Când scrii `ion.citeste(120)`, Python caută metoda `citeste` în clasa obiectului (`Carte`) și o apelează cu obiectul ca prim argument. Cele două rânduri de mai jos fac **exact același lucru**:

```python
class Carte:
    def __init__(self, titlu, pagini):
        self.titlu = titlu
        self.pagini = pagini
        self.pagina_curenta = 0

    def citeste(self, numar_pagini):
        self.pagina_curenta += numar_pagini


ion = Carte("Ion", 480)
ion.citeste(50)
Carte.citeste(ion, 50)
print(ion.pagina_curenta)
```

```text
100
```

De aici vine `self`: nu e un cuvânt magic, ci primul parametru al unei funcții obișnuite. Python îl completează când apelezi metoda prin obiect. Același mecanism e în spatele metodelor pe care le folosești de la început: `"ana".upper()` e `str.upper("ana")`.

Fiecare obiect ține minte, în memorie, atributele **lui**. Metodele însă există **o singură dată**, în clasă, și sunt împărțite de toate obiectele. Când afișezi un obiect fără să-i fi spus cum, Python afișează doar clasa și adresa lui din memorie, ceva de felul `<__main__.Carte object at 0x7f3a2c1b4d90>`. Adresa diferă la fiecare rulare. La lecția 35 vei învăța să alegi tu cum arată un obiect afișat.

## Exemplu complet

Primul pas spre biblioteca pe care o dezvoltăm în tot modulul: clasa `Carte`, care știe dacă e împrumutată și de cine. (Fiecare lecție își scrie exemplul de la capăt, ca să fie complet; clasele se pot schimba ușor de la o lecție la alta.)

<!-- fisier: biblioteca.py -->
```python
class Carte:
    """O carte din bibliotecă."""

    def __init__(self, titlu, autor, an):
        self.titlu = titlu
        self.autor = autor
        self.an = an
        self.imprumutata_de = None  # numele membrului, sau None dacă e pe raft

    def disponibila(self):
        return self.imprumutata_de is None

    def imprumuta(self, nume_membru):
        if not self.disponibila():
            print(f"„{self.titlu}” e deja împrumutată de {self.imprumutata_de}.")
            return False
        self.imprumutata_de = nume_membru
        print(f"{nume_membru} a împrumutat „{self.titlu}”.")
        return True

    def returneaza(self):
        if self.disponibila():
            print(f"„{self.titlu}” nu era împrumutată.")
            return
        print(f"{self.imprumutata_de} a returnat „{self.titlu}”.")
        self.imprumutata_de = None

    def descriere(self):
        stare = "pe raft" if self.disponibila() else f"la {self.imprumutata_de}"
        return f"{self.titlu} ({self.autor}, {self.an}) - {stare}"


raft = [
    Carte("Ion", "Liviu Rebreanu", 1920),
    Carte("Enigma Otiliei", "George Călinescu", 1938),
    Carte("Maitreyi", "Mircea Eliade", 1933),
]

raft[0].imprumuta("Ana Popescu")
raft[0].imprumuta("Mihai Ionescu")
raft[2].imprumuta("Mihai Ionescu")
raft[0].returneaza()
raft[1].returneaza()

print()
for carte in raft:
    print(carte.descriere())

disponibile = [c.titlu for c in raft if c.disponibila()]
print(f"\nPe raft: {', '.join(disponibile)}")
```

```text
Ana Popescu a împrumutat „Ion”.
„Ion” e deja împrumutată de Ana Popescu.
Mihai Ionescu a împrumutat „Maitreyi”.
Ana Popescu a returnat „Ion”.
„Enigma Otiliei” nu era împrumutată.

Ion (Liviu Rebreanu, 1920) - pe raft
Enigma Otiliei (George Călinescu, 1938) - pe raft
Maitreyi (Mircea Eliade, 1933) - la Mihai Ionescu

Pe raft: Ion, Enigma Otiliei
```

Observă:
- obiectele se pot pune în liste și pot fi parcurse cu `for` sau comprehension (lecțiile 12 și 16), ca orice altă valoare;
- `imprumutata_de` pornește de la `None` (lecția 18) și e creat în `__init__`, chiar dacă la început nu are o valoare reală;
- metodele se pot apela între ele prin `self`: `imprumuta()` folosește `self.disponibila()`;
- docstring-ul clasei (lecția 22) spune pe scurt ce reprezintă.

## Greșeli frecvente

### 1. Lipsește self din definiția metodei

<!-- fisier: carte.py -->
```python
class Carte:
    def __init__(self, titlu):
        self.titlu = titlu

    def descriere():
        return "o carte"


ion = Carte("Ion")
print(ion.descriere())
```

```text
Traceback (most recent call last):
  File "carte.py", line 10, in <module>
    print(ion.descriere())
          ^^^^^^^^^^^^^^^
TypeError: Carte.descriere() takes 0 positional arguments but 1 was given
```

Mesajul pare ciudat, pentru că tu n-ai dat niciun argument. L-a dat însă Python: obiectul `ion`, ca `self` (vezi „pe dedesubt”). Orice metodă are `self` ca prim parametru: `def descriere(self):`.

### 2. Lipsește self. când folosești un atribut

<!-- fisier: carte.py -->
```python
class Carte:
    def __init__(self, titlu):
        self.titlu = titlu

    def descriere(self):
        return f"Cartea „{titlu}”"


print(Carte("Ion").descriere())
```

```text
Traceback (most recent call last):
  File "carte.py", line 9, in <module>
    print(Carte("Ion").descriere())
          ^^^^^^^^^^^^^^^^^^^^^^^^
  File "carte.py", line 6, in descriere
    return f"Cartea „{titlu}”"
                      ^^^^^
NameError: name 'titlu' is not defined. Did you mean: 'self.titlu'?
```

Python chiar îți sugerează soluția. În metodă, `titlu` simplu ar fi o variabilă locală (lecția 20), care nu există. Atributul obiectului e `self.titlu`. Parametrul `titlu` din `__init__` a existat doar cât a rulat `__init__`.

### 3. Argumente lipsă la crearea obiectului

<!-- fisier: carte.py -->
```python
class Carte:
    def __init__(self, titlu, autor, pagini):
        self.titlu = titlu
        self.autor = autor
        self.pagini = pagini


ion = Carte("Ion")
```

```text
Traceback (most recent call last):
  File "carte.py", line 8, in <module>
    ion = Carte("Ion")
          ^^^^^^^^^^^^
TypeError: Carte.__init__() missing 2 required positional arguments: 'autor' and 'pagini'
```

Argumentele de la crearea obiectului merg la `__init__`, deci se aplică aceleași reguli ca la orice funcție (lecția 18). Dacă unele date sunt opționale, dă-le valori implicite în `__init__`.

### 4. __init__ scris greșit

<!-- fisier: carte.py -->
```python
class Carte:
    def __int__(self, titlu):
        self.titlu = titlu


ion = Carte("Ion")
```

```text
Traceback (most recent call last):
  File "carte.py", line 6, in <module>
    ion = Carte("Ion")
          ^^^^^^^^^^^^
TypeError: Carte() takes no arguments
```

`__int__` (fără „i”) nu e `__init__`, ci altă metodă specială (cea folosită de `int()`). Clasa a rămas fără `__init__`, deci nu acceptă argumente. Când vezi „takes no arguments” la crearea unui obiect, verifică literă cu literă numele `__init__` și cele două underscore-uri de fiecare parte.

### 5. Atribut care nu a fost creat

<!-- fisier: carte.py -->
```python
class Membru:
    def __init__(self, nume):
        self.nume = nume


ana = Membru("Ana Popescu")
ana.email = "ana@exemplu.ro"
mihai = Membru("Mihai Ionescu")
print(mihai.email)
```

```text
Traceback (most recent call last):
  File "carte.py", line 9, in <module>
    print(mihai.email)
          ^^^^^^^^^^^
AttributeError: 'Membru' object has no attribute 'email'
```

Ana are `email` pentru că i l-ai adăugat separat, iar Mihai nu are. Creează toate atributele în `__init__`, cu o valoare implicită dacă e nevoie (`self.email = ""`), ca fiecare obiect al clasei să aibă aceleași atribute.

O greșeală înrudită: uitarea parantezelor la apelul unei metode. `print(ana.descriere)` nu dă eroare, dar afișează ceva de felul `<bound method Membru.descriere of <__main__.Membru object at 0x7f...>>`, adică metoda însăși, nu rezultatul ei. Ca să o apelezi, pune parantezele: `ana.descriere()`.

## Exercițiu

În `capitole/32-clase-obiecte/clase_obiecte.py`, scrie clasa `Membru` pentru bibliotecă:

1. `__init__` primește `nume`, `varsta` și `oras`, iar `oras` are valoarea implicită `"Cluj"`; pe lângă acestea, fiecare membru pornește cu lista goală `carti` (titlurile împrumutate) și cu `limita = 3`;
2. metoda `poate_imprumuta()` întoarce `True` dacă membrul are mai puțin de `limita` cărți;
3. metoda `imprumuta(titlu)` adaugă titlul în listă dacă se poate și întoarce `True`, altfel afișează un mesaj și întoarce `False`;
4. metoda `returneaza(titlu)` scoate titlul din listă sau afișează un mesaj dacă membrul nu are cartea;
5. metoda `fisa()` întoarce un text de forma `Ana Popescu (25 de ani, Cluj) - 2/3 cărți: Ion, Maitreyi`;
6. creează-i pe Ana Popescu (25 de ani, Cluj) și pe Mihai Ionescu (31 de ani, Iași), fă câteva împrumuturi și returnări (inclusiv unul peste limită și o returnare a unei cărți pe care membrul nu o are) și afișează fișele.

## Pe scurt

- O clasă e un șablon (`class Carte:`), iar un obiect e un exemplar creat după el (`Carte(...)`).
- `__init__` e apelată automat la crearea obiectului și creează atributele cu `self.atribut = valoare`.
- `self` e obiectul curent; e primul parametru al oricărei metode, iar Python îl completează singur.
- Atributele (`obiect.atribut`) sunt datele fiecărui obiect; metodele (`obiect.metoda()`) sunt funcțiile clasei, care lucrează cu acele date.
- Creează toate atributele în `__init__`; numele claselor se scriu în CamelCase.
- `obiect.metoda(x)` e același lucru cu `Clasa.metoda(obiect, x)`, de aici vine `self`.
