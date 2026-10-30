## Ce este

Bucla **`for`** ia pe rând fiecare element dintr-o **secvență** și execută blocul o dată pentru fiecare:

```python
for litera in "Ana":
    print(litera)
```

```text
A
n
a
```

La fiecare iterație, variabila `litera` primește următorul caracter din `"Ana"`. Când nu mai sunt caractere, bucla se termină.

Ca să repeți ceva de un număr de ori, folosești **`range()`**, care produce o secvență de numere:

```python
for numar in range(5):
    print(numar, end=" ")
```

```text
0 1 2 3 4 
```

## De ce contează

`for` e bucla pe care o vei folosi cel mai des în Python. Aproape orice prelucrare de date are forma „pentru fiecare element, fă ceva”: pentru fiecare produs din coș, adaugă prețul la total; pentru fiecare rând din fișier, citește datele; pentru fiecare articol din baza de date, afișează titlul. Și în template-urile Django (lecția 48) vei scrie `{% for articol in articole %}`.

Față de `while`, `for` e mai sigur. Nu trebuie să inițializezi un contor, nu trebuie să-l actualizezi și nu poți crea din greșeală o buclă infinită: bucla se termină singură când se termină secvența.

## Cum funcționează

### Iterarea peste un text

Un string e o secvență de caractere, deci `for` îl parcurge caracter cu caracter:

```python
cuvant = "Iași"
for caracter in cuvant:
    print(f"[{caracter}]", end="")
print()
```

```text
[I][a][ș][i]
```

Numele variabilei (`caracter`, `litera`) îl alegi tu. Alege unul care spune ce primește la fiecare pas.

Rezultatul lui `split()` (lecția 4) e o listă, adică tot o secvență, deci poți parcurge cuvintele unui text:

```python
propozitie = "Ana învață Python la Cluj"
for cuvant in propozitie.split():
    print(f"{cuvant:<8} are {len(cuvant)} litere")
```

```text
Ana      are 3 litere
învață   are 6 litere
Python   are 6 litere
la       are 2 litere
Cluj     are 4 litere
```

Listele au lecția lor (12). Tot ce vezi acum despre `for` va funcționa identic pe ele.

### range(): secvențe de numere

`range()` are trei forme:

| Formă | Numere produse | Exemplu | Rezultat |
|---|---|---|---|
| `range(stop)` | de la 0 până **înainte** de `stop` | `range(5)` | 0 1 2 3 4 |
| `range(start, stop)` | de la `start` până înainte de `stop` | `range(2, 6)` | 2 3 4 5 |
| `range(start, stop, pas)` | din `pas` în `pas` | `range(0, 20, 5)` | 0 5 10 15 |

Regula e cea de la slicing (lecția 4): **`stop` nu e inclus**. Ca să numeri de la 1 la 10, scrii `range(1, 11)`.

Cu pas negativ, numărătoarea merge înapoi (și aici `stop` nu e inclus, deci `0` nu apare):

```python
for secunda in range(5, 0, -1):
    print(secunda, end="... ")
print("Start!")
```

```text
5... 4... 3... 2... 1... Start!
```

Când ai nevoie doar de repetare, fără să folosești numărul, convenția e să numești variabila `_`:

```python
for _ in range(3):
    print("Hip, hip, ura!")
```

```text
Hip, hip, ura!
Hip, hip, ura!
Hip, hip, ura!
```

### Acumulatori

Tiparele de la `while` (lecția 9) funcționează la fel și aici: inițializezi înainte de buclă, actualizezi în buclă și afișezi după.

```python
# Suma și numărul multiplilor de 3 dintre 1 și 30
suma = 0
cati = 0
for numar in range(1, 31):
    if numar % 3 == 0:
        suma += numar
        cati += 1
print(f"{cati} multipli de 3, cu suma {suma}")
```

```text
10 multipli de 3, cu suma 165
```

Același lucru pentru caractere: câte vocale are un text?

```python
text = "Ana are mere și pere"
vocale = 0
for litera in text.lower():
    if litera in "aeiouăîâ":
        vocale += 1
print(f"Vocale: {vocale}")
```

```text
Vocale: 9
```

Și pentru maxim: cel mai lung cuvânt.

```python
text = "Ana învață programare în fiecare seară"
cel_mai_lung = ""
for cuvant in text.split():
    if len(cuvant) > len(cel_mai_lung):
        cel_mai_lung = cuvant
print(f"Cel mai lung cuvânt: {cel_mai_lung} ({len(cel_mai_lung)} litere)")
```

