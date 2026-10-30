## Ce este

La lecția 18, fiecare parametru primea argumentul de pe aceeași poziție, iar toate erau obligatorii. Python îți permite mult mai multă flexibilitate:
- **valori implicite**: parametri opționali, care au o valoare dacă nu primesc alta;
- **argumente keyword**: argumente date după nume (`oras="Cluj"`), nu după poziție;
- **`*args`**: oricâte argumente poziționale;
- **`**kwargs`**: oricâte argumente keyword.

```python
def saluta(nume, salut="Salut", semn="!"):
    print(f"{salut}, {nume}{semn}")

saluta("Ana")
saluta("Mihai", "Bună ziua")
saluta("Ioana", semn="?")
```

```text
Salut, Ana!
Bună ziua, Mihai!
Salut, Ioana?
```

## De ce contează

Ai folosit deja toate acestea fără să știi cum funcționează: `print(..., sep=".", end="")` (lecția 5), `sorted(..., reverse=True)` (lecția 12), `enumerate(..., start=1)` (lecția 17), `max(..., default=0)`. Sunt argumente keyword cu valori implicite. Așa se scriu funcțiile ușor de folosit: cazul obișnuit e simplu, iar cazurile speciale se cer explicit, după nume.

În Django vei întâlni la fiecare pas apeluri ca `path("articol/<int:id>/", detaliu, name="detaliu")` sau `models.CharField(max_length=200, blank=True)`, iar în codul altora vei vedea des `*args` și `**kwargs`.

## Cum funcționează

### Valori implicite

Un parametru cu `=valoare` în definiție e **opțional**: dacă apelul nu-i dă argument, primește valoarea implicită.

```python
def pret_final(pret, tva=0.21, reducere=0):
    return round(pret * (1 + tva) * (1 - reducere), 2)

print(pret_final(100))
print(pret_final(100, 0.11))
print(pret_final(100, 0.11, 0.1))
```

```text
121.0
111.0
99.9
```

Regula: parametrii **cu** valoare implicită stau **după** cei fără. `def f(a, b=1)` e corect, `def f(a=1, b)` dă eroare (vezi greșelile frecvente).

### Argumente keyword

La apel, poți da un argument **după numele parametrului**:

```python
def pret_final(pret, tva=0.21, reducere=0):
    return round(pret * (1 + tva) * (1 - reducere), 2)

print(pret_final(100, reducere=0.1))
print(pret_final(reducere=0.1, pret=100, tva=0.11))
```

```text
108.9
99.9
```

Avantajele:
- poți sări peste parametrii opționali din mijloc: în primul apel, `tva` rămâne implicit, iar `reducere` primește valoare;
- ordinea nu mai contează, pentru că fiecare valoare spune unde merge;
- apelul se explică singur: `pret_final(100, reducere=0.1)` e mai clar decât `pret_final(100, 0.21, 0.1)`.

Poți amesteca cele două feluri, dar **argumentele poziționale vin primele**, iar cele keyword după ele.

### Parametri care se dau doar după nume

Un `*` singur în lista de parametri spune: „tot ce urmează se dă **doar** după nume”. E util pentru opțiunile care ar fi confuze ca simple valori:

<!-- fisier: tabel.py -->
```python
def afiseaza_note(note, *, sortat=False, descrescator=False):
    if sortat:
        note = sorted(note, reverse=descrescator)
    print(note)

afiseaza_note([9, 4, 10], sortat=True)
afiseaza_note([9, 4, 10], sortat=True, descrescator=True)
afiseaza_note([9, 4, 10], True)
```

```text
[4, 9, 10]
[10, 9, 4]
Traceback (most recent call last):
  File "tabel.py", line 8, in <module>
    afiseaza_note([9, 4, 10], True)
TypeError: afiseaza_note() takes 1 positional argument but 2 were given
```

Un apel de felul `afiseaza_note(note, True, False)` nu spune nimic celui care îl citește, iar Python îl refuză. Cu nume, apelul e clar.

### *args: oricâte argumente poziționale

Un parametru cu `*` în față adună **toate** argumentele poziționale rămase într-un **tuplu**. Numele convențional e `args`, dar poți alege unul care spune ce conține:

```python
def media(*note):
    print("am primit:", note)
    return sum(note) / len(note)

print(media(9, 10))
print(media(7, 6, 9, 10))
```

```text
am primit: (9, 10)
9.5
am primit: (7, 6, 9, 10)
8.0
```

Seamănă cu `*` de la despachetare (lecția 13): `prima, *restul = lista`. Așa funcționează și `print()`, care acceptă oricâte valori.

### **kwargs: oricâte argumente keyword

Cu `**` în față, un parametru adună argumentele keyword rămase într-un **dicționar** (numele convențional e `kwargs`):

