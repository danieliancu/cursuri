## Ce este

O **listă** (tipul `list`) este o colecție ordonată de valori, păstrate împreună sub un singur nume. Se scrie între paranteze drepte, cu elementele separate prin virgulă:

```python
cumparaturi = ["pâine", "lapte", "ouă", "cafea"]
note = [9, 7.5, 10, 8]
print(cumparaturi)
print(len(cumparaturi), type(cumparaturi))
```

```text
['pâine', 'lapte', 'ouă', 'cafea']
4 <class 'list'>
```

Ai mai întâlnit liste fără să le studiezi: rezultatul lui `split()` (lecția 4) e o listă. Spre deosebire de un string, o listă poate conține **orice fel de valori** și, foarte important, poate fi **modificată** după ce a fost creată.

## De ce contează

Programele lucrează rar cu o singură valoare: au mai multe produse într-un coș, mai multe note ale unui elev, mai mulți utilizatori, mai multe rânduri dintr-un fișier, mai multe articole dintr-un blog. Fără liste, ar trebui să creezi câte o variabilă pentru fiecare (`produs1`, `produs2`, ...) și n-ai putea lucra cu un număr de elemente pe care nu-l știi dinainte.

Listele sunt cea mai folosită colecție din Python. În Django, rezultatul unei interogări la baza de date (lecția 52) se folosește aproape exact ca o listă.

## Cum funcționează

### Crearea unei liste

```python
goala = []
numere = [3, 1, 4, 1, 5]            # elementele se pot repeta
amestec = ["Ana", 25, 1.68, True]   # tipuri diferite (posibil, dar rar util)
litere = list("Cluj")               # list() transformă o secvență în listă
pana_la_cinci = list(range(1, 6))
print(litere)
print(pana_la_cinci)
```

```text
['C', 'l', 'u', 'j']
[1, 2, 3, 4, 5]
```

În practică, o listă conține de obicei elemente **de același fel**: toate prețuri, toate nume. Asta face codul ușor de înțeles.

### Indexare și slicing

Tot ce știi de la stringuri (lecția 4) funcționează și aici: indexul începe de la 0, indicii negativi numără de la final, iar slicing-ul ia o bucată.

```python
cumparaturi = ["pâine", "lapte", "ouă", "cafea", "mere"]
print(cumparaturi[0])
print(cumparaturi[-1])
print(cumparaturi[1:3])
print(cumparaturi[:2])
print(cumparaturi[::-1])
```

```text
pâine
mere
['lapte', 'ouă']
['pâine', 'lapte']
['mere', 'cafea', 'ouă', 'lapte', 'pâine']
```

Indexarea dă **un element**, iar slicing-ul dă **o listă nouă** (chiar dacă are un singur element).

### Listele se pot modifica

Spre deosebire de stringuri, listele sunt **mutabile**: poți schimba un element direct.

```python
cumparaturi = ["pâine", "lapte", "ouă"]
cumparaturi[1] = "iaurt"
print(cumparaturi)
```

```text
['pâine', 'iaurt', 'ouă']
```

### Adăugare

```python
cumparaturi = ["pâine", "lapte"]
cumparaturi.append("ouă")               # la final
cumparaturi.insert(0, "cafea")          # pe poziția 0, restul se mută la dreapta
cumparaturi.extend(["mere", "pere"])    # adaugă toate elementele altei liste
print(cumparaturi)
```

```text
['cafea', 'pâine', 'lapte', 'ouă', 'mere', 'pere']
```

`append()` e cea mai folosită: construiești o listă pornind de la `[]` și adăugând elemente unul câte unul, de obicei într-o buclă.

Spre deosebire de metodele stringurilor, aceste metode **modifică lista pe loc** și nu întorc o listă nouă. Revenim la asta la greșeli frecvente.

### Ștergere

```python
cumparaturi = ["cafea", "pâine", "lapte", "ouă", "lapte"]
cumparaturi.remove("lapte")     # șterge PRIMA apariție a valorii
print(cumparaturi)

ultimul = cumparaturi.pop()     # scoate ultimul element și îl întoarce
print(ultimul, cumparaturi)

primul = cumparaturi.pop(0)     # scoate elementul de pe poziția 0
print(primul, cumparaturi)

del cumparaturi[0]              # șterge după poziție, fără să întoarcă ceva
print(cumparaturi)
```

