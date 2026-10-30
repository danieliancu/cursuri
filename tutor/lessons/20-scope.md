## Ce este

**Domeniul** unei variabile (în engleză „scope”) este partea de program în care numele ei poate fi folosit. Ai văzut deja la lecția 18 că variabilele create într-o funcție nu există în afara ei:

```python
oras = "Cluj"          # variabilă globală: creată în afara oricărei funcții

def prezinta():
    nume = "Ana"       # variabilă locală: există doar cât rulează funcția
    print(nume, "din", oras)

prezinta()
print(oras)
```

```text
Ana din Cluj
Cluj
```

- o variabilă **locală** e creată într-o funcție (inclusiv parametrii) și dispare când funcția se termină;
- o variabilă **globală** e creată la nivelul fișierului și se poate citi din orice funcție a lui.

## De ce contează

Domeniile sunt motivul pentru care funcțiile sunt sigure: poți numi o variabilă `total` în zece funcții diferite fără să se încurce între ele. Cine nu înțelege regulile ajunge însă la erori ciudate, ca `UnboundLocalError`, sau la funcții care modifică „pe ascuns” date din alt colț al programului.

Lecția îți arată cum caută Python un nume, de ce o atribuire într-o funcție schimbă totul și de ce programatorii buni evită aproape mereu variabilele globale modificabile.

## Cum funcționează

### Fiecare apel are variabilele lui

Variabilele locale cu același nume din funcții diferite (sau din apeluri diferite ale aceleiași funcții) sunt complet separate:

```python
def total_cos(preturi):
    total = 0
    for pret in preturi:
        total += pret
    return total

def total_note(note):
    total = 0
    for nota in note:
        total += nota
    return total

total = "nu e atins de funcții"
print(total_cos([4.5, 8.99]), total_note([9, 10]))
print(total)
```

```text
13.49 19
nu e atins de funcții
```

Trei variabile `total`, trei domenii diferite: câte una în fiecare funcție și una globală.

### Regula LEGB: unde caută Python un nume

Când folosești un nume, Python îl caută în patru locuri, în această ordine, și se oprește la primul găsit:
1. **L**ocal: în funcția care rulează acum;
2. **E**nclosing (înconjurător): în funcțiile care o conțin, dacă e definită într-o altă funcție;
3. **G**lobal: la nivelul fișierului;
4. **B**uilt-in: numele predefinite ale lui Python (`print`, `len`, `sum`, `list`...).

```python
mesaj = "global"

def exterioara():
    mesaj = "din exterioara"

    def interioara():
        print(mesaj)      # nu e local, îl găsește în funcția înconjurătoare

    interioara()

exterioara()
print(len("Cluj"))        # len nu e nicăieri definit de noi: e built-in
```

```text
din exterioara
4
```

O funcție definită în altă funcție e un lucru pe care îl vei întâlni mai ales la decoratori (lecția 38). Deocamdată reține ordinea L, E, G, B.

### Atribuirea face o variabilă locală

Regula cea mai importantă a lecției: dacă **atribui** o valoare unui nume oriunde într-o funcție, acel nume e **local în toată funcția**. Citirea unei variabile globale merge fără probleme, dar atribuirea creează o variabilă locală nouă, cu același nume, care o „acoperă” pe cea globală:

```python
scor = 0

def adauga_puncte():
    scor = 10        # variabilă LOCALĂ nouă; cea globală nu se schimbă
    print("în funcție:", scor)

adauga_puncte()
print("global:", scor)
```

```text
în funcție: 10
global: 0
```

Iar dacă încerci să citești variabila **înainte** de atribuire, în aceeași funcție, primești o eroare care pare de neînțeles:

<!-- fisier: scor.py -->
```python
scor = 0

def adauga_puncte():
    scor = scor + 10
    return scor

adauga_puncte()
```

```text
Traceback (most recent call last):
  File "scor.py", line 7, in <module>
    adauga_puncte()
  File "scor.py", line 4, in adauga_puncte
    scor = scor + 10
           ^^^^
UnboundLocalError: cannot access local variable 'scor' where it is not associated with a value
```