```python
def fisa(nume, **detalii):
    print(f"== {nume} ==")
    for cheie, valoare in detalii.items():
        print(f"{cheie}: {valoare}")

fisa("Ana Popescu", varsta=25, oras="Cluj")
fisa("Mihai Ionescu", oras="Iași", profesie="programator", hobby="șah")
```

```text
== Ana Popescu ==
varsta: 25
oras: Cluj
== Mihai Ionescu ==
oras: Iași
profesie: programator
hobby: șah
```

Ordinea completă a parametrilor, când apar toate felurile, e: obișnuiți, `*args`, doar-după-nume, `**kwargs`. În practică, rar ai nevoie de toate deodată.

### * și ** la apel: despachetarea argumentelor

La **apel**, `*` și `**` fac invers: desfac o colecție în argumente separate.

```python
def prezinta(nume, varsta, oras):
    print(f"{nume}, {varsta} de ani, din {oras}")

persoana = ("Ana Popescu", 25, "Cluj")
prezinta(*persoana)

date = {"oras": "Iași", "nume": "Mihai Ionescu", "varsta": 31}
prezinta(**date)

note = [9, 10, 8]
print(*note, sep=" | ")
```

```text
Ana Popescu, 25 de ani, din Cluj
Mihai Ionescu, 31 de ani, din Iași
9 | 10 | 8
```

`prezinta(*persoana)` e la fel ca `prezinta("Ana Popescu", 25, "Cluj")`, iar `prezinta(**date)` dă fiecare valoare după cheia ei.

### Ce se întâmplă „pe dedesubt”: valoarea implicită se creează o singură dată

Valoarea implicită e calculată **o singură dată**, când Python execută rândul cu `def`, nu la fiecare apel. Pentru numere și stringuri nu contează, fiindcă sunt imutabile. Pentru o listă sau un dicționar însă, toate apelurile împart **același obiect**:

```python
def adauga_produs(produs, cos=[]):
    cos.append(produs)
    return cos

print(adauga_produs("pâine"))
print(adauga_produs("lapte"))
print(adauga_produs("ouă"))
```

```text
['pâine']
['pâine', 'lapte']
['pâine', 'lapte', 'ouă']
```

Fiecare apel trebuia să înceapă cu un coș gol. În schimb, lista implicită a crescut de la un apel la altul. E aceeași problemă de aliasing de la lecția 12, doar că aici e ascunsă în definiție.

Soluția standard: valoarea implicită e `None`, iar lista se creează **în** funcție, la fiecare apel:

```python
def adauga_produs(produs, cos=None):
    if cos is None:
        cos = []
    cos.append(produs)
    return cos

print(adauga_produs("pâine"))
print(adauga_produs("lapte"))
```

```text
['pâine']
['lapte']
```

Regula de reținut: **nu folosi niciodată o listă, un dicționar sau un set ca valoare implicită**. Folosește `None`.

## Exemplu complet

O funcție de raport pentru un magazin ca cel din lecția 14 (aici, fiecare produs are un tuplu `(preț, stoc)`), cu opțiuni după nume și cu un număr variabil de categorii de produse.

<!-- fisier: raport.py -->
```python
def raport(titlu, *categorii, moneda="lei", latime=30, doar_in_stoc=False):
    """Afișează produsele din toate categoriile primite, cu prețuri aliniate."""
    print(f"{titlu:^{latime}}")
    print("=" * latime)
    total = 0
    for categorie in categorii:
        for produs, (pret, stoc) in categorie.items():
            if doar_in_stoc and stoc == 0:
                continue
            marcaj = "" if stoc else " *"
            print(f"{produs + marcaj:<{latime - 12}}{pret:>8.2f} {moneda}")
            total += pret
    print("-" * latime)
    print(f"{'Total prețuri':<{latime - 12}}{total:>8.2f} {moneda}")


lactate = {"lapte": (8.99, 5), "iaurt": (3.49, 0)}
panificatie = {"pâine": (4.5, 20), "cornuri": (2.0, 12)}
cafea = {"cafea boabe": (32.0, 3)}

raport("Toate produsele", lactate, panificatie, cafea)
print()
raport("În stoc", lactate, cafea, doar_in_stoc=True, latime=26)
```

```text
       Toate produsele        
==============================
lapte                 8.99 lei
iaurt *               3.49 lei
pâine                 4.50 lei
cornuri               2.00 lei
cafea boabe          32.00 lei
------------------------------
Total prețuri        50.98 lei

         În stoc          
==========================
lapte             8.99 lei
cafea boabe      32.00 lei
--------------------------
Total prețuri    40.99 lei
```

Observă:
- `*categorii` acceptă oricâte dicționare, deci același cod merge pentru una sau zece categorii;
- opțiunile `moneda`, `latime` și `doar_in_stoc` stau după `*categorii`, deci se pot da **doar** după nume. Apelul al doilea se citește singur;
- `for produs, (pret, stoc) in categorie.items():` despachetează și tuplul din valoare (lecția 17);
- `*` marchează produsele fără stoc.

