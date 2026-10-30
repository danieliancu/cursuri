## Ce este

Un **traceback** este raportul pe care Python îl afișează când programul se oprește din cauza unei erori. Îl tot vezi din lecția 1. Acum înveți să-l citești sistematic, pentru că îți spune aproape tot ce trebuie să știi ca să repari problema:
- **ce** s-a întâmplat: tipul erorii și mesajul, pe ultimul rând;
- **unde** s-a întâmplat: fișierul, rândul și funcția;
- **cum** s-a ajuns acolo: lanțul de funcții care s-au apelat una pe alta.

<!-- fisier: note.py -->
```python
def medie(note):
    return sum(note) / len(note)


def raport(elev, note):
    print(f"{elev}: {medie(note):.2f}")


raport("Ana", [9, 10, 8])
raport("Mihai", [])
```

```text
Ana: 9.00
Traceback (most recent call last):
  File "note.py", line 10, in <module>
    raport("Mihai", [])
  File "note.py", line 6, in raport
    print(f"{elev}: {medie(note):.2f}")
                     ^^^^^^^^^^^
  File "note.py", line 2, in medie
    return sum(note) / len(note)
           ~~~~~~~~~~^~~~~~~~~~~
ZeroDivisionError: division by zero
```

## De ce contează

Programatorii începători se sperie de un traceback și sar direct la „nu merge”. Programatorii cu experiență îl citesc primii, pentru că acolo e jumătate din rezolvare. Un traceback lung nu înseamnă o problemă mai gravă, ci doar că eroarea a apărut adânc, într-o funcție apelată de alte funcții.

În Django, un singur clic pe o pagină trece prin zeci de funcții (ale tale și ale framework-ului), iar tracebackurile au des 20–30 de rânduri. Dacă știi unde să te uiți, găsești în câteva secunde rândul tău care contează.

## Cum funcționează

### Citește de jos în sus

Un traceback are trei părți:

1. **Antetul** `Traceback (most recent call last):` înseamnă „ultimul apel e cel mai de jos”. Tracebackul pornește de la începutul programului și coboară până la locul erorii.
2. **Cadrele** (în engleză „frames”): câte două-trei rânduri pentru fiecare funcție aflată în execuție în acel moment:
   - `File "note.py", line 10, in <module>`: fișierul, rândul și funcția. `<module>` înseamnă „codul de la nivelul de bază al fișierului”, din afara oricărei funcții;
   - rândul de cod, așa cum e scris;
   - uneori, semnele `^^^` și `~~~` care subliniază exact bucata cu probleme.
3. **Ultimul rând**: tipul erorii și mesajul. **Începe mereu de aici.**

Pentru exemplul din „Ce este”, citirea de jos în sus spune o poveste:
- `ZeroDivisionError: division by zero`: s-a împărțit la zero;
- în funcția `medie`, rândul 2, `sum(note) / len(note)`: `len(note)` a fost 0;
- `medie` a fost apelată din `raport`, rândul 6;
- `raport` a fost apelată de la rândul 10, cu `raport("Mihai", [])`: **aici** a apărut lista goală.

Eroarea s-a produs în `medie`, dar cauza e la rândul 10, unde Mihai nu are note. Rândul de jos îți spune **unde a explodat**; restul cadrelor te ajută să afli **de unde a venit** valoarea greșită.

### Ce se întâmplă „pe dedesubt”: stiva de apeluri

Când o funcție apelează altă funcție, Python ține minte unde trebuie să revină. Lista apelurilor în curs se numește **stiva de apeluri** (în engleză „call stack”): `<module>` a apelat `raport`, care a apelat `medie`. Când apare o eroare, Python o „aruncă” în sus prin stivă: dacă funcția curentă nu o tratează, eroarea trece la funcția care a apelat-o, apoi la următoarea și tot așa. Dacă nicio funcție nu o tratează, programul se oprește și afișează stiva exact cum era în momentul erorii. Acela e tracebackul.

Faptul că eroarea „urcă” prin funcții e cheia lecției următoare: la lecția 24 vei învăța s-o prinzi cu `try / except`, în funcția potrivită.

### Erorile pe care le vei vedea cel mai des

