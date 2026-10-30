## Ce este

O **funcție** este o bucată de cod cu nume, pe care o scrii o dată și o folosești ori de câte ori ai nevoie. Ai folosit deja multe funcții scrise de alții: `print()`, `len()`, `input()`, `sorted()`. Acum vei scrie propriile funcții, cu cuvântul cheie **`def`**:

```python
def saluta(nume):
    print(f"Salut, {nume}!")

saluta("Ana")
saluta("Mihai")
```

```text
Salut, Ana!
Salut, Mihai!
```

Primele două rânduri **definesc** funcția: îi spun lui Python ce înseamnă `saluta`. Ultimele două o **apelează**: o pun la treabă, de fiecare dată cu alt nume.

## De ce contează

Până acum, programele tale erau o singură listă lungă de instrucțiuni. Pe măsură ce cresc, apar trei probleme:
- **repetarea**: același calcul (o medie, o validare de număr) apare în mai multe locuri, iar o greșeală trebuie corectată peste tot;
- **lizibilitatea**: un program de 200 de rânduri fără structură e greu de citit;
- **testarea**: nu poți verifica separat o bucată din mijlocul programului.

Funcțiile rezolvă toate trei: dai un nume unei idei („calculează media”, „citește un număr valid”), o scrii o singură dată și o poți verifica singură. În Django, aproape tot codul tău va fi în funcții: fiecare pagină a site-ului e o funcție numită „view” (lecția 47).

## Cum funcționează

### Definirea și apelul

```python
def nume_functie(parametru1, parametru2):
    # corpul funcției, indentat cu 4 spații
    ...
```

- `def` începe definiția, urmat de numele funcției (snake_case, ca la variabile, lecția 2);
- între paranteze sunt **parametrii**: nume pentru valorile pe care funcția le primește. Pot lipsi, dar parantezele rămân: `def meniu():`;
- după `:` urmează corpul, indentat, ca la `if` și `for`.

Definiția **nu execută** corpul. Python doar ține minte funcția. Corpul rulează abia la **apel**, când scrii numele urmat de paranteze:

```python
def linie():
    print("-" * 20)

print("Înainte")
linie()
print("Între")
linie()
```

```text
Înainte
--------------------
Între
--------------------
```

O funcție trebuie definită **înainte** de rândul care o apelează, pentru că Python execută fișierul de sus în jos (lecția 1).

### Parametri și argumente

Cele două cuvinte se confundă des:
- **parametrul** e numele din definiție (`nume` din `def saluta(nume):`);
- **argumentul** e valoarea concretă dată la apel (`"Ana"` din `saluta("Ana")`).

La apel, Python leagă fiecare parametru de argumentul de pe aceeași poziție, ca la o atribuire: `nume = "Ana"`. Apoi rulează corpul.

```python
def prezinta(nume, varsta, oras):
    print(f"{nume}, {varsta} de ani, din {oras}")

prezinta("Ana Popescu", 25, "Cluj")
prezinta("Mihai Ionescu", 31, "Iași")
```

```text
Ana Popescu, 25 de ani, din Cluj
Mihai Ionescu, 31 de ani, din Iași
```

### return: funcția dă înapoi un rezultat

Funcțiile de până acum **afișau** ceva. Cele mai utile funcții însă **calculează** o valoare și o dau înapoi celui care le-a apelat, cu `return`:

```python
def media(note):
    return sum(note) / len(note)

m = media([9, 10, 8])
print(m)
print(f"Media lui Mihai: {media([7, 6, 9]):.2f}")
if media([4, 5, 3]) < 5:
    print("Corigent")
```

```text
9.0
Media lui Mihai: 7.33
Corigent
```

Apelul `media([9, 10, 8])` **devine** valoarea `9.0`, exact ca `len("Ana")` devine `3`. De aceea îl poți pune într-o variabilă, într-un f-string sau într-o condiție.

### return vs print

E diferența cea mai importantă din lecție:
- `print()` **afișează** pe ecran. Valoarea nu mai poate fi folosită de program;
- `return` **dă înapoi** valoarea. Programul decide ce face cu ea: o afișează, o salvează, o compară.

