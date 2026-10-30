## Ce este

Python are câteva funcții care fac buclele mai scurte și mai clare. Le vei folosi aproape în fiecare program:
- **`enumerate()`** dă fiecare element împreună cu poziția lui;
- **`zip()`** parcurge mai multe secvențe în paralel;
- **`reversed()`** parcurge o secvență de la coadă;
- **`sum()`, `min()`, `max()`, `any()`, `all()`** reduc o colecție la o singură valoare;
- **`sorted(..., key=...)`** sortează după un criteriu ales de tine.

```python
elevi = ["Ana", "Mihai", "Ioana"]
note = [9, 7, 10]
for pozitie, (nume, nota) in enumerate(zip(elevi, note), start=1):
    print(f"{pozitie}. {nume}: {nota}")
print("Media:", sum(note) / len(note))
```

```text
1. Ana: 9
2. Mihai: 7
3. Ioana: 10
Media: 8.666666666666666
```

`enumerate(zip(...))` dă perechi de forma `(poziție, (nume, nota))`. Parantezele din `for` despachetează și tuplul interior, deci fiecare valoare primește direct numele ei.

## De ce contează

În lecțiile trecute ai scris de mâna ta lucruri pe care Python le are deja: `range(len(lista))` ca să ai și poziția (lecția 12), acumulatori pentru sumă și pentru maxim (lecția 10), două liste parcurse cu același index. Funcțiile din lecția asta fac același lucru într-un rând, fără variabile auxiliare și fără greșeli „off-by-one”.

Sunt și o parte din „stilul Python”: cod care spune **ce** vrei („suma notelor”, „cel mai scump produs”), nu **cum** se calculează pas cu pas.

## Cum funcționează

### enumerate(): element și poziție

```python
cumparaturi = ["pâine", "lapte", "ouă"]
for i, produs in enumerate(cumparaturi):
    print(i, produs)
for nr, produs in enumerate(cumparaturi, start=1):
    print(f"{nr}. {produs}")
```

```text
0 pâine
1 lapte
2 ouă
1. pâine
2. lapte
3. ouă
```

`enumerate()` produce perechi `(poziție, element)`, pe care le despachetezi în `for` (lecția 13). Cu `start=1` numerotarea începe de la 1, ca pentru oameni. Compară cu varianta din exemplul complet al lecției 12, `for pozitie in range(len(cumparaturi))`: aici nu mai ai nevoie de `cumparaturi[pozitie]`.

### zip(): mai multe secvențe în paralel

```python
produse = ["pâine", "lapte", "cafea"]
preturi = [4.5, 8.99, 32.0]
cantitati = [2, 1, 1]

for produs, pret, cant in zip(produse, preturi, cantitati):
    print(f"{produs:<6} {cant} x {pret:.2f}")

preturi_dupa_produs = dict(zip(produse, preturi))
print(preturi_dupa_produs)
```

```text
pâine  2 x 4.50
lapte  1 x 8.99
cafea  1 x 32.00
{'pâine': 4.5, 'lapte': 8.99, 'cafea': 32.0}
```

`zip()` ia câte un element din fiecare secvență și le grupează în tupluri: întâi primele elemente, apoi al doilea și așa mai departe. Ca un fermoar („zip”), care prinde pe rând câte un dinte din fiecare parte. `dict(zip(chei, valori))` e felul obișnuit de a construi un dicționar din două liste.

Dacă secvențele au lungimi diferite, `zip()` se oprește la **cea mai scurtă**, fără nicio eroare (vezi greșelile frecvente).

### reversed(): de la coadă

```python
for secunda in reversed(range(1, 4)):
    print(secunda, end=" ")
print("Start!")
istoric = ["Cluj", "Iași", "Brașov"]
print(list(reversed(istoric)))
print(istoric)
```

```text
3 2 1 Start!
['Brașov', 'Iași', 'Cluj']
['Cluj', 'Iași', 'Brașov']
```