```text
['cafea', 'pâine', 'ouă', 'lapte']
lapte ['cafea', 'pâine', 'ouă']
cafea ['pâine', 'ouă']
['ouă']
```

Pe scurt: `remove()` caută după **valoare**, iar `pop()` și `del` lucrează după **poziție**. `pop()` e util când vrei și elementul scos. Pentru a goli o listă, există `clear()`.

### Căutare: in, index(), count()

```python
cumparaturi = ["pâine", "lapte", "ouă", "lapte"]
print("ouă" in cumparaturi)
print("cafea" not in cumparaturi)
print(cumparaturi.index("lapte"))
print(cumparaturi.count("lapte"))
```

```text
True
True
1
2
```

`index()` dă poziția primei apariții. Dacă valoarea lipsește, dă eroare (`ValueError`), așa că verifică întâi cu `in`.

### Parcurgere cu for

`for` (lecția 10) funcționează pe liste exact ca pe texte:

```python
preturi = [4.5, 8.99, 32.0, 12.5]
total = 0
for pret in preturi:
    total += pret
print(f"Total: {total:.2f} lei")
```

```text
Total: 57.99 lei
```

Un tipar foarte des întâlnit: construiești o listă nouă din alta, păstrând doar unele elemente sau transformându-le.

```python
note = [9, 4, 7.5, 10, 3, 8]
promovate = []
for nota in note:
    if nota >= 5:
        promovate.append(nota)
print(promovate)
```

```text
[9, 7.5, 10, 8]
```

La lecția 16 vei vedea o scriere mai scurtă pentru asta (list comprehension).

### Sortare: sort() și sorted()

```python
note = [9, 4, 7.5, 10, 3]
note.sort()
print(note)

nume = ["Mihai", "ana", "Bogdan", "Ana"]
in_ordine = sorted(nume)
print(in_ordine)
print(nume)
print(sorted(note, reverse=True))
```

```text
[3, 4, 7.5, 9, 10]
['Ana', 'Bogdan', 'Mihai', 'ana']
['Mihai', 'ana', 'Bogdan', 'Ana']
[10, 9, 7.5, 4, 3]
```

Diferența e importantă:
- `lista.sort()` **modifică** lista pe loc și nu întoarce nimic;
- `sorted(lista)` **creează o listă nouă**, sortată, iar originalul rămâne neschimbat. Funcționează pe orice secvență, inclusiv pe un string.

`reverse=True` sortează descrescător. Stringurile se sortează după regulile de la lecția 7: literele mari înaintea celor mici. Sortarea după alte criterii (de exemplu, fără să conteze literele mari) se face cu `key`, la lecția 17.

### Liste imbricate

Elementele unei liste pot fi alte liste. Așa reprezinți un tabel: o listă de rânduri.

```python
catalog = [
    ["Ana", 9, 10, 8],
    ["Mihai", 7, 6, 9],
    ["Ioana", 10, 9, 10],
]
print(catalog[1])
print(catalog[1][0], catalog[1][2])

for rand in catalog:
    nume = rand[0]
    note = rand[1:]
    media = (note[0] + note[1] + note[2]) / len(note)
    print(f"{nume:<6} {media:.2f}")
```

```text
['Mihai', 7, 6, 9]
Mihai 6
Ana    9.00
Mihai  7.33
Ioana  9.67
```

`catalog[1][2]` se citește de la stânga la dreapta: `catalog[1]` e rândul lui Mihai, iar `[2]` e al treilea element din acel rând. Media e calculată aici pentru exact trei note; o funcție care adună oricâte elemente, `sum()`, apare la lecția 14.

### Ce se întâmplă „pe dedesubt”: două nume, aceeași listă

Îți amintești de la lecția 2 că variabilele sunt etichete pe obiecte? Pentru numere și stringuri, diferența nu se vedea, pentru că ele nu pot fi modificate. La liste se vede:

```python
lista_ana = ["pâine", "lapte"]
lista_mihai = lista_ana          # NU e o copie: e a doua etichetă pe aceeași listă
lista_mihai.append("bere")
print(lista_ana)
print(lista_ana is lista_mihai)
```

```text
['pâine', 'lapte', 'bere']
True
```

