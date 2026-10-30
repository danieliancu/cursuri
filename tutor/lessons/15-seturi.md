## Ce este

Un **set** (în română „mulțime”, tipul `set`) este o colecție de elemente **unice** și **fără ordine**. Se scrie cu acolade, ca un dicționar, dar fără perechi:

```python
note = {9, 7, 10, 7, 9, 9}
print(note)
print(len(note), type(note))
print(10 in note)
```

```text
{9, 10, 7}
3 <class 'set'>
True
```

Duplicatele au dispărut singure: un set ține minte doar **dacă** un element există, nu de câte ori sau pe ce poziție.

## De ce contează

Seturile răspund rapid la trei feluri de întrebări care apar des:
- **„Am mai văzut asta?”**: numere deja încercate într-un joc, e-mailuri deja înscrise, pagini deja vizitate;
- **„Care sunt valorile distincte?”**: orașele din care vin clienții, etichetele folosite pe un blog;
- **„Ce au în comun / ce diferă?”** între două grupuri: produse pe care le au ambele liste de cumpărături, elevi înscriși la un curs, dar nu și la celălalt.

Toate se pot face și cu liste, dar mai lent și cu mai mult cod. Seturile le rezolvă într-un rând, cu operații de mulțimi, ca la matematică.

## Cum funcționează

### Crearea unui set

```python
orase = {"Cluj", "Iași", "Cluj", "Brașov"}
din_lista = set([3, 1, 3, 2, 1])
litere = set("banana")
gol = set()  # NU {} — aceea e un dicționar gol
print(sorted(orase))
print(din_lista)
print(sorted(litere))
print(type(gol), type({}))
```

```text
['Brașov', 'Cluj', 'Iași']
{1, 2, 3}
['a', 'b', 'n']
<class 'set'> <class 'dict'>
```

De ce `sorted()`? Un set **nu are ordine**. Când îl afișezi, Python îl arată într-o ordine care depinde de detalii interne (vezi „pe dedesubt”), iar la seturile de stringuri ea se poate schimba **de la o rulare la alta**. Când vrei o afișare previzibilă, transformi setul în listă sortată.

Elementele unui set trebuie să fie imutabile, exact ca cheile unui dicționar (lecția 14): numere, stringuri, tupluri, dar nu liste.

### Adăugare și ștergere

```python
incercate = {50, 25}
incercate.add(37)
incercate.add(25)        # există deja: nu se întâmplă nimic
print(sorted(incercate))

incercate.remove(50)     # KeyError dacă nu există
incercate.discard(99)    # nu dă eroare dacă nu există
print(sorted(incercate))
```

```text
[25, 37, 50]
[25, 37]
```

`add()` e echivalentul lui `append()` de la liste. Diferența e că un element existent nu se dublează.

### Testul de apartenență

`in` pe un set e foarte rapid, oricât de mare ar fi setul. Pe o listă, Python compară elementele unul câte unul. Pentru verificări repetate de felul „am mai văzut asta?”, setul e alegerea potrivită:

```python
vazute = set()
for numar in [5, 3, 5, 8, 3, 1]:
    if numar in vazute:
        print(f"{numar} apare din nou")
    else:
        vazute.add(numar)
```

```text
5 apare din nou
3 apare din nou
```

Gândește-te la jocul din lecția 11, unde numerele încercate erau ținute într-un text cu spații. Cu un set, aceeași idee devine `if numar in incercate:` și `incercate.add(numar)`.

### Operații de mulțimi

Lista Anei și lista lui Mihai:

```python
ana = {"pâine", "lapte", "cafea", "mere"}
mihai = {"pâine", "bere", "mere", "chipsuri"}

print("ambele:     ", sorted(ana & mihai))   # intersecție
print("oricare:    ", sorted(ana | mihai))   # uniune
print("doar Ana:   ", sorted(ana - mihai))   # diferență
print("doar unul:  ", sorted(ana ^ mihai))   # diferență simetrică
```

```text
ambele:      ['mere', 'pâine']
oricare:     ['bere', 'cafea', 'chipsuri', 'lapte', 'mere', 'pâine']
doar Ana:    ['cafea', 'lapte']
doar unul:   ['bere', 'cafea', 'chipsuri', 'lapte']
```

