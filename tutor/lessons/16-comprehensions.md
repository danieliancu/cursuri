## Ce este

Un **comprehension** este o scriere scurtă pentru „construiește o colecție nouă dintr-o buclă”. În loc de:

```python
preturi = [4.5, 8.99, 32.0]
cu_tva = []
for pret in preturi:
    cu_tva.append(round(pret * 1.21, 2))
print(cu_tva)
```

```text
[5.45, 10.88, 38.72]
```

scrii, într-un singur rând:

```python
preturi = [4.5, 8.99, 32.0]
cu_tva = [round(pret * 1.21, 2) for pret in preturi]
print(cu_tva)
```

```text
[5.45, 10.88, 38.72]
```

Se citește aproape ca o propoziție: „lista cu `round(pret * 1.21, 2)` **pentru fiecare** `pret` **din** `preturi`”. Există trei variante: **list comprehension** `[...]`, **dict comprehension** `{k: v ...}` și **set comprehension** `{...}`.

## De ce contează

Tiparul „pornesc de la o colecție goală, parcurg alta, adaug ceva transformat sau filtrat” apare mereu (l-ai scris de mai multe ori în lecțiile 12–15). Comprehension-ul îl reduce la un rând care spune direct **ce** conține rezultatul, fără pașii mecanici (`= []`, `append`).

Îl vei întâlni în aproape orice cod Python scris de alții, inclusiv în Django, unde construiești liste de opțiuni sau dicționare de date pentru template-uri. Trebuie să știi să-l citești, să-l scrii și, la fel de important, să recunoști când o buclă normală e mai clară.

## Cum funcționează

### List comprehension

Forma de bază: `[expresie for element in secventa]`.

```python
nume = ["ana", "mihai", "ioana"]
print([n.title() for n in nume])
print([len(n) for n in nume])
print([x * x for x in range(1, 6)])
print([litera.upper() for litera in "cluj"])
```

```text
['Ana', 'Mihai', 'Ioana']
[3, 5, 5]
[1, 4, 9, 16, 25]
['C', 'L', 'U', 'J']
```

Pentru fiecare element din secvență, Python calculează expresia din față și pune rezultatul în lista nouă. Secvența originală rămâne neschimbată.

### Cu filtru: if la final

Adaugi `if conditie` la final ca să păstrezi doar unele elemente:

```python
note = [9, 4, 7.5, 10, 3, 8]
print([n for n in note if n >= 5])
print([n for n in note if n < 5])

cuvinte = "Ana învață Python la Cluj în fiecare seară".split()
print([c for c in cuvinte if len(c) > 4])
```

```text
[9, 7.5, 10, 8]
[4, 3]
['învață', 'Python', 'fiecare', 'seară']
```

Primul exemplu e bucla din lecția 12 (`promovate`), redusă la un rând.

### Cu alegere: if / else în față

Dacă vrei să **transformi** fiecare element diferit, după o condiție, folosești expresia condițională din lecția 8 (`a if conditie else b`). Ea stă **în față**, ca parte a expresiei:

```python
note = [9, 4, 7.5, 10, 3]
print(["promovat" if n >= 5 else "corigent" for n in note])
```

```text
['promovat', 'corigent', 'promovat', 'promovat', 'corigent']
```

Regula de reținut:
- `if` **la final** = filtru: unele elemente nu intră deloc;
- `if ... else` **în față** = alegere: toate elementele intră, dar transformate diferit.

### Dict comprehension

`{cheie: valoare for element in secventa}` construiește un dicționar:

```python
produse = ["pâine", "lapte", "cafea"]
lungimi = {p: len(p) for p in produse}
print(lungimi)

preturi_produse = {"pâine": 4.5, "lapte": 8.99, "cafea": 32.0}
scumpe = {p: pret for p, pret in preturi_produse.items() if pret > 5}
print(scumpe)
reduse = {p: round(pret * 0.9, 2) for p, pret in preturi_produse.items()}
print(reduse)
```

```text
{'pâine': 5, 'lapte': 5, 'cafea': 5}
{'lapte': 8.99, 'cafea': 32.0}
{'pâine': 4.05, 'lapte': 8.09, 'cafea': 28.8}
```

Așa a fost construit „stocul rămas” din exemplul complet al lecției 14. Despachetarea cu `items()` funcționează în comprehension exact ca în `for`.

Un truc util: inversarea unui dicționar (cheile devin valori și invers).

```python
coduri = {"CJ": "Cluj", "IS": "Iași", "BV": "Brașov"}
dupa_oras = {oras: cod for cod, oras in coduri.items()}
print(dupa_oras["Iași"])
```

```text
IS
```

### Set comprehension

La fel ca list comprehension, dar cu acolade. Rezultatul e un set, deci duplicatele dispar:

```python
emailuri = ["ana@exemplu.ro", "mihai@gmail.com", "ioana@exemplu.ro", "radu@yahoo.com"]
domenii = {e.split("@")[1] for e in emailuri}
print(sorted(domenii))
```

