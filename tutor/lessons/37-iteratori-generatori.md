## Ce este

Ai folosit `for` pe texte, liste, dicționare, `range()`, `enumerate()`, `zip()` și fișiere. Toate funcționează pe baza aceluiași mecanism, numit **protocolul de iterare**:
- un **iterabil** (în engleză „iterable”) este orice obiect pe care îl poți parcurge cu `for`: o listă, un string, un dicționar, un `range`;
- un **iterator** este obiectul care face parcurgerea propriu-zisă: ține minte unde a ajuns și, la fiecare cerere, dă **următorul** element.

```python
carti = ["Ion", "Enigma Otiliei", "Maitreyi"]
iterator = iter(carti)
print(next(iterator))
print(next(iterator))
print(next(iterator))
```

```text
Ion
Enigma Otiliei
Maitreyi
```

Un **generator** este cel mai simplu mod de a-ți scrie propriul iterator: o funcție care, în loc de `return`, folosește **`yield`** ca să dea valorile una câte una.

```python
def numara_pana_la(n):
    numar = 1
    while numar <= n:
        yield numar
        numar += 1


for x in numara_pana_la(3):
    print(x)
```

```text
1
2
3
```

## De ce contează

Iteratorii și generatoarele îți permit să lucrezi cu **șiruri de date foarte mari sau chiar infinite** fără să le ții pe toate în memorie: un fișier de jurnal de câțiva gigaocteți (GB), toate rândurile dintr-un tabel, numere generate la cerere. Valorile sunt produse **abia când e nevoie de ele** (evaluare „leneșă”, în engleză „lazy evaluation”).

Ai văzut deja efectele acestui mecanism fără să știi de unde vin: la lecția 10, `range(1_000_000_000)` nu ocupa memorie; la lecția 17, un `zip()` parcurs a doua oară era gol. Acum vei înțelege de ce. În Django, un `QuerySet` (lecția 52) folosește aceeași idee: interogarea la baza de date se face abia când începi să parcurgi rezultatele.

## Cum funcționează

### Ce face for, de fapt

Un `for` ca acesta:

```python
for carte in ["Ion", "Maitreyi"]:
    print(carte)
```

```text
Ion
Maitreyi
```

face, pe dedesubt, următorii pași:
1. cere un iterator de la obiect: `iter(lista)`;
2. cere repetat `next(iterator)` și execută blocul cu fiecare valoare;
3. când iteratorul nu mai are valori, el ridică excepția `StopIteration`, iar `for` o prinde și se oprește.

Același lucru scris „de mână”, cu `try / except` (lecția 24):

```python
carti = ["Ion", "Maitreyi"]
iterator = iter(carti)
while True:
    try:
        carte = next(iterator)
    except StopIteration:
        break
    print(carte)
```

```text
Ion
Maitreyi
```

Nu vei scrie niciodată asta în cod real: `for` o face pentru tine. Dar te ajută să înțelegi ce urmează.

### Iterabil sau iterator?

O listă e **iterabilă**, dar nu e un iterator: de fiecare dată când `for` cere `iter(lista)`, primește un iterator **nou**, care pornește de la început. De aceea poți parcurge o listă de câte ori vrei.

Un iterator e iterabil și el (`iter(iterator)` îl întoarce pe el însuși), dar **se consumă**: după ce a dat toate valorile, rămâne gol.

```python
carti = ["Ion", "Maitreyi"]
it = iter(carti)
print(list(it))
print(list(it))
print(list(carti))
print(list(carti))
```

```text
['Ion', 'Maitreyi']
[]
['Ion', 'Maitreyi']
['Ion', 'Maitreyi']
```

Asta explică cele două observații din lecțiile trecute:
- `range()` (lecția 10) e un **iterabil** leneș: nu ține numerele în memorie, dar îți dă un iterator nou la fiecare parcurgere, deci nu se consumă;
- `enumerate()`, `zip()` și `reversed()` (lecția 17) sunt **iteratori**: se consumă la prima parcurgere.

```python
numere = range(3)
print(list(numere), list(numere))
perechi = zip("ab", [1, 2])
print(list(perechi), list(perechi))
print(iter(perechi) is perechi)
```

