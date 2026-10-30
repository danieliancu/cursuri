## Ce este

**Moștenirea** (în engleză „inheritance”) îți permite să creezi o clasă nouă pornind de la una existentă. Clasa nouă, numită **clasă derivată** (sau „subclasă”, „clasă copil”), primește automat toate atributele și metodele clasei de bază (numită și „superclasă” sau „clasă părinte”). Apoi poate adăuga altele noi sau le poate schimba pe cele moștenite.

```python
class Material:
    def __init__(self, titlu, an):
        self.titlu = titlu
        self.an = an

    def descriere(self):
        return f"{self.titlu} ({self.an})"


class Revista(Material):
    pass


natgeo = Revista("National Geographic nr. 10", 2026)
print(natgeo.descriere())
print(isinstance(natgeo, Material))
```

```text
National Geographic nr. 10 (2026)
True
```

`class Revista(Material):` se citește „`Revista` este un fel de `Material`”. Deși `Revista` e goală, are `__init__` și `descriere()`, moștenite de la `Material`.

## De ce contează

O bibliotecă nu are doar cărți: are reviste, ebook-uri, audiobook-uri. Toate au un titlu și un an, toate se pot împrumuta, dar fiecare are și particularitățile ei: o carte are autor și pagini, o revistă se împrumută doar 7 zile, un ebook nu are exemplare fizice. Fără moștenire, ai copia același cod în patru clase, iar o corectură ar trebui făcută în patru locuri.

Cu moștenirea, partea comună stă **o singură dată**, în clasa de bază, iar fiecare clasă derivată scrie doar ce o deosebește.

Și în Django moștenești tot timpul: fiecare model e `class Articol(models.Model)` (lecția 50), fiecare formular `class ContactForm(forms.Form)` (lecția 55), iar un view bazat pe clasă moștenește tot comportamentul de la `ListView` sau `DetailView` (lecția 58). Tu scrii doar diferențele.

## Cum funcționează

### Adăugarea de atribute și metode noi

O clasă derivată poate avea metode pe care clasa de bază nu le are:

```python
class Material:
    def __init__(self, titlu, an):
        self.titlu = titlu
        self.an = an


class Revista(Material):
    def este_recenta(self, an_curent):
        return an_curent - self.an <= 1


natgeo = Revista("National Geographic nr. 10", 2026)
print(natgeo.este_recenta(2026))
```

```text
True
```

Metoda nouă folosește `self.an`, un atribut creat de `__init__`-ul moștenit.

### super().__init__(): extinderea constructorului

Când clasa derivată are nevoie de atribute în plus, își scrie propriul `__init__`. Acesta **înlocuiește** `__init__`-ul clasei de bază, deci trebuie să-l apeleze explicit pe cel vechi, cu `super()`, ca atributele comune să fie create în continuare:

```python
class Material:
    def __init__(self, titlu, an):
        self.titlu = titlu
        self.an = an
        self.imprumutat_de = None


class Carte(Material):
    def __init__(self, titlu, an, autor, pagini):
        super().__init__(titlu, an)   # titlu, an, imprumutat_de
        self.autor = autor
        self.pagini = pagini


ion = Carte("Ion", 1920, "Liviu Rebreanu", 480)
print(ion.titlu, ion.autor, ion.pagini, ion.imprumutat_de)
```

```text
Ion Liviu Rebreanu 480 None
```

`super()` înseamnă „clasa de bază, pentru obiectul ăsta”. `super().__init__(titlu, an)` rulează `Material.__init__` pe același obiect, apoi `Carte.__init__` adaugă ce are în plus. Regula: în `__init__`-ul unei clase derivate, **primul** lucru e de obicei apelul `super().__init__(...)`.

### Suprascrierea metodelor

O clasă derivată poate redefini o metodă moștenită, adică o poate **suprascrie** (în engleză „override”). Python o va folosi pe cea mai apropiată de obiect:

```python
class Material:
    def __init__(self, titlu, an):
        self.titlu = titlu
        self.an = an

    def zile_imprumut(self):
        return 14

    def descriere(self):
        return f"{self.titlu} ({self.an})"


class Revista(Material):
    def zile_imprumut(self):
        return 7


class Carte(Material):
    def __init__(self, titlu, an, autor):
        super().__init__(titlu, an)
        self.autor = autor

    def descriere(self):
        return f"{super().descriere()}, de {self.autor}"


materiale = [
    Carte("Ion", 1920, "Liviu Rebreanu"),
    Revista("Dilema veche nr. 1050", 2026),
]
for m in materiale:
    print(f"{m.descriere():<35} {m.zile_imprumut()} zile")
```

```text
Ion (1920), de Liviu Rebreanu       14 zile
Dilema veche nr. 1050 (2026)        7 zile
```

Două feluri de suprascriere:
- `Revista.zile_imprumut` **înlocuiește** complet metoda de bază;
- `Carte.descriere` o **extinde**: apelează varianta de bază cu `super().descriere()` și adaugă autorul. Așa nu repeți formatul `titlu (an)`.

Cel mai important lucru din exemplu: bucla `for` apelează `m.descriere()` și `m.zile_imprumut()` **fără să știe** dacă `m` e carte sau revistă. Fiecare obiect răspunde în felul lui. Proprietatea asta se numește **polimorfism** și e principalul câștig al moștenirii: codul care folosește obiectele rămâne simplu, oricâte tipuri noi de materiale ai adăuga.

### isinstance() și issubclass()

Ai folosit `isinstance()` și `issubclass()` la lecția 25; acum vezi cum se comportă cu clasele tale derivate.

`isinstance(obiect, Clasa)` întreabă dacă obiectul e de acea clasă **sau** de o clasă derivată din ea:

```python
class Material:
    pass


class Carte(Material):
    pass


class Ebook(Carte):
    pass


carte_digitala = Ebook()
print(isinstance(carte_digitala, Ebook))
print(isinstance(carte_digitala, Carte))
print(isinstance(carte_digitala, Material))
print(type(carte_digitala) == Carte)
print(issubclass(Ebook, Material))
```

```text
True
True
True
False
True
```

Un ebook **este** o carte și **este** un material. `type(x) == Clasa` verifică doar clasa exactă, deci ignoră moștenirea. De aceea, aproape întotdeauna, `isinstance` e alegerea corectă.

Totuși, dacă te trezești scriind des `if isinstance(m, Revista): ... elif isinstance(m, Carte): ...`, e un semn că acel comportament ar trebui să fie o metodă suprascrisă în fiecare clasă (ca `zile_imprumut` de mai sus).

### Moștenire și excepții

Ai folosit deja moștenirea la lecția 25: o excepție proprie e o clasă derivată din `Exception`. Ierarhiile de excepții sunt foarte utile, pentru că un `except` pe clasa de bază prinde și toate clasele derivate:

```python
class EroareBiblioteca(Exception):
    """Orice problemă din bibliotecă."""


class CarteIndisponibila(EroareBiblioteca):
    pass


class LimitaDepasita(EroareBiblioteca):
    pass


erori = [CarteIndisponibila("„Ion” e împrumutată."), LimitaDepasita("Ana are deja 3 cărți.")]
for eroare in erori:
    try:
        raise eroare
    except EroareBiblioteca as e:
        print(f"{type(e).__name__}: {e}")
```

```text
CarteIndisponibila: „Ion” e împrumutată.
LimitaDepasita: Ana are deja 3 cărți.
```

Codul care apelează biblioteca poate prinde orice problemă a ei cu `except EroareBiblioteca`, sau doar una anume, cu `except LimitaDepasita`. Exact așa sunt organizate și excepțiile din Python: `ValueError`, `TypeError` și `KeyError` derivă toate din `Exception`.

### Compoziție vs moștenire