| Eroare | Ce înseamnă | Exemplu tipic |
|---|---|---|
| `SyntaxError` | codul nu respectă regulile limbajului | ghilimele sau paranteze neînchise, `:` lipsă |
| `IndentationError` | indentare greșită (un tip de `SyntaxError`) | spații în plus, bloc neindentat |
| `NameError` | nume necunoscut | variabilă scrisă greșit sau folosită înainte de atribuire |
| `TypeError` | operație pe un tip nepotrivit | `"25" + 1`, funcție apelată cu prea multe argumente |
| `ValueError` | tipul e bun, valoarea nu | `int("abc")` |
| `IndexError` | poziție inexistentă | `lista[10]` într-o listă cu 3 elemente |
| `KeyError` | cheie inexistentă într-un dicționar | `preturi["ceai"]` |
| `AttributeError` | obiectul nu are metoda sau atributul cerut | `(1, 2).append(3)` |
| `ZeroDivisionError` | împărțire la zero | `x / 0` |

Câteva le-ai întâlnit deja. Iată cum arată ultimul rând pentru restul:

<!-- fisier: erori.py -->
```python
def salut(nume):
    return f"Salut, {nume}!"


print(salut("Ana", "Mihai"))
```

```text
Traceback (most recent call last):
  File "erori.py", line 5, in <module>
    print(salut("Ana", "Mihai"))
          ^^^^^^^^^^^^^^^^^^^^^
TypeError: salut() takes 1 positional argument but 2 were given
```

Mesajul spune exact problema: funcția primește un argument, dar a primit două.

<!-- fisier: erori.py -->
```python
persoana = {"nume": "Ana Popescu", "varsta": 25}
print(persoana["oras"])
```

```text
Traceback (most recent call last):
  File "erori.py", line 2, in <module>
    print(persoana["oras"])
          ~~~~~~~~^^^^^^^^
KeyError: 'oras'
```

La `KeyError`, mesajul e chiar cheia care lipsește.

### SyntaxError nu are cadre

Erorile de sintaxă sunt găsite **înainte** ca programul să pornească (lecția 1), deci nu există stivă de apeluri și nici antetul `Traceback`. Python arată doar fișierul, rândul și locul:

<!-- fisier: erori.py -->
```python
note = [9, 10, 8
print(note)
```

```text
  File "erori.py", line 1
    note = [9, 10, 8
           ^
SyntaxError: '[' was never closed
```

Atenție: uneori locul arătat la o eroare de sintaxă e **după** greșeala reală, pentru că Python își dă seama abia mai târziu că ceva nu se potrivește. Dacă rândul indicat pare corect, uită-te și la rândul de deasupra.

### Cadre din codul altora

Când folosești funcții din biblioteca standard sau din Django, tracebackul conține și cadre din fișierele lor. Aici am folosit modulul `json` (`import` îl înveți la lecția 29, iar JSON la lecția 28):

<!-- fisier: date.py -->
```python
import json


def citeste_setari(text):
    return json.loads(text)


setari = citeste_setari("{'tema': 'dark'}")
```

```text
Traceback (most recent call last):
  File "date.py", line 8, in <module>
    setari = citeste_setari("{'tema': 'dark'}")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "date.py", line 5, in citeste_setari
    return json.loads(text)
           ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/json/decoder.py", line 338, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/json/decoder.py", line 354, in raw_decode
    obj, end = self.scan_once(s, idx)
               ^^^^^^^^^^^^^^^^^^^^^^
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

Ultimele trei cadre sunt în fișierele lui Python (`/usr/local/lib/python3.12/...`; numerele de rând de acolo pot diferi puțin de la o versiune la alta). Codul acela e testat de milioane de oameni, deci problema e aproape sigur la tine. Regula: **caută ultimul cadru din fișierele tale**. Aici e `date.py`, rândul 5, iar mesajul spune ce lipsește: JSON vrea ghilimele duble, nu simple.

## Exemplu complet

Un program care calculează mediile dintr-un catalog are două greșeli. Le găsim doar citind tracebackurile, pe rând.

<!-- fisier: catalog.py -->
```python
catalog = {
    "Ana Popescu": [9, 10, 8],
    "Mihai Ionescu": [7, 6, 9],
    "Ioana Marin": [10, "9", 10],
}


