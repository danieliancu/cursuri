## Ce este

Un **tuplu** (tipul `tuple`) este o colecție ordonată, ca lista, dar **imutabilă**: după ce l-ai creat, nu-i mai poți schimba, adăuga sau șterge elemente. Se scrie cu paranteze rotunde:

```python
persoana = ("Ana Popescu", 25, "Cluj")
print(persoana)
print(persoana[0], persoana[-1])
print(len(persoana), type(persoana))
```

```text
('Ana Popescu', 25, 'Cluj')
Ana Popescu Cluj
3 <class 'tuple'>
```

Strâns legată de tupluri e **despachetarea** (în engleză „unpacking”): elementele unui tuplu (sau ale oricărei secvențe) sunt atribuite dintr-o dată mai multor variabile.

```python
persoana = ("Ana Popescu", 25, "Cluj")
nume, varsta, oras = persoana
print(f"{nume} are {varsta} de ani și locuiește în {oras}.")
```

```text
Ana Popescu are 25 de ani și locuiește în Cluj.
```

## De ce contează

Listele sunt potrivite pentru colecții care cresc și scad: o listă de cumpărături, elevii unei clase. Multe date au însă o structură **fixă**: un punct are exact două coordonate, o dată calendaristică are zi, lună și an, o înregistrare are nume, vârstă și oraș. Pentru acestea, tuplul spune clar „acestea sunt părțile unui singur lucru și nu se schimbă”, iar Python te oprește dacă încerci să-l modifici din greșeală.

Despachetarea o vei folosi peste tot: când parcurgi perechi de valori, când o funcție întoarce mai multe rezultate (lecția 18) sau când iterezi peste un dicționar (lecția 14).

## Cum funcționează

### Crearea tuplurilor

```python
punct = (3, 4)
data = (29, 10, 2026)
gol = ()
un_element = ("Cluj",)       # virgula e obligatorie
fara_paranteze = 1, 2, 3     # parantezele sunt opționale
din_lista = tuple(["a", "b"])
print(un_element, fara_paranteze, din_lista)
```

```text
('Cluj',) (1, 2, 3) ('a', 'b')
```

Ce face un tuplu e de fapt **virgula**, nu parantezele. Parantezele doar grupează. De aceea `("Cluj")` e un simplu string între paranteze, iar `("Cluj",)` e un tuplu cu un element. Tot de aceea, la lecția 3, `pret = 3,5` a creat tuplul `(3, 5)`.

### Ce poți și ce nu poți face

Tot ce **citește** funcționează ca la liste: indexare, slicing, `len()`, `in`, `for`, `count()`, `index()`, `sorted()` (care întoarce însă o listă), `+` și `*` (care creează tupluri noi).

```python
zile = ("luni", "marți", "miercuri", "joi", "vineri")
print(zile[1:3])
print("sâmbătă" in zile)
print(zile + ("sâmbătă", "duminică"))
for zi in zile[:2]:
    print(zi.upper())
```

```text
('marți', 'miercuri')
False
('luni', 'marți', 'miercuri', 'joi', 'vineri', 'sâmbătă', 'duminică')
LUNI
MARȚI
```

Tot ce **modifică** lipsește: un tuplu nu are `append`, `remove`, `sort` și nici atribuire pe poziție.

### Testul „este unul dintre”

La lecția 7 am promis o scriere scurtă pentru „orașul e Cluj sau Iași”. Iat-o:

```python
oras = "Iași"
print(oras in ("Cluj", "Iași", "Timișoara"))
```

```text
True
```

E mult mai clar decât `oras == "Cluj" or oras == "Iași" or oras == "Timișoara"`. Se folosește un tuplu (nu o listă) pentru că grupul de valori e fix.

### Despachetarea

Numărul de variabile din stânga trebuie să fie egal cu numărul de elemente:

```python
zi, luna, an = (29, 10, 2026)
print(f"{zi:02}.{luna:02}.{an}")

x, y = "AB"                       # funcționează pe orice secvență
prenume, nume_familie = "Ana Popescu".split()
print(x, y, prenume, nume_familie)
```

```text
29.10.2026
A B Ana Popescu
```

Cu `*`, o variabilă „adună” restul elementelor într-o **listă**:

```python
note = [10, 9, 7, 8, 6]
prima, *restul = note
*primele, ultima = note
cea_mai_mare, *_, cea_mai_mica = sorted(note, reverse=True)
print(prima, restul)
print(primele, ultima)
print(cea_mai_mare, cea_mai_mica)
```

```text
10 [9, 7, 8, 6]
[10, 9, 7, 8] 6
10 6
```

`_` e convenția pentru „valoare de care nu am nevoie” (ai văzut-o la `for _ in range(...)`, lecția 10).

### Interschimbarea a două variabile

În multe limbaje ai nevoie de o variabilă temporară. În Python, despachetarea o face într-un rând:

```python
a = "Cluj"
b = "Iași"
a, b = b, a
print(a, b)
```

```text
Iași Cluj
```

Partea din dreapta, `b, a`, creează întâi tuplul `("Iași", "Cluj")`, iar apoi acesta e despachetat în `a` și `b`.

### Despachetarea în for

Când parcurgi o listă de tupluri, poți despacheta direct în `for`:

```python
persoane = [
    ("Ana Popescu", 25, "Cluj"),
    ("Mihai Ionescu", 31, "Iași"),
    ("Ioana Marin", 19, "Brașov"),
]
for nume, varsta, oras in persoane:
    print(f"{nume:<14} vârsta {varsta:>2}  {oras}")
```

```text
Ana Popescu    vârsta 25  Cluj
Mihai Ionescu  vârsta 31  Iași
Ioana Marin    vârsta 19  Brașov
```

E mult mai lizibil decât `persoana[0]`, `persoana[1]`, `persoana[2]`: fiecare valoare are un nume care spune ce e.

### Mai multe valori deodată

Unele funcții întorc mai multe rezultate sub forma unui tuplu, pe care îl despachetezi. Un exemplu din Python: `divmod()` dă deodată rezultatul lui `//` și pe cel al lui `%` (lecția 3).

```python
rezultat = divmod(135, 60)
print(rezultat)
ore, minute = divmod(135, 60)
print(f"{ore} ore și {minute} minute")
```

```text
(2, 15)
2 ore și 15 minute
```

La lecția 18 vei scrie propriile funcții care întorc mai multe valori exact așa: `return minim, maxim`.

### Ce se întâmplă „pe dedesubt”: imutabil nu înseamnă „înghețat complet”

Un tuplu nu-și poate schimba **elementele**: fiecare poziție arată mereu spre același obiect. Dacă însă acel obiect e mutabil, de exemplu o listă, obiectul în sine se poate modifica:

```python
elev = ("Ana", [9, 10])
elev[1].append(8)
print(elev)
```

```text
('Ana', [9, 10, 8])
```

Tuplul arată tot spre aceeași listă, doar că lista a crescut. În practică, pune în tupluri valori imutabile (numere, stringuri, alte tupluri). Atunci tuplul e cu adevărat neschimbabil și poate fi folosit în locuri unde Python cere asta, de exemplu ca cheie de dicționar (lecția 14).

## Exemplu complet

Programul zilei Anei: activitățile sunt tupluri `(ora, minut, activitate, durata_minute)`. Programul le sortează, calculează orele de final și semnalează suprapunerile.

<!-- fisier: program_zi.py -->
```python
activitati = [
    (14, 0, "Curs Python", 90),
    (9, 30, "Sală", 60),
    (12, 0, "Prânz", 45),
    (15, 0, "Ședință", 30),
    (8, 0, "Cafea", 20),
]

ultimul_final = 0  # în minute de la miezul nopții
for ora, minut, nume, durata in sorted(activitati):
    start = ora * 60 + minut
    final = start + durata
    ora_final, minut_final = divmod(final, 60)

    marcaj = "  <- se suprapune!" if start < ultimul_final else ""
    print(f"{ora:02}:{minut:02}-{ora_final:02}:{minut_final:02}  {nume}{marcaj}")
    ultimul_final = max(ultimul_final, final)

total = 0
for *_, durata in activitati:
    total += durata
ore, minute = divmod(total, 60)
print(f"\nTimp ocupat: {ore} h {minute} min")
```

```text
08:00-08:20  Cafea
09:30-10:30  Sală
12:00-12:45  Prânz
14:00-15:30  Curs Python
15:00-15:30  Ședință  <- se suprapune!

Timp ocupat: 4 h 5 min
```

Observă:
- `sorted()` pe o listă de tupluri le sortează după primul element, iar la egalitate după al doilea și așa mai departe. Așa obținem ordinea cronologică fără niciun efort;
- orele sunt transformate în minute de la miezul nopții (`ora * 60 + minut`), ca să poată fi comparate și adunate ușor; `divmod()` le transformă înapoi în ore și minute;
- `ultimul_final` ține minte cel mai târziu moment la care s-a terminat ceva până acum; o activitate care începe înaintea lui se suprapune cu una anterioară;
- `for *_, durata in activitati:` ia doar ultimul element din fiecare tuplu.

## Greșeli frecvente

### 1. Încercarea de a modifica un tuplu

<!-- fisier: tuplu.py -->
```python
data = (29, 10, 2026)
data[0] = 30
```

```text
Traceback (most recent call last):
  File "tuplu.py", line 2, in <module>
    data[0] = 30
    ~~~~^^^
TypeError: 'tuple' object does not support item assignment
```

Un tuplu nu se poate modifica. Creezi unul nou, eventual pornind de la cel vechi:

```python
data = (29, 10, 2026)
zi, luna, an = data
data = (zi + 1, luna, an)
```

