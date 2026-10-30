## Ce este

La lecția 32, fiecare atribut aparținea unui obiect (`self.titlu`), iar fiecare metodă lucra cu un obiect (`self`). O clasă poate avea însă și:
- **atribute de clasă**: date comune tuturor obiectelor, scrise direct în corpul clasei;
- **`@classmethod`**: metode care lucrează cu clasa, nu cu un obiect (de exemplu, alte feluri de a crea obiecte);
- **`@staticmethod`**: funcții obișnuite, puse în clasă pentru că țin de ea;
- **`@property`**: metode care se folosesc ca atribute, fără paranteze.

```python
class Carte:
    taxa_intarziere = 0.5  # atribut de clasă: lei pe zi, aceeași pentru toate cărțile

    def __init__(self, titlu, autor):
        self.titlu = titlu          # atribute de instanță: diferite la fiecare carte
        self.autor = autor
        self.imprumutata_de = None

    @property
    def disponibila(self):
        return self.imprumutata_de is None


ion = Carte("Ion", "Liviu Rebreanu")
print(ion.disponibila)
print(ion.taxa_intarziere, Carte.taxa_intarziere)
```

```text
True
0.5 0.5
```

La lecția 32, `disponibila()` era o metodă obișnuită; aici a devenit un property, deci se citește fără paranteze: `ion.disponibila`.

Semnul `@` din fața unei metode se numește **decorator**. Deocamdată reține doar că schimbă felul în care se comportă metoda de sub el. Cum funcționează decoratorii și cum îți scrii propriii decoratori, la lecția 38.

## De ce contează

Clasele reale au nevoie de toate acestea:
- o setare comună (taxa de întârziere, numărul maxim de împrumuturi) se scrie **o singură dată**, în clasă, nu copiată în fiecare obiect;
- datele vin adesea în alte forme (un rând dintr-un fișier CSV, un dicționar JSON, lecția 28), iar un `@classmethod` creează obiectul direct din ele;
- un `@property` arată ca un atribut simplu (`carte.disponibila`), dar valoarea lui e mereu calculată din starea actuală, deci nu poate rămâne „în urmă”;
- tot cu `@property` poți **verifica** valorile înainte să fie salvate, ca un obiect să nu ajungă niciodată într-o stare imposibilă (o carte cu -5 pagini).

În Django vei vedea toate tiparele astea: atribute de clasă în modele și formulare (lecțiile 50 și 55), `@property` în modele, `@classmethod` pentru constructori alternativi.

## Cum funcționează

### Atribute de clasă vs atribute de instanță

Un atribut scris direct în corpul clasei, în afara metodelor, aparține **clasei** și e comun tuturor obiectelor:

```python
class Membru:
    limita = 3          # atribut de clasă
    total_membri = 0    # atribut de clasă, folosit ca numărător

    def __init__(self, nume):
        self.nume = nume
        Membru.total_membri += 1


ana = Membru("Ana Popescu")
mihai = Membru("Mihai Ionescu")
print(ana.limita, mihai.limita)
print(Membru.total_membri)

Membru.limita = 5   # schimbare pentru toată lumea
print(ana.limita, mihai.limita)
```

```text
3 3
2
5 5
```

Când scrii `ana.limita`, Python caută întâi un atribut `limita` **în obiectul** `ana`. Nu-l găsește, așa că îl caută **în clasă**. De aceea toate obiectele „văd” valoarea din clasă, iar o schimbare în clasă se vede peste tot.

Observă că în `__init__` am scris `Membru.total_membri += 1`, nu `self.total_membri += 1`. Diferența e importantă, vezi greșelile frecvente.

### Metode care modifică starea

Metodele care schimbă atributele obiectului trebuie să păstreze obiectul într-o stare **corectă**. Ele verifică întâi dacă operația are sens:

```python
class Membru:
    limita = 3

    def __init__(self, nume):
        self.nume = nume
        self.carti = []

    def imprumuta(self, titlu):
        if len(self.carti) >= self.limita:
            raise ValueError(f"{self.nume} are deja {self.limita} cărți.")
        self.carti.append(titlu)


ana = Membru("Ana Popescu")
for titlu in ["Ion", "Maitreyi", "Baltagul", "Moromeții"]:
    try:
        ana.imprumuta(titlu)
    except ValueError as eroare:
        print("Refuzat:", eroare)
print(ana.carti)
```

```text
Refuzat: Ana Popescu are deja 3 cărți.
['Ion', 'Maitreyi', 'Baltagul']
```

Metoda ridică o excepție (lecția 25) în loc să afișeze un mesaj. Așa decide **codul care o apelează** ce face cu eroarea: o afișează, o scrie într-un fișier sau o arată într-o pagină web. `self.limita` citește atributul de clasă, la fel ca `ana.limita`.

### @classmethod: alt fel de a crea obiecte

O metodă marcată cu `@classmethod` primește **clasa** ca prim parametru, numit prin convenție `cls`, în loc de un obiect. Cea mai des întâlnită folosire: un „constructor alternativ”, care creează obiecte din alte forme de date.

```python
class Carte:
    def __init__(self, titlu, autor, an):
        self.titlu = titlu
        self.autor = autor
        self.an = an

    @classmethod
    def din_text(cls, rand):
        """Creează o carte dintr-un rând de forma „titlu;autor;an”."""
        titlu, autor, an = rand.split(";")
        return cls(titlu.strip(), autor.strip(), int(an))


randuri = ["Ion; Liviu Rebreanu; 1920", "Maitreyi;Mircea Eliade;1933"]
carti = [Carte.din_text(r) for r in randuri]
for carte in carti:
    print(carte.titlu, "-", carte.autor, "-", carte.an)
```

```text
Ion - Liviu Rebreanu - 1920
Maitreyi - Mircea Eliade - 1933
```

`cls(...)` înseamnă `Carte(...)`. Folosim `cls` în loc de numele scris de mână pentru ca metoda să funcționeze corect și în clasele derivate (lecția 34).

Un nume de felul `din_text`, `din_dict` sau `din_csv` spune clar de unde vin datele. E mult mai clar decât un `__init__` care încearcă să ghicească ce i s-a dat.

### @staticmethod: o funcție care ține de clasă

O metodă marcată cu `@staticmethod` nu primește nici `self`, nici `cls`. E o funcție obișnuită, pusă în clasă pentru că are legătură cu ea:

```python
class Carte:
    @staticmethod
    def an_valid(an):
        return 1450 <= an <= 2026   # tiparul cu litere mobile apare pe la 1450


print(Carte.an_valid(1920))
print(Carte.an_valid(3000))
```

```text
True
False
```

Folosește `@staticmethod` rar: dacă funcția nu are nevoie de clasă sau de obiect, de cele mai multe ori poate fi o funcție simplă în modul (lecția 29). E utilă când vrei ca toate operațiile legate de cărți să stea în același loc.

### @property: metode citite ca atribute

Un `@property` e o metodă care se **citește fără paranteze**, ca un atribut. Valoarea e calculată la fiecare citire, deci e mereu actuală:

```python
class Membru:
    limita = 3

    def __init__(self, prenume, nume_familie):
        self.prenume = prenume
        self.nume_familie = nume_familie
        self.carti = []

    @property
    def nume_complet(self):
        return f"{self.prenume} {self.nume_familie}"

    @property
    def locuri_libere(self):
        return self.limita - len(self.carti)


ana = Membru("Ana", "Popescu")
print(ana.nume_complet, ana.locuri_libere)
ana.carti.append("Ion")
ana.nume_familie = "Popescu-Marin"
print(ana.nume_complet, ana.locuri_libere)
```

```text
Ana Popescu 3
Ana Popescu-Marin 2
```

Dacă `nume_complet` ar fi fost un atribut obișnuit, calculat o singură dată în `__init__`, ar fi rămas „Ana Popescu” după schimbarea numelui de familie. Ca property, e recalculat de fiecare dată.

### property cu setter: verificarea valorilor