```text
[0, 1, 2] [0, 1, 2]
[('a', 1), ('b', 2)] []
True
```

### Funcții generator: yield

O funcție care conține `yield` e o **funcție generator**. Când o apelezi, corpul ei **nu rulează încă**: primești un obiect generator, adică un iterator. Codul rulează abia când îi ceri valori, și doar până la următorul `yield`, unde se oprește și „îngheață”, păstrându-și toate variabilele locale.

```python
def pasi():
    print("  [pornesc]")
    yield "primul"
    print("  [continui]")
    yield "al doilea"
    print("  [termin]")


gen = pasi()
print("generatorul a fost creat")
print(next(gen))
print(next(gen))
for rest in gen:
    print(rest)
print("gata")
```

```text
generatorul a fost creat
  [pornesc]
primul
  [continui]
al doilea
  [termin]
gata
```

Urmărește ordinea:
- `pasi()` nu a afișat nimic: doar a creat generatorul;
- primul `next()` a rulat codul până la primul `yield` și a întors `"primul"`;
- al doilea `next()` a continuat **exact de unde rămăsese**, până la al doilea `yield`;
- `for` a cerut următoarea valoare: codul a rulat până la final, a afișat `[termin]`, iar ieșirea din funcție a însemnat `StopIteration`, deci `for` s-a oprit fără nicio iterație.

Comparat cu o funcție obișnuită: `return` dă **o valoare și termină** funcția; `yield` dă **o valoare și pune funcția pe pauză**.

### Un generator în loc de o listă construită

Tiparul din lecția 12 („pornesc de la o listă goală și adaug cu `append`”) se poate scrie aproape mereu și ca generator:

```python
def preturi_cu_tva(preturi):
    rezultat = []
    for pret in preturi:
        rezultat.append(round(pret * 1.21, 2))
    return rezultat


def preturi_cu_tva_gen(preturi):
    for pret in preturi:
        yield round(pret * 1.21, 2)


print(preturi_cu_tva([10, 20]))
print(list(preturi_cu_tva_gen([10, 20])))
```

```text
[12.1, 24.2]
[12.1, 24.2]
```

Rezultatul e același. Diferența: varianta cu listă calculează **tot** de la început și ține totul în memorie; varianta cu `yield` calculează câte o valoare, exact când e cerută. Pentru câteva elemente nu contează. Pentru un milion de rânduri dintr-un fișier, contează enorm.

### Expresii generator

La lecția 16 ai văzut că un comprehension între paranteze rotunde nu dă un tuplu, ci o **expresie generator**. E scrierea scurtă a unei funcții generator simple:

```python
preturi = [4.5, 8.99, 32.0]
cu_tva = (round(p * 1.21, 2) for p in preturi)
print(next(cu_tva))
print(list(cu_tva))
print(sum(p * 2 for p in preturi))
```

```text
5.45
[10.88, 38.72]
90.98
```

Observă că `list(cu_tva)` a dat doar ultimele două valori: prima fusese deja consumată de `next()`. Când o expresie generator e singurul argument al unei funcții, parantezele ei pot lipsi, ca la `sum(...)`.

### Generatoare infinite

Un generator poate produce valori **la nesfârșit**: nu e o problemă, pentru că valorile se calculează doar când le ceri. Cel care parcurge trebuie să se oprească singur, de exemplu cu `break` (lecția 11) sau cu `itertools.islice()`, care ia doar primele `n` valori:

```python
from itertools import islice


def numere_de_inventar(prefix):
    numar = 1
    while True:
        yield f"{prefix}-{numar:04}"
        numar += 1


coduri = numere_de_inventar("BIB")
print(next(coduri), next(coduri))
print(list(islice(coduri, 3)))
```

```text
BIB-0001 BIB-0002
['BIB-0003', 'BIB-0004', 'BIB-0005']
```

Generatorul își amintește unde a rămas: după primele două coduri, `islice` a continuat de la 3.

### yield from: delegarea către alt iterabil

Când un generator vrea să dea toate valorile unui alt iterabil, în loc de o buclă `for ... yield` poate scrie `yield from`:

