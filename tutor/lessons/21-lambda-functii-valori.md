## Ce este

În Python, o funcție e un **obiect**, ca un număr sau o listă. Asta înseamnă că o poți pune într-o variabilă, într-o listă sau într-un dicționar și o poți da ca argument altei funcții:

```python
def dublu(x):
    return x * 2

operatie = dublu          # fără paranteze: obiectul funcție, nu rezultatul
print(operatie(21))
print(type(dublu))
```

```text
42
<class 'function'>
```

O **funcție `lambda`** e o funcție mică, fără nume, scrisă într-un singur rând, direct acolo unde ai nevoie de ea:

```python
produse = [("pâine", 4.5), ("cafea", 32.0), ("lapte", 8.99)]
print(sorted(produse, key=lambda produs: produs[1]))
```

```text
[('pâine', 4.5), ('lapte', 8.99), ('cafea', 32.0)]
```

## De ce contează

Ai folosit deja funcții date ca argument: `sorted(orase, key=len)` și `max(voturi, key=voturi.get)` (lecția 17). Acolo ai fost limitat la funcțiile existente. Acum poți da **orice criteriu**: „după preț”, „după media notelor”, „după al doilea element”. Lecția 17 a promis exact asta.

Ideea „dau o funcție, iar altcineva o apelează la momentul potrivit” e peste tot în programarea reală. În Django, de exemplu, scrii funcții-view și le dai lui `path()` (lecția 47). Nu le apelezi tu: le apelează Django când vine o cerere pentru adresa respectivă.

## Cum funcționează

### Funcțiile sunt valori

Numele unei funcții e o variabilă ca oricare alta (lecția 2), legată de un obiect funcție. Cu paranteze, **apelezi** funcția. Fără paranteze, **vorbești despre ea**.

```python
def saluta_formal(nume):
    return f"Bună ziua, {nume}."

def saluta_prietenos(nume):
    return f"Salut, {nume}!"

saluturi = {"formal": saluta_formal, "prietenos": saluta_prietenos}
stil = "prietenos"
print(saluturi[stil]("Ana"))

for functie in [saluta_formal, saluta_prietenos]:
    print(functie("Mihai"))
```

```text
Salut, Ana!
Bună ziua, Mihai.
Salut, Mihai!
```

`saluturi[stil]` dă funcția din dicționar, iar `("Ana")` o apelează. Un dicționar de funcții e o alternativă elegantă la un lanț lung de `if / elif`, cum vei vedea în exemplul complet.

### Funcții care primesc funcții

O funcție poate primi o altă funcție ca parametru și o poate apela când are nevoie:

```python
def aplica_tuturor(functie, valori):
    return [functie(v) for v in valori]

def cu_tva(pret):
    return round(pret * 1.21, 2)

print(aplica_tuturor(cu_tva, [4.5, 8.99, 32.0]))
print(aplica_tuturor(len, ["Ana", "Mihai"]))
print(aplica_tuturor(str.upper, ["cluj", "iași"]))
```

```text
[5.45, 10.88, 38.72]
[3, 5]
['CLUJ', 'IAȘI']
```

`aplica_tuturor` nu știe ce face funcția primită și nici nu-i pasă. Asta o face reutilizabilă.

### key= cu propriile funcții

Iată promisiunea din lecția 17: sortarea după orice criteriu. Scrii o funcție care primește **un element** și întoarce **valoarea după care se compară**:

```python
elevi = [("Ana", [9, 10, 8]), ("Mihai", [7, 6, 9]), ("Ioana", [10, 9, 10])]

def media_elevului(elev):
    nume, note = elev
    return sum(note) / len(note)

for nume, note in sorted(elevi, key=media_elevului, reverse=True):
    print(nume, note)
print("Cel mai slab:", min(elevi, key=media_elevului)[0])
```

```text
Ioana [10, 9, 10]
Ana [9, 10, 8]
Mihai [7, 6, 9]
Cel mai slab: Mihai
```

`sorted()` apelează `media_elevului` o dată pentru fiecare elev și ordonează elevii după rezultat. Nu mai e nevoie de trucul cu tuplurile din lecția 17.

### lambda: funcții scurte, fără nume

Pentru un criteriu de un rând, o definiție separată cu `def` e prea mult. `lambda` o scrie pe loc:

```text
lambda parametri: expresie
```

E echivalentă cu o funcție care face `return expresie`. Exemple:

```python
produse = {"pâine": 4.5, "cafea": 32.0, "lapte": 8.99, "ouă": 1.2}

dupa_pret = sorted(produse.items(), key=lambda pereche: pereche[1])
print(dupa_pret)

scumpe_intai = sorted(produse, key=lambda p: produse[p], reverse=True)
print(scumpe_intai)

orase = ["Iași", "cluj", "Brașov", "arad"]
print(sorted(orase, key=lambda o: (len(o), o.lower())))
```

```text
[('ouă', 1.2), ('pâine', 4.5), ('lapte', 8.99), ('cafea', 32.0)]
['cafea', 'lapte', 'pâine', 'ouă']
['arad', 'cluj', 'Iași', 'Brașov']
```

Ultimul exemplu întoarce un **tuplu** ca cheie: compară întâi lungimea, iar la lungimi egale, numele fără litere mari (tuplurile se compară element cu element, lecția 13).

Limitele lui `lambda`:
- conține **o singură expresie**, al cărei rezultat e întors automat; nu poate avea `if` pe mai multe rânduri, bucle, `return` sau atribuiri;
- poate folosi expresia condițională (lecția 8): `lambda nota: "promovat" if nota >= 5 else "corigent"`.

Dacă îți trebuie mai mult, scrie o funcție cu `def` și un nume clar.

### map() și filter()

Două funcții clasice care primesc o funcție:
- `map(functie, secventa)` aplică funcția fiecărui element;
- `filter(functie, secventa)` păstrează elementele pentru care funcția dă o valoare adevărată.

Ambele întorc iteratori (lecția 17), de aceea le transformi în listă ca să vezi rezultatul:

```python
note = [9, 4, 7.5, 10, 3]
print(list(map(lambda n: n + 1, note)))
print(list(filter(lambda n: n >= 5, note)))
print(list(map(int, ["7", "8", "10"])))
```

```text
[10, 5, 8.5, 11, 4]
[9, 7.5, 10]
[7, 8, 10]
```

Aceleași rezultate se obțin cu comprehension-uri (lecția 16), pe care majoritatea programatorilor Python le preferă, pentru că se citesc mai ușor:

```python
note = [9, 4, 7.5, 10, 3]
print([n + 1 for n in note])
print([n for n in note if n >= 5])
print([int(t) for t in ["7", "8", "10"]])
```

```text
[10, 5, 8.5, 11, 4]
[9, 7.5, 10]
[7, 8, 10]
```

`map` rămâne comod când ai deja o funcție cu nume: `map(int, bucati)` e mai scurt decât `[int(b) for b in bucati]`. Trebuie să le recunoști pe amândouă, pentru că le vei întâlni în codul altora.

### Ce se întâmplă „pe dedesubt”: o funcție poate crea și întoarce altă funcție

Fiindcă funcțiile sunt valori, o funcție poate **întoarce** o funcție nouă, construită pe loc. Funcția nouă ține minte variabilele funcției care a creat-o, chiar și după ce aceasta s-a terminat (scope-ul „Enclosing” din regula LEGB, lecția 20):

```python
def fa_reducere(procent):
    def aplica(pret):
        return round(pret * (1 - procent / 100), 2)
    return aplica

reducere_10 = fa_reducere(10)
reducere_black_friday = fa_reducere(40)
print(reducere_10(50), reducere_black_friday(50))
```

```text
45.0 30.0
```

`fa_reducere(10)` s-a terminat, dar funcția `aplica` pe care a întors-o își amintește că `procent` era 10. O astfel de funcție se numește **closure** („închidere”). Pe acest mecanism se bazează decoratorii (lecția 38), pe care îi vei folosi des în Django (de exemplu `@login_required`, lecția 57).

## Exemplu complet

Un calculator de conversii pentru călătoria Anei. Operațiile sunt păstrate într-un dicționar de funcții (unele cu `def`, altele cu `lambda`), iar meniul se construiește singur din dicționar.

