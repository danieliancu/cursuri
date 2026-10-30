## Ce este

Tipul **`bool`** (de la matematicianul George Boole) are doar două valori: `True` (adevărat) și `False` (fals). Ele se scriu cu literă mare și fără ghilimele.

Valorile booleene apar cel mai des ca rezultat al unei **comparații**, adică al unei întrebări cu răspuns da sau nu:

```python
varsta = 25
print(varsta >= 18)
print(varsta < 18)
print(type(True))
```

```text
True
False
<class 'bool'>
```

`varsta >= 18` întreabă „este vârsta cel puțin 18?”. Răspunsul e o valoare `bool`, pe care o poți afișa sau păstra într-o variabilă, ca pe orice altă valoare.

## De ce contează

Programele iau decizii tot timpul: are utilizatorul voie să intre? E coșul gol? Parola e suficient de lungă? Produsul mai e în stoc? Fiecare astfel de întrebare e o expresie care dă `True` sau `False`. La lecția 8 (`if`), aceste valori vor decide ce cod se execută, iar la lecția 9 (`while`) cât timp se repetă. Lecția de acum îți arată cum construiești corect întrebările.

## Cum funcționează

### Operatorii de comparație

| Operator | Întrebarea | Exemplu | Rezultat |
|---|---|---|---|
| `==` | sunt egale? | `5 == 5` | `True` |
| `!=` | sunt diferite? | `5 != 3` | `True` |
| `<` | mai mic? | `3 < 5` | `True` |
| `>` | mai mare? | `3 > 5` | `False` |
| `<=` | mai mic sau egal? | `5 <= 5` | `True` |
| `>=` | mai mare sau egal? | `3 >= 5` | `False` |

Atenție la diferența dintre `=` și `==`:
- `=` este **atribuire**: „leagă numele de valoare” (lecția 2);
- `==` este **comparație**: „sunt cele două valori egale?”.

```python
oras = "Cluj"          # atribuire
este_cluj = oras == "Cluj"  # comparație, rezultatul e păstrat
print(este_cluj)
print(oras != "Iași")
```

```text
True
True
```

### Comparații înlănțuite

Ca la matematică, poți scrie un interval dintr-o dată:

```python
varsta = 25
print(18 <= varsta < 65)
print(0 < varsta < 18)
```

```text
True
False
```

`18 <= varsta < 65` înseamnă „vârsta e cel puțin 18 **și** mai mică decât 65”. Puține alte limbaje permit scrierea asta. În Python e normală și se recomandă.

### Comparația stringurilor

Stringurile se compară caracter cu caracter, de la stânga la dreapta, ca în dicționar (ordinea **lexicografică**):

```python
print("Ana" == "Ana")
print("Ana" == "ana")
print("Ana" < "Mihai")
print("Ana" < "Andrei")
print("Ana" < "Anastasia")
print("Zoe" < "ana")
```

```text
True
False
True
True
True
True
```

Ce trebuie să știi:
- literele mari și mici contează: `"Ana"` și `"ana"` sunt diferite;
- `"Ana" < "Andrei"`: primele două litere sunt la fel, iar la a treia `a` vine înaintea lui `d`, deci `"Ana"` e mai mică;
- `"Ana" < "Anastasia"`: când un text e începutul celuilalt, cel mai scurt e mai mic;
- literele mari fără diacritice (A–Z) vin înaintea celor mici, deci `"Zoe" < "ana"`.

Pe dedesubt, fiecare caracter are un număr (codul Unicode), iar Python compară numerele. Le poți vedea cu `ord()`:

```python
print(ord("A"), ord("Z"), ord("a"), ord("z"), ord("ă"))
print("ăla" > "zebră")
```

```text
65 90 97 122 259
True
```

Diacriticele au coduri mari, deci ajung după `z`. Pentru comparații care să nu țină cont de literele mari și mici, convertește ambele părți la fel: `nume.lower() == "ana"`.

### Operatorul in

`in` întreabă dacă un text apare în altul:

```python
email = "ana.popescu@exemplu.ro"
print("@" in email)
print("gmail" in email)
print("gmail" not in email)
```

```text
True
False
True
```

`in` funcționează și pentru liste, tupluri, dicționare și seturi (modulul 3), unde caută un element întreg, nu o bucată de text.

### and, or, not

Cu acești operatori combini mai multe întrebări:
- **`a and b`**: `True` doar dacă **ambele** sunt adevărate;
- **`a or b`**: `True` dacă **măcar una** e adevărată;
- **`not a`**: inversează valoarea.

```python
varsta = 25
are_permis = True
oras = "Cluj"

print(varsta >= 18 and are_permis)
print(oras == "Cluj" or oras == "Iași")
print(not are_permis)
```