Un property poate avea și un **setter**, o metodă apelată când **atribui** o valoare. Ea poate verifica valoarea înainte s-o salveze:

```python
class Carte:
    def __init__(self, titlu, pagini):
        self.titlu = titlu
        self.pagini = pagini      # trece deja prin setter-ul de mai jos

    @property
    def pagini(self):
        return self._pagini

    @pagini.setter
    def pagini(self, valoare):
        if valoare <= 0:
            raise ValueError(f"Numărul de pagini trebuie să fie pozitiv, nu {valoare}.")
        self._pagini = valoare


ion = Carte("Ion", 480)
ion.pagini = 482
print(ion.pagini)
try:
    ion.pagini = -5
except ValueError as eroare:
    print(eroare)
print(ion.pagini)
```

```text
482
Numărul de pagini trebuie să fie pozitiv, nu -5.
482
```

Valoarea reală stă în `self._pagini`, cu `_` în față. Underscore-ul de la început e o **convenție**: „atribut intern, nu-l folosi direct din afara clasei”. Python nu te oprește să scrii `ion._pagini = -5`, dar oricine citește codul înțelege că ocolești regulile clasei.

Observă că `__init__` scrie `self.pagini = pagini`, deci și valoarea de la creare trece prin verificare: nu poți crea o carte cu -5 pagini.

### Ce se întâmplă „pe dedesubt”: unde caută Python un atribut

Fiecare obiect are un dicționar cu atributele lui, numit `__dict__`. Clasa are și ea un `__dict__`, cu atributele de clasă și metodele. Când scrii `obiect.nume`, Python caută:
1. în `obiect.__dict__` (atributele de instanță);
2. dacă nu găsește, în clasa obiectului (atributele de clasă și metodele);
3. dacă nu găsește nici acolo, dă `AttributeError`.

(Un property e un caz special: Python îl găsește în clasă și îl apelează, indiferent ce e în obiect.)

```python
class Membru:
    limita = 3

    def __init__(self, nume):
        self.nume = nume


ana = Membru("Ana Popescu")
print(ana.__dict__)
print("limita" in ana.__dict__, "limita" in Membru.__dict__)
```

```text
{'nume': 'Ana Popescu'}
False True
```

Atributele de instanță sunt literalmente un dicționar (lecția 14). De aceea poți adăuga oricând atribute noi unui obiect: e doar o cheie nouă în dicționarul lui.

## Exemplu complet

Biblioteca primește o clasă nouă, `Biblioteca`, care ține cărțile într-un dicționar, le încarcă din rânduri de text și calculează taxele de întârziere.

<!-- fisier: biblioteca.py -->
```python
class Carte:
    zile_imprumut = 14       # comune tuturor cărților
    taxa_pe_zi = 0.5

    def __init__(self, cod, titlu, autor):
        self.cod = cod
        self.titlu = titlu
        self.autor = autor
        self.imprumutata_de = None
        self.zi_imprumut = None   # ziua din an în care a fost împrumutată

    @classmethod
    def din_text(cls, rand):
        cod, titlu, autor = (bucata.strip() for bucata in rand.split(";"))
        return cls(cod, titlu, autor)

    @property
    def disponibila(self):
        return self.imprumutata_de is None

    def taxa(self, zi_curenta):
        """Taxa de întârziere, dacă ar fi returnată în `zi_curenta`."""
        if self.disponibila:
            return 0
        intarziere = zi_curenta - self.zi_imprumut - self.zile_imprumut
        return max(intarziere, 0) * self.taxa_pe_zi


class Biblioteca:
    def __init__(self, nume):
        self.nume = nume
        self.carti = {}   # cod -> Carte

    def adauga(self, carte):
        self.carti[carte.cod] = carte

    def imprumuta(self, cod, membru, zi):
        carte = self.carti[cod]
        if not carte.disponibila:
            raise ValueError(f"„{carte.titlu}” e la {carte.imprumutata_de}.")
        carte.imprumutata_de = membru
        carte.zi_imprumut = zi

    @property
    def disponibile(self):
        return [c.titlu for c in self.carti.values() if c.disponibila]


catalog = """
R01; Ion; Liviu Rebreanu
E01; Maitreyi; Mircea Eliade
C01; Enigma Otiliei; George Călinescu
"""

biblioteca = Biblioteca("Biblioteca Județeană Cluj")
for rand in catalog.strip().splitlines():
    biblioteca.adauga(Carte.din_text(rand))

biblioteca.imprumuta("R01", "Ana Popescu", zi=100)
biblioteca.imprumuta("E01", "Mihai Ionescu", zi=110)
try:
    biblioteca.imprumuta("R01", "Mihai Ionescu", zi=111)
except ValueError as eroare:
    print("Nu se poate:", eroare)

zi_curenta = 120
print(f"\n{biblioteca.nume}, ziua {zi_curenta}:")
for carte in biblioteca.carti.values():
    stare = "pe raft" if carte.disponibila else f"la {carte.imprumutata_de}"
    print(f"  {carte.cod}  {carte.titlu:<16} {stare:<18} taxă: {carte.taxa(zi_curenta):.2f} lei")
print("Disponibile:", ", ".join(biblioteca.disponibile))

Carte.taxa_pe_zi = 1.0   # biblioteca scumpește taxa, pentru toate cărțile
print(f"Taxa pentru „Ion” cu noul tarif: {biblioteca.carti['R01'].taxa(zi_curenta):.2f} lei")
```