```text
['exemplu.ro', 'gmail.com', 'yahoo.com']
```

### Comprehension-uri cu două for

Poți pune mai multe `for`, în **aceeași ordine** în care le-ai scrie ca bucle imbricate:

```python
catalog = [["Ana", 9, 10], ["Mihai", 7, 6], ["Ioana", 10, 9]]
toate_notele = [nota for rand in catalog for nota in rand[1:]]
print(toate_notele)

perechi = [(a, b) for a in "AB" for b in range(1, 3)]
print(perechi)
```

```text
[9, 10, 7, 6, 10, 9]
[('A', 1), ('A', 2), ('B', 1), ('B', 2)]
```

Primul se citește: „pentru fiecare `rand` din catalog, pentru fiecare `nota` din `rand[1:]`, ia `nota`”. Echivalentul cu bucle:

```python
catalog = [["Ana", 9, 10], ["Mihai", 7, 6], ["Ioana", 10, 9]]
toate_notele = []
for rand in catalog:
    for nota in rand[1:]:
        toate_notele.append(nota)
print(toate_notele)
```

```text
[9, 10, 7, 6, 10, 9]
```

Cu două `for` încă se poate citi. Cu trei sau cu condiții complicate, scrie bucle normale.

### Când NU folosești un comprehension

Un comprehension e potrivit când **construiești o colecție**. Nu e potrivit când:
- **nu ai nevoie de rezultat** și bucla doar face ceva (afișează, salvează, modifică altceva). Pentru asta există `for`;
- **logica are mai mulți pași**: variabile intermediare, mai multe `if`-uri, `break`. O buclă normală, cu nume clare, se citește mai ușor;
- **rândul devine prea lung** ca să-l înțelegi dintr-o privire.

Regula practică: dacă trebuie să citești un comprehension de două ori ca să-l înțelegi, transformă-l în buclă.

### Ce se întâmplă „pe dedesubt”: variabila din comprehension e locală

Variabila unui comprehension (`n` din `[n for n in note]`) există **doar în interiorul** lui. Nu „scapă” afară și nu strică o variabilă cu același nume:

```python
n = "valoare importantă"
patrate = [n * n for n in range(4)]
print(patrate)
print(n)
```

```text
[0, 1, 4, 9]
valoare importantă
```

Spre deosebire de comprehension, variabila unei bucle `for` obișnuite rămâne după buclă, cu ultima valoare. E unul dintre motivele pentru care comprehension-urile sunt mai sigure. Mai multe despre unde „trăiesc” variabilele, la lecția 20.

Ca observație: dacă scrii expresia între paranteze rotunde în loc de pătrate, nu obții un „tuple comprehension”, ci o **expresie generator**, care produce valorile pe rând, fără să le păstreze pe toate în memorie. O poți da direct funcțiilor ca `sum()`: `sum(n * n for n in range(4))`. Generatoarele au lecția lor, lecția 37.

## Exemplu complet

Analiza rezultatelor unei clase, cu date brute în format „nume:nota1,nota2,...”. Fiecare pas e un comprehension.

<!-- fisier: rezultate.py -->
```python
date_brute = [
    "ana popescu: 9, 10, 8",
    "Mihai Ionescu:7,6,9",
    "  ioana marin : 10,9,10 ",
    "radu pop: 4, 5, 3",
    "Elena Dima: 6,7",
]

# 1. Dicționar nume -> listă de note (nume curățat, note convertite în numere)
catalog = {
    linie.split(":")[0].strip().title(): [int(n) for n in linie.split(":")[1].split(",")]
    for linie in date_brute
}

# 2. Media fiecăruia
medii = {nume: sum(note) / len(note) for nume, note in catalog.items()}

# 3. Cine a promovat și cine nu
promovati = sorted(nume for nume, media in medii.items() if media >= 5)
corigenti = sorted(nume for nume, media in medii.items() if media < 5)

# 4. Toate notele, distincte
note_distincte = sorted({n for note in catalog.values() for n in note})

for nume, media in medii.items():
    print(f"{nume:<15} {catalog[nume]!s:<12} {media:5.2f}")
print()
print("Promovați:", ", ".join(promovati))
print("Corigenți:", ", ".join(corigenti))
print("Note distincte acordate:", note_distincte)
```

```text
Ana Popescu     [9, 10, 8]    9.00
Mihai Ionescu   [7, 6, 9]     7.33
Ioana Marin     [10, 9, 10]   9.67
Radu Pop        [4, 5, 3]     4.00
Elena Dima      [6, 7]        6.50

Promovați: Ana Popescu, Elena Dima, Ioana Marin, Mihai Ionescu
Corigenți: Radu Pop
Note distincte acordate: [3, 4, 5, 6, 7, 8, 9, 10]
```

