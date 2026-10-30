## Ce este

**Metodele speciale** sunt metode cu nume înconjurate de două underscore-uri de fiecare parte, ca `__init__` (lecția 32). Python le apelează **singur**, în anumite situații:
- `print(obiect)` și `str(obiect)` apelează `__str__`;
- `obiect1 == obiect2` apelează `__eq__`;
- `len(obiect)` apelează `__len__`;
- `obiect1 < obiect2` (și deci `sorted()`) apelează `__lt__`.

Li se mai spune „metode dunder” (de la „double underscore”) sau „metode magice”.

```python
class Carte:
    def __init__(self, titlu, autor):
        self.titlu = titlu
        self.autor = autor

    def __str__(self):
        return f"„{self.titlu}” de {self.autor}"


ion = Carte("Ion", "Liviu Rebreanu")
print(ion)
print(f"Recomandarea zilei: {ion}")
```

```text
„Ion” de Liviu Rebreanu
Recomandarea zilei: „Ion” de Liviu Rebreanu
```

## De ce contează

Fără metode speciale, obiectele tale se comportă stângaci:
- `print(ion)` afișează ceva de felul `<__main__.Carte object at 0x7f3a2c1b4d90>`, care nu-ți spune nimic;
- două obiecte `Carte` cu exact aceleași date nu sunt egale (`==` dă `False`);
- `sorted(carti)` dă eroare, pentru că Python nu știe cum se compară două cărți.

Cu câteva metode speciale, obiectele tale se comportă ca tipurile din Python: se afișează frumos, se compară, se sortează, răspund la `len()` și la `in`. Codul care le folosește devine natural: `if carte in biblioteca:`, `sorted(carti)`, `print(membru)`.

În Django, `__str__` e prima metodă pe care o scrii la fiecare model: panoul de administrare (lecția 54) o folosește ca să afișeze fiecare obiect din baza de date într-o listă sau într-un meniu de selecție.

## Cum funcționează

### __str__ și __repr__: cum arată un obiect

Python are două feluri de a transforma un obiect în text:
- **`__str__`**: textul pentru **oameni**, folosit de `print()`, `str()` și f-strings;
- **`__repr__`**: textul pentru **programatori**, folosit în consola interactivă Python, în listele afișate și la depanare. Ideal, arată ca codul care ar recrea obiectul.

```python
class Carte:
    def __init__(self, titlu, autor):
        self.titlu = titlu
        self.autor = autor

    def __str__(self):
        return f"„{self.titlu}” de {self.autor}"

    def __repr__(self):
        return f"Carte({self.titlu!r}, {self.autor!r})"


ion = Carte("Ion", "Liviu Rebreanu")
print(ion)
print(repr(ion))
print([ion, Carte("Maitreyi", "Mircea Eliade")])
print(f"{ion!r}")
```

```text
„Ion” de Liviu Rebreanu
Carte('Ion', 'Liviu Rebreanu')
[Carte('Ion', 'Liviu Rebreanu'), Carte('Maitreyi', 'Mircea Eliade')]
Carte('Ion', 'Liviu Rebreanu')
```

Observă al treilea rând: când afișezi o **listă**, Python folosește `__repr__` pentru elementele ei, nu `__str__`. E același motiv pentru care `print(["Ana"])` arată `['Ana']`, cu ghilimele: e reprezentarea pentru programatori.

`!r` într-un f-string (lecția 26) cere `repr()` în loc de `str()`. L-am folosit în `__repr__` ca titlurile să apară cu ghilimele: `'Ion'`.

Dacă scrii doar una dintre ele, scrie `__repr__`: când `__str__` lipsește, Python îl folosește pe `__repr__` și pentru `print()`.

### __eq__: când sunt două obiecte egale

Implicit, `==` între două obiecte ale clasei tale verifică dacă sunt **același obiect** (ca `is`, lecția 12). Două cărți cu aceleași date, create separat, nu sunt egale:

```python
class Carte:
    def __init__(self, isbn, titlu):
        self.isbn = isbn
        self.titlu = titlu


print(Carte("978-973-46-0001-1", "Ion") == Carte("978-973-46-0001-1", "Ion"))
```

```text
False
```

Cu `__eq__` alegi tu ce înseamnă „egal”. Pentru cărți, două exemplare sunt aceeași carte dacă au același ISBN:

```python
class Carte:
    def __init__(self, isbn, titlu):
        self.isbn = isbn
        self.titlu = titlu

    def __eq__(self, alta):
        if not isinstance(alta, Carte):
            return NotImplemented
        return self.isbn == alta.isbn

    def __hash__(self):
        return hash(self.isbn)


a = Carte("978-973-46-0001-1", "Ion")
b = Carte("978-973-46-0001-1", "Ion (ediție nouă)")
print(a == b, a != b)
print(a == "Ion")
print(len({a, b}))
```

```text
True False
False
1
```

Trei detalii:
- `return NotImplemented` (o valoare specială, nu o eroare) îi spune lui Python „nu știu să compar cu asta”. Python încearcă atunci și comparația inversă, iar dacă nici ea nu merge, `==` dă `False`. Așa `a == "Ion"` nu crapă;
- `!=` funcționează automat, ca opusul lui `__eq__`;
- dacă definești `__eq__`, Python **elimină** hash-ul implicit, iar obiectele nu mai pot fi puse în seturi sau folosite drept chei de dicționar. Obiectele egale trebuie să aibă același hash (lecția 14), așa că scrii și `__hash__`, calculat din **aceleași** date ca egalitatea (aici, ISBN-ul).

### __lt__: ordinea și sortarea

`sorted()` și `min()` / `max()` compară obiectele cu `<`. Pentru obiectele tale, `<` apelează `__lt__` („less than”):

```python
class Carte:
    def __init__(self, titlu, an):
        self.titlu = titlu
        self.an = an

    def __repr__(self):
        return f"Carte({self.titlu!r}, {self.an})"

    def __lt__(self, alta):
        return self.an < alta.an


carti = [Carte("Maitreyi", 1933), Carte("Ion", 1920), Carte("Enigma Otiliei", 1938)]
print(sorted(carti))
print(min(carti))
print(sorted(carti, key=lambda c: c.titlu))
```

```text
[Carte('Ion', 1920), Carte('Maitreyi', 1933), Carte('Enigma Otiliei', 1938)]
Carte('Ion', 1920)
[Carte('Enigma Otiliei', 1938), Carte('Ion', 1920), Carte('Maitreyi', 1933)]
```

`__lt__` definește **ordinea naturală** a obiectelor (aici, după an). Pentru o altă ordine, `key=` (lecțiile 17 și 21) are prioritate și nu folosește `__lt__`.

Mai există `__le__` (`<=`), `__gt__` (`>`) și `__ge__` (`>=`). Pentru `sorted()` ajunge `__lt__`. Dacă vrei toți operatorii, decoratorul `functools.total_ordering` îi generează din `__eq__` și `__lt__`.

### __len__ și __contains__: obiecte care se poartă ca o colecție

```python
class Raft:
    def __init__(self, nume):
        self.nume = nume
        self.titluri = []

    def __len__(self):
        return len(self.titluri)

    def __contains__(self, titlu):
        return titlu.lower() in (t.lower() for t in self.titluri)


raft = Raft("Literatură română")
raft.titluri += ["Ion", "Maitreyi"]
print(len(raft))
print("ion" in raft, "Baltagul" in raft)
if raft:
    print(f"Raftul „{raft.nume}” nu e gol.")
```

```text
2
True False
Raftul „Literatură română” nu e gol.
```

- `len(raft)` apelează `raft.__len__()`;
- `x in raft` apelează `raft.__contains__(x)`. Aici am făcut căutarea fără să conteze literele mari și mici;
- `if raft:` folosește tot `__len__`: un obiect cu lungimea 0 e considerat fals, la fel ca o listă goală (truthiness, lecția 7).

Ca obiectul să poată fi parcurs și cu `for`, îi trebuie `__iter__`; la lecția 37 vei vedea cum îl scrii cel mai simplu, cu un generator.

### Ce se întâmplă „pe dedesubt”: operatorii sunt apeluri de metode

Pentru Python, aproape fiecare operator e un apel de metodă specială, de obicei pe obiectul din stânga (la `in`, pe cel din dreapta):

| Scrii | Python apelează |
|---|---|
| `str(x)`, `print(x)` | `x.__str__()` |
| `x == y` | `x.__eq__(y)` |
| `x < y` | `x.__lt__(y)` |
| `len(x)` | `x.__len__()` |
| `y in x` | `x.__contains__(y)` |
| `x + y` | `x.__add__(y)` |

Asta e valabil și pentru tipurile din Python. `3 + 4` e `(3).__add__(4)`, iar `"Ana" == "Ana"` e `"Ana".__eq__("Ana")`:

```python
print((3).__add__(4))
print("Ana".__eq__("Ana"))
print([1, 2, 3].__len__())
```

```text
7
True
3
```

