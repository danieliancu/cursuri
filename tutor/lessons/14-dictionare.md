## Ce este

Un **dicționar** (tipul `dict`) păstrează perechi **cheie → valoare**. În loc să cauți o valoare după poziție, ca la liste, o cauți după **cheie**, ca într-un dicționar adevărat, unde cauți după cuvânt și găsești definiția.

```python
persoana = {
    "nume": "Ana Popescu",
    "varsta": 25,
    "oras": "Cluj",
}
print(persoana["nume"])
print(persoana["oras"])
print(len(persoana), type(persoana))
```

```text
Ana Popescu
Cluj
3 <class 'dict'>
```

Se scrie cu acolade `{ }`, iar fiecare pereche are forma `cheie: valoare`. Cheile sunt de obicei stringuri, dar pot fi și numere sau tupluri.

## De ce contează

Multe date sunt natural de forma „nume → informație”: un produs și prețul lui, un elev și notele lui, un cuvânt și de câte ori apare, un cod de țară și numele țării, un utilizator și setările lui. Cu o listă, ca să afli prețul cafelei ar trebui să parcurgi toate produsele. Cu un dicționar, scrii `preturi["cafea"]` și ai răspunsul imediat.

Dicționarele sunt peste tot în Python și în Django: setările din `settings.py` (lecția 46), datele trimise unui template (lecția 48), datele dintr-un formular (lecția 55), răspunsurile JSON ale unui API (lecția 60). JSON (lecția 28) seamănă aproape perfect cu un dicționar Python.

## Cum funcționează

### Crearea unui dicționar

```python
preturi = {"pâine": 4.5, "lapte": 8.99, "cafea": 32.0}
gol = {}
stoc = dict(mere=12, pere=0)  # altă scriere; cheile respectă regulile numelor de variabile
print(preturi)
print(stoc)
```

```text
{'pâine': 4.5, 'lapte': 8.99, 'cafea': 32.0}
{'mere': 12, 'pere': 0}
```

Cheile sunt **unice**: dacă aceeași cheie apare de două ori, rămâne ultima valoare. Valorile se pot repeta oricât.

Un dicționar păstrează ordinea în care au fost adăugate cheile. Nu are însă poziții: `preturi[0]` nu înseamnă „primul element”, ci „valoarea cheii `0`”.

### Citirea valorilor: [] și get()

```python
preturi = {"pâine": 4.5, "lapte": 8.99, "cafea": 32.0}
print(preturi["cafea"])
print(preturi.get("cafea"))
print(preturi.get("ceai"))
print(preturi.get("ceai", 0))
```

```text
32.0
32.0
None
0
```

- `dictionar[cheie]` dă valoarea, dar produce `KeyError` dacă cheia nu există;
- `dictionar.get(cheie)` dă `None` dacă cheia nu există, iar `get(cheie, implicit)` dă valoarea implicită pe care o alegi.

Folosește `[]` când cheia **trebuie** să existe (lipsa ei ar fi o greșeală pe care vrei s-o vezi). Folosește `get()` când lipsa cheii e un caz normal.

### Adăugare, modificare, ștergere

Atribuirea pe o cheie **adaugă** perechea dacă nu există și o **modifică** dacă există:

```python
preturi = {"pâine": 4.5, "lapte": 8.99}
preturi["cafea"] = 32.0      # cheie nouă: se adaugă
preturi["lapte"] = 9.49      # cheie existentă: se modifică
print(preturi)

del preturi["pâine"]
scos = preturi.pop("cafea")  # șterge și întoarce valoarea
print(scos, preturi)

preturi.update({"ouă": 1.2, "lapte": 9.99})  # mai multe deodată
print(preturi)
```

```text
{'pâine': 4.5, 'lapte': 9.49, 'cafea': 32.0}
32.0 {'lapte': 9.49}
{'lapte': 9.99, 'ouă': 1.2}
```

### in: există cheia?

`in` caută printre **chei**, nu printre valori:

```python
preturi = {"pâine": 4.5, "lapte": 8.99}
print("lapte" in preturi)
print(8.99 in preturi)
print(8.99 in preturi.values())
```

```text
True
False
True
```

Căutarea unei chei e foarte rapidă, oricât de mare ar fi dicționarul (vezi „pe dedesubt”).