`reversed()` nu modifică lista, ci o parcurge invers. Lista are și metoda `reverse()`, care o întoarce pe loc (și întoarce `None`, ca `sort()`, lecția 12).

### sum(), min(), max()

```python
preturi = [4.5, 8.99, 32.0, 12.5]
print(sum(preturi))
print(min(preturi), max(preturi))
print(max("Ana", "Mihai", "Ioana"))
print(min([], default=0))
```

```text
57.99
4.5 32.0
Mihai
0
```

`min()` și `max()` primesc fie mai multe valori separate (lecția 3), fie o colecție. Pe o colecție goală dau eroare, dacă nu le dai o valoare `default`.

### any() și all()

- `any(colectie)` e `True` dacă **măcar un** element e adevărat;
- `all(colectie)` e `True` dacă **toate** elementele sunt adevărate.

Le combini aproape mereu cu o expresie generator (lecția 16):

```python
note = [9, 4, 7, 10]
print(any(n < 5 for n in note))       # există vreo notă sub 5?
print(all(n >= 5 for n in note))      # toate sunt de trecere?

parola = "Secret2026"
print(any(c.isdigit() for c in parola) and any(c.isupper() for c in parola))
```

```text
True
False
True
```

Se citesc foarte natural: „există vreo notă sub 5?”, „toate notele sunt de trecere?”. Ca `and` și `or` (lecția 7), se opresc imediat ce știu răspunsul.

### Sortare după un criteriu: key=

`sorted()`, `min()` și `max()` acceptă `key=`, o **funcție** aplicată fiecărui element. Compararea se face după rezultatul ei, nu după elementul în sine. Funcția se scrie **fără paranteze**, pentru că o dai mai departe, nu o apelezi tu.

```python
orase = ["Iași", "cluj", "Brașov", "Arad", "bacău"]
print(sorted(orase))
print(sorted(orase, key=str.lower))
print(sorted(orase, key=len))
print(max(orase, key=len))
```

```text
['Arad', 'Brașov', 'Iași', 'bacău', 'cluj']
['Arad', 'bacău', 'Brașov', 'cluj', 'Iași']
['Iași', 'cluj', 'Arad', 'bacău', 'Brașov']
Brașov
```

- `key=str.lower` compară variantele cu litere mici (`str.lower` e metoda `lower` a stringurilor, dată ca funcție, fără s-o apelezi), deci ordinea nu mai depinde de literele mari (problema din lecția 7);
- `key=len` compară lungimile. La lungimi egale, ordinea originală se păstrează (sortarea e „stabilă”).

Un truc foarte util: cheia cu valoarea maximă dintr-un dicționar, cu `key=dictionar.get`:

```python
voturi = {"Cluj": 120, "Iași": 95, "Brașov": 130}
print(max(voturi, key=voturi.get))
print(sorted(voturi, key=voturi.get, reverse=True))
```

```text
Brașov
['Brașov', 'Cluj', 'Iași']
```

`max(voturi, ...)` parcurge cheile, iar `voturi.get(cheie)` dă valoarea fiecăreia, deci compararea se face după voturi.

Pentru criterii mai complicate (de exemplu „al doilea element al tuplului”) vei scrie propriile funcții (lecția 18) sau funcții scurte, numite `lambda` (lecția 21). Până atunci, un truc: pune criteriul **primul** în tuplu și sortează tuplurile.

```python
produse = {"pâine": 4.5, "lapte": 8.99, "cafea": 32.0}
for pret, produs in sorted((pret, produs) for produs, pret in produse.items()):
    print(f"{produs:<6} {pret:>6.2f}")
```

```text
pâine    4.50
lapte    8.99
cafea   32.00
```

### Ce se întâmplă „pe dedesubt”: enumerate, zip și reversed sunt „leneșe”

`enumerate()`, `zip()` și `reversed()` nu construiesc o listă nouă. Întorc un obiect care produce câte o valoare **abia când i se cere**, ca `range()` (lecția 10). Nu ocupă memorie pentru toate valorile deodată, așa că merg și pe secvențe foarte mari. Spre deosebire de `range()`, însă, un astfel de obiect **se consumă**: după ce l-ai parcurs o dată, e gol.

