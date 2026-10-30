## Ce este

Instrucțiunea **`try / except`** îți permite să **prinzi** o eroare (o **excepție**, în limbajul Python) și să decizi tu ce se întâmplă, în loc ca programul să se oprească.

<!-- stdin: douăzeci și cinci -->
```python
text = input("Vârsta: ")
try:
    varsta = int(text)
    print(f"Peste 10 ani vei avea {varsta + 10} de ani.")
except ValueError:
    print(f"„{text}” nu e un număr întreg.")
print("Programul continuă.")
```

```text
Vârsta: douăzeci și cinci
„douăzeci și cinci” nu e un număr întreg.
Programul continuă.
```

Python încearcă (în engleză „try”) blocul de sub `try`. Dacă acolo apare un `ValueError`, sare imediat la blocul `except ValueError` și execută codul de acolo. Programul nu se oprește și nu apare niciun traceback.

## De ce contează

Unele erori nu sunt greșeli ale programatorului, ci situații normale din lumea reală: utilizatorul scrie litere unde se aștepta un număr, un fișier lipsește, rețeaua cade, un formular vine incomplet. Un program bun nu „crapă” în fața lor, ci le tratează: explică problema, cere din nou sau folosește o valoare implicită.

La lecția 6 am văzut că `int(input(...))` oprește programul la primul răspuns greșit și am promis că vom vedea cum se „prinde” eroarea. La lecțiile 8–11 am ocolit problema cu `isdigit()` și cu trucuri ca `replace(".", "", 1)`, care se complică repede (minus, virgulă, spații). Cu `try / except` lași chiar funcția `int()` (sau `float()`) să decidă ce e valid. În Django vei folosi același mecanism, de exemplu când un articol cerut nu există în baza de date.

## Cum funcționează

### Forma completă

```python
try:
    # codul care poate da eroare
    ...
except TipEroare:
    # rulează doar dacă în try a apărut TipEroare
    ...
else:
    # rulează doar dacă în try NU a apărut nicio eroare
    ...
finally:
    # rulează ÎNTOTDEAUNA, cu sau fără eroare
    ...
```

Doar `try` și măcar un `except` (sau un `finally`) sunt obligatorii. Ordinea execuției:
1. se execută blocul `try`, rând cu rând;
2. dacă un rând dă eroare, restul blocului `try` **se sare**, iar Python caută un `except` potrivit tipului erorii;
3. dacă nu a fost nicio eroare, se execută `else`;
4. la final, indiferent ce s-a întâmplat, se execută `finally`.

```python
for text in ["8", "opt", "0"]:
    print(f"--- {text}")
    try:
        numar = int(text)
        rezultat = 100 / numar
    except ValueError:
        print("nu e un număr")
    except ZeroDivisionError:
        print("nu pot împărți la zero")
    else:
        print(f"100 / {numar} = {rezultat}")
    finally:
        print("gata cu acest text")
```

```text
--- 8
100 / 8 = 12.5
gata cu acest text
--- opt
nu e un număr
gata cu acest text
--- 0
nu pot împărți la zero
gata cu acest text
```

### Prinde erori specifice

În `except` scrii tipul erorii pe care o aștepți. Poți avea mai multe `except` (ca mai sus) sau poți prinde mai multe tipuri în același bloc, într-un tuplu:

```python
date = {"pret": "12,5"}
try:
    pret = float(date["pret"])
except (KeyError, ValueError):
    pret = 0.0
print(pret)
```

```text
0.0
```

Prinde **doar** erorile pe care știi să le tratezi. O eroare la care nu te așteptai (de exemplu un `NameError` dintr-un nume scris greșit) trebuie să apară, ca s-o vezi și s-o repari.

### Mesajul erorii: as

Cu `as nume`, primești chiar obiectul excepției. Afișat, el dă mesajul erorii:

```python
try:
    varsta = int("25 de ani")
except ValueError as eroare:
    print(f"Nu am putut converti: {eroare}")
    print(type(eroare).__name__)
```

```text
Nu am putut converti: invalid literal for int() with base 10: '25 de ani'
ValueError
```