### Parcurgerea unui dicționar

Un dicționar are trei „vederi”: `keys()` (cheile), `values()` (valorile) și `items()` (perechile, ca tupluri). Cea mai folosită e `items()`, cu despachetare în `for` (lecția 13):

```python
preturi = {"pâine": 4.5, "lapte": 8.99, "cafea": 32.0}

for produs, pret in preturi.items():
    print(f"{produs:<8}{pret:>7.2f} lei")

print(list(preturi.keys()))

total = 0
for pret in preturi.values():
    total += pret
print(f"Total: {total:.2f}")
```

```text
pâine      4.50 lei
lapte      8.99 lei
cafea     32.00 lei
['pâine', 'lapte', 'cafea']
Total: 45.49
```

Un `for` direct pe dicționar (`for produs in preturi:`) parcurge **cheile**, la fel ca `keys()`.

### Numărarea cu un dicționar

Un tipar clasic: câte apariții are fiecare element? Cheia e elementul, iar valoarea e numărul de apariții.

```python
text = "ana are mere ana are pere ana"
aparitii = {}
for cuvant in text.split():
    aparitii[cuvant] = aparitii.get(cuvant, 0) + 1
print(aparitii)
```

```text
{'ana': 3, 'are': 2, 'mere': 1, 'pere': 1}
```

`aparitii.get(cuvant, 0)` dă numărul de până acum, sau 0 la prima apariție. La lecția 31 vei vedea `Counter`, care face exact asta și mai mult.

### Dicționare care conțin colecții

Valorile pot fi orice: liste, alte dicționare. Așa construiești structuri de date reale.

```python
catalog = {
    "Ana": [9, 10, 8],
    "Mihai": [7, 6, 9],
}
catalog["Ioana"] = [10, 9]          # elev nou
catalog["Ana"].append(10)           # o notă nouă pentru Ana

for elev, note in catalog.items():
    media = sum(note) / len(note)
    print(f"{elev:<6} {note}  media {media:.2f}")
```

```text
Ana    [9, 10, 8, 10]  media 9.25
Mihai  [7, 6, 9]  media 7.33
Ioana  [10, 9]  media 9.50
```

`sum()` adună elementele unei liste de numere. O vei revedea la lecția 17, împreună cu prietenii ei (`min`, `max`, `any`, `all`).

Un dicționar în dicționar descrie un obiect cu mai multe niveluri. Accesul se face pas cu pas, de la stânga la dreapta:

```python
utilizator = {
    "nume": "Ana Popescu",
    "adresa": {"oras": "Cluj", "strada": "Memorandumului", "numar": 28},
    "roluri": ["elev", "autor"],
}
print(utilizator["adresa"]["oras"])
print(utilizator["roluri"][-1])
```

```text
Cluj
autor
```

Exact așa arată datele JSON pe care le vei citi la lecția 28 sau le vei primi de la un API.

### Listă sau dicționar?

- **listă**: elemente de același fel, în ordine, accesate după poziție sau parcurse pe rând (o listă de cumpărături, notele unui elev);
- **dicționar**: valori găsite după un nume sau un identificator (prețul unui produs, setările unei aplicații, datele unei persoane cu câmpuri numite).

Adesea le combini: o listă de dicționare (mai mulți utilizatori, fiecare cu câmpurile lui) sau un dicționar de liste (elevii, fiecare cu notele lui).

### Ce se întâmplă „pe dedesubt”: de ce cheile trebuie să fie imutabile

Un dicționar nu caută cheia comparând-o pe rând cu toate cheile. Din cheie, Python calculează un număr numit **hash**, care spune direct „unde” se află perechea în memorie. Așa găsește cheia la fel de repede într-un dicționar cu 10 elemente ca într-unul cu 10 milioane.

Hash-ul unei chei trebuie să rămână mereu același, altfel perechea s-ar „pierde”. De aceea cheile trebuie să fie **imutabile**: stringuri, numere, tupluri (de valori imutabile). O listă nu poate fi cheie, pentru că s-ar putea schimba după ce a fost pusă în dicționar.

```python
distante = {("Cluj", "Iași"): 390, ("Cluj", "Brașov"): 270}
print(distante[("Cluj", "Iași")])
print(hash("Cluj") == hash("Cluj"))
```