```text
Nu se poate: „Ion” e la Ana Popescu.

Biblioteca Județeană Cluj, ziua 120:
  R01  Ion              la Ana Popescu     taxă: 3.00 lei
  E01  Maitreyi         la Mihai Ionescu   taxă: 0.00 lei
  C01  Enigma Otiliei   pe raft            taxă: 0.00 lei
Disponibile: Enigma Otiliei
Taxa pentru „Ion” cu noul tarif: 6.00 lei
```

Observă:
- `Carte.taxa_pe_zi = 1.0` schimbă taxa pentru **toate** cărțile, pentru că e atribut de clasă;
- `disponibila` și `disponibile` sunt property-uri: se citesc fără paranteze și sunt mereu actuale;
- `splitlines()` sparge un text pe mai multe rânduri într-o listă de rânduri, iar `strip()` de dinainte scoate rândurile goale de la margini;
- `Biblioteca.imprumuta` ridică `ValueError`, iar codul de jos decide să afișeze mesajul.

## Greșeli frecvente

### 1. Atribut de clasă „modificat” prin self

```python
class Membru:
    total_membri = 0

    def __init__(self, nume):
        self.nume = nume
        self.total_membri += 1


ana = Membru("Ana Popescu")
mihai = Membru("Mihai Ionescu")
print(Membru.total_membri, ana.total_membri, mihai.total_membri)
```

```text
0 1 1
```

Nicio eroare, dar numărătoarea e greșită. `self.total_membri += 1` înseamnă `self.total_membri = self.total_membri + 1`. Citirea găsește 0 în clasă, dar **atribuirea** creează un atribut nou **în obiect**, care ascunde de acum atributul clasei. Pentru a modifica un atribut de clasă, scrie numele clasei: `Membru.total_membri += 1`.

### 2. Listă ca atribut de clasă

```python
class Membru:
    carti = []   # o singură listă, comună tuturor!

    def __init__(self, nume):
        self.nume = nume


ana = Membru("Ana Popescu")
mihai = Membru("Mihai Ionescu")
ana.carti.append("Ion")
print(mihai.carti)
```

```text
['Ion']
```

Spre deosebire de greșeala 1, aici nu există atribuire: `append()` modifică lista găsită în clasă, care e aceeași pentru toți (aliasing, lecția 12). Mihai „are” cartea Anei. Datele care diferă de la un obiect la altul, mai ales listele și dicționarele, se creează în `__init__`: `self.carti = []`.

### 3. Property apelat cu paranteze

<!-- fisier: carte.py -->
```python
class Carte:
    def __init__(self):
        self.imprumutata_de = None

    @property
    def disponibila(self):
        return self.imprumutata_de is None


ion = Carte()
print(ion.disponibila())
```