Dacă trebuie să modifici des datele, probabil ai nevoie de o listă, nu de un tuplu.

### 2. Metode de listă pe un tuplu

<!-- fisier: tuplu.py -->
```python
orase = ("Cluj", "Iași")
orase.append("Brașov")
```

```text
Traceback (most recent call last):
  File "tuplu.py", line 2, in <module>
    orase.append("Brașov")
    ^^^^^^^^^^^^
AttributeError: 'tuple' object has no attribute 'append'
```

`AttributeError` înseamnă că obiectul nu are metoda (sau atributul) cerut. Poți crea un tuplu nou (`orase = orase + ("Brașov",)`) sau, dacă lista de orașe crește, poți folosi de la început o listă.

### 3. Tuplu cu un element, fără virgulă

```python
orase = ("Cluj")
print(type(orase), len(orase))
for oras in orase:
    print(oras, end=" ")
```

```text
<class 'str'> 4
C l u j 
```

Fără virgulă, `("Cluj")` e doar stringul `"Cluj"`, iar `for` îl parcurge literă cu literă. Corect: `("Cluj",)`.

Invers, o virgulă uitată la final creează un tuplu fără să vrei:

```python
nume = "Ana",
print(f"Salut, {nume}!")
```

```text
Salut, ('Ana',)!
```

### 4. Număr greșit de variabile la despachetare

<!-- fisier: tuplu.py -->
```python
nume, varsta = ("Ana Popescu", 25, "Cluj")
```

```text
Traceback (most recent call last):
  File "tuplu.py", line 1, in <module>
    nume, varsta = ("Ana Popescu", 25, "Cluj")
    ^^^^^^^^^^^^
ValueError: too many values to unpack (expected 2)
```

Iar invers:

<!-- fisier: tuplu.py -->
```python
prenume, al_doilea, nume_familie = "Ana Popescu".split()
```

```text
Traceback (most recent call last):
  File "tuplu.py", line 1, in <module>
    prenume, al_doilea, nume_familie = "Ana Popescu".split()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: not enough values to unpack (expected 3, got 2)
```

Greșeala apare des cu datele introduse de utilizator, care nu au mereu forma la care te aștepți. Verifică întâi lungimea (`len(bucati) == 3`) sau folosește `*`, care acceptă orice număr de elemente rămase:

```python
prenume, *restul = "Ana Maria Popescu".split()
print(prenume, restul)
```

```text
Ana ['Maria', 'Popescu']
```

### 5. Parantezele care lipsesc din tuplu, în for

<!-- fisier: tuplu.py -->
```python
for oras in "Cluj", "Iași":
    print(oras)
print(len("Cluj", "Iași"))
```

```text
Cluj
Iași
Traceback (most recent call last):
  File "tuplu.py", line 3, in <module>
    print(len("Cluj", "Iași"))
          ^^^^^^^^^^^^^^^^^^^
TypeError: len() takes exactly one argument (2 given)
```

În `for`, virgulele au creat un tuplu, deci bucla a mers. Într-un apel de funcție însă, virgulele **separă argumente**, iar `len()` a primit două în loc de unul. Ca să transmiți un tuplu unei funcții, pune parantezele: `len(("Cluj", "Iași"))`. Regula practică: pune mereu parantezele la tupluri, cu excepția despachetării și a lui `return`.

## Exercițiu

În `capitole/13-tupluri/tupluri.py`, scrie un program pentru **distanțele dintre orașe**:

1. o listă de tupluri `(oras, x, y)` cu coordonatele (în km, pe o hartă imaginară) a cel puțin 5 orașe; de exemplu `("Cluj", 0, 0)`, `("Iași", 280, 120)`;
2. cere două orașe de la utilizator; dacă unul nu există, afișează orașele disponibile și cere din nou;
3. găsește coordonatele lor parcurgând lista cu despachetare în `for` și calculează distanța: `((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5`;
4. afișează distanța cu o zecimală, apoi durata cu mașina la 80 km/h, în ore și minute, folosind `divmod()`;
5. la final, afișează **perechea de orașe cele mai apropiate** dintre toate (două bucle `for` imbricate), cu interschimbarea numelor astfel încât primul să fie mereu cel mai mic alfabetic.

## Pe scurt

- Un tuplu e o colecție ordonată și **imutabilă**: `(1, 2)`; virgula face tuplul, deci un element se scrie `("Cluj",)`.
- Se citește ca o listă (indexare, slicing, `in`, `for`), dar nu are metode care modifică.
- Tuplurile sunt potrivite pentru date cu structură fixă, iar `x in ("a", "b")` e testul „este unul dintre”.
- Despachetare: `a, b = (1, 2)`; `prima, *restul = lista`; `a, b = b, a` interschimbă două variabile.
- `for nume, varsta in persoane:` despachetează fiecare element al listei.
- Prea multe sau prea puține variabile la despachetare dau `ValueError`; metodele care lipsesc dau `AttributeError`.