<!-- fisier: conversii.py -->
<!-- stdin: km_mile\n100\nc_f\n-5\nx\neur_ron\n120,5\n\n -->
```python
def celsius_in_fahrenheit(c):
    return c * 9 / 5 + 32


CONVERSII = {
    "km_mile": ("km → mile", lambda km: km * 0.621371),
    "c_f": ("°C → °F", celsius_in_fahrenheit),
    "eur_ron": ("EUR → RON (curs 5,07)", lambda eur: eur * 5.07),
    "l100_mpg": ("l/100 km → mile/galon", lambda l: 235.215 / l),
}


def citeste_numar(mesaj):
    while True:
        text = input(mesaj).strip().replace(",", ".")
        fara_semn = text[1:] if text.startswith("-") else text
        if fara_semn.replace(".", "", 1).isdigit():
            return float(text)
        print("Scrie un număr.")


def main():
    while True:
        print("\nConversii:", ", ".join(f"{cod} ({descriere})" for cod, (descriere, _) in CONVERSII.items()))
        cod = input("Cod (gol = ieșire): ").strip()
        if not cod:
            return
        if cod not in CONVERSII:
            print("Cod necunoscut.")
            continue
        descriere, functie = CONVERSII[cod]
        valoare = citeste_numar("Valoare: ")
        print(f"{descriere}: {valoare:g} → {functie(valoare):.2f}")


main()
```

```text

Conversii: km_mile (km → mile), c_f (°C → °F), eur_ron (EUR → RON (curs 5,07)), l100_mpg (l/100 km → mile/galon)
Cod (gol = ieșire): km_mile
Valoare: 100
km → mile: 100 → 62.14

Conversii: km_mile (km → mile), c_f (°C → °F), eur_ron (EUR → RON (curs 5,07)), l100_mpg (l/100 km → mile/galon)
Cod (gol = ieșire): c_f
Valoare: -5
°C → °F: -5 → 23.00

Conversii: km_mile (km → mile), c_f (°C → °F), eur_ron (EUR → RON (curs 5,07)), l100_mpg (l/100 km → mile/galon)
Cod (gol = ieșire): x
Cod necunoscut.

Conversii: km_mile (km → mile), c_f (°C → °F), eur_ron (EUR → RON (curs 5,07)), l100_mpg (l/100 km → mile/galon)
Cod (gol = ieșire): eur_ron
Valoare: 120,5
EUR → RON (curs 5,07): 120.5 → 610.94

Conversii: km_mile (km → mile), c_f (°C → °F), eur_ron (EUR → RON (curs 5,07)), l100_mpg (l/100 km → mile/galon)
Cod (gol = ieșire): 
```

Observă:
- ca să adaugi o conversie nouă, adaugi **un rând** în dicționar. Meniul și restul programului nu se schimbă;
- nicăieri nu apare un `if cod == "km_mile": ... elif cod == "c_f": ...`, pentru că dicționarul face alegerea;
- conversia de temperatură e scrisă cu `def`, pentru că are un nume care explică formula. Celelalte sunt înmulțiri simple, potrivite pentru `lambda`;
- cursul valutar e scris direct în cod doar pentru exemplu. Într-o aplicație reală ar veni dintr-o sursă actualizată.

## Greșeli frecvente

### 1. return sau atribuire în lambda

<!-- fisier: lam.py -->
```python
dublu = lambda x: return x * 2
```

```text
  File "lam.py", line 1
    dublu = lambda x: return x * 2
                      ^^^^^^
SyntaxError: invalid syntax
```

`lambda` conține doar o expresie, al cărei rezultat e întors automat. Scrie `lambda x: x * 2`, iar dacă îți trebuie instrucțiuni, folosește `def`.

### 2. Funcția-cheie care uită return

<!-- fisier: lam.py -->
```python
def media_elevului(elev):
    nume, note = elev
    sum(note) / len(note)

elevi = [("Ana", [9, 10]), ("Mihai", [7, 6])]
print(sorted(elevi, key=media_elevului))
```

```text
Traceback (most recent call last):
  File "lam.py", line 6, in <module>
    print(sorted(elevi, key=media_elevului))
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: '<' not supported between instances of 'NoneType' and 'NoneType'
```

Media e calculată și aruncată, iar funcția întoarce `None` pentru fiecare elev. `sorted()` încearcă apoi să compare `None` cu `None`. Când vezi `NoneType` într-o eroare, verifică întâi dacă o funcție a uitat `return`.