Nu vei scrie niciodată așa în cod real. Exemplul arată doar că obiectele tale și tipurile din Python folosesc **același** mecanism. De aceea o clasă cu metodele speciale potrivite poate fi folosită oriunde se așteaptă „ceva ce se poate aduna” sau „ceva cu o lungime”.

## Exemplu complet

Biblioteca, cu metode speciale: cărți care se afișează, se compară și se sortează natural, plus o bibliotecă ce se comportă ca o colecție.

<!-- fisier: biblioteca.py -->
```python
class Carte:
    def __init__(self, isbn, titlu, autor, an):
        self.isbn = isbn
        self.titlu = titlu
        self.autor = autor
        self.an = an

    def __str__(self):
        return f"„{self.titlu}” ({self.autor}, {self.an})"

    def __repr__(self):
        return f"Carte({self.isbn!r}, {self.titlu!r})"

    def __eq__(self, alta):
        if not isinstance(alta, Carte):
            return NotImplemented
        return self.isbn == alta.isbn

    def __hash__(self):
        return hash(self.isbn)

    def __lt__(self, alta):
        return self.titlu.lower() < alta.titlu.lower()


class Biblioteca:
    def __init__(self, nume):
        self.nume = nume
        self.exemplare = {}   # Carte -> număr de exemplare

    def adauga(self, carte, bucati=1):
        self.exemplare[carte] = self.exemplare.get(carte, 0) + bucati

    def __len__(self):
        return sum(self.exemplare.values())

    def __contains__(self, carte):
        return self.exemplare.get(carte, 0) > 0

    def __str__(self):
        return f"{self.nume}: {len(self.exemplare)} titluri, {len(self)} exemplare"


biblioteca = Biblioteca("Biblioteca Județeană Cluj")
biblioteca.adauga(Carte("978-1", "Ion", "Liviu Rebreanu", 1920), 3)
biblioteca.adauga(Carte("978-2", "Maitreyi", "Mircea Eliade", 1933))
biblioteca.adauga(Carte("978-3", "enigma Otiliei", "George Călinescu", 1938), 2)
# încă un exemplar din „Ion”
biblioteca.adauga(Carte("978-1", "Ion", "Liviu Rebreanu", 1920))

print(biblioteca)
for carte in sorted(biblioteca.exemplare):
    print(f"  {biblioteca.exemplare[carte]} x {carte}")

cautata = Carte("978-2", "Maitreyi", "Mircea Eliade", 1933)
print(cautata in biblioteca, Carte("978-9", "Baltagul", "Mihail Sadoveanu", 1930) in biblioteca)
print(repr(min(biblioteca.exemplare)))
```

```text
Biblioteca Județeană Cluj: 3 titluri, 7 exemplare
  2 x „enigma Otiliei” (George Călinescu, 1938)
  4 x „Ion” (Liviu Rebreanu, 1920)
  1 x „Maitreyi” (Mircea Eliade, 1933)
True False
Carte('978-3', 'enigma Otiliei')
```

Observă:
- „Ion” adăugat a doua oară e un obiect **nou**, dar, datorită lui `__eq__` și `__hash__`, dicționarul îl recunoaște ca aceeași cheie, deci crește numărul de exemplare la 4;
- `cautata in biblioteca` funcționează cu un obiect creat separat, din același motiv;
- `sorted()` folosește `__lt__`, care compară titlurile fără să conteze literele mari și mici, deci „enigma Otiliei” vine prima;
- `len(self)` din `__str__` apelează `__len__`-ul aceleiași clase.

## Greșeli frecvente

### 1. __str__ care nu întoarce un string

<!-- fisier: speciale.py -->
```python
class Carte:
    def __init__(self, an):
        self.an = an

    def __str__(self):
        return self.an


print(Carte(1920))
```

```text
Traceback (most recent call last):
  File "speciale.py", line 9, in <module>
    print(Carte(1920))
TypeError: __str__ returned non-string (type int)
```

`__str__` (și `__repr__`) trebuie să întoarcă **obligatoriu** un `str`. Folosește un f-string: `return f"{self.an}"`.

### 2. __str__ care afișează în loc să întoarcă

<!-- fisier: speciale.py -->
```python
class Carte:
    def __init__(self, titlu):
        self.titlu = titlu

    def __str__(self):
        print(f"Cartea {self.titlu}")


print(Carte("Ion"))
```

```text
Cartea Ion
Traceback (most recent call last):
  File "speciale.py", line 9, in <module>
    print(Carte("Ion"))
TypeError: __str__ returned non-string (type NoneType)
```