```python
def dublu_print(x):
    print(x * 2)

def dublu_return(x):
    return x * 2

a = dublu_print(5)
b = dublu_return(5)
print("a =", a)
print("b =", b)
```

```text
10
a = None
b = 10
```

`dublu_print(5)` a afișat `10`, dar n-a dat nimic înapoi, așa că `a` e `None`. O funcție care calculează ceva ar trebui aproape mereu să folosească `return`. Afișarea o lași în seama codului care o apelează.

### None: valoarea întoarsă implicit

O funcție fără `return` (sau cu un `return` gol) întoarce **`None`**, valoarea specială care înseamnă „nimic”. Ai mai întâlnit-o la `append()` și `sort()` (lecția 12), care sunt tot funcții fără rezultat.

```python
def nimic():
    pass

rezultat = nimic()
print(rezultat, type(rezultat))
print(rezultat is None)
```

```text
None <class 'NoneType'>
True
```

Ca să verifici dacă o valoare e `None`, convenția e să folosești `is None` (sau `is not None`), nu `== None`.

### return oprește funcția

`return` termină funcția **imediat**, oriunde s-ar afla, chiar și în mijlocul unei bucle sau al mai multor bucle imbricate. Așa poți ieși dintr-o căutare dublă, lucru pe care `break` nu-l poate face (lecția 11):

```python
def cauta_nota(catalog, nota_cautata):
    for rand in catalog:
        for nota in rand[1:]:
            if nota == nota_cautata:
                return rand[0]   # iese din ambele bucle și din funcție
    return None                  # am parcurs tot și n-am găsit

catalog = [["Ana", 9, 10], ["Mihai", 7, 6], ["Ioana", 10, 9]]
print(cauta_nota(catalog, 10))
print(cauta_nota(catalog, 4))
```

```text
Ana
None
```

Funcțiile cu mai multe `return` sunt normale. Un tipar des folosit e să tratezi cazurile speciale la început, cu `return` timpuriu:

```python
def calificativ(nota):
    if nota >= 9:
        return "Foarte bine"
    if nota >= 7:
        return "Bine"
    if nota >= 5:
        return "Suficient"
    return "Insuficient"

for n in [9.5, 7, 4]:
    print(n, calificativ(n))
```

```text
9.5 Foarte bine
7 Bine
4 Insuficient
```

Nu mai e nevoie de `elif` și `else`: dacă o ramură a dat `return`, restul funcției nu mai rulează.

### Mai multe valori întoarse

Pentru mai multe rezultate, întorci un tuplu și îl despachetezi la apel (lecția 13), exact cum face `divmod()`:

```python
def min_max(note):
    return min(note), max(note)

cea_mai_mica, cea_mai_mare = min_max([9, 4, 7, 10])
print(cea_mai_mica, cea_mai_mare)
```

```text
4 10
```

### De ce împărțim codul în funcții

Iată promisiunea din lecția 16: o linie de forma `"ana popescu: 9, 10, 8"` trebuia transformată într-un nume și o listă de note, iar comprehension-ul care făcea asta era greu de citit. Cu o funcție, logica primește un nume și poate avea pașii ei:

```python
def citeste_linie(linie):
    """Transformă "ana popescu: 9, 10, 8" în ("Ana Popescu", [9, 10, 8])."""
    nume, note_text = linie.split(":")
    note = [int(n) for n in note_text.split(",")]
    return nume.strip().title(), note

date_brute = ["ana popescu: 9, 10, 8", "Mihai Ionescu:7,6,9"]
catalog = dict(citeste_linie(linie) for linie in date_brute)
print(catalog)
print(citeste_linie("  ioana marin : 10,9,10 "))
```

```text
{'Ana Popescu': [9, 10, 8], 'Mihai Ionescu': [7, 6, 9]}
('Ioana Marin', [10, 9, 10])
```

Textul dintre ghilimele triple de sub `def` se numește **docstring**: explică ce face funcția. Despre el, la lecția 22.