Moștenirea exprimă relația „**este un**”: un ebook **este o** carte. Multe relații sunt însă de tipul „**are un**”: o bibliotecă **are** cărți, un împrumut **are** un membru și o carte. Pentru acestea, obiectul păstrează celelalte obiecte în atributele lui. Asta se numește **compoziție**:

```python
class Membru:
    def __init__(self, nume):
        self.nume = nume


class Carte:
    def __init__(self, titlu):
        self.titlu = titlu


class Imprumut:
    def __init__(self, membru, carte, zile):
        self.membru = membru   # Imprumut ARE un Membru
        self.carte = carte     # ... și o Carte
        self.zile = zile

    def descriere(self):
        return f"{self.membru.nume} are „{self.carte.titlu}” pentru {self.zile} zile"


imprumut = Imprumut(Membru("Ana Popescu"), Carte("Ion"), 14)
print(imprumut.descriere())
```

```text
Ana Popescu are „Ion” pentru 14 zile
```

Ar fi greșit ca `Imprumut` să moștenească din `Membru`, pentru că un împrumut nu **este** un membru. Regula practică: folosește moștenirea doar când propoziția „X este un fel de Y” e adevărată. În rest, folosește compoziția. În practică, compoziția e mult mai des întâlnită.

### Ce se întâmplă „pe dedesubt”: ordinea de căutare

Când scrii `obiect.metoda()`, Python caută metoda întâi în clasa obiectului, apoi în clasa ei de bază, apoi în baza bazei și așa mai departe, până la `object`, clasa de bază a tuturor claselor din Python. Ordinea se numește **MRO** („method resolution order”) și o poți vedea:

```python
class Material:
    pass


class Carte(Material):
    pass


class Ebook(Carte):
    pass


print([clasa.__name__ for clasa in Ebook.__mro__])
```

```text
['Ebook', 'Carte', 'Material', 'object']
```

Prima clasă din listă care are metoda câștigă. De aceea o metodă suprascrisă în `Ebook` o „ascunde” pe cea din `Carte`. `super()` înseamnă „continuă căutarea de la clasa următoare din listă”.

Python permite și moștenirea din **mai multe** clase deodată (`class A(B, C):`). Django o folosește pentru „mixin-uri” (lecția 58). Pentru clasele tale, la început, rămâi la o singură clasă de bază.

## Exemplu complet

Biblioteca, cu moștenire: materiale de mai multe feluri, membri de mai multe feluri și o singură funcție de împrumut care merge pentru toate.

<!-- fisier: biblioteca.py -->
```python
class EroareBiblioteca(Exception):
    pass


class Material:
    zile = 14

    def __init__(self, titlu, an):
        self.titlu = titlu
        self.an = an
        self.imprumutat_de = None

    def descriere(self):
        return f"{self.titlu} ({self.an})"

    def se_poate_imprumuta(self):
        return self.imprumutat_de is None


class Carte(Material):
    def __init__(self, titlu, an, autor):
        super().__init__(titlu, an)
        self.autor = autor

    def descriere(self):
        return f"{super().descriere()}, {self.autor}"


class Revista(Material):
    zile = 7


class Ebook(Carte):
    zile = 10

    def se_poate_imprumuta(self):
        return True   # copii digitale nelimitate


class Membru:
    limita = 3

    def __init__(self, nume):
        self.nume = nume
        self.materiale = []


class MembruStudent(Membru):
    limita = 5


def imprumuta(membru, material):
    if len(membru.materiale) >= membru.limita:
        raise EroareBiblioteca(f"{membru.nume} a atins limita de {membru.limita}.")
    if not material.se_poate_imprumuta():
        raise EroareBiblioteca(f"„{material.titlu}” e la {material.imprumutat_de.nume}.")
    if not isinstance(material, Ebook):
        material.imprumutat_de = membru
    membru.materiale.append(material)
    print(f"{membru.nume}: {material.descriere()} - {material.zile} zile")


ion = Carte("Ion", 1920, "Liviu Rebreanu")
dilema = Revista("Dilema veche nr. 1050", 2026)
ebook = Ebook("Maitreyi", 1933, "Mircea Eliade")

ana = MembruStudent("Ana Popescu")
mihai = Membru("Mihai Ionescu")

for membru, material in [(ana, ion), (mihai, ion), (mihai, dilema), (ana, ebook), (mihai, ebook)]:
    try:
        imprumuta(membru, material)
    except EroareBiblioteca as eroare:
        print("Refuzat:", eroare)

print()
for membru in (ana, mihai):
    tip = "student" if isinstance(membru, MembruStudent) else "standard"
    print(f"{membru.nume} ({tip}, limită {membru.limita}): {len(membru.materiale)} materiale")
```