```text
390
True
```

Un tuplu e cheia potrivită pentru o pereche de valori, cum e o pereche de orașe.

## Exemplu complet

Un mic magazin: stocul și prețurile sunt într-un dicționar de dicționare. Clientul comandă produse, iar programul verifică stocul, calculează totalul și actualizează stocul.

<!-- fisier: magazin.py -->
<!-- stdin: cafea 2\nlapte 10\nceai 1\npâine 3\nmere\n\n -->
```python
magazin = {
    "pâine": {"pret": 4.5, "stoc": 20},
    "lapte": {"pret": 8.99, "stoc": 5},
    "cafea": {"pret": 32.0, "stoc": 3},
}
cos = {}  # produs -> cantitate

print("Comandă: „produs cantitate” pe fiecare rând; rând gol = gata.")
while True:
    linie = input("> ").strip().lower()
    if not linie:
        break
    bucati = linie.split()
    if len(bucati) != 2 or not bucati[1].isdigit():
        print("Scrie produsul și cantitatea, de exemplu: cafea 2")
        continue
    produs, cantitate = bucati[0], int(bucati[1])

    if produs not in magazin:
        print(f"Nu avem „{produs}”. Avem: {', '.join(magazin)}.")
        continue
    disponibil = magazin[produs]["stoc"] - cos.get(produs, 0)
    if cantitate > disponibil:
        print(f"Mai avem doar {disponibil} buc. de {produs}.")
        continue
    cos[produs] = cos.get(produs, 0) + cantitate

print("\n--- Bon ---")
total = 0
for produs, cantitate in cos.items():
    pret = magazin[produs]["pret"]
    magazin[produs]["stoc"] -= cantitate
    total += pret * cantitate
    print(f"{produs:<8}{cantitate:>3} x {pret:>6.2f} = {pret * cantitate:>7.2f}")
print(f"{'TOTAL':<23}{total:>7.2f}")

print("\nStoc rămas:", {produs: date["stoc"] for produs, date in magazin.items()})
```

```text
Comandă: „produs cantitate” pe fiecare rând; rând gol = gata.
> cafea 2
> lapte 10
Mai avem doar 5 buc. de lapte.
> ceai 1
Nu avem „ceai”. Avem: pâine, lapte, cafea.
> pâine 3
> mere
Scrie produsul și cantitatea, de exemplu: cafea 2
> 

--- Bon ---
cafea     2 x  32.00 =   64.00
pâine     3 x   4.50 =   13.50
TOTAL                    77.50

Stoc rămas: {'pâine': 17, 'lapte': 5, 'cafea': 1}
```

Detalii:
- `", ".join(magazin)` lipește **cheile** dicționarului, pentru că parcurgerea unui dicționar dă cheile;
- `cos.get(produs, 0)` tratează la fel un produs nou și unul deja comandat;
- ultimul rând folosește un **dict comprehension**, o scriere scurtă pentru „construiește un dicționar dintr-o buclă”. Îl vei învăța la lecția 16.

## Greșeli frecvente

### 1. Cheie inexistentă

<!-- fisier: dictionar.py -->
```python
preturi = {"pâine": 4.5, "lapte": 8.99}
print(preturi["ceai"])
```

```text
Traceback (most recent call last):
  File "dictionar.py", line 2, in <module>
    print(preturi["ceai"])
          ~~~~~~~^^^^^^^^
KeyError: 'ceai'
```

`KeyError` îți arată cheia care lipsește. Folosește `in` sau `get()` când cheia poate lipsi.

### 2. Cheia „aproape” corectă

<!-- fisier: dictionar.py -->
```python
note = {"Ana": 9, "Mihai": 7}
nume = input("Elev: ").strip()
print(note[nume])
```

Cu `ana` tastat cu literă mică, rezultatul e `KeyError: 'ana'`. Pentru un dicționar, `"Ana"` și `"ana"` sunt chei diferite, la fel `1` și `"1"`. Adu cheile la o formă comună când le salvezi și când le cauți (de exemplu cu `.title()` sau `.lower()`). Atenție și la numere citite cu `input()`: rămân stringuri până le convertești.

<!-- fisier: dictionar.py -->
```python
camere = {101: "Ana", 102: "Mihai"}
print(camere["101"])
```