E util pentru jurnale sau pentru programatori. Utilizatorilor obișnuiți le arăți de obicei un mesaj scris de tine, în română.

### Validarea input-ului, varianta finală

Bucla `while True` din lecția 11, combinată cu `try`, e felul standard de a cere o valoare până e validă:

<!-- stdin: abc\n\n-12,5 -->
```python
while True:
    text = input("Temperatura (°C): ").strip().replace(",", ".")
    try:
        temperatura = float(text)
        break
    except ValueError:
        print("Scrie un număr, de exemplu 21.5 sau -4.")
print(f"{temperatura} °C = {temperatura * 9 / 5 + 32:.1f} °F")
```

```text
Temperatura (°C): abc
Scrie un număr, de exemplu 21.5 sau -4.
Temperatura (°C): 
Scrie un număr, de exemplu 21.5 sau -4.
Temperatura (°C): -12,5
-12.5 °C = 9.5 °F
```

Observă cum `-12,5` (cu minus și virgulă) a trecut fără probleme. Cu `isdigit()` ar fi fost respins.

Pusă într-o funcție, validarea se scrie o singură dată și se folosește oriunde:

<!-- stdin: zece\n10\n2,5 -->
```python
def citeste_numar(mesaj: str) -> float:
    """Întreabă până primește un număr; acceptă și virgula zecimală."""
    while True:
        text = input(mesaj).strip().replace(",", ".")
        try:
            return float(text)
        except ValueError:
            print("  Nu e un număr valid, mai încearcă.")


lungime = citeste_numar("Lungimea (m): ")
latime = citeste_numar("Lățimea (m): ")
print(f"Suprafața: {lungime * latime:.2f} m²")
```

```text
Lungimea (m): zece
  Nu e un număr valid, mai încearcă.
Lungimea (m): 10
Lățimea (m): 2,5
Suprafața: 25.00 m²
```

`return` din interiorul lui `try` iese direct din funcție (și deci din buclă) cu valoarea bună.

### else și finally, când le folosești

- **`else`** ține în afara lui `try` codul care nu trebuie protejat. Așa, un `except ValueError` nu prinde din greșeală un `ValueError` venit din alt rând. Regula: în `try` pui **doar** rândurile care pot da eroarea așteptată.
- **`finally`** e pentru „curățenie” care trebuie făcută oricum: închiderea unui fișier, a unei conexiuni, un mesaj de final. La fișiere (lecția 27) vei folosi mai des `with`, care face asta automat (lecția 39).

### EAFP: „mai ușor să ceri iertare decât permisiune”

În Python sunt două stiluri pentru situațiile care pot eșua:
- **verifici înainte** („look before you leap”): `if cheie in dictionar: ...`;
- **încerci și prinzi eroarea** („easier to ask forgiveness than permission”, prescurtat EAFP): `try: dictionar[cheie] except KeyError: ...`.

Ambele sunt corecte. EAFP e preferat când verificarea ar fi complicată sau ar repeta munca operației. De exemplu, „textul e un număr zecimal valid?” e greu de verificat cu `if`, dar trivial cu `try: float(text)`.

### Ce se întâmplă „pe dedesubt”: excepția urcă până la primul try potrivit

La lecția 23 ai văzut că o eroare urcă prin stiva de apeluri. Un `try` poate s-o prindă **la orice nivel**, nu doar în funcția unde a apărut:

```python
def medie(note):
    return sum(note) / len(note)


def raport(catalog):
    for elev, note in catalog.items():
        try:
            print(f"{elev}: {medie(note):.2f}")
        except ZeroDivisionError:
            print(f"{elev}: fără note")


raport({"Ana": [9, 10], "Radu": [], "Mihai": [7]})
```

```text
Ana: 9.50
Radu: fără note
Mihai: 7.00
```

Eroarea a apărut în `medie`, care nu are `try`. A urcat la `raport`, unde a fost prinsă, iar bucla a continuat cu Mihai. Alegerea nivelului e o decizie de design: `medie()` nu știe ce înseamnă „fără note” pentru afișare, `raport()` știe.

## Exemplu complet