Detalii:
- `int(" 10")` acceptă spațiile de la margini (lecția 6), deci notele nu mai trebuie curățate cu `strip()`;
- `sorted(nume for ...)` primește o expresie generator, fără paranteze în plus;
- `{catalog[nume]!s:<12}`: `!s` transformă lista în text înainte de aliniere, pentru că formatul cu lățime nu se poate aplica direct unei liste;
- primul pas e la limita lizibilității: un dict comprehension cu un list comprehension în interior. Dacă ți se pare greu de citit, ai dreptate. La lecția 18 vei putea muta această logică într-o funcție cu nume clar.

## Greșeli frecvente

### 1. else pus după filtru

<!-- fisier: comp.py -->
```python
note = [9, 4, 10]
rezultat = [n for n in note if n >= 5 else 0]
```

```text
  File "comp.py", line 2
    rezultat = [n for n in note if n >= 5 else 0]
                                          ^^^^
SyntaxError: invalid syntax
```

`if` de la final e un filtru și nu poate avea `else`. Pentru alegere, expresia condițională stă în față:

```python
note = [9, 4, 10]
rezultat = [n if n >= 5 else 0 for n in note]
print(rezultat)
```

```text
[9, 0, 10]
```

### 2. Comprehension folosit doar pentru efect

```python
nume = ["Ana", "Mihai"]
rezultat = [print(f"Salut, {n}!") for n in nume]
print(rezultat)
```

```text
Salut, Ana!
Salut, Mihai!
[None, None]
```

Mesajele s-au afișat, dar s-a construit și o listă inutilă de `None` (valoarea întoarsă de `print`). Când nu ai nevoie de colecția rezultată, scrie un `for` obișnuit:

```python
nume = ["Ana", "Mihai"]
for n in nume:
    print(f"Salut, {n}!")
```

### 3. Paranteze rotunde în loc de pătrate

```python
patrate = (x * x for x in range(4))
print(patrate)
print(len([x * x for x in range(4)]))
```

Primul `print` nu afișează numerele, ci ceva de forma `<generator object <genexpr> at 0x7f...>`: e o expresie generator (vezi „pe dedesubt”), nu un tuplu și nici o listă. `len()` pe ea ar da `TypeError`. Pentru o listă, folosește paranteze pătrate. Pentru un tuplu, `tuple(x * x for x in range(4))`.

### 4. Chei duplicate într-un dict comprehension

```python
elevi = ["Ana Popescu", "Ana Ionescu", "Mihai Pop"]
dupa_prenume = {e.split()[0]: e for e in elevi}
print(dupa_prenume)
```

```text
{'Ana': 'Ana Ionescu', 'Mihai': 'Mihai Pop'}
```

Ana Popescu a dispărut fără nicio eroare: cheia `"Ana"` a apărut de două ori, iar a doua valoare a înlocuit-o pe prima (lecția 14). Alege o cheie care e cu adevărat unică (aici, numele complet) sau grupează valorile într-o listă cu o buclă normală.

### 5. Set sau dicționar?

```python
cu_doua_puncte = {x: x * 2 for x in range(3)}
fara = {x * 2 for x in range(3)}
print(type(cu_doua_puncte), type(fara))
```

```text
<class 'dict'> <class 'set'>
```

Ambele folosesc acolade. Diferența e `:`: cu `cheie: valoare` obții un dicționar, fără `:` obții un set. Citește atent când întâlnești `{... for ...}` în codul altcuiva.

## Exercițiu

În `capitole/16-comprehensions/comprehensions.py`, pornește de la lista de produse:

```python
produse = [
    ("pâine", 4.5, 20), ("lapte", 8.99, 0), ("cafea", 32.0, 3),
    ("mere", 6.49, 50), ("ceai", 14.0, 0), ("ouă", 1.2, 120),
]
```

(fiecare tuplu e `(nume, preț, stoc)`) și scrie, **fiecare într-un singur comprehension**:

1. lista numelor produselor aflate în stoc;
2. un dicționar `nume -> preț` doar pentru produsele mai scumpe de 5 lei;
3. un dicționar `nume -> valoarea stocului` (preț × stoc), rotunjită la 2 zecimale;
4. lista etichetelor de raft, de forma `"PÂINE — 4.50 lei"`, cu numele cu litere mari și `"(stoc epuizat)"` adăugat la produsele cu stoc 0 (folosește `if ... else` în față);
5. setul primelor litere ale tuturor produselor.

Afișează fiecare rezultat. La final, alege unul dintre comprehension-uri, rescrie-l ca buclă `for` și verifică dacă dă același rezultat.

## Pe scurt

- `[expresie for x in secventa]` construiește o listă; `{k: v for ...}` un dicționar; `{expresie for ...}` un set.
- `if` la final filtrează elementele; `a if conditie else b` în față alege transformarea.
- Mai multe `for` se scriu în ordinea buclelor imbricate; peste două niveluri, scrie bucle normale.
- Variabila unui comprehension nu iese în afara lui.
- `( ... for ...)` e o expresie generator, nu un tuplu; poate fi dată direct lui `sum()`, `sorted()` și altor funcții.
- Folosește comprehension-uri pentru a construi colecții, nu pentru efecte (`print`) sau pentru logică complicată.