```python
def toate_cartile(rafturi):
    for raft in rafturi:
        yield from raft


rafturi = [["Ion", "Baltagul"], ["Maitreyi"], ["Enigma Otiliei"]]
print(list(toate_cartile(rafturi)))
```

```text
['Ion', 'Baltagul', 'Maitreyi', 'Enigma Otiliei']
```

### Fișierele sunt iteratori

Un fișier deschis cu `open()` (lecția 27) e și el un iterator: `for linie in fisier` citește **câte un rând**, nu tot fișierul deodată. Combinat cu generatoare, poți prelucra fișiere oricât de mari, pas cu pas, ca pe o „bandă rulantă” (în engleză „pipeline”):

```python
with open("jurnal.txt", "w", encoding="utf-8") as f:
    f.write("INFO pornire\nEROARE disc plin\nINFO salvare\nEROARE rețea\n")


def linii(cale):
    with open(cale, encoding="utf-8") as fisier:
        for linie in fisier:
            yield linie.rstrip("\n")


def doar_erori(randuri):
    for rand in randuri:
        if rand.startswith("EROARE"):
            yield rand


for eroare in doar_erori(linii("jurnal.txt")):
    print(eroare)
```

```text
EROARE disc plin
EROARE rețea
```

Fiecare etapă primește un iterator și dă alt iterator. În orice moment, în memorie se află **un singur rând**, indiferent cât de mare e fișierul.

### Ce se întâmplă „pe dedesubt”: generatorul își păstrează starea

Un obiect generator ține minte trei lucruri: codul funcției, valorile tuturor variabilelor locale și locul exact unde s-a oprit. De aceea poate continua de unde a rămas. Diferența de memorie față de o listă se poate măsura cu `sys.getsizeof()` (dimensiunea obiectului, în octeți):

```python
import sys

lista = [x * x for x in range(1_000_000)]
generator = (x * x for x in range(1_000_000))
print(sys.getsizeof(lista) > 8_000_000)
print(sys.getsizeof(generator) < 500)
print(sum(generator) == sum(lista))
```

```text
True
True
True
```

Lista cu un milion de pătrate ocupă peste 8 MB doar pentru referințele către numere. Generatorul ocupă câteva sute de octeți, oricât de multe valori ar produce. Rezultatul final (suma) e același.

Ca observație: poți scrie un iterator și ca o clasă cu metodele speciale `__iter__()` și `__next__()` (metodele speciale sunt la lecția 35). Generatoarele fac exact asta automat, cu mult mai puțin cod, de aceea în practică le folosești aproape mereu pe ele.

Tot cu un generator faci și o clasă a ta să poată fi parcursă cu `for`, cum am promis la lecția 35: scrii `__iter__` ca funcție generator.

```python
class Raft:
    def __init__(self, nume):
        self.nume = nume
        self.titluri = []

    def __iter__(self):
        yield from self.titluri


raft = Raft("Literatură română")
raft.titluri += ["Ion", "Maitreyi"]
for titlu in raft:
    print(titlu)
print(sorted(raft))
```

```text
Ion
Maitreyi
['Ion', 'Maitreyi']
```

`for titlu in raft` apelează `iter(raft)`, deci `raft.__iter__()`, care întoarce un generator nou la fiecare parcurgere. Așa, raftul se poate parcurge de câte ori vrei, ca o listă, și merge cu tot ce primește un iterabil (`sorted`, `list`, `sum`).

## Exemplu complet

Biblioteca din modulul 7, acum cu generatoare: catalogul vine dintr-un fișier CSV cu `;` (lecția 28), citit rând cu rând cu `csv.reader`, iar căutarea e o „bandă rulantă” de generatoare.