```text
Traceback (most recent call last):
  File "carte.py", line 11, in <module>
    print(ion.disponibila())
          ^^^^^^^^^^^^^^^^^
TypeError: 'bool' object is not callable
```

`ion.disponibila` dă deja valoarea `True`, iar `True()` încearcă să „apeleze” un `bool`. Un property se citește fără paranteze.

### 4. Atribuire pe un property fără setter

<!-- fisier: carte.py -->
```python
class Membru:
    def __init__(self, prenume, nume_familie):
        self.prenume = prenume
        self.nume_familie = nume_familie

    @property
    def nume_complet(self):
        return f"{self.prenume} {self.nume_familie}"


ana = Membru("Ana", "Popescu")
ana.nume_complet = "Ana Marin"
```

```text
Traceback (most recent call last):
  File "carte.py", line 12, in <module>
    ana.nume_complet = "Ana Marin"
    ^^^^^^^^^^^^^^^^
AttributeError: property 'nume_complet' of 'Membru' object has no setter
```

Un property fără setter se poate doar citi. Modifică atributele din care e calculat (`ana.nume_familie = "Marin"`) sau adaugă un setter, dacă are sens.

### 5. Setter care se apelează pe el însuși

<!-- fisier: carte.py -->
```python
class Carte:
    @property
    def pagini(self):
        return self.pagini

    @pagini.setter
    def pagini(self, valoare):
        self.pagini = valoare


ion = Carte()
ion.pagini = 480
```

```text
Traceback (most recent call last):
  File "carte.py", line 12, in <module>
    ion.pagini = 480
RecursionError: maximum recursion depth exceeded
```

(Tracebackul real e mai lung, cu un rând de forma `[Previous line repeated 996 more times]`; l-am scurtat.) În setter, `self.pagini = valoare` apelează **din nou** setter-ul, care se apelează din nou, la nesfârșit, până când Python se oprește. Valoarea se păstrează într-un atribut cu **alt nume**, prin convenție cu `_` în față: `self._pagini = valoare` și `return self._pagini`.

## Exercițiu

În `capitole/33-atribute-metode/atribute_metode.py`, scrie clasa `Membru` pentru bibliotecă:

1. atribute de clasă: `limita = 3` și `numar_membri = 0`, care crește doar după ce un membru a fost creat cu succes (pune incrementarea la finalul lui `__init__`, după validarea email-ului);
2. `__init__(self, nume, email)`; email-ul trece printr-un **property cu setter** care îl salvează cu litere mici și ridică `ValueError` dacă nu conține exact un `@`;
3. un `@classmethod` `din_dict(cls, date)` care creează un membru dintr-un dicționar `{"nume": ..., "email": ...}`;
4. un property `poate_imprumuta`, care spune dacă membrul are mai puțin de `limita` cărți (lista `carti` se creează în `__init__`);
5. un `@staticmethod` `email_valid(email)`, folosit de setter, care întoarce `True` sau `False`;
6. creează trei membri dintr-o listă de dicționare (unul cu email greșit, prins cu `try / except`), afișează `Membru.numar_membri` și verifică, prin două obiecte diferite, că listele lor de cărți sunt independente.

## Pe scurt

- Atributele scrise în corpul clasei sunt comune tuturor obiectelor; cele create cu `self.x = ...` sunt ale fiecărui obiect.
- La citire, Python caută întâi în obiect, apoi în clasă; o atribuire prin `self` creează mereu un atribut al obiectului.
- Listele și dicționarele care diferă de la un obiect la altul se creează în `__init__`, nu în corpul clasei.
- `@classmethod` primește clasa (`cls`) și e potrivit pentru constructori alternativi (`din_text`, `din_dict`); `@staticmethod` nu primește nimic special.
- `@property` transformă o metodă într-un atribut calculat, citit fără paranteze; cu `@x.setter` poți verifica valorile la atribuire.
- `_nume` înseamnă, prin convenție, „atribut intern al clasei”.