Un calculator care nu se oprește la nicio intrare greșită. Operațiile vin ca text, de exemplu `12 / 4`.

<!-- fisier: calculator.py -->
<!-- stdin: 12 / 4\n7 x 3\n5 / 0\nabc + 2\n2 ** 10\n10 -\nstop -->
```python
def calculeaza(a: float, operator: str, b: float) -> float:
    if operator == "+":
        return a + b
    if operator == "-":
        return a - b
    if operator == "*":
        return a * b
    if operator == "/":
        return a / b
    if operator == "**":
        return a ** b
    raise ValueError(f"operator necunoscut: {operator}")


print("Calculator. Scrie „a operator b” (ex. 12 / 4); „stop” = ieșire.")
while True:
    linie = input("> ").strip()
    if linie == "stop":
        break
    try:
        text_a, operator, text_b = linie.split()
        a = float(text_a.replace(",", "."))
        b = float(text_b.replace(",", "."))
        rezultat = calculeaza(a, operator, b)
    except ZeroDivisionError:
        print("  Nu se poate împărți la zero.")
    except ValueError as eroare:
        print(f"  Intrare greșită ({eroare}).")
    else:
        print(f"  = {rezultat:g}")
```

```text
Calculator. Scrie „a operator b” (ex. 12 / 4); „stop” = ieșire.
> 12 / 4
  = 3
> 7 x 3
  Intrare greșită (operator necunoscut: x).
> 5 / 0
  Nu se poate împărți la zero.
> abc + 2
  Intrare greșită (could not convert string to float: 'abc').
> 2 ** 10
  = 1024
> 10 -
  Intrare greșită (not enough values to unpack (expected 3, got 2)).
> stop
```

Câteva lucruri de observat:
- un singur `except ValueError` prinde trei probleme diferite: despachetarea greșită (lecția 13), conversia eșuată și operatorul necunoscut;
- `raise ValueError(...)` din `calculeaza()` **creează** o eroare în mod intenționat. Cum și când faci asta, la lecția 25;
- calculul e în `try`, dar afișarea e în `else`, deci o eventuală greșeală la afișare nu ar fi ascunsă.

## Greșeli frecvente

### 1. except gol, care ascunde greșelile tale

```python
preturi = {"pâine": 4.5, "lapte": 8.99}
try:
    total = pretrui["pâine"] * 2
except:
    total = 0
print(total)
```

```text
0
```

Programul pare să meargă, dar `pretrui` e scris greșit. `NameError`-ul a fost prins de `except`-ul gol, care prinde **orice**, și transformat în „total 0”. Greșeala va ieși la iveală mult mai târziu, greu de găsit. Un `except` gol prinde chiar și Ctrl+C (`KeyboardInterrupt`), deci, dacă o buclă rulează în acel `try`, programul s-ar putea să nu mai poată fi oprit normal. Scrie mereu tipul erorii așteptate:

<!-- fisier: total.py -->
```python
preturi = {"pâine": 4.5, "lapte": 8.99}
try:
    total = pretrui["pâine"] * 2
except KeyError:
    total = 0
print(total)
```

```text
Traceback (most recent call last):
  File "total.py", line 3, in <module>
    total = pretrui["pâine"] * 2
            ^^^^^^^
NameError: name 'pretrui' is not defined. Did you mean: 'preturi'?
```

Acum greșeala de tastare iese la iveală imediat, cu tot cu sugestie. Nici `except Exception:` nu e mult mai bun: prinde aproape tot. Folosește-l doar la cel mai înalt nivel al unui program (de exemplu, ca să scrii eroarea într-un jurnal), niciodată ca să „faci să meargă”.

### 2. Prinderea altui tip de eroare decât cel care apare

<!-- fisier: total.py -->
```python
try:
    rezultat = 10 / 0
except ValueError:
    print("Valoare greșită.")
```

```text
Traceback (most recent call last):
  File "total.py", line 2, in <module>
    rezultat = 10 / 0
               ~~~^~~
ZeroDivisionError: division by zero
```

`except ValueError` nu prinde un `ZeroDivisionError`, așa că eroarea trece mai departe. Ca să știi ce tip să prinzi, provoacă eroarea o dată și citește ultimul rând din traceback (lecția 23).