| Operator | Metodă | Rezultat |
|---|---|---|
| `a & b` | `a.intersection(b)` | elementele din **ambele** |
| `a \| b` | `a.union(b)` | elementele din **oricare** |
| `a - b` | `a.difference(b)` | elementele din `a` care **nu** sunt în `b` |
| `a ^ b` | `a.symmetric_difference(b)` | elementele din **exact unul** dintre ele |

Metodele acceptă orice secvență, nu doar seturi: `ana.union(["ouă", "unt"])` funcționează, pe când `ana | ["ouă", "unt"]` dă eroare.

Există și comparații între mulțimi:

```python
necesare = {"pâine", "lapte"}
cos = {"pâine", "lapte", "cafea"}
print(necesare <= cos)               # submulțime: toate sunt în coș?
print(necesare.isdisjoint({"bere"})) # nimic în comun?
```

```text
True
True
```

### Eliminarea duplicatelor dintr-o listă

```python
orase = ["Cluj", "Iași", "Cluj", "Brașov", "Iași", "Cluj"]
unice = sorted(set(orase))
print(unice)
print(f"{len(orase)} înregistrări, {len(unice)} orașe distincte")
```

```text
['Brașov', 'Cluj', 'Iași']
6 înregistrări, 3 orașe distincte
```

`set()` pierde ordinea. Dacă ai nevoie de elementele unice **în ordinea primei apariții**, folosește un dicționar, care păstrează ordinea cheilor (lecția 14):

```python
orase = ["Cluj", "Iași", "Cluj", "Brașov", "Iași", "Cluj"]
print(list(dict.fromkeys(orase)))
```

```text
['Cluj', 'Iași', 'Brașov']
```

`dict.fromkeys(orase)` creează un dicționar cu orașele drept chei (toate cu valoarea `None`). Cheile duplicate dispar, iar ordinea primei apariții rămâne.

### Ce se întâmplă „pe dedesubt”: setul e un dicționar fără valori

Un set funcționează exact ca un dicționar care are doar chei. Pentru fiecare element, Python calculează un hash (lecția 14), care îi spune direct unde e elementul în memorie. De aici vin toate proprietățile setului:
- `in` e rapid, pentru că nu se caută element cu element;
- elementele trebuie să fie imutabile, pentru că hash-ul lor nu are voie să se schimbe;
- nu există ordine, pentru că poziția depinde de hash, nu de momentul adăugării.

Hash-ul unui string e calculat diferit la fiecare pornire a lui Python (o măsură de securitate), de aceea ordinea afișată a unui set de stringuri variază de la o rulare la alta. Programul tău nu trebuie să depindă niciodată de ea.

## Exemplu complet

Înscrierile la două cursuri. Programul citește listele de înscriși (cu duplicate și scrieri diferite), le curăță și răspunde la câteva întrebări.

<!-- fisier: cursuri.py -->
```python
python_inscrisi = ["Ana", "mihai", "Ioana", "Andrei", "ana", "Elena"]
django_inscrisi = ["Mihai", "Ana", "Radu", "Elena", "radu", "Sorin"]

python_curs = set()
for nume in python_inscrisi:
    python_curs.add(nume.strip().title())
django_curs = set()
for nume in django_inscrisi:
    django_curs.add(nume.strip().title())

print(f"Python: {len(python_curs)} elevi unici (din {len(python_inscrisi)} înscrieri)")
print(f"Django: {len(django_curs)} elevi unici (din {len(django_inscrisi)} înscrieri)")
print()

ambele = python_curs & django_curs
print("La ambele cursuri:      ", ", ".join(sorted(ambele)))
print("Doar Python:            ", ", ".join(sorted(python_curs - django_curs)))
print("Doar Django:            ", ", ".join(sorted(django_curs - python_curs)))
print("Total elevi distincți:  ", len(python_curs | django_curs))

# Django se predă după Python: cine s-a înscris la Django fără Python?
fara_baza = django_curs - python_curs
if fara_baza:
    print(f"\nAtenție: {len(fara_baza)} elevi la Django fără cursul de Python: {', '.join(sorted(fara_baza))}")
```

```text
Python: 5 elevi unici (din 6 înscrieri)
Django: 5 elevi unici (din 6 înscrieri)

La ambele cursuri:       Ana, Elena, Mihai
Doar Python:             Andrei, Ioana
Doar Django:             Radu, Sorin
Total elevi distincți:   7

Atenție: 2 elevi la Django fără cursul de Python: Radu, Sorin
```