```text
Traceback (most recent call last):
  File "dictionar.py", line 2, in <module>
    print(camere["101"])
          ~~~~~~^^^^^^^
KeyError: '101'
```

### 3. Listă folosită drept cheie

<!-- fisier: dictionar.py -->
```python
distante = {}
distante[["Cluj", "Iași"]] = 390
```

```text
Traceback (most recent call last):
  File "dictionar.py", line 2, in <module>
    distante[["Cluj", "Iași"]] = 390
    ~~~~~~~~^^^^^^^^^^^^^^^^^^
TypeError: unhashable type: 'list'
```

„Unhashable” înseamnă că valoarea nu poate avea un hash, pentru că e mutabilă (vezi „pe dedesubt”). Folosește un tuplu: `distante[("Cluj", "Iași")] = 390`.

### 4. Modificarea dicționarului în timp ce îl parcurgi

<!-- fisier: dictionar.py -->
```python
stoc = {"mere": 12, "pere": 0, "prune": 0}
for produs in stoc:
    if stoc[produs] == 0:
        del stoc[produs]
```

```text
Traceback (most recent call last):
  File "dictionar.py", line 2, in <module>
    for produs in stoc:
RuntimeError: dictionary changed size during iteration
```

Ca la liste (lecția 12), nu adăuga și nu șterge chei în timp ce parcurgi dicționarul. Parcurge o **copie** a cheilor (`list(stoc)`) sau construiește un dicționar nou:

```python
stoc = {"mere": 12, "pere": 0, "prune": 0}
for produs in list(stoc):
    if stoc[produs] == 0:
        del stoc[produs]
print(stoc)
```

```text
{'mere': 12}
```

Modificarea **valorilor** cheilor existente în timpul parcurgerii e permisă: `stoc[produs] -= 1` nu schimbă numărul de chei.

### 5. for pe dicționar se așteaptă să dea perechi

<!-- fisier: dictionar.py -->
```python
preturi = {"pâine": 4.5, "lapte": 8.99}
for produs, pret in preturi:
    print(produs, pret)
```

```text
Traceback (most recent call last):
  File "dictionar.py", line 2, in <module>
    for produs, pret in preturi:
        ^^^^^^^^^^^^
ValueError: too many values to unpack (expected 2)
```

`for` pe dicționar dă doar **cheile**. Python a încercat să despacheteze stringul `"pâine"` în două variabile și a găsit 5 litere. Pentru perechi, folosește `.items()`:

```python
preturi = {"pâine": 4.5, "lapte": 8.99}
for produs, pret in preturi.items():
    print(produs, pret)
```

## Exercițiu

În `capitole/14-dictionare/dictionare.py`, scrie o **agendă de contacte**:

1. agenda e un dicționar `nume -> {"telefon": ..., "oras": ...}`; pornește cu 2–3 contacte scrise în cod;
2. un meniu cu `while True` (lecția 11): `1` = adaugă/actualizează contact, `2` = caută după nume, `3` = șterge, `4` = afișează toate, sortate după nume, `5` = statistică pe orașe, `0` = ieșire;
3. numele se salvează și se caută cu `.title()`, ca „ana popescu” și „Ana Popescu” să fie același contact; un nume care nu există afișează un mesaj, fără `KeyError`;
4. la statistică, construiește un dicționar `oras -> număr de contacte` (tiparul de numărare din lecție) și afișează-l;
5. bonus: la căutare, dacă numele nu există exact, afișează contactele al căror nume **conține** textul căutat.

## Pe scurt

- Un dicționar păstrează perechi `cheie: valoare` și caută după cheie, nu după poziție: `{"nume": "Ana"}`.
- `d[cheie]` dă `KeyError` dacă cheia lipsește; `d.get(cheie, implicit)` nu dă eroare.
- `d[cheie] = valoare` adaugă sau modifică; `del`, `pop()` și `update()` completează operațiile.
- `in` caută printre chei; `items()`, `keys()` și `values()` parcurg perechile, cheile și valorile.
- Tiparul de numărare: `d[x] = d.get(x, 0) + 1`.
- Cheile trebuie să fie imutabile (string, număr, tuplu); nu adăuga și nu șterge chei în timp ce parcurgi dicționarul.