### 3. Mai multe tipuri fără paranteze

<!-- fisier: total.py -->
```python
try:
    pret = float("12,5")
except ValueError, TypeError:
    pret = 0.0
```

```text
  File "total.py", line 3
    except ValueError, TypeError:
           ^^^^^^^^^^^^^^^^^^^^^
SyntaxError: multiple exception types must be parenthesized
```

Mesajul spune exact soluția: `except (ValueError, TypeError):`.

### 4. Folosirea unei variabile care nu a primit valoare în try

<!-- fisier: total.py -->
<!-- stdin: abc -->
```python
try:
    varsta = int(input("Vârsta: "))
except ValueError:
    print("Nu e un număr.")
print(f"Ai {varsta} de ani.")
```

```text
Vârsta: abc
Nu e un număr.
Traceback (most recent call last):
  File "total.py", line 5, in <module>
    print(f"Ai {varsta} de ani.")
                ^^^^^^
NameError: name 'varsta' is not defined. Did you mean: 'vars'?
```

(Sugestia `vars` e o potrivire întâmplătoare cu o funcție a lui Python; aici nu ajută.) Când `int()` a eșuat, atribuirea nu a mai avut loc, deci `varsta` nu există. După un `except`, gândește-te ce valoare are fiecare variabilă: fie îi dai o valoare implicită în `except`, fie repeți întrebarea (ca în bucla din lecție), fie folosești variabila doar în `else`.

### 5. Un try prea mare

<!-- nu-rula -->
```python
try:
    text = input("Cantitate: ")
    cantitate = int(text)
    pret = preturi[produs]
    total = cantitate * pret
    print(f"Total: {total:.2f}")
    istoric.append(total)
except ValueError:
    print("Cantitatea trebuie să fie un număr întreg.")
```

Mesajul presupune că `ValueError` vine din `int(text)`, dar orice rând din bloc l-ar putea produce, iar mesajul ar fi greșit. Pune în `try` doar rândul (sau rândurile) care pot da eroarea pe care o tratezi, iar restul în `else` sau după bloc:

<!-- nu-rula -->
```python
try:
    cantitate = int(input("Cantitate: "))
except ValueError:
    print("Cantitatea trebuie să fie un număr întreg.")
else:
    total = cantitate * preturi[produs]
    print(f"Total: {total:.2f}")
    istoric.append(total)
```

## Exercițiu

În `capitole/24-try-except/try_except.py`, scrie un **convertor de unități** robust:

1. o funcție `citeste_numar(mesaj)` care întreabă până primește un număr (acceptă minus și virgulă zecimală), ca în lecție;
2. o funcție `citeste_optiune(mesaj, optiuni)` care întreabă până primește una dintre opțiunile din lista `optiuni`;
3. un meniu cu `while True`: `1` = °C → °F, `2` = km → mile (1 km = 0.621371 mile), `3` = kg → livre (1 kg = 2.20462 livre), `0` = ieșire;
4. după fiecare rezultat, întreabă „Vrei și conversia inversă? (da/nu)” (cu `citeste_optiune`); la „da”, cere o valoare și convertește invers (de exemplu °F → °C);
5. un dicționar care numără câte conversii s-au făcut din fiecare tip, afișat la ieșire.

Nu folosi `isdigit()` nicăieri: toată validarea se face cu `try / except`. Testează cu răspunsuri goale, litere, numere negative și cu virgulă.

## Pe scurt

- `try:` rulează codul; la eroare, Python sare la `except TipEroare:` potrivit, iar programul continuă.
- `else` rulează doar dacă nu a fost nicio eroare; `finally` rulează întotdeauna.
- Prinde doar tipurile de erori pe care le aștepți și știi să le tratezi; niciodată `except:` gol.
- `except (A, B):` prinde mai multe tipuri; `except A as eroare:` îți dă mesajul erorii.
- `while True` + `try` + `break` (sau `return` într-o funcție) e tiparul standard de validare.
- O excepție poate fi prinsă la orice nivel din stiva de apeluri; ține blocul `try` cât mai mic.