Mihai a adăugat „bere” pe lista lui, dar a apărut și pe a Anei, pentru că e **aceeași listă**. Fenomenul se numește **aliasing**: două nume pentru același obiect. Operatorul `is` verifică exact asta: dacă două nume arată spre același obiect (spre deosebire de `==`, care verifică dacă valorile sunt egale).

Ca să obții o listă **separată**, faci o copie:

```python
lista_ana = ["pâine", "lapte"]
lista_mihai = lista_ana.copy()   # sau list(lista_ana), sau lista_ana[:]
lista_mihai.append("bere")
print(lista_ana)
print(lista_mihai)
```

```text
['pâine', 'lapte']
['pâine', 'lapte', 'bere']
```

Atenție: `copy()` copiază doar lista „de sus”. Într-o listă imbricată, listele interioare rămân comune. Când ai nevoie de copii complete, există `copy.deepcopy()` din modulul `copy` al bibliotecii standard (despre module și `import`, la lecția 29).

## Exemplu complet

Lista de cumpărături a Anei, gestionată dintr-un meniu.

<!-- fisier: cumparaturi.py -->
<!-- stdin: 1\nlapte\n1\npâine\n1\nlapte\n1\nouă\n3\n2\npâine\n2\nmere\n4\n0 -->
```python
cumparaturi = []

while True:
    print("\n1 = adaugă, 2 = șterge, 3 = afișează, 4 = sortează, 0 = gata")
    optiune = input("Alege: ").strip()

    if optiune == "0":
        break
    elif optiune == "1":
        produs = input("Produs: ").strip().lower()
        if not produs:
            print("Numele produsului e gol.")
        elif produs in cumparaturi:
            print(f"„{produs}” e deja pe listă.")
        else:
            cumparaturi.append(produs)
    elif optiune == "2":
        produs = input("Ce ștergi? ").strip().lower()
        if produs in cumparaturi:
            cumparaturi.remove(produs)
            print(f"Am șters „{produs}”.")
        else:
            print(f"„{produs}” nu e pe listă.")
    elif optiune == "3":
        if not cumparaturi:
            print("Lista e goală.")
        for pozitie in range(len(cumparaturi)):
            print(f"{pozitie + 1}. {cumparaturi[pozitie]}")
    elif optiune == "4":
        cumparaturi.sort()
        print("Sortată.")
    else:
        print("Opțiune necunoscută.")

print(f"\nDe cumpărat ({len(cumparaturi)}): {', '.join(cumparaturi)}")
```

```text

1 = adaugă, 2 = șterge, 3 = afișează, 4 = sortează, 0 = gata
Alege: 1
Produs: lapte

1 = adaugă, 2 = șterge, 3 = afișează, 4 = sortează, 0 = gata
Alege: 1
Produs: pâine

1 = adaugă, 2 = șterge, 3 = afișează, 4 = sortează, 0 = gata
Alege: 1
Produs: lapte
„lapte” e deja pe listă.

1 = adaugă, 2 = șterge, 3 = afișează, 4 = sortează, 0 = gata
Alege: 1
Produs: ouă

1 = adaugă, 2 = șterge, 3 = afișează, 4 = sortează, 0 = gata
Alege: 3
1. lapte
2. pâine
3. ouă

1 = adaugă, 2 = șterge, 3 = afișează, 4 = sortează, 0 = gata
Alege: 2
Ce ștergi? pâine
Am șters „pâine”.

1 = adaugă, 2 = șterge, 3 = afișează, 4 = sortează, 0 = gata
Alege: 2
Ce ștergi? mere
„mere” nu e pe listă.

1 = adaugă, 2 = șterge, 3 = afișează, 4 = sortează, 0 = gata
Alege: 4
Sortată.

1 = adaugă, 2 = șterge, 3 = afișează, 4 = sortează, 0 = gata
Alege: 0

De cumpărat (2): lapte, ouă
```

Observă:
- lista pornește goală și crește cu `append()`;
- `if not cumparaturi:` verifică dacă lista e goală (o listă goală e considerată falsă, lecția 7);
- `", ".join(cumparaturi)` lipește elementele cu virgulă (lecția 4) și funcționează doar pe liste de stringuri;
- numerotarea folosește `range(len(...))` ca să avem și poziția. La lecția 17 vei vedea `enumerate()`, care face asta mai elegant.

## Greșeli frecvente

### 1. Index în afara listei

<!-- fisier: lista.py -->
```python
cumparaturi = ["pâine", "lapte", "ouă"]
print(cumparaturi[3])
```