Textul s-a afișat (din interiorul metodei), apoi `print` a primit `None` (funcția nu are `return`, lecția 18) și a dat eroare. Metodele speciale **întorc** valori, nu afișează: `return f"Cartea {self.titlu}"`.

### 3. __eq__ fără __hash__

<!-- fisier: speciale.py -->
```python
class Carte:
    def __init__(self, isbn):
        self.isbn = isbn

    def __eq__(self, alta):
        return self.isbn == alta.isbn


carti = {Carte("978-1"), Carte("978-2")}
```

```text
Traceback (most recent call last):
  File "speciale.py", line 9, in <module>
    carti = {Carte("978-1"), Carte("978-2")}
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: unhashable type: 'Carte'
```

Definirea lui `__eq__` a eliminat hash-ul implicit (vezi „Cum funcționează”). Dacă obiectele trebuie puse în seturi sau folosite drept chei, adaugă `__hash__` bazat pe aceleași date: `return hash(self.isbn)`.

### 4. __eq__ care presupune că celălalt e de același tip

<!-- fisier: speciale.py -->
```python
class Carte:
    def __init__(self, isbn):
        self.isbn = isbn

    def __eq__(self, alta):
        return self.isbn == alta.isbn


print(Carte("978-1") == "978-1")
```

```text
Traceback (most recent call last):
  File "speciale.py", line 9, in <module>
    print(Carte("978-1") == "978-1")
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "speciale.py", line 6, in __eq__
    return self.isbn == alta.isbn
                        ^^^^^^^^^
AttributeError: 'str' object has no attribute 'isbn'
```

`==` poate primi orice în dreapta, inclusiv un string sau `None`. Verifică tipul și întoarce `NotImplemented` pentru celelalte cazuri, ca în exemplul din lecție.

### 5. Sortare fără __lt__

<!-- fisier: speciale.py -->
```python
class Carte:
    def __init__(self, titlu):
        self.titlu = titlu


carti = sorted([Carte("Ion"), Carte("Maitreyi")])
```

```text
Traceback (most recent call last):
  File "speciale.py", line 6, in <module>
    carti = sorted([Carte("Ion"), Carte("Maitreyi")])
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: '<' not supported between instances of 'Carte' and 'Carte'
```

Python nu știe care carte e „mai mică”. Ai două soluții: definești `__lt__` (ordinea naturală a clasei) sau dai un criteriu la sortare: `sorted(carti, key=lambda c: c.titlu)` (lecția 21).

## Exercițiu

În `capitole/35-metode-speciale/metode_speciale.py`, adaugă metode speciale claselor bibliotecii:

1. clasa `Membru(nume, numar_legitimatie)` cu:
   - `__str__`, de forma `Ana Popescu (legitimația 1024)`;
   - `__repr__`, de forma `Membru('Ana Popescu', 1024)`;
   - `__eq__` și `__hash__` după numărul legitimației;
   - `__lt__` după nume, fără să conteze literele mari și mici;
2. clasa `ListaAsteptare(titlu)` care ține membrii care așteaptă o carte, cu metoda `adauga(membru)` (un membru nu poate fi adăugat de două ori: folosește `in`), `__len__`, `__contains__` și `__str__` (de exemplu `„Ion”: 3 în așteptare`);
3. creează 4 membri, inclusiv două obiecte diferite cu aceeași legitimație, și demonstrează că:
   - al doilea obiect cu aceeași legitimație nu poate fi adăugat în lista de așteptare;
   - `sorted()` pe membri merge;
   - `print()` pe o listă de membri folosește `__repr__`;
   - `if lista:` e fals pentru o listă de așteptare goală.

## Pe scurt

- Metodele speciale (`__nume__`) sunt apelate automat de Python: `print` → `__str__`, `==` → `__eq__`, `<` → `__lt__`, `len` → `__len__`, `in` → `__contains__`.
- `__str__` e textul pentru oameni, `__repr__` pentru programatori (folosit și în listele afișate); ambele trebuie să întoarcă un `str`.
- Fără `__eq__`, `==` compară identitatea obiectelor; cu `__eq__`, compară ce alegi tu.
- Cine definește `__eq__` trebuie să definească și `__hash__`, din aceleași date, ca obiectele să poată sta în seturi și dicționare.
- În `__eq__`, verifică tipul celuilalt obiect și întoarce `NotImplemented` dacă nu știi să compari.
- `__lt__` dă ordinea naturală pentru `sorted`, `min` și `max`; `__len__` face ca `if obiect:` să funcționeze ca la colecții.