<!-- fisier: biblioteca.py -->
```python
import csv
from dataclasses import dataclass
from itertools import islice


@dataclass
class Carte:
    titlu: str
    autor: str
    an: int
    disponibila: bool


def scrie_catalog(cale):
    randuri = [
        "Ion;Liviu Rebreanu;1920;da",
        "Enigma Otiliei;George Călinescu;1938;nu",
        "Maitreyi;Mircea Eliade;1933;da",
        "Baltagul;Mihail Sadoveanu;1930;da",
        "Pădurea spânzuraților;Liviu Rebreanu;1922;nu",
        "Moromeții;Marin Preda;1955;da",
    ]
    with open(cale, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(randuri) + "\n")


def citeste_carti(cale):
    """Dă câte o Carte pentru fiecare rând din fișier, fără să încarce tot fișierul."""
    with open(cale, encoding="utf-8", newline="") as fisier:
        for titlu, autor, an, disponibila in csv.reader(fisier, delimiter=";"):
            yield Carte(titlu, autor, int(an), disponibila == "da")


def disponibile(carti):
    for carte in carti:
        if carte.disponibila:
            yield carte


def din_perioada(carti, de_la, pana_la):
    return (c for c in carti if de_la <= c.an <= pana_la)


scrie_catalog("catalog.csv")

print("Disponibile, apărute între 1920 și 1940:")
for carte in din_perioada(disponibile(citeste_carti("catalog.csv")), 1920, 1940):
    print(f"  {carte.titlu} ({carte.autor}, {carte.an})")

print("\nPrimele două cărți din catalog:")
for carte in islice(citeste_carti("catalog.csv"), 2):
    print(f"  {carte.titlu}")

autori = {c.autor for c in citeste_carti("catalog.csv")}
print(f"\nAutori distincți: {len(autori)}")
cea_mai_noua = max(citeste_carti("catalog.csv"), key=lambda c: c.an)
print(f"Cea mai nouă carte: {cea_mai_noua.titlu} ({cea_mai_noua.an})")
```

```text
Disponibile, apărute între 1920 și 1940:
  Ion (Liviu Rebreanu, 1920)
  Maitreyi (Mircea Eliade, 1933)
  Baltagul (Mihail Sadoveanu, 1930)

Primele două cărți din catalog:
  Ion
  Enigma Otiliei

Autori distincți: 5
Cea mai nouă carte: Moromeții (1955)
```

Observă:
- `csv.reader` e și el un iterator: dă câte un rând, ca listă de câmpuri, abia când îl cere `for`;
- fiecare căutare apelează din nou `citeste_carti(...)`, pentru că un generator se consumă; funcția generator e „rețeta”, iar fiecare apel creează un generator nou;
- `islice(..., 2)` citește doar primele două rânduri din fișier și se oprește: restul nu e citit deloc;
- `din_perioada` întoarce o expresie generator, iar `disponibile` folosește `yield`: ambele variante produc un iterator și se pot combina liber.

## Greșeli frecvente

### 1. next() pe un iterator epuizat

<!-- fisier: gen.py -->
```python
def doua_carti():
    yield "Ion"
    yield "Maitreyi"


gen = doua_carti()
print(next(gen))
print(next(gen))
print(next(gen))
```

```text
Ion
Maitreyi
Traceback (most recent call last):
  File "gen.py", line 9, in <module>
    print(next(gen))
          ^^^^^^^^^
StopIteration
```

Când apelezi `next()` de mână, trebuie să tratezi finalul: cu `try / except StopIteration` sau cu o valoare implicită, `next(gen, None)`, care întoarce `None` în loc să dea eroare. În cele mai multe cazuri, un `for` e soluția mai simplă.

### 2. Parcurgerea aceluiași generator de două ori

```python
def disponibile(carti):
    for titlu, e_libera in carti:
        if e_libera:
            yield titlu


carti = [("Ion", True), ("Baltagul", False), ("Maitreyi", True)]
libere = disponibile(carti)
print("Număr:", len(list(libere)))
print("Titluri:", list(libere))
```

```text
Număr: 2
Titluri: []
```

Prima numărare a consumat generatorul. Ai două soluții: transformi rezultatul o singură dată într-o listă (`libere = list(disponibile(carti))`) și o folosești de câte ori vrei, sau apelezi din nou funcția generator pentru fiecare parcurgere.

### 3. len() sau indexare pe un generator

<!-- fisier: gen.py -->
```python
patrate = (x * x for x in range(5))
print(len(patrate))
```