def medie(note):
    return sum(note) / len(note)


def afiseaza(catalog):
    for elev, note in catalog.items():
        print(f"{elev:<14} {medie(note):.2f}")


afiseaza(catalog)
```

```text
Ana Popescu    9.00
Mihai Ionescu  7.33
Traceback (most recent call last):
  File "catalog.py", line 17, in <module>
    afiseaza(catalog)
  File "catalog.py", line 14, in afiseaza
    print(f"{elev:<14} {medie(note):.2f}")
                        ^^^^^^^^^^^
  File "catalog.py", line 9, in medie
    return sum(note) / len(note)
           ^^^^^^^^^
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

Citirea de jos în sus:
1. `TypeError: unsupported operand type(s) for +: 'int' and 'str'`: cineva a încercat să adune un număr cu un text;
2. în `medie`, la `sum(note)`: adunarea vine din `sum()`, deci în lista de note e un string;
3. `medie` a fost apelată din `afiseaza`, iar Ana și Mihai s-au afișat deja, deci problema e la **al treilea** elev;
4. în catalog, Ioana are `"9"` între ghilimele. Asta e cauza.

După corectură (`9` în loc de `"9"`), programul merge. Adăugăm un elev nou, fără note încă:

<!-- fisier: catalog.py -->
```python
catalog = {
    "Ana Popescu": [9, 10, 8],
    "Mihai Ionescu": [7, 6, 9],
    "Ioana Marin": [10, 9, 10],
    "Radu Pop": [],
}


def medie(note):
    return sum(note) / len(note)


def afiseaza(catalog):
    for elev, note in catalog.items():
        print(f"{elev:<14} {medie(note):.2f}")


afiseaza(catalog)
```

```text
Ana Popescu    9.00
Mihai Ionescu  7.33
Ioana Marin    9.67
Traceback (most recent call last):
  File "catalog.py", line 18, in <module>
    afiseaza(catalog)
  File "catalog.py", line 15, in afiseaza
    print(f"{elev:<14} {medie(note):.2f}")
                        ^^^^^^^^^^^
  File "catalog.py", line 10, in medie
    return sum(note) / len(note)
           ~~~~~~~~~~^~~~~~~~~~~
ZeroDivisionError: division by zero
```

Aceeași funcție, altă eroare. Aici nu e o greșeală de date, ci un caz pe care `medie()` nu-l tratează: un elev fără note. Repararea ține de decizie: ce afișăm pentru Radu? O variantă e ca `afiseaza()` să verifice `if note:` și să scrie „fără note”. La lecțiile 24 și 25 vei vedea alte variante.

## Greșeli frecvente

### 1. Citirea doar a primelor rânduri

Primele rânduri ale unui traceback lung arată de unde **a pornit** programul (`<module>`), adică partea cea mai puțin interesantă. Informația importantă e la final. Obișnuiește-te să derulezi direct la ultimul rând, apoi să urci câte un cadru.

### 2. Repararea rândului indicat, când cauza e în altă parte

<!-- fisier: pret.py -->
```python
def pret_cu_tva(pret):
    total = pret * 1.21


def total_cos(preturi):
    suma = 0
    for pret in preturi:
        suma += pret_cu_tva(pret)
    return suma


print(total_cos([10, 20]))
```

```text
Traceback (most recent call last):
  File "pret.py", line 12, in <module>
    print(total_cos([10, 20]))
          ^^^^^^^^^^^^^^^^^^^
  File "pret.py", line 8, in total_cos
    suma += pret_cu_tva(pret)
TypeError: unsupported operand type(s) for +=: 'int' and 'NoneType'
```

Eroarea e raportată la rândul 8, dar rândul 8 e corect. `NoneType` e tipul lui `None`, valoarea întoarsă de o funcție fără `return` (lecția 18). Cauza e în `pret_cu_tva`, care calculează `total`, dar uită să-l întoarcă. Când mesajul pomenește `None` sau `NoneType`, întreabă-te: ce funcție trebuia să întoarcă ceva și nu a întors?

```python
def pret_cu_tva(pret):
    return pret * 1.21
```

### 3. Ignorarea sugestiilor „Did you mean”

