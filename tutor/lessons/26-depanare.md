## Ce este

**Depanarea** (în engleză „debugging”) înseamnă să găsești și să repari cauza unui comportament greșit al programului. Uneori programul se oprește cu o eroare și ai un traceback (lecția 23). Alteori, mai greu, programul merge până la capăt, dar rezultatul e greșit.

```python
note = ["9", "10", "7"]
print("Nota maximă:", max(note))
```

```text
Nota maximă: 9
```

Nu există nicio eroare, totuși 10 e mai mare decât 9. Lecția asta îți dă metodele și uneltele cu care afli **de ce**: un proces de lucru, `print()` folosit cu cap și depanatorul **pdb**, cu care oprești programul la mijloc și te uiți în el.

## De ce contează

Programatorii petrec mult mai mult timp citind și depanând cod decât scriindu-l. Diferența dintre un începător și cineva cu experiență nu e că al doilea nu face greșeli, ci că le găsește repede, cu metodă, în loc să schimbe lucruri la întâmplare până „merge”.

Depanarea cu metodă îți dă și încredere: când știi **de ce** a apărut o problemă, știi și că reparația e corectă, nu doar că a ascuns simptomul.

## Cum funcționează

### Procesul, pas cu pas

1. **Citește ce vezi.** Dacă ai un traceback, citește-l de jos în sus (lecția 23). Dacă nu, formulează exact problema: „pentru intrarea X mă așteptam la Y, dar am primit Z”.
2. **Reprodu problema.** Găsește intrarea care o produce **de fiecare dată**. O problemă pe care nu o poți reproduce nu o poți nici verifica după ce ai reparat-o.
3. **Izolează.** Micșorează cazul: date mai puține, mai puțin cod. Comentează (cu `#`) bucăți din program sau copiază funcția suspectă într-un fișier separat, cu o intrare fixă. Adesea, problema devine evidentă doar din atât.
4. **Fă o ipoteză și verifică-o.** „Cred că `note` conține texte, nu numere.” Apoi **verifică** (cu `print` sau cu pdb), nu presupune.
5. **Repară un singur lucru**, apoi rulează din nou. Dacă schimbi cinci lucruri deodată, nu mai știi care a contat.
6. **Verifică și cazurile vecine**: celelalte ramuri, lista goală, valorile de la limită.

### print() făcut bine

Cea mai simplă unealtă rămâne `print()`, dacă îl folosești bine. Formatul `{x=}` din lecția 5 afișează și numele, și valoarea, cu ghilimele la stringuri:

```python
note = ["9", "10", "7"]
print(f"{note=}")
print(f"{max(note)=}")
print(f"{type(note[0])=}")
```

```text
note=['9', '10', '7']
max(note)='9'
type(note[0])=<class 'str'>
```

Acum e clar: notele sunt **texte**, iar textele se compară caracter cu caracter (lecția 7), deci `"9" > "10"`. Simplul `print(note[0])` ar fi afișat `9` și nu ți-ar fi arătat diferența.

Ghilimelele din `{x=}` (forma „repr” a valorii) dezvăluie și caractere invizibile:

```python
nume = "Ana \n"
print("[" + nume + "]")
print(f"{nume=}")
print(f"{nume!r}")
```

```text
[Ana 
]
nume='Ana \n'
'Ana \n'
```

`!r` cere forma „repr” fără numele variabilei. Când compari texte și nu înțelegi de ce nu sunt egale, afișează-le cu `!r`. Aproape mereu e vorba de un spațiu, un rând nou sau o literă mare.

Câteva sfaturi pentru afișările de depanare:
- pune-le **înainte și după** locul suspect, ca să vezi unde se schimbă valoarea;
- marchează-le, de exemplu cu `print(f"DEBUG {x=}")`, ca să le găsești și să le ștergi ușor;
- în bucle, afișează și contorul: `print(f"DEBUG {i=} {element=}")`.

### Depanatorul: breakpoint() și pdb

Cu `print()` trebuie să ghicești dinainte ce vrei să vezi. Un **depanator** (în engleză „debugger”) oprește programul într-un punct ales de tine și te lasă să inspectezi orice variabilă, apoi să mergi mai departe rând cu rând. Python are unul inclus, **pdb** („Python debugger”).

Îl pornești scriind `breakpoint()` în cod, acolo unde vrei să se oprească programul. Când execuția ajunge acolo, în terminal apare promptul `(Pdb)` și programul așteaptă comenzi:

| Comandă | Ce face |
|---|---|
| `p expresie` | afișează valoarea unei expresii (`p total`, `p len(note)`) |
| `pp expresie` | la fel, dar aranjat frumos (util la dicționare mari) |
| `n` („next”) | execută rândul curent și se oprește la următorul |
| `s` („step”) | ca `n`, dar dacă rândul apelează o funcție, intră în ea |
| `c` („continue”) | continuă până la următorul `breakpoint()` sau până la final |
| `l` („list”) | arată codul din jurul rândului curent |
| `w` („where”) | arată stiva de apeluri, ca un traceback |
| `q` („quit”) | oprește programul |

O sesiune reală. Comenzile scrise după `(Pdb)` sunt tastate de utilizator:

<!-- fisier: medie.py -->
<!-- stdin: p note\nn\nn\np total, nota\nc\nc\nc -->
```python
def medie(note):
    total = 0
    for nota in note:
        breakpoint()
        total += nota
    return total / len(note)


print(medie([9, 7, 10]))
```

```text
> medie.py(5)medie()
-> total += nota
(Pdb) p note
[9, 7, 10]
(Pdb) n
> medie.py(3)medie()
-> for nota in note:
(Pdb) n
> medie.py(4)medie()
-> breakpoint()
(Pdb) p total, nota
(9, 7)
(Pdb) c
> medie.py(5)medie()
-> total += nota
(Pdb) c
> medie.py(5)medie()
-> total += nota
(Pdb) c
8.666666666666666
```

Cum se citește:
- `> medie.py(5)medie()` înseamnă „ești în fișierul `medie.py`, la rândul 5, în funcția `medie`”, iar rândul de sub săgeata `->` e cel care **urmează** să se execute (încă nu s-a executat);
- după primul `n`, `total += nota` s-a executat, iar programul a revenit la `for`; după al doilea `n` a trecut la nota următoare, deci `nota` e acum 7, iar `total` e 9;
- `c` continuă până la următorul `breakpoint()`, adică la iterația următoare; după ultima notă, `c` lasă programul să se termine și vezi rezultatul.

Comenzile le tastezi în terminal, ca pe orice răspuns la `input()`. În aplicația PyTutor, programul oprit în pdb se poate întrerupe oricând și cu butonul **Oprește**.

Un `breakpoint()` într-o buclă se oprește la **fiecare** iterație. Când te interesează doar un caz, pune-l într-un `if`:

<!-- nu-rula -->
```python
for elev, note in catalog.items():
    if elev == "Ioana":
        breakpoint()
    ...
```

### Alte tehnici simple

- **Explică problema cu voce tare**, rând cu rând, cuiva sau chiar unui obiect de pe birou (metoda e cunoscută ca „rubber duck debugging”, după rățușca de cauciuc). Când explici ce **ar trebui** să facă fiecare rând, observi adesea rândul care nu face asta.
- **Caută prin înjumătățire.** Dacă nu știi unde apare problema într-un program lung, verifică valoarea la jumătatea drumului. E deja greșită? Problema e în prima jumătate. Repetă până rămân câteva rânduri.
- **Ia o pauză.** Multe greșeli devin evidente după zece minute de altceva.
- **Întreabă tutorele**, cu întrebarea formulată ca la pasul 1 al procesului.

### Ce se întâmplă „pe dedesubt”: cum oprește pdb programul

Python poate apela o funcție „de supraveghere” înaintea fiecărui rând executat. `breakpoint()` pornește pdb, care își instalează o astfel de funcție. Înaintea fiecărui rând, pdb verifică dacă trebuie să se oprească (după `n`, `s` sau un nou `breakpoint()`). Dacă da, citește comenzi din terminal, exact ca `input()`. De aceea programul încetinește puțin cât timp pdb e activ și de aceea pdb are nevoie de cineva care să-i răspundă în terminal.

## Exemplu complet

Programul de mai jos ar trebui să afișeze nota maximă a fiecărui elev și să-i găsească pe cei cu media sub 5. Rezultatul e greșit, deși nu apare nicio eroare.