Avantajele se văd imediat:
- comprehension-ul a devenit `dict(citeste_linie(linie) for linie in date_brute)`, care se citește ca o propoziție. `dict()` primește perechi `(cheie, valoare)`, exact ca la `dict(zip(...))` din lecția 17, iar `citeste_linie()` întoarce tocmai o astfel de pereche;
- `citeste_linie()` poate fi încercată separat, cu orice linie, ca în ultimul rând;
- dacă formatul datelor se schimbă, modifici un singur loc.

O regulă practică: o funcție face **un singur lucru**, pe care îl poți descrie într-o propoziție scurtă. Numele ei e de obicei un verb: `citeste_linie`, `calculeaza_media`, `afiseaza_tabel`.

### Ce se întâmplă „pe dedesubt”: fiecare apel are spațiul lui

La fiecare apel, Python creează un spațiu nou pentru variabilele funcției: parametrii și variabilele create în corp. Când funcția se termină, spațiul dispare. Două apeluri ale aceleiași funcții nu-și amestecă variabilele, iar variabilele din funcție nu se văd în afara ei:

<!-- fisier: functie.py -->
```python
def calculeaza_total(preturi):
    total = 0
    for pret in preturi:
        total += pret
    return total

print(calculeaza_total([4.5, 8.99]))
print(total)
```

```text
13.49
Traceback (most recent call last):
  File "functie.py", line 8, in <module>
    print(total)
          ^^^^^
NameError: name 'total' is not defined
```

`total` a existat doar cât a rulat funcția. Singurul drum prin care un rezultat iese din funcție e `return`. Regulile complete despre unde „trăiește” o variabilă sunt la lecția 20.

## Exemplu complet

Jocul „Ghicește numărul” din lecția 11, reorganizat în funcții. Fiecare funcție face un singur lucru, iar partea de jos a programului se citește ca un rezumat al jocului.

<!-- fisier: ghiceste.py -->
<!-- stdin: abc\n50\n25\n37 -->
```python
def citeste_numar(mesaj, minim, maxim):
    """Întreabă până primește un număr întreg între minim și maxim."""
    while True:
        text = input(mesaj).strip()
        if text.isdigit() and minim <= int(text) <= maxim:
            return int(text)
        print(f"Scrie un număr întreg între {minim} și {maxim}.")


def indiciu(incercare, secret):
    """Textul afișat după o încercare greșită."""
    if incercare < secret:
        return "Prea mic."
    return "Prea mare."


def joaca(secret, max_incercari):
    """Rulează o partidă; întoarce numărul de încercări sau None dacă jucătorul a pierdut."""
    for nr in range(1, max_incercari + 1):
        incercare = citeste_numar(f"[{nr}/{max_incercari}] Numărul: ", 1, 100)
        if incercare == secret:
            return nr
        print(indiciu(incercare, secret))
    return None


print("Ghicește numărul (între 1 și 100)!")
rezultat = joaca(37, 7)
if rezultat is None:
    print("Ai rămas fără încercări. Numărul era 37.")
else:
    cuvant = "încercare" if rezultat == 1 else "încercări"
    print(f"Bravo! Ai ghicit din {rezultat} {cuvant}.")
```

```text
Ghicește numărul (între 1 și 100)!
[1/7] Numărul: abc
Scrie un număr întreg între 1 și 100.
[1/7] Numărul: 50
Prea mare.
[2/7] Numărul: 25
Prea mic.
[3/7] Numărul: 37
Bravo! Ai ghicit din 3 încercări.
```

Observă:
- `citeste_numar()` folosește `return` chiar din interiorul lui `while True`: nu mai e nevoie de `break`;
- `joaca()` întoarce `None` când jucătorul pierde, iar codul de jos tratează separat cele două cazuri;
- `citeste_numar()` nu știe nimic despre joc. O poți folosi oriunde ai nevoie de un număr validat, de exemplu pentru vârstă sau pentru o notă.

## Greșeli frecvente

### 1. Uitarea parantezelor la apel

```python
def saluta():
    print("Salut!")

saluta
print(saluta)
```

Fără paranteze, funcția **nu se apelează**. Primul rând nu face nimic, iar al doilea afișează ceva de forma `<function saluta at 0x7f...>`: descrierea obiectului funcție, nu rezultatul ei. Ca să rulezi funcția, scrie `saluta()`.