```text
True
True
False
```

Ordinea în care se calculează: întâi comparațiile, apoi `not`, apoi `and` și la final `or`. Ca la operațiile aritmetice, parantezele fac codul mai clar:

```python
varsta = 16
cu_parinte = True
este_weekend = False
poate_intra = (varsta >= 18 or cu_parinte) and not este_weekend
print(poate_intra)
```

```text
True
```

Pas cu pas: `varsta >= 18` e `False`, dar `cu_parinte` e `True`, deci paranteza dă `True`; `not este_weekend` e `True`; iar `True and True` dă `True`.

### Truthiness: ce valori „contează” ca false

Orice valoare din Python poate fi folosită acolo unde se așteaptă un `bool`. Funcția `bool()` arată cum e considerată. Sunt considerate **false** (în engleză „falsy”):
- `False`;
- numărul zero: `0` și `0.0`;
- textul gol: `""`;
- colecțiile goale (listă, dicționar etc., din modulul 3);
- `None` (valoarea „nimic”, la lecția 18).

**Orice altceva** e considerat adevărat („truthy”).

```python
print(bool(0), bool(42), bool(-1))
print(bool(""), bool("Ana"), bool(" "), bool("0"))
```

```text
False True True
False True True True
```

Atenție: `" "` (un spațiu) și `"0"` nu sunt goale, deci sunt adevărate. Truthiness va fi foarte util la `if` (lecția 8): `if nume:` înseamnă „dacă numele nu e gol”.

### Ce se întâmplă „pe dedesubt”: and și or întorc una dintre valori

`and` și `or` nu întorc neapărat `True` sau `False`. Ele întorc **una dintre cele două valori** și se opresc imediat ce știu răspunsul (comportament numit „scurtcircuitare”, în engleză „short-circuit”):
- `a or b` întoarce `a` dacă `a` e adevărat, altfel întoarce `b`;
- `a and b` întoarce `a` dacă `a` e fals, altfel întoarce `b`.

Pe asta se bazează un truc des întâlnit, valoarea implicită:

<!-- stdin: \n -->
```python
nume = input("Numele (opțional): ").strip()
afisat = nume or "Anonim"
print(f"Salut, {afisat}!")
```

```text
Numele (opțional): 
Salut, Anonim!
```

Utilizatorul n-a scris nimic, `nume` e `""` (fals), deci `or` a întors a doua valoare.

## Exemplu complet

Verificarea unui formular de înscriere la un curs. Deocamdată programul doar afișează rezultatele verificărilor; la lecția 8 le vom folosi ca să decidem ce mesaj primește utilizatorul.

<!-- fisier: inscriere.py -->
<!-- stdin: Ana Popescu\nana.popescu@exemplu.ro\n25\nparola12\nda -->
```python
nume = input("Nume complet: ").strip()
email = input("E-mail: ").strip().lower()
varsta = int(input("Vârsta: "))
parola = input("Parola: ")
accept = input("Accepți regulamentul? (da/nu) ").strip().lower()

nume_valid = len(nume.split()) >= 2
email_valid = "@" in email and "." in email and " " not in email
varsta_valida = 16 <= varsta <= 99
parola_valida = len(parola) >= 8 and parola != parola.lower()
a_acceptat = accept == "da"

print()
print(f"Nume complet (cel puțin 2 cuvinte): {nume_valid}")
print(f"E-mail valid:                        {email_valid}")
print(f"Vârstă între 16 și 99:               {varsta_valida}")
print(f"Parolă de 8+ caractere cu majusculă: {parola_valida}")
print(f"Regulament acceptat:                 {a_acceptat}")

totul_ok = nume_valid and email_valid and varsta_valida and parola_valida and a_acceptat
print()
print(f"Înscriere acceptată: {totul_ok}")
```

```text
Nume complet: Ana Popescu
E-mail: ana.popescu@exemplu.ro
Vârsta: 25
Parola: parola12
Accepți regulamentul? (da/nu) da

Nume complet (cel puțin 2 cuvinte): True
E-mail valid:                        True
Vârstă între 16 și 99:               True
Parolă de 8+ caractere cu majusculă: False
Regulament acceptat:                 True

Înscriere acceptată: False
```

`len(nume.split())` numără cuvintele: `len()` funcționează și pe lista de bucăți dată de `split()` (lecția 4). Parola `parola12` nu are nicio literă mare, așa că `parola != parola.lower()` e `False`: dacă textul ar conține măcar o majusculă, varianta lui cu litere mici ar fi diferită.

## Greșeli frecvente

### 1. = în loc de ==

<!-- fisier: varsta.py -->
```python
varsta = 25
print(varsta = 18)
```