```python
perechi = zip(["Ana", "Mihai"], [9, 7])
print(list(perechi))
print(list(perechi))
```

```text
[('Ana', 9), ('Mihai', 7)]
[]
```

Dacă ai nevoie de rezultat de mai multe ori, salvează-l ca listă: `perechi = list(zip(...))`. Obiectele de felul ăsta se numesc **iteratori**; vei vedea la lecția 37 cum funcționează și cum îți poți scrie propriii iteratori.

## Exemplu complet

Clasamentul unui concurs de programare. Datele vin în trei liste paralele, iar programul folosește tot ce ai învățat în lecție.

<!-- fisier: concurs.py -->
```python
concurenti = ["Ana", "Mihai", "Ioana", "Radu", "Elena"]
puncte_problema1 = [100, 70, 100, 40, 90]
puncte_problema2 = [80, 100, 95, 0, 85]
timpi_minute = [95, 110, 87, 120, 101]

# Total pe concurent, într-un dicționar construit cu zip
totaluri = {
    nume: p1 + p2
    for nume, p1, p2 in zip(concurenti, puncte_problema1, puncte_problema2)
}
timp = dict(zip(concurenti, timpi_minute))

# Clasament: punctaj descrescător; la egalitate, timpul mai mic câștigă
clasament = sorted((-totaluri[n], timp[n], n) for n in concurenti)

print(f"{'Loc':<4}{'Nume':<8}{'Puncte':>7}{'Timp':>6}")
for loc, (_, minute, nume) in enumerate(clasament, start=1):
    print(f"{loc:<4}{nume:<8}{totaluri[nume]:>7}{minute:>6}")

print()
print("Punctaj maxim:", max(totaluri.values()), "-", max(totaluri, key=totaluri.get))
print("Media:", round(sum(totaluri.values()) / len(totaluri), 1))
print("Cineva a luat 0 la o problemă?", any(p == 0 for p in puncte_problema1 + puncte_problema2))
print("Toți au terminat sub 2 ore?", all(t < 120 for t in timpi_minute))
print("Concurenții, în ordine inversă:", ", ".join(reversed(concurenti)))
```

```text
Loc Nume     Puncte  Timp
1   Ioana       195    87
2   Ana         180    95
3   Elena       175   101
4   Mihai       170   110
5   Radu         40   120

Punctaj maxim: 195 - Ioana
Media: 152.0
Cineva a luat 0 la o problemă? True
Toți au terminat sub 2 ore? False
Concurenții, în ordine inversă: Elena, Radu, Ioana, Mihai, Ana
```

Trucul din clasament: tuplurile se sortează după primul element, apoi după al doilea (lecția 13). Punem `-totaluri[n]` (punctaj negativ, ca sortarea crescătoare să pună punctajele mari primele), apoi timpul, apoi numele. La afișare, `_` ignoră punctajul negativ.

## Greșeli frecvente

### 1. zip pe secvențe de lungimi diferite

```python
elevi = ["Ana", "Mihai", "Ioana"]
note = [9, 7]
for nume, nota in zip(elevi, note):
    print(nume, nota)
```

```text
Ana 9
Mihai 7
```

Ioana a dispărut fără nicio eroare: `zip()` s-a oprit la lista mai scurtă. Când lungimile **trebuie** să fie egale, cere-i lui Python să verifice, cu `strict=True`:

<!-- fisier: zip.py -->
```python
elevi = ["Ana", "Mihai", "Ioana"]
note = [9, 7]
for nume, nota in zip(elevi, note, strict=True):
    print(nume, nota)
```

```text
Ana 9
Mihai 7
Traceback (most recent call last):
  File "zip.py", line 3, in <module>
    for nume, nota in zip(elevi, note, strict=True):
ValueError: zip() argument 2 is shorter than argument 1
```

O eroare vizibilă e mai bună decât un elev care lipsește fără să observe nimeni.