```text
Cel mai lung cuvânt: programare (10 litere)
```

Pornim cu `""`, care are lungimea 0, deci orice cuvânt real îl va înlocui.

### Bucle imbricate

O buclă în altă buclă: pentru **fiecare** iterație a buclei exterioare, cea interioară rulează **complet**.

```python
for rand in range(1, 6):
    for coloana in range(1, 6):
        print(f"{rand * coloana:4}", end="")
    print()
```

```text
   1   2   3   4   5
   2   4   6   8  10
   3   6   9  12  15
   4   8  12  16  20
   5  10  15  20  25
```

Bucla interioară afișează un rând întreg (cu `end=""`, deci fără să treacă la rând nou). Apoi `print()`-ul gol, aflat în bucla exterioară dar în afara celei interioare, trece la rândul următor. Indentarea arată de ce buclă aparține fiecare rând. În total, blocul interior rulează de 5 × 5 = 25 de ori.

### for sau while?

- **`for`**: când parcurgi ceva ce există deja (un text, o listă, un interval de numere) sau știi de câte ori repeți;
- **`while`**: când repeți până se întâmplă ceva și nu știi dinainte când (un răspuns valid, o sumă atinsă, „ieșire” din meniu).

Suma de la 1 la 100 se poate scrie cu ambele, dar varianta cu `for` e mai scurtă și nu poate deveni infinită:

```python
suma = 0
for numar in range(1, 101):
    suma += numar
print(suma)
```

```text
5050
```

### Ce se întâmplă „pe dedesubt”: range nu creează toate numerele

`range(1_000_000_000)` nu ocupă memorie pentru un miliard de numere. Un `range` ține minte doar `start`, `stop` și `pas`, iar fiecare număr îl calculează abia când `for` îl cere. De aceea poți scrie `range` cu numere oricât de mari fără să umpli memoria:

```python
numere = range(0, 1_000_000_000, 7)
print(numere)
print(len(numere))
print(numere[3])
```

```text
range(0, 1000000000, 7)
142857143
21
```

`len()` și indexarea funcționează pe loc, prin calcul: `numere[3]` e al patrulea număr din șirul 0, 7, 14, 21, ..., fără ca primele trei să fie create.

La fiecare iterație, `for` îi cere secvenței „următorul element”, până când aceasta răspunde că nu mai are. Același mecanism funcționează pentru texte, liste, fișiere și chiar rezultatele din baza de date în Django. Detaliile, la lecția 37 (iteratori și generatori).

## Exemplu complet

Statistica notelor unei clase. Programul întreabă câte note sunt, le citește pe rând (cu validare) și afișează media, cea mai mare și cea mai mică notă, precum și câți elevi au promovat.

<!-- fisier: note.py -->
<!-- stdin: 5\n9\n4.5\nzece\n10\n7\n6.5 -->
```python
text = input("Câte note introduci? ").strip()
while not text.isdigit() or int(text) == 0:
    text = input("Scrie un număr întreg pozitiv: ").strip()
numar_note = int(text)

suma = 0.0
promovati = 0
nota_max = 0.0
nota_min = 10.0

for i in range(1, numar_note + 1):
    text = input(f"Nota {i}: ").strip().replace(",", ".")
    while not text.replace(".", "", 1).isdigit() or not 1 <= float(text) <= 10:
        text = input(f"Nota {i} (între 1 și 10): ").strip().replace(",", ".")
    nota = float(text)

    suma += nota
    if nota >= 5:
        promovati += 1
    if nota > nota_max:
        nota_max = nota
    if nota < nota_min:
        nota_min = nota

print()
print(f"Media clasei:  {suma / numar_note:.2f}")
print(f"Nota maximă:   {nota_max:g}")
print(f"Nota minimă:   {nota_min:g}")
print(f"Promovați:     {promovati} din {numar_note}")
print("Promovabilitate: " + "#" * promovati + "." * (numar_note - promovati))
```

```text
Câte note introduci? 5
Nota 1: 9
Nota 2: 4.5
Nota 3: zece
Nota 3 (între 1 și 10): 10
Nota 4: 7
Nota 5: 6.5

Media clasei:  7.40
Nota maximă:   10
Nota minimă:   4.5
Promovați:     4 din 5
Promovabilitate: ####.
```

Câteva detalii:
- `range(1, numar_note + 1)` numerotează notele de la 1, cum ne așteptăm să le vadă un om;
- în condiția buclei de validare, `or` se oprește la prima parte adevărată (lecția 7), deci `float(text)` se calculează doar dacă textul arată ca un număr;
- `nota_min` pornește de la 10, cea mai mare notă posibilă, ca prima notă reală să o înlocuiască. `nota_max` pornește de la 0 din același motiv;
- formatul `:g` afișează numărul fără zecimale inutile: `10` în loc de `10.0`.