Python decide care nume sunt locale **înainte** să ruleze funcția, uitându-se la atribuiri. Fiindcă există `scor = ...`, `scor` e local peste tot în funcție. Când partea dreaptă încearcă să-l citească, variabila locală nu are încă nicio valoare.

### global: când chiar vrei să modifici o variabilă globală

Cuvântul cheie `global` îi spune lui Python: „numele acesta, în funcția asta, e cel global”.

```python
scor = 0

def adauga_puncte(puncte):
    global scor
    scor += puncte

adauga_puncte(10)
adauga_puncte(5)
print(scor)
```

```text
15
```

Funcționează, dar **evită-l**. O funcție care modifică o variabilă globală:
- are un efect ascuns: din apelul `adauga_puncte(10)` nu se vede că schimbă ceva în afara ei;
- e greu de testat, pentru că rezultatul depinde de starea globală de dinainte;
- poate fi stricată de orice alt cod care modifică aceeași variabilă.

Varianta curată primește valoarea ca parametru și întoarce rezultatul nou, cu `return`. Codul care o apelează decide ce face cu el:

```python
def adauga_puncte(scor, puncte):
    return scor + puncte

scor = 0
scor = adauga_puncte(scor, 10)
scor = adauga_puncte(scor, 5)
print(scor)
```

```text
15
```

Acum tot ce folosește funcția intră prin parametri și tot ce produce iese prin `return`. Se vede totul din apel.

Pentru funcții imbricate există și `nonlocal`, care face același lucru pentru o variabilă din funcția înconjurătoare. Îl vei folosi rar.

### Constantele globale sunt în regulă

Citirea valorilor globale care **nu se schimbă** e perfect normală. Prin convenție, astfel de **constante** se scriu cu litere mari, sus în fișier:

```python
TVA = 0.21
PRAG_TRANSPORT_GRATUIT = 100

def total_de_plata(valoare_cos):
    transport = 0 if valoare_cos >= PRAG_TRANSPORT_GRATUIT else 15
    return round(valoare_cos * (1 + TVA) + transport, 2)

print(total_de_plata(80))
print(total_de_plata(120))
```

```text
111.8
145.2
```

Literele mari nu le fac imposibil de modificat (Python nu are constante adevărate), dar le spun celor care citesc codul: „aceasta e o setare fixă”. Așa arată și `settings.py` din Django (lecția 46): `DEBUG`, `ALLOWED_HOSTS`, `DATABASES`.

### Ce se întâmplă „pe dedesubt”: obiectele mutabile nu respectă granițele

Regulile de domeniu sunt despre **nume**, nu despre obiecte. Dacă o funcție primește o listă și o modifică cu `append()`, nu creează niciun nume nou: modifică **obiectul**, care e același și în afara funcției (aliasing, lecția 12).

```python
def adauga(cos, produs):
    cos.append(produs)       # modifică lista primită; nu e nicio atribuire

cumparaturi = ["pâine"]
adauga(cumparaturi, "lapte")
print(cumparaturi)
```

```text
['pâine', 'lapte']
```

Parametrul `cos` și variabila `cumparaturi` sunt două etichete pe **aceeași** listă. E un comportament util (funcția nu mai trebuie să întoarcă lista), dar trebuie să fie **intenționat** și clar din numele funcției. O funcție numită `total(cos)` n-ar trebui să modifice coșul. Dacă vrei ca lista originală să rămână neatinsă, lucrează pe o copie: `cos = cos.copy()`.

## Exemplu complet

Lista de cumpărături din lecția 12, rescrisă fără variabile globale modificabile. Lista e creată în `main()` și trimisă funcțiilor care au nevoie de ea, iar fiecare funcție spune clar ce face cu ea.