```text
Traceback (most recent call last):
  File "gen.py", line 2, in <module>
    print(len(patrate))
          ^^^^^^^^^^^^
TypeError: object of type 'generator' has no len()
```

Un generator nu știe câte valori va produce până nu le produce. Din același motiv, nici `patrate[0]` nu funcționează (`TypeError: 'generator' object is not subscriptable`). Dacă ai nevoie de lungime sau de indexare, folosește o listă: `patrate = [x * x for x in range(5)]`.

### 4. Așteptarea ca apelul unei funcții generator să ruleze codul

```python
def salveaza_carti(titluri):
    for titlu in titluri:
        print(f"Salvez {titlu}...")
        yield titlu


salveaza_carti(["Ion", "Maitreyi"])
print("Gata?")
```

```text
Gata?
```

Nu s-a salvat nimic: apelul a creat doar generatorul, iar codul din corp nu a rulat, pentru că nimeni nu a cerut valori. Dacă o funcție trebuie să **facă** ceva (să salveze, să afișeze, să modifice), scrie-o ca funcție obișnuită, fără `yield`. Generatoarele sunt pentru a **produce** valori pe care altcineva le parcurge.

### 5. next() pe o listă

<!-- fisier: gen.py -->
```python
carti = ["Ion", "Maitreyi"]
print(next(carti))
```

```text
Traceback (most recent call last):
  File "gen.py", line 2, in <module>
    print(next(carti))
          ^^^^^^^^^^^
TypeError: 'list' object is not an iterator
```

O listă e iterabilă, dar nu e un iterator (vezi „Iterabil sau iterator?”). Cere întâi un iterator: `it = iter(carti)`, apoi `next(it)`.

## Exercițiu

În `capitole/37-iteratori-generatori/iteratori_generatori.py`:

1. scrie o funcție generator `imprumuturi_restante(imprumuturi, zi_curenta)` care primește o listă de tupluri `(titlu, cititor, zi_returnare)` (zilele sunt numere întregi, de exemplu `12`) și dă, unul câte unul, tuplurile `(titlu, cititor, zile_intarziere)` pentru împrumuturile cu `zi_returnare < zi_curenta`, unde `zile_intarziere = zi_curenta - zi_returnare`;
2. scrie o funcție generator infinită `zile_lucratoare(start)` care dă numerele zilelor începând de la `start`, sărind peste fiecare a 6-a și a 7-a zi din săptămână (consideră că ziua 1 e luni, deci 6, 7, 13, 14, 20, 21 ... sunt weekend); afișează primele 10 zile lucrătoare de la ziua 1 cu `islice`;
3. scrie în cod un fișier `imprumuturi.txt` cu cel puțin 6 rânduri de forma `titlu;cititor;zi_returnare`, apoi o funcție generator care îl citește rând cu rând și dă tupluri; leagă-o de funcția de la punctul 1 și afișează restanțele pentru ziua 15;
4. calculează totalul penalităților (2 lei pe zi de întârziere) cu `sum()` și o expresie generator, fără să construiești nicio listă;
5. afișează, cu `next(..., None)`, prima restanță găsită, sau mesajul „Nicio restanță” dacă nu există.

## Pe scurt

- Un **iterabil** se poate parcurge cu `for`; un **iterator** dă valori una câte una cu `next()` și se consumă. `for` folosește `iter()` și `next()` până la `StopIteration`.
- `range()` e iterabil (se poate parcurge oricând din nou); `zip`, `enumerate`, generatoarele și fișierele sunt iteratori (se consumă).
- O funcție cu `yield` e o funcție generator: apelul ei creează un generator, iar corpul rulează abia când cineva cere valori, pauză cu pauză.
- `(expresie for x in ...)` e o expresie generator, scrierea scurtă a unei funcții generator simple.
- Generatoarele produc valori la cerere: merg pe date foarte mari sau infinite, iar `islice()`, `break` și `next(gen, implicit)` te ajută să te oprești.
- Un generator nu are `len()` și indexare; dacă ai nevoie de ele sau de mai multe parcurgeri, transformă-l în listă.