<!-- fisier: catalog.py -->
```python
DATE = """
Ana Popescu: 9, 10, 8
Mihai Ionescu: 7,6,9
Ioana Marin: 10, 9, 10
Radu Pop: 4, 5, 3
"""


def citeste_catalog(text):
    catalog = {}
    for linie in text.strip().split("\n"):
        nume, note = linie.split(":")
        catalog[nume] = note.split(",")
    return catalog


catalog = citeste_catalog(DATE)
for elev, note in catalog.items():
    print(f"{elev:<14} nota maximă: {max(note)}")
```

```text
Ana Popescu    nota maximă:  9
Mihai Ionescu  nota maximă: 9
Ioana Marin    nota maximă:  9
Radu Pop       nota maximă:  5
```

Ioana are un 10, dar maximul afișat e 9. Observă și spațiul în plus din fața unor note. Urmăm procesul:

1. **Problema:** pentru Ioana, cu notele 10, 9, 10, mă aștept la maximul 10, dar primesc 9;
2. **Reproducere:** se întâmplă la fiecare rulare, cu aceleași date;
3. **Ipoteză:** notele nu sunt numere. **Verificare:** afișăm ce conține `note` pentru un elev:

<!-- fisier: catalog.py -->
```python
DATE = """
Ana Popescu: 9, 10, 8
Mihai Ionescu: 7,6,9
Ioana Marin: 10, 9, 10
Radu Pop: 4, 5, 3
"""


def citeste_catalog(text):
    catalog = {}
    for linie in text.strip().split("\n"):
        nume, note = linie.split(":")
        catalog[nume] = note.split(",")
    return catalog


catalog = citeste_catalog(DATE)
print(f"DEBUG {catalog['Ioana Marin']=}")
```

```text
DEBUG catalog['Ioana Marin']=[' 10', ' 9', ' 10']
```

Confirmat, și chiar mai mult: notele sunt texte, cu spațiu în față. Între texte, `' 9'` e mai mare decât `' 10'` (după spațiu se compară `'9'` cu `'1'`).

4. **Reparația**, un singur lucru: convertim notele în numere chiar la citire. `int()` ignoră spațiile (lecția 6), deci rezolvă ambele probleme. Apoi rulăm din nou și verificăm și restul cerinței:

<!-- fisier: catalog.py -->
```python
DATE = """
Ana Popescu: 9, 10, 8
Mihai Ionescu: 7,6,9
Ioana Marin: 10, 9, 10
Radu Pop: 4, 5, 3
"""


def citeste_catalog(text):
    catalog = {}
    for linie in text.strip().split("\n"):
        nume, note = linie.split(":")
        catalog[nume.strip()] = [int(nota) for nota in note.split(",")]
    return catalog


catalog = citeste_catalog(DATE)
for elev, note in catalog.items():
    print(f"{elev:<14} nota maximă: {max(note)}")

corigenti = [elev for elev, note in catalog.items() if sum(note) / len(note) < 5]
print("Corigenți:", ", ".join(corigenti) or "niciunul")
```

```text
Ana Popescu    nota maximă: 10
Mihai Ionescu  nota maximă: 9
Ioana Marin    nota maximă: 10
Radu Pop       nota maximă: 5
Corigenți: Radu Pop
```

5. **Cazurile vecine:** ce se întâmplă cu un rând gol la mijloc sau cu o notă scrisă greșit („zece”)? Pentru acestea ai uneltele din lecțiile 24 și 25: `try / except` la conversie și un mesaj clar pentru rândul cu probleme.

Am șters rândul `DEBUG` după ce și-a făcut treaba.

## Greșeli frecvente

### 1. Schimbări la întâmplare

Modifici un rând, rulezi, nu merge; modifici altul, rulezi, tot nu merge; după zece modificări, „merge”, dar nu știi de ce, iar codul e plin de schimbări inutile care pot strica altceva. Înainte de orice modificare, spune-ți ipoteza („cred că X e greșit pentru că Y”), verific-o, apoi schimbă **un singur** lucru.

### 2. print() care ascunde tipul

```python
cantitate = "3"
pret = 4.5
print(cantitate, pret)
print(cantitate * 2)
```

```text
3 4.5
33
```

`print(cantitate)` afișează `3`, la fel ca pentru numărul 3, așa că nu vezi problema. Folosește `{x=}` sau `!r`, care arată ghilimelele: `print(f"{cantitate=}")` afișează `cantitate='3'`.

### 3. breakpoint() uitat în cod

<!-- fisier: medie.py -->
```python
note = [9, 7, 10]
breakpoint()
print(sum(note) / len(note))
```