<!-- fisier: cumparaturi.py -->
<!-- stdin: 1\nlapte\n1\npâine\n1\nlapte\n2\nmere\n3\n0 -->
```python
MENIU = "1 = adaugă, 2 = șterge, 3 = afișează, 0 = gata"


def citeste_produs(mesaj):
    return input(mesaj).strip().lower()


def adauga(cos, produs):
    """Adaugă produsul în coș (modifică lista primită). Întoarce False dacă era deja acolo."""
    if produs in cos:
        return False
    cos.append(produs)
    return True


def sterge(cos, produs):
    """Șterge produsul din coș (modifică lista primită). Întoarce False dacă nu era acolo."""
    if produs not in cos:
        return False
    cos.remove(produs)
    return True


def afiseaza(cos):
    if not cos:
        print("Lista e goală.")
    for nr, produs in enumerate(cos, start=1):
        print(f"{nr}. {produs}")


def main():
    cos = []  # locală în main: nicio altă funcție nu o poate atinge decât dacă o primește
    while True:
        optiune = input(f"\n{MENIU}\nAlege: ").strip()
        if optiune == "0":
            return cos
        if optiune == "1":
            produs = citeste_produs("Produs: ")
            if not adauga(cos, produs):
                print(f"„{produs}” e deja pe listă.")
        elif optiune == "2":
            produs = citeste_produs("Ce ștergi? ")
            if not sterge(cos, produs):
                print(f"„{produs}” nu e pe listă.")
        elif optiune == "3":
            afiseaza(cos)


lista_finala = main()
print(f"\nDe cumpărat: {', '.join(lista_finala)}")
```

```text

1 = adaugă, 2 = șterge, 3 = afișează, 0 = gata
Alege: 1
Produs: lapte

1 = adaugă, 2 = șterge, 3 = afișează, 0 = gata
Alege: 1
Produs: pâine

1 = adaugă, 2 = șterge, 3 = afișează, 0 = gata
Alege: 1
Produs: lapte
„lapte” e deja pe listă.

1 = adaugă, 2 = șterge, 3 = afișează, 0 = gata
Alege: 2
Ce ștergi? mere
„mere” nu e pe listă.

1 = adaugă, 2 = șterge, 3 = afișează, 0 = gata
Alege: 3
1. lapte
2. pâine

1 = adaugă, 2 = șterge, 3 = afișează, 0 = gata
Alege: 0

De cumpărat: lapte, pâine
```

Observă:
- singura variabilă globală e constanta `MENIU`, care doar se citește;
- `cos` trăiește în `main()` și ajunge la celelalte funcții ca argument, deci din fiecare apel se vede ce date folosește;
- `adauga` și `sterge` modifică lista primită (spun asta în docstring) și întorc un `bool`, ca `main()` să decidă ce mesaj afișează;
- o funcție `main()` care conține programul propriu-zis e o convenție des întâlnită. La lecția 29 vei vedea cum se combină cu `if __name__ == "__main__":`.

## Greșeli frecvente

### 1. UnboundLocalError la modificarea unei variabile globale

<!-- fisier: contor.py -->
```python
incercari = 0

def incercare_noua():
    incercari += 1

incercare_noua()
```

```text
Traceback (most recent call last):
  File "contor.py", line 6, in <module>
    incercare_noua()
  File "contor.py", line 4, in incercare_noua
    incercari += 1
    ^^^^^^^^^
UnboundLocalError: cannot access local variable 'incercari' where it is not associated with a value
```

`+=` e o atribuire, deci `incercari` devine locală în funcție, iar valoarea ei locală nu există încă. Soluția recomandată: transmite valoarea ca parametru și întoarce rezultatul (`return incercari + 1`).

### 2. Așteptarea ca atribuirea din funcție să schimbe variabila de afară

```python
def reseteaza(cos):
    cos = []

cumparaturi = ["pâine", "lapte"]
reseteaza(cumparaturi)
print(cumparaturi)
```

```text
['pâine', 'lapte']
```

`cos = []` mută doar eticheta **locală** `cos` pe o listă nouă. Lista originală nu e atinsă. Ca să golești chiar lista primită, folosește o metodă care o modifică: `cos.clear()`. Sau, mai clar, întoarce o listă nouă și atribuie-o la apel.