<!-- fisier: pret.py -->
```python
cumparaturi = ["pâine", "lapte"]
cumparaturi.apend("ouă")
```

```text
Traceback (most recent call last):
  File "pret.py", line 2, in <module>
    cumparaturi.apend("ouă")
    ^^^^^^^^^^^^^^^^^
AttributeError: 'list' object has no attribute 'apend'. Did you mean: 'append'?
```

Python 3.12 îți sugerează des numele corect, la `NameError`, `AttributeError` și `ImportError`. Citește mesajul până la capăt înainte să cauți altundeva.

### 4. O variabilă atribuită doar pe o ramură

<!-- fisier: pret.py -->
```python
def calificativ(nota):
    if nota >= 9:
        rezultat = "Foarte bine"
    elif nota >= 5:
        rezultat = "Suficient"
    return rezultat


print(calificativ(9.5))
print(calificativ(4))
```

```text
Foarte bine
Traceback (most recent call last):
  File "pret.py", line 10, in <module>
    print(calificativ(4))
          ^^^^^^^^^^^^^^
  File "pret.py", line 6, in calificativ
    return rezultat
           ^^^^^^^^
UnboundLocalError: cannot access local variable 'rezultat' where it is not associated with a value
```

`UnboundLocalError` e o variantă de `NameError`: variabila e locală funcției (lecția 20), dar pe drumul pe care l-a luat execuția nu a primit nicio valoare. Pentru nota 4, nicio ramură nu e adevărată. Lipsește un `else` (sau o valoare inițială înainte de `if`).

### 5. Căutarea problemei în codul bibliotecii

Când ultimele cadre sunt în fișiere ca `/usr/local/lib/python3.12/...` sau `.../site-packages/django/...`, tentația e să citești codul acela. Aproape întotdeauna, greșit e ce le-ai dat tu: un argument de tipul greșit, un text în formatul greșit. Urcă până la ultimul cadru din fișierele tale și verifică valorile transmise de acolo, ca în exemplul cu `json` de mai sus.

## Exercițiu

În `capitole/23-traceback/traceback_exercitii.py` (numele are `_exercitii`, pentru că `traceback` e și numele unui modul din biblioteca standard), copiază programul de mai jos. Are **trei** greșeli. Rulează-l, citește tracebackul, repară **doar** greșeala indicată, apoi rulează din nou, până merge.

<!-- nu-rula -->
```python
def pret_total(produs, cantitate, preturi):
    return preturi[produs] * cantitate


def bon(comanda, preturi):
    total = 0
    for produs, cantitate in comanda:
        valoare = pret_total(produs, cantitate, preturi)
        print(f"{produs:<8} {cantitate} x = {valoare:.2f}")
        total += valoare
    return total


preturi = {"pâine": 4.5, "lapte": 8.99, "cafea": 32.0}
comanda = [("pâine", 2), ("Lapte", 1), ("cafea", "1")]
print(f"Total: {bon(comanda, preturi):.2f}")
print(f"Produse comandate: {len(comanda)")
```

Pentru fiecare greșeală, scrie deasupra rândului reparat un comentariu cu:
1. tipul erorii și mesajul;
2. rândul raportat **ultimul** în traceback;
3. rândul unde era **de fapt** cauza (poate fi altul).

Indiciu: una dintre greșeli e de sintaxă, deci apare prima, înainte să ruleze ceva.

## Pe scurt

- Un traceback se citește **de jos în sus**: ultimul rând dă tipul și mesajul erorii, cadrele de deasupra arată drumul prin funcții.
- Fiecare cadru are fișierul, rândul și funcția (`<module>` = codul din afara funcțiilor); `^^^` și `~~~` subliniază bucata cu probleme.
- Eroarea urcă prin stiva de apeluri până o prinde cineva (lecția 24) sau până oprește programul.
- Rândul unde „explodează” nu e mereu rândul greșit: urmărește de unde vine valoarea (de exemplu, `None` dintr-o funcție fără `return`).
- `SyntaxError` nu are cadre, pentru că apare înainte de rulare; uneori greșeala reală e pe rândul de deasupra.
- În tracebackurile lungi, caută ultimul cadru din fișierele tale și citește sugestiile „Did you mean”.