### 2. print în loc de return

<!-- fisier: arie.py -->
```python
def aria(lungime, latime):
    print(lungime * latime)

total = aria(3, 4) + aria(2, 5)
```

```text
12
10
Traceback (most recent call last):
  File "arie.py", line 4, in <module>
    total = aria(3, 4) + aria(2, 5)
            ~~~~~~~~~~~^~~~~~~~~~~~
TypeError: unsupported operand type(s) for +: 'NoneType' and 'NoneType'
```

`aria()` afișează rezultatul, dar întoarce `None`, iar două valori `None` nu se pot aduna. Corect:

```python
def aria(lungime, latime):
    return lungime * latime

total = aria(3, 4) + aria(2, 5)
print(total)
```

```text
22
```

### 3. Apelul înainte de definiție

<!-- fisier: functie.py -->
```python
print(dublu(5))

def dublu(x):
    return x * 2
```

```text
Traceback (most recent call last):
  File "functie.py", line 1, in <module>
    print(dublu(5))
          ^^^^^
NameError: name 'dublu' is not defined
```

Când rulează rândul 1, Python n-a ajuns încă la `def`. Pune definițiile funcțiilor sus, iar codul care le folosește dedesubt, ca în exemplul complet.

### 4. Număr greșit de argumente

<!-- fisier: functie.py -->
```python
def prezinta(nume, varsta, oras):
    print(f"{nume}, {varsta} de ani, din {oras}")

prezinta("Ana Popescu", 25)
```

```text
Traceback (most recent call last):
  File "functie.py", line 4, in <module>
    prezinta("Ana Popescu", 25)
TypeError: prezinta() missing 1 required positional argument: 'oras'
```

Python îți spune exact ce lipsește: argumentul pentru parametrul `oras`. Cu prea multe argumente, mesajul e `takes 3 positional arguments but 4 were given`. La lecția 19 vei vedea cum faci parametri opționali, cu valori implicite.

### 5. Cod după return

```python
def media(note):
    return sum(note) / len(note)
    print("Media a fost calculată.")

print(media([8, 10]))
```

```text
9.0
```

Mesajul nu apare niciodată: `return` termină funcția, iar rândul de după el nu se mai execută. Dacă vrei să afișezi ceva, fă-o înainte de `return` sau, mai bine, în codul care apelează funcția.

## Exercițiu

În `capitole/18-functii-definire/functii_definire.py`, rescrie cu funcții **calculatorul de reducere** din exercițiul lecției 8:

1. `citeste_suma(mesaj)` întreabă până primește o sumă validă (poate avea zecimale și virgulă) și întoarce un `float`;
2. `cost_transport(valoare_cos)` întoarce 15 sub 100 de lei și 0 de la 100 de lei în sus;
3. `reducere(valoare_cos, cod)` întoarce, după regulile din lecția 8, un tuplu `(reducere_lei, mesaj)`: `mesaj` e `""` sau explicația (cod necunoscut, coș sub 150 lei pentru `VARA2026`). Funcția nu afișează nimic; mesajul îl afișează codul principal;
4. `afiseaza_bon(valoare_cos, reducere_lei, transport)` afișează bonul cu 2 zecimale;
5. la final, codul principal are doar câteva rânduri: citește datele, apelează funcțiile și afișează bonul.

Verifică funcțiile **separat**, înainte de codul principal, cu câteva `print()`-uri de felul `print(cost_transport(99.99), cost_transport(100))`.

## Pe scurt

- `def nume(parametri):` definește o funcție; corpul rulează doar la apel: `nume(argumente)`.
- Parametrii sunt numele din definiție, argumentele sunt valorile de la apel.
- `return valoare` dă rezultatul înapoi și oprește funcția imediat, chiar din mai multe bucle imbricate.
- O funcție fără `return` întoarce `None`; verifici cu `is None`.
- `return a, b` întoarce un tuplu, pe care îl despachetezi la apel.
- O funcție bună face un singur lucru, are un nume-verb clar și întoarce rezultatul, în loc să-l afișeze.