### 2. Ordinea inversă la enumerate

```python
cumparaturi = ["pâine", "lapte"]
for produs, i in enumerate(cumparaturi):
    print(f"{i}: {produs}")
```

```text
pâine: 0
lapte: 1
```

`enumerate()` dă mereu **întâi poziția**, apoi elementul. Corect: `for i, produs in enumerate(cumparaturi):`.

### 3. Paranteze după funcția din key=

<!-- fisier: key.py -->
```python
orase = ["Iași", "Cluj", "Brașov"]
print(sorted(orase, key=len()))
```

```text
Traceback (most recent call last):
  File "key.py", line 2, in <module>
    print(sorted(orase, key=len()))
                            ^^^^^
TypeError: len() takes exactly one argument (0 given)
```

Cu paranteze, Python **apelează** `len` imediat, fără argument. `key=` vrea funcția însăși, ca s-o apeleze el pentru fiecare element: `key=len`.

### 4. min() sau max() pe o colecție goală

<!-- fisier: key.py -->
```python
note = []
print(max(note))
```

```text
Traceback (most recent call last):
  File "key.py", line 2, in <module>
    print(max(note))
          ^^^^^^^^^
ValueError: max() iterable argument is empty
```

Colecția goală nu are maxim. Folosește `max(note, default=0)` sau verifică întâi `if note:`. La fel, `sum(note) / len(note)` dă `ZeroDivisionError` pe o listă goală.

### 5. sum() pe stringuri

<!-- fisier: key.py -->
```python
cuvinte = ["Ana", "are", "mere"]
print(sum(cuvinte))
```

```text
Traceback (most recent call last):
  File "key.py", line 2, in <module>
    print(sum(cuvinte))
          ^^^^^^^^^^^^
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

`sum()` pornește de la 0 și adună, deci funcționează doar pe numere. Pentru a lipi texte, folosește `" ".join(cuvinte)` (lecția 4).

## Exercițiu

În `capitole/17-iterare-avansata/iterare_avansata.py`, scrie analiza **vânzărilor unei săptămâni** pentru o cafenea:

```python
zile = ["luni", "marți", "miercuri", "joi", "vineri", "sâmbătă", "duminică"]
cafele = [120, 95, 110, 130, 160, 210, 180]
prajituri = [40, 35, 30, 45, 60, 95, 80]
```

1. afișează un tabel numerotat (`enumerate` de la 1) cu ziua, cafelele, prăjiturile și totalul zilei (`zip`);
2. afișează ziua cu cele mai multe cafele vândute, folosind un dicționar `zi -> cafele` (`dict(zip(...))`) și `max(..., key=...)`;
3. afișează totalul săptămânii și media zilnică pentru fiecare produs (`sum`);
4. răspunde cu `any`/`all`: a existat o zi cu peste 200 de cafele? S-au vândut în fiecare zi cel puțin 30 de prăjituri?
5. afișează zilele sortate după totalul vânzărilor, de la cea mai bună la cea mai slabă (folosește trucul cu tuplurile din lecție);
6. verifică, cu `zip(..., strict=True)`, că cele trei liste au aceeași lungime; apoi șterge intenționat o valoare și vezi ce eroare primești.

## Pe scurt

- `enumerate(secventa, start=1)` dă perechi `(poziție, element)`; poziția e mereu prima.
- `zip(a, b, ...)` parcurge secvențe în paralel și se oprește la cea mai scurtă; `strict=True` cere lungimi egale. `dict(zip(chei, valori))` construiește un dicționar.
- `reversed()` parcurge invers, fără să modifice secvența.
- `sum`, `min`, `max` (cu `default=` pentru colecții goale), `any` („măcar unul”) și `all` („toate”).
- `key=functie` (fără paranteze) alege criteriul de comparare: `key=len`, `key=str.lower`, `key=dictionar.get`.
- `enumerate`, `zip` și `reversed` sunt iteratori: se consumă la prima parcurgere; păstrează-i cu `list()` dacă îți trebuie din nou.