```text
> medie.py(3)<module>()
-> print(sum(note) / len(note))
(Pdb) 
Traceback (most recent call last):
  File "medie.py", line 3, in <module>
    print(sum(note) / len(note))
    ^^^^^
  File "/usr/local/lib/python3.12/bdb.py", line 100, in trace_dispatch
    return self.dispatch_line(frame)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/bdb.py", line 125, in dispatch_line
    if self.quitting: raise BdbQuit
                      ^^^^^^^^^^^^^
bdb.BdbQuit
```

Așa arată un `breakpoint()` uitat atunci când programul rulează fără cineva care să tasteze comenzi: de exemplu, când tutorele îți rulează fișierul ca să-l verifice. pdb nu primește nicio comandă, iar programul se oprește cu `bdb.BdbQuit`. Același mesaj apare și când ieși tu din pdb cu `q`, situație în care e normal. Înainte să spui „am terminat”, caută prin cod `breakpoint()` și `DEBUG` și șterge-le.

### 4. Ascunderea simptomului în loc de repararea cauzei

<!-- nu-rula -->
```python
try:
    nota_maxima = max(note)
except TypeError:
    nota_maxima = 0
```

Dacă `max()` dă `TypeError` pentru că lista amestecă texte și numere, un `try / except` face eroarea să dispară, dar datele rămân greșite, iar rezultatul (0) e o minciună. `try / except` e pentru situații **așteptate** din lumea reală (lecția 24), nu pentru greșelile din propriul cod. Află de unde vin textele și repară acolo.

### 5. Rularea altui fișier decât cel modificat

Modifici `capitole/24-try-except/try_except.py`, dar în terminal rulezi în continuare comanda veche, cu alt fișier. Sau ai modificat fișierul, dar nu l-ai salvat. Rezultatul nu se schimbă orice ai face. Când o modificare evidentă „nu are niciun efect”, verifică întâi că rulezi ce crezi că rulezi: pune un `print("DEBUG versiunea nouă")` la începutul fișierului. Butonul **Rulează și verifică** salvează și rulează mereu fișierul deschis în editor.

## Exercițiu

În `capitole/26-depanare/depanare.py`, copiază programul de mai jos. Ar trebui să calculeze totalul unui coș de cumpărături, cu 10% reducere pentru produsele de cel puțin 20 de lei, dar rezultatul e greșit, fără nicio eroare.

```python
COS = """
pâine; 4.50; 2
cafea; 32.00; 1
lapte; 8.99 ; 3
ciocolată; 21.5; 2
"""


def citeste_cos(text):
    cos = []
    for linie in text.strip().split("\n"):
        produs, pret, cantitate = linie.split(";")
        cos.append((produs, pret.strip(), int(cantitate)))
    return cos


def total(cos):
    suma = 0
    for produs, pret, cantitate in cos:
        pret = float(pret)
        if str(pret) >= "20":
            pret = pret * 0.9
        suma = pret * cantitate
    return suma


print(f"Total: {total(citeste_cos(COS)):.2f} lei")
```

1. Calculează de mână totalul corect și scrie-l într-un comentariu.
2. Găsește greșelile (sunt **două**) **doar** cu `print(f"DEBUG {...=}")` și cu `breakpoint()` (folosește măcar o dată `p`, `n` și `c`). Nu modifica nimic înainte să fi confirmat ipoteza.
3. Pentru fiecare greșeală, scrie într-un comentariu ipoteza, cum ai verificat-o și reparația.
4. La final, șterge toate rândurile `DEBUG` și orice `breakpoint()`, apoi apasă **Rulează și verifică**.

## Pe scurt

- Depanează cu metodă: formulează problema, reprodu-o, izolează-o, verifică o ipoteză, repară un singur lucru, verifică și cazurile vecine.
- `print(f"{x=}")` și `!r` arată și tipul (ghilimele) și caracterele invizibile; marchează afișările cu `DEBUG`.
- `breakpoint()` oprește programul în pdb: `p` afișează, `n` merge un rând, `s` intră în funcție, `c` continuă, `l` arată codul, `w` arată stiva, `q` iese.
- În pdb, rândul de după `->` e cel care **urmează** să se execute.
- Nu ascunde o greșeală cu `try / except`: găsește-i cauza.
- Înainte să predai codul, șterge `DEBUG`-urile și `breakpoint()`-urile.