```text
Ana Popescu: Ion (1920), Liviu Rebreanu - 14 zile
Refuzat: „Ion” e la Ana Popescu.
Mihai Ionescu: Dilema veche nr. 1050 (2026) - 7 zile
Ana Popescu: Maitreyi (1933), Mircea Eliade - 10 zile
Mihai Ionescu: Maitreyi (1933), Mircea Eliade - 10 zile

Ana Popescu (student, limită 5): 2 materiale
Mihai Ionescu (standard, limită 3): 2 materiale
```

Observă:
- `Ebook` moștenește `descriere()` de la `Carte`, care la rândul ei extinde varianta din `Material`;
- atributele de clasă (`zile`, `limita`) pot fi și ele suprascrise, fără nicio metodă;
- funcția `imprumuta()` nu are nevoie de câte un `if` pentru fiecare tip de material, pentru că fiecare obiect știe singur dacă se poate împrumuta și pentru câte zile. Singurul `isinstance` e pentru o regulă care chiar ține de tip (ebook-ul nu ajunge fizic la nimeni);
- `material.imprumutat_de.nume`: atributul ține un obiect `Membru` întreg (compoziție), nu doar un nume.

## Greșeli frecvente

### 1. Lipsește super().__init__()

<!-- fisier: mostenire.py -->
```python
class Material:
    def __init__(self, titlu):
        self.titlu = titlu


class Carte(Material):
    def __init__(self, titlu, autor):
        self.autor = autor


ion = Carte("Ion", "Liviu Rebreanu")
print(ion.titlu)
```

```text
Traceback (most recent call last):
  File "mostenire.py", line 12, in <module>
    print(ion.titlu)
          ^^^^^^^^^
AttributeError: 'Carte' object has no attribute 'titlu'
```

`Carte.__init__` a înlocuit `Material.__init__`, iar acesta nu a mai rulat, deci `titlu` nu a fost creat niciodată. Adaugă `super().__init__(titlu)` la începutul lui `Carte.__init__`.

### 2. Argumente greșite la super().__init__()

<!-- fisier: mostenire.py -->
```python
class Material:
    def __init__(self, titlu, an):
        self.titlu = titlu
        self.an = an


class Carte(Material):
    def __init__(self, titlu, an, autor):
        super().__init__(titlu)
        self.autor = autor


ion = Carte("Ion", 1920, "Liviu Rebreanu")
```

```text
Traceback (most recent call last):
  File "mostenire.py", line 13, in <module>
    ion = Carte("Ion", 1920, "Liviu Rebreanu")
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "mostenire.py", line 9, in __init__
    super().__init__(titlu)
TypeError: Material.__init__() missing 1 required positional argument: 'an'
```

`super().__init__(...)` primește argumentele cerute de `__init__`-ul clasei de **bază**. Tracebackul arată ambele niveluri: crearea cărții și apelul lui `super()`. Uită-te la ultimul rând ca să vezi care `__init__` s-a plâns.

### 3. Metodă „suprascrisă” cu un nume ușor diferit

```python
class Material:
    def zile_imprumut(self):
        return 14


class Revista(Material):
    def zile_imprumuturi(self):
        return 7


print(Revista().zile_imprumut())
```