Observă:
- numele sunt aduse la aceeași formă (`strip().title()`) **înainte** de a intra în set; altfel „ana” și „Ana” ar fi două elemente diferite;
- fiecare întrebare („la ambele”, „doar la unul”) e o singură operație de mulțimi;
- rezultatele sunt sortate înainte de afișare, ca ordinea să fie mereu aceeași.

## Greșeli frecvente

### 1. {} pentru un set gol

<!-- fisier: set.py -->
```python
vazute = {}
vazute.add(5)
```

```text
Traceback (most recent call last):
  File "set.py", line 2, in <module>
    vazute.add(5)
    ^^^^^^^^^^
AttributeError: 'dict' object has no attribute 'add'
```

`{}` e un **dicționar** gol: dicționarele au existat înaintea seturilor și au păstrat scrierea. Setul gol se scrie `set()`.

### 2. Indexarea unui set

<!-- fisier: set.py -->
```python
orase = {"Cluj", "Iași", "Brașov"}
print(orase[0])
```

```text
Traceback (most recent call last):
  File "set.py", line 2, in <module>
    print(orase[0])
          ~~~~~^^^
TypeError: 'set' object is not subscriptable
```

„Not subscriptable” înseamnă că nu poți folosi `[]` pe acel obiect. Un set nu are poziții, deci nu are nici „primul element”. Dacă ai nevoie de ordine, transformă-l: `sorted(orase)[0]`.

### 3. remove() pe un element care nu există

<!-- fisier: set.py -->
```python
incercate = {25, 50}
incercate.remove(37)
```

```text
Traceback (most recent call last):
  File "set.py", line 2, in <module>
    incercate.remove(37)
KeyError: 37
```

Când nu ești sigur că elementul există, folosește `discard()`, care nu dă eroare.

### 4. Liste în set

<!-- fisier: set.py -->
```python
perechi = set()
perechi.add(["Ana", "Mihai"])
```

```text
Traceback (most recent call last):
  File "set.py", line 2, in <module>
    perechi.add(["Ana", "Mihai"])
TypeError: unhashable type: 'list'
```

Aceeași regulă ca la cheile de dicționar: elementele unui set trebuie să fie imutabile. Folosește un tuplu: `perechi.add(("Ana", "Mihai"))`.

### 5. Așteptarea unei ordini

```python
note = [10, 7, 9, 7, 10]
unice = set(note)
print(list(unice))
```

```text
[9, 10, 7]
```

Ai fi putut aștepta `[10, 7, 9]` (ordinea primei apariții) sau `[7, 9, 10]` (ordinea crescătoare), dar setul nu garantează niciuna. Ordinea pe care o vezi e un detaliu intern. Pentru o ordine anume, spune explicit ce vrei: `sorted(unice)` sau `list(dict.fromkeys(note))`.

## Exercițiu

În `capitole/15-seturi/seturi.py`, scrie un **analizor de texte**:

1. două texte scrise în cod (de exemplu, două paragrafe despre Cluj și despre Iași);
2. pentru fiecare text, construiește setul de cuvinte: litere mici și fără semnele `.,;:!?` (le poți scoate cu `replace()` într-o buclă `for` peste stringul `".,;:!?"`);
3. afișează, sortate: cuvintele comune ambelor texte, cuvintele care apar doar în primul și câte cuvinte distincte are fiecare text;
4. calculează **asemănarea** dintre texte: numărul de cuvinte comune împărțit la numărul total de cuvinte distincte din ambele texte, afișat ca procent cu `:.1%` (lecția 5);
5. cere apoi cuvinte de la utilizator (rând gol = gata) și spune, pentru fiecare, în care dintre texte apare: în ambele, doar în unul sau în niciunul.

## Pe scurt

- Un set conține elemente unice, fără ordine: `{1, 2, 3}`, `set(lista)`; setul gol e `set()`, nu `{}`.
- `add()` adaugă, `remove()` șterge (cu `KeyError` dacă lipsește), `discard()` șterge fără eroare.
- `in` pe un set e foarte rapid, ideal pentru „am mai văzut asta?”.
- `&` intersecție, `|` uniune, `-` diferență, `^` diferență simetrică; `<=` verifică submulțimea.
- `set(lista)` elimină duplicatele, dar pierde ordinea; `list(dict.fromkeys(lista))` o păstrează.
- Elementele trebuie să fie imutabile; un set nu are indexare și nu are o ordine pe care să te bazezi.