## Greșeli frecvente

### 1. Uitarea că stop nu e inclus

```python
# Vrem numerele de la 1 la 5
for numar in range(1, 5):
    print(numar, end=" ")
```

```text
1 2 3 4 
```

`range(1, 5)` se oprește înainte de 5. Corect: `range(1, 6)`. Regula de reținut: `range(a, b)` are `b - a` numere.

### 2. for pe un număr

<!-- fisier: bucla.py -->
```python
for i in 5:
    print(i)
```

```text
Traceback (most recent call last):
  File "bucla.py", line 1, in <module>
    for i in 5:
             ^
TypeError: 'int' object is not iterable
```

„Not iterable” înseamnă că valoarea nu e o secvență pe care `for` s-o poată parcurge. Un număr nu are elemente. Ca să repeți de 5 ori, scrii `for i in range(5):`.

### 3. range() cu un float sau cu un text

<!-- fisier: bucla.py -->
<!-- stdin: 3 -->
```python
de_cate_ori = input("De câte ori? ")
for _ in range(de_cate_ori):
    print("Salut!")
```

```text
De câte ori? 3
Traceback (most recent call last):
  File "bucla.py", line 2, in <module>
    for _ in range(de_cate_ori):
             ^^^^^^^^^^^^^^^^^^
TypeError: 'str' object cannot be interpreted as an integer
```

`range()` acceptă doar numere întregi. Cu un `float`, de exemplu `range(2.5)`, mesajul e același, dar spune `'float' object`. Convertește cu `int()` (lecția 6):

```python
de_cate_ori = int(input("De câte ori? "))
for _ in range(de_cate_ori):
    print("Salut!")
```

### 4. print-ul rezultatului pus în buclă

```python
suma = 0
for numar in range(1, 5):
    suma += numar
    print(f"Suma: {suma}")
```

```text
Suma: 1
Suma: 3
Suma: 6
Suma: 10
```

Rezultatul final trebuia afișat o singură dată, **după** buclă, deci fără indentare:

```python
suma = 0
for numar in range(1, 5):
    suma += numar
print(f"Suma: {suma}")
```

```text
Suma: 10
```

### 5. Modificarea variabilei buclei nu schimbă iterațiile

```python
for numar in range(5):
    print(numar, end=" ")
    numar += 10
```

```text
0 1 2 3 4 
```

La fiecare iterație, `for` dă variabilei **următorul** element din `range`, indiferent ce i-ai făcut între timp. Nu poți „sări” elemente modificând variabila. Pentru pași diferiți, schimbă `range` (de exemplu `range(0, 50, 10)`); pentru a sări peste unele elemente, există `continue` (lecția 11).

## Exercițiu

În `capitole/10-for-range/for_range.py`, scrie trei programe mici, unul după altul, separate prin câte un rând de `=`:

1. **Analiza unui text:** cere o propoziție și afișează câte litere, câte cifre, câte spații și câte alte caractere conține. Folosește `isdigit()`, iar pentru litere metoda `isalpha()` (`"ă".isalpha()` e `True`).
2. **Tabla înmulțirii:** cere un număr `n` între 1 și 10 și afișează tabla înmulțirii de la 1 × 1 la `n` × `n`, cu coloanele aliniate, plus un rând de antet cu numerele coloanelor.
3. **Brad din steluțe:** cere înălțimea `h` și desenează un brad cu `h` rânduri, centrat, ca mai jos pentru `h = 4`:

```text
   *
  ***
 *****
*******
```

Indiciu: pe rândul `i` (numărând de la 0) sunt `h - 1 - i` spații și `2 * i + 1` steluțe.

## Pe scurt

- `for element in secventa:` execută blocul o dată pentru fiecare element (caracterele unui text, cuvintele din `split()` și, mai târziu, listele).
- `range(stop)`, `range(start, stop)`, `range(start, stop, pas)`: numere întregi, fără `stop`; un pas negativ numără înapoi.
- `for` se termină singur, deci e mai sigur decât `while` când știi ce parcurgi.
- Acumulatorii se inițializează înainte de buclă și se afișează după ea.
- În buclele imbricate, cea interioară rulează complet la fiecare iterație a celei exterioare.
- `for` pe un număr dă `TypeError: ... not iterable`; `range()` vrea `int`, nu `str` sau `float`.