### 3. Rezultatul lui map() sau filter() afișat direct

```python
note = [9, 4, 10]
promovate = filter(lambda n: n >= 5, note)
print(promovate)
print(list(promovate))
print(list(promovate))
```

Primul `print` afișează ceva de forma `<filter object at 0x7f...>`, nu notele: `filter()` întoarce un iterator. Al doilea afișează `[9, 10]`, iar al treilea `[]`, pentru că iteratorul s-a consumat (lecția 17). Transformă rezultatul în listă **o singură dată**: `promovate = list(filter(...))`.

### 4. lambda creată într-o buclă care „uită” valoarea

```python
reduceri = []
for procent in [10, 20, 30]:
    reduceri.append(lambda pret: pret * (1 - procent / 100))

print([r(100) for r in reduceri])
```

```text
[70.0, 70.0, 70.0]
```

Te-ai fi așteptat la `[90.0, 80.0, 70.0]`. O funcție își citește variabilele **când e apelată**, nu când e creată, iar la apel `procent` are deja ultima valoare, 30. Soluția sigură e o funcție care construiește funcția (closure-ul din „pe dedesubt”), care fixează valoarea la fiecare apel:

```python
def fa_reducere(procent):
    return lambda pret: pret * (1 - procent / 100)

reduceri = [fa_reducere(p) for p in [10, 20, 30]]
print([r(100) for r in reduceri])
```

```text
[90.0, 80.0, 70.0]
```

### 5. lambda dată unui nume

```python
media = lambda note: sum(note) / len(note)
print(media([9, 10]))
```

```text
9.5
```

Funcționează, dar nu are niciun avantaj față de `def`. Mai mult, în mesajele de eroare funcția apare cu numele `<lambda>`, nu `media`, deci e mai greu de găsit. Ghidul de stil PEP 8 (lecția 40) recomandă `def` ori de câte ori funcția primește un nume. `lambda` e pentru funcțiile de unică folosință, scrise direct ca argument.

## Exercițiu

În `capitole/21-lambda-functii-valori/lambda_functii_valori.py`, pornește de la lista de produse:

```python
produse = [
    {"nume": "pâine", "pret": 4.5, "stoc": 20, "categorie": "panificație"},
    {"nume": "cafea", "pret": 32.0, "stoc": 3, "categorie": "băuturi"},
    {"nume": "lapte", "pret": 8.99, "stoc": 0, "categorie": "lactate"},
    {"nume": "ceai", "pret": 14.0, "stoc": 12, "categorie": "băuturi"},
    {"nume": "iaurt", "pret": 3.49, "stoc": 30, "categorie": "lactate"},
]
```

1. afișează produsele sortate după preț; apoi, într-o a doua listă, sortate descrescător după stoc; folosește `sorted` cu `lambda`;
2. sortează-le după categorie, iar în cadrul categoriei după nume (o cheie de tip tuplu);
3. găsește produsul cu cea mai mare valoare a stocului (preț × stoc), cu `max` și `key=`;
4. scrie o funcție `filtreaza(produse, conditie)` care primește o funcție-condiție și întoarce produsele pentru care ea e adevărată; apeleaz-o cu cel puțin trei condiții diferite, scrise ca `lambda` (de exemplu: în stoc, sub 10 lei, din categoria „băuturi”);
5. construiește un dicționar `CRITERII = {"pret": ..., "nume": ..., "stoc": ...}` cu funcții-cheie și lasă utilizatorul să aleagă criteriul de sortare de la tastatură.

## Pe scurt

- Funcțiile sunt obiecte: le poți pune în variabile, liste și dicționare și le poți da ca argument (fără paranteze).
- `key=functie` primește un element și întoarce valoarea după care se compară; o funcție-cheie fără `return` dă `None` și erori de comparare.
- `lambda parametri: expresie` e o funcție scurtă, fără nume, cu o singură expresie; pentru orice mai lung, sau cu nume, folosește `def`.
- `map()` și `filter()` aplică o funcție fiecărui element și întorc iteratori; comprehension-urile fac de obicei același lucru mai lizibil.
- Un dicționar de funcții poate înlocui un lanț lung de `if / elif`.
- O funcție poate întoarce altă funcție care își amintește variabilele (closure); lambda-urile create în bucle citesc variabila la apel, nu la creare.