```text
Traceback (most recent call last):
  File "lista.py", line 2, in <module>
    print(cumparaturi[3])
          ~~~~~~~~~~~^^^
IndexError: list index out of range
```

O listă cu 3 elemente are indicii 0, 1 și 2. Ultimul element e `cumparaturi[-1]`. Aceeași eroare apare dacă încerci `cumparaturi[0]` pe o listă goală, așa că verifică întâi `if cumparaturi:`.

### 2. Atribuirea rezultatului lui append() sau sort()

```python
note = [9, 4, 7]
note = note.append(10)
print(note)

preturi = [32, 4.5, 8.99]
sortate = preturi.sort()
print(sortate)
```

```text
None
None
```

`append()` și `sort()` modifică lista pe loc și întorc `None`, o valoare specială care înseamnă „nimic” (o vei întâlni din nou la lecția 18). Prin atribuire, ai pierdut lista. Corect:

```python
note = [9, 4, 7]
note.append(10)

preturi = [32, 4.5, 8.99]
sortate = sorted(preturi)
```

E opusul regulii de la stringuri (lecția 4): metodele stringurilor întorc un string nou, iar metodele listelor de obicei modifică lista și întorc `None`.

### 3. remove() pe o valoare care nu există

<!-- fisier: lista.py -->
```python
cumparaturi = ["pâine", "lapte"]
cumparaturi.remove("cafea")
```

```text
Traceback (most recent call last):
  File "lista.py", line 2, in <module>
    cumparaturi.remove("cafea")
ValueError: list.remove(x): x not in list
```

Verifică întâi cu `in`, ca în exemplul complet. Același lucru e valabil pentru `index()`.

### 4. Copie care nu e copie

```python
original = [1, 2, 3]
copie = original
copie.append(4)
print(original)
```

```text
[1, 2, 3, 4]
```

`copie = original` nu copiază nimic, ci doar mai lipește o etichetă pe aceeași listă (vezi „pe dedesubt”). Folosește `original.copy()`.

### 5. Ștergerea elementelor în timp ce parcurgi lista

```python
note = [4, 3, 9, 2, 8]
for nota in note:
    if nota < 5:
        note.remove(nota)
print(note)
```

```text
[3, 9, 8]
```

Nota 3 a rămas, deși e sub 5. După ce `remove()` șterge 4, toate elementele se mută cu o poziție la stânga, iar `for` trece la poziția următoare și „sare” peste 3. Nu modifica o listă în timp ce o parcurgi. Construiește una nouă, cu elementele pe care le păstrezi:

```python
note = [4, 3, 9, 2, 8]
pastrate = []
for nota in note:
    if nota >= 5:
        pastrate.append(nota)
note = pastrate
print(note)
```

```text
[9, 8]
```

## Exercițiu

În `capitole/12-liste/liste.py`, scrie un program pentru **catalogul unei clase**:

1. pornește de la o listă goală de elevi; fiecare elev e o listă `[nume, nota1, nota2, nota3]`;
2. într-o buclă, cere numele elevului (gol = gata) și cele trei note ale lui, validate ca la lecția 10, apoi adaugă elevul în catalog;
3. la final afișează un tabel cu numele, cele trei note și media fiecăruia (2 zecimale, coloane aliniate);
4. afișează separat lista elevilor cu media sub 5, sau mesajul „Toți elevii au promovat”;
5. afișează numele elevilor sortate alfabetic, fără să schimbi ordinea din catalog (gândește-te: `sort()` sau `sorted()`?).

## Pe scurt

- O listă e o colecție ordonată și **modificabilă**: `[1, 2, 3]`, `list("abc")`, `list(range(5))`.
- Indexarea și slicing-ul funcționează ca la stringuri; `lista[i] = valoare` schimbă un element.
- Adăugare: `append`, `insert`, `extend`. Ștergere: `remove` (după valoare), `pop` și `del` (după poziție). Căutare: `in`, `index`, `count`.
- `lista.sort()` modifică lista și întoarce `None`; `sorted(lista)` întoarce o listă nouă.
- O listă imbricată reprezintă un tabel: `catalog[rand][coloana]`.
- `b = a` nu copiază o listă, ci creează un alias; pentru o copie folosește `a.copy()`. Nu modifica o listă în timp ce o parcurgi.