## Greșeli frecvente

### 1. Parametru obligatoriu după unul cu valoare implicită

<!-- fisier: arg.py -->
```python
def saluta(salut="Salut", nume):
    print(f"{salut}, {nume}!")
```

```text
  File "arg.py", line 1
    def saluta(salut="Salut", nume):
                              ^^^^
SyntaxError: parameter without a default follows parameter with a default
```

Python n-ar ști ce înseamnă `saluta("Ana")`: e salutul sau numele? Pune parametrii obligatorii primii: `def saluta(nume, salut="Salut"):`.

### 2. Argument pozițional după unul keyword

<!-- fisier: arg.py -->
```python
def prezinta(nume, varsta, oras):
    print(nume, varsta, oras)

prezinta(nume="Ana", 25, "Cluj")
```

```text
  File "arg.py", line 4
    prezinta(nume="Ana", 25, "Cluj")
                                   ^
SyntaxError: positional argument follows keyword argument
```

La apel, argumentele poziționale vin întâi, apoi cele după nume: `prezinta("Ana", 25, oras="Cluj")`.

### 3. Același parametru primit de două ori

<!-- fisier: arg.py -->
```python
def prezinta(nume, varsta, oras):
    print(nume, varsta, oras)

prezinta("Ana", 25, nume="Ana Popescu", oras="Cluj")
```

```text
Traceback (most recent call last):
  File "arg.py", line 4, in <module>
    prezinta("Ana", 25, nume="Ana Popescu", oras="Cluj")
TypeError: prezinta() got multiple values for argument 'nume'
```

`"Ana"` a mers deja în `nume`, după poziție, iar apoi `nume=` a încercat să-i dea altă valoare.

### 4. Nume de argument scris greșit

<!-- fisier: arg.py -->
```python
def pret_final(pret, tva=0.21, reducere=0):
    return round(pret * (1 + tva) * (1 - reducere), 2)

print(pret_final(100, reduceri=0.1))
```

```text
Traceback (most recent call last):
  File "arg.py", line 4, in <module>
    print(pret_final(100, reduceri=0.1))
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: pret_final() got an unexpected keyword argument 'reduceri'
```

E un avantaj al argumentelor keyword: o greșeală de tastare dă o eroare clară, în loc să treacă neobservată. Numele trebuie să fie exact cel din definiție.

### 5. Listă ca valoare implicită

```python
def inscrie(elev, clasa=[]):
    clasa.append(elev)
    return clasa

clasa_a = inscrie("Ana")
clasa_b = inscrie("Mihai")
print(clasa_a, clasa_b)
print(clasa_a is clasa_b)
```

```text
['Ana', 'Mihai'] ['Ana', 'Mihai']
True
```

Cele două „clase” sunt de fapt aceeași listă, creată o singură dată, la `def` (vezi „pe dedesubt”). Folosește `clasa=None` și creează lista în funcție.

## Exercițiu

În `capitole/19-argumente/argumente.py`, scrie funcții pentru **catalogul clasei** din lecția 12:

1. `media(*note, zecimale=2)` întoarce media notelor primite, rotunjită; fără nicio notă întoarce `None` (fără eroare);
2. `adauga_elev(nume, *note, catalog=None)` adaugă elevul și notele lui într-un dicționar `nume -> listă de note` și întoarce dicționarul; dacă nu primește un catalog, creează unul nou (atenție la capcana din lecție);
3. `afiseaza_catalog(catalog, *, sortat_dupa="nume", prag_trecere=5)` afișează un tabel cu numele, notele și media fiecăruia; `sortat_dupa` poate fi `"nume"` sau `"medie"` (media descrescător; folosește trucul cu tupluri din lecția 17); elevii cu media sub prag sunt marcați cu `*`;
4. construiește un catalog cu 4 elevi apelând `adauga_elev` (primul apel fără `catalog`, celelalte cu `catalog=`) și afișează-l în ambele ordini;
5. apelează `media(*catalog["Ana"])` ca să vezi despachetarea la apel.

## Pe scurt

- `def f(a, b=valoare):` face parametrul `b` opțional; parametrii cu valoare implicită stau după cei obligatorii.
- La apel, `f(1, b=2)`: argumentele poziționale întâi, apoi cele după nume, care pot fi în orice ordine.
- Parametrii de după un `*` singur se pot da doar după nume.
- `*args` adună argumentele poziționale rămase într-un tuplu; `**kwargs` adună argumentele keyword rămase într-un dicționar.
- La apel, `f(*secventa)` și `f(**dictionar)` desfac colecțiile în argumente.
- Valoarea implicită se creează o singură dată: pentru liste și dicționare folosește `None` și creează obiectul în funcție.