```text
Traceback (most recent call last):
  File "varsta.py", line 2, in <module>
    print(varsta = 18)
TypeError: 'varsta' is an invalid keyword argument for print()
```

Mesajul pare fără legătură, pentru că în paranteze `=` are alt sens (argumentele cu nume, ca `sep=` și `end=` din lecția 5). Pentru comparație se folosește `==`:

```python
varsta = 25
print(varsta == 18)
```

### 2. Compararea unui text cu un număr

Valoarea citită cu `input()` e text, iar textul nu e niciodată egal cu un număr:

<!-- stdin: 18 -->
```python
varsta = input("Vârsta: ")
print(varsta == 18)
```

```text
Vârsta: 18
False
```

Cu `<` sau `>` e și mai rău: fie primești o eroare, fie un rezultat greșit fără nicio eroare.

<!-- fisier: varsta.py -->
<!-- stdin: 9 -->
```python
varsta = input("Vârsta: ")
print(varsta > "10")
print(varsta > 10)
```

```text
Vârsta: 9
True
Traceback (most recent call last):
  File "varsta.py", line 3, in <module>
    print(varsta > 10)
          ^^^^^^^^^^^
TypeError: '>' not supported between instances of 'str' and 'int'
```

`"9" > "10"` e `True`, pentru că se compară caracter cu caracter, iar `"9"` vine după `"1"`. Convertește întâi: `varsta = int(input("Vârsta: "))`.

### 3. Condiție scrisă ca în vorbire

<!-- fisier: varsta.py -->
```python
varsta = 25
print(varsta >= 18 and <= 65)
```

```text
  File "varsta.py", line 2
    print(varsta >= 18 and <= 65)
                           ^^
SyntaxError: invalid syntax
```

Fiecare parte a lui `and` trebuie să fie o comparație completă. Și mai bine, folosește comparația înlănțuită:

```python
varsta = 25
print(varsta >= 18 and varsta <= 65)
print(18 <= varsta <= 65)
```

### 4. „Egal cu unul sau altul”, scris greșit

```python
oras = "Brașov"
print(oras == "Cluj" or "Iași")
```

```text
Iași
```

Python a citit expresia ca `(oras == "Cluj") or "Iași"`. Prima parte e `False`, așa că `or` a întors a doua valoare, `"Iași"`, un text care e considerat adevărat. Rezultatul ar fi fost adevărat pentru orice oraș! Corect:

```python
oras = "Brașov"
print(oras == "Cluj" or oras == "Iași")
```

```text
False
```

(La lecția 13 vei vedea varianta scurtă: `oras in ("Cluj", "Iași")`.)

### 5. Egalitatea între numere float

```python
total = 0.1 + 0.2
print(total == 0.3)
print(abs(total - 0.3) < 0.000001)
print(round(total, 2) == 0.3)
```

```text
False
True
True
```

Din cauza impreciziei `float` (lecția 3), două calcule care „ar trebui” să dea același rezultat pot diferi foarte puțin. Nu compara valori `float` cu `==`. Verifică dacă diferența e foarte mică sau rotunjește ambele valori.

## Exercițiu

În `capitole/07-bool-comparatii/bool_comparatii.py`, scrie un verificator de parolă:

1. cere utilizatorului un nume de utilizator și o parolă;
2. calculează și afișează, fiecare cu textul lui, dacă parola:
   - are cel puțin 10 caractere;
   - conține cel puțin o literă mare și cel puțin o literă mică (indiciu: compară cu `.lower()` și `.upper()`);
   - **nu** conține numele de utilizator, indiferent de literele mari sau mici;
   - nu e una dintre parolele interzise `"parola123"` sau `"qwerty1234"` (scrie condiția corect, nu ca la greșeala 4);
3. afișează la final o singură valoare, `Parolă puternică: True/False`, calculată din toate verificările;
4. cere și un text opțional, „cum să te salutăm”, și folosește `or` ca să afișezi numele de utilizator dacă textul e gol.

## Pe scurt

- `bool` are două valori, `True` și `False`; comparațiile (`==`, `!=`, `<`, `>`, `<=`, `>=`) produc valori `bool`.
- `=` atribuie, `==` compară; intervalele se scriu natural: `18 <= varsta < 65`.
- Stringurile se compară caracter cu caracter, iar literele mari A–Z vin înaintea celor mici; `in` caută un text în altul.
- `and`, `or` și `not` combină condiții; fiecare parte trebuie să fie o expresie completă.
- Sunt considerate false: `False`, `0`, `""`, colecțiile goale și `None`; restul e considerat adevărat.
- Nu compara un text cu un număr și nu compara valori `float` cu `==`.