```text
14
```

Nicio eroare, dar revista primește 14 zile: `zile_imprumuturi` e o metodă nouă, iar `zile_imprumut` a rămas cea moștenită. O suprascriere funcționează doar dacă numele e **identic**. Când un comportament „nu se schimbă” în clasa derivată, verifică întâi numele metodei.

### 4. Apelul metodei de bază fără super()

<!-- fisier: mostenire.py -->
```python
class Material:
    def __init__(self, titlu):
        self.titlu = titlu

    def descriere(self):
        return self.titlu


class Carte(Material):
    def descriere(self):
        return self.descriere() + " (carte)"


print(Carte("Ion").descriere())
```

```text
Traceback (most recent call last):
  File "mostenire.py", line 14, in <module>
    print(Carte("Ion").descriere())
          ^^^^^^^^^^^^^^^^^^^^^^^^
RecursionError: maximum recursion depth exceeded
```

(Traceback scurtat.) `self.descriere()` caută metoda începând cu clasa obiectului, deci găsește tot `Carte.descriere`, care se apelează la nesfârșit. Ca să ajungi la varianta din clasa de bază, scrie `super().descriere()`.

### 5. Moștenire unde trebuia compoziție

```python
class Membru:
    def __init__(self, nume):
        self.nume = nume


class Imprumut(Membru):   # un împrumut „este un” membru?
    def __init__(self, nume, titlu):
        super().__init__(nume)
        self.titlu = titlu


imprumut = Imprumut("Ana Popescu", "Ion")
print(isinstance(imprumut, Membru))
```

```text
True
```

Codul merge, dar modelul e greșit: Python îți spune acum că un împrumut **este** un membru, deci un împrumut ar putea fi trimis oriunde se așteaptă un membru, inclusiv ca membru al altui împrumut. Și ce faci când un membru are două împrumuturi? Folosește compoziția: `Imprumut` **are** un `Membru` (`self.membru = membru`), ca în secțiunea „Compoziție vs moștenire”.

## Exercițiu

În `capitole/34-mostenire/mostenire.py`, extinde biblioteca:

1. clasa de bază `Material(titlu, an)` cu atributul de clasă `zile = 14`, metoda `descriere()` și metoda `taxa(zile_intarziere)`, care întoarce `zile_intarziere * 0.5`;
2. `Carte(Material)` adaugă `autor` (cu `super().__init__`) și extinde `descriere()` cu autorul;
3. `Revista(Material)` are `zile = 7` și suprascrie `taxa()`: 1 leu pe zi;
4. `Audiobook(Carte)` adaugă `durata_minute` și extinde `descriere()` cu durata în ore și minute (`divmod`, lecția 13);
5. o ierarhie de excepții: `EroareBiblioteca(Exception)` și, derivată din ea, `MaterialInexistent`;
6. o listă cu cel puțin câte un obiect din fiecare clasă; afișează, pentru fiecare, descrierea, numărul de zile de împrumut și taxa pentru 3 zile de întârziere, **fără niciun `isinstance` în buclă**;
7. o funcție `cauta(materiale, titlu)` care întoarce materialul cu acel titlu sau ridică `MaterialInexistent`; apeleaz-o cu un titlu care nu există și prinde eroarea cu `except EroareBiblioteca`.

## Pe scurt

- `class Derivata(Baza):` primește automat toate atributele și metodele clasei de bază.
- Un `__init__` propriu înlocuiește `__init__`-ul de bază; apelează-l cu `super().__init__(...)`.
- O metodă cu același nume suprascrie metoda moștenită; `super().metoda()` apelează varianta de bază.
- Polimorfism: același apel (`m.descriere()`) face lucrul potrivit pentru fiecare tip de obiect.
- `isinstance(obiect, Clasa)` ține cont de moștenire; `type(obiect) == Clasa`, nu.
- Moștenire pentru „este un”, compoziție (obiecte în atribute) pentru „are un”; compoziția e mai des potrivită.