### 3. Un nume built-in acoperit de o variabilă

<!-- fisier: suma.py -->
```python
note = [9, 10, 8]
sum = 0
for nota in note:
    sum += nota
print(sum)
print(sum([4, 5]))
```

```text
27
Traceback (most recent call last):
  File "suma.py", line 6, in <module>
    print(sum([4, 5]))
          ^^^^^^^^^^^
TypeError: 'int' object is not callable
```

`sum` e o funcție built-in, ultimul loc în care caută regula LEGB. Variabila globală `sum = 0` e găsită înainte, deci `sum([4, 5])` încearcă să „apeleze” numărul 27. Nu folosi ca nume de variabile `sum`, `list`, `dict`, `str`, `input`, `max`, `min`, `len`, `type`, `id`. Alege `suma`, `lista_note`, `total`.

### 4. Variabila locală folosită în afara funcției

<!-- fisier: medie.py -->
```python
def calculeaza(note):
    media = sum(note) / len(note)

calculeaza([9, 10])
print(media)
```

```text
Traceback (most recent call last):
  File "medie.py", line 5, in <module>
    print(media)
          ^^^^^
NameError: name 'media' is not defined
```

`media` a dispărut odată cu apelul. Funcția trebuie să întoarcă rezultatul, iar codul de afară să-l păstreze: `media = calculeaza([9, 10])`, cu `return sum(note) / len(note)` în funcție.

### 5. Funcție care modifică, fără să spună, datele primite

```python
def cele_mai_bune(note, cate):
    note.sort(reverse=True)
    return note[:cate]

note_ana = [8, 10, 9, 7]
print(cele_mai_bune(note_ana, 2))
print(note_ana)
```

```text
[10, 9]
[10, 9, 8, 7]
```

Cine apelează funcția nu se așteaptă ca notele Anei să fie reordonate, dar `sort()` a modificat lista originală (vezi „pe dedesubt”). Folosește `sorted()`, care creează o listă nouă: `return sorted(note, reverse=True)[:cate]`.

## Exercițiu

În `capitole/20-scope/scope.py`, pornește de la programul de mai jos, care funcționează, dar folosește variabile globale modificate din funcții:

```python
sold = 100
istoric = []

def depune(suma):
    global sold
    sold += suma
    istoric.append(f"+{suma}")

def retrage(suma):
    global sold
    if suma <= sold:
        sold -= suma
        istoric.append(f"-{suma}")

depune(50)
retrage(30)
retrage(500)
print(sold, istoric)
```

1. rulează-l și notează rezultatul;
2. rescrie-l **fără `global`** și fără variabile globale modificate: `depune(sold, suma)` și `retrage(sold, suma)` întorc soldul nou, iar `retrage` întoarce și un `bool` care spune dacă retragerea a reușit (un tuplu, lecția 18);
3. istoricul devine o listă creată în `main()` și transmisă unei funcții `inregistreaza(istoric, operatie)`, care o modifică pe loc (scrie asta într-un comentariu);
4. adaugă o constantă `LIMITA_RETRAGERE = 200` și refuză retragerile mai mari, cu un mesaj;
5. verifică că programul nou dă același rezultat ca vechiul pentru aceleași operații.

## Pe scurt

- Variabilele create într-o funcție (inclusiv parametrii) sunt locale: dispar la final și nu se văd afară.
- Python caută un nume în ordinea LEGB: local, funcția înconjurătoare, global, built-in.
- O atribuire oriunde într-o funcție face numele local în toată funcția; citirea lui înainte dă `UnboundLocalError`.
- `global` permite modificarea unei variabile globale, dar e de evitat: transmite valori prin parametri și întoarce rezultate cu `return`.
- Constantele globale, scrise cu LITERE_MARI, sunt în regulă, pentru că doar se citesc.
- O funcție poate modifica un obiect mutabil primit (o listă): fă-o doar intenționat și nu acoperi nume built-in ca `sum` sau `list`.
