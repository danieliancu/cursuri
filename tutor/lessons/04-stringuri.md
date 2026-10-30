## Ce este

Un **șir de caractere** (în engleză „string”, în Python tipul `str`) este o bucată de text: o succesiune de caractere (litere, cifre, spații, semne) scrisă între ghilimele.

```python
nume = "Ana Popescu"
oras = 'Cluj'
print(nume, "din", oras)
print(type(nume))
```

```text
Ana Popescu din Cluj
<class 'str'>
```

Ai folosit deja stringuri în primele lecții. Acum vezi ce poți face cu ele: le iei pe bucăți, le transformi, le cauți și le combini.

## De ce contează

Foarte multe date din programele reale sunt text: nume, adrese, e-mailuri, mesaje, conținutul unui fișier, o pagină HTML, tot ce tastează utilizatorul. Înainte să le folosești, de cele mai multe ori trebuie să le cureți (spații în plus, litere mari amestecate) și să le spargi în bucăți. Metodele din lecția asta sunt cele pe care le vei folosi zilnic.

## Cum funcționează

### Ghilimele

Un string se scrie între ghilimele duble sau simple. Alege-le pe cele care nu apar în text:

```python
replica = 'Ea a spus "Bună!" și a plecat.'
nume_irlandez = "O'Brien"
print(replica)
print(nume_irlandez)
```

```text
Ea a spus "Bună!" și a plecat.
O'Brien
```

Un string poate fi și gol: `""`. Este tot un `str`, doar că nu are niciun caracter.

### Lipire și repetare: + și *

```python
prenume = "Ana"
nume_familie = "Popescu"
nume_complet = prenume + " " + nume_familie
print(nume_complet)
print("-" * 20)
```

```text
Ana Popescu
--------------------
```

`+` lipește două stringuri (operația se numește „concatenare”), iar `*` repetă un string de un număr de ori. Spre deosebire de `print()` cu virgule, `+` nu pune spațiu între bucăți: trebuie să-l adaugi tu.

`+` funcționează doar între stringuri. Pentru a combina text cu numere, folosește deocamdată `print()` cu virgule. La lecția 5 vei învăța f-strings, metoda cea mai comodă.

### Lungimea: len()

```python
oras = "Iași"
print(len(oras))
print(len("Ana Popescu"))
print(len(""))
```

```text
4
11
0
```

`len()` (de la „length”) numără caracterele, inclusiv spațiile. `ș` este un singur caracter, la fel ca orice altă literă.

### Indexarea: un caracter după poziție

Fiecare caracter are o poziție numită **index**. Numărătoarea începe de la **0**:

```text
 A   n   a       P   o   p   e   s   c   u
 0   1   2   3   4   5   6   7   8   9  10
-11 -10 -9  -8  -7  -6  -5  -4  -3  -2  -1
```

```python
nume = "Ana Popescu"
print(nume[0])
print(nume[4])
print(nume[-1])
print(nume[-3])
```

```text
A
P
u
s
```

Indicii negativi numără de la final: `-1` e ultimul caracter, `-2` penultimul și așa mai departe. Sunt comozi pentru că nu trebuie să știi lungimea textului.

### Slicing: o bucată din text

**Slicing** (în română „feliere”) extrage o bucată: `text[start:stop]` ia caracterele de la `start` până **înainte** de `stop`.

```python
nume = "Ana Popescu"
print(nume[0:3])
print(nume[4:11])
print(nume[:3])
print(nume[4:])
print(nume[-7:])
```

```text
Ana
Popescu
Ana
Popescu
Popescu
```

- `nume[0:3]` înseamnă pozițiile 0, 1 și 2 (fără 3). Lungimea bucății e `stop - start`;
- dacă lipsește `start`, se pornește de la început; dacă lipsește `stop`, se merge până la final.

Există și un al treilea număr, pasul: `text[start:stop:pas]`. Pasul spune din câte în câte caractere mergi: `[::2]` ia un caracter da, unul nu, iar un pas negativ merge de la coadă spre început. Cel mai cunoscut caz e `text[::-1]`, care inversează textul:

```python
print("Cluj"[::-1])
print("0123456789"[::2])
```

```text
julC
02468
```

Spre deosebire de indexare, slicing-ul nu dă eroare dacă depășești lungimea, ci se oprește la final: `"Ana"[0:100]` dă `"Ana"`.

### Metode

O **metodă** este o funcție care aparține unui obiect. Se apelează cu un punct: `text.upper()`. Iată cele mai folosite metode ale stringurilor.

**Litere mari și mici:**

```python
oras = "cluj-Napoca"
print(oras.upper())
print(oras.lower())
print(oras.title())
```

```text
CLUJ-NAPOCA
cluj-napoca
Cluj-Napoca
```

**Spații de la margini.** `strip()` scoate spațiile, tab-urile și caracterele de rând nou de la început și de la final, dar nu pe cele din interior. Variantele `lstrip()` și `rstrip()` curăță doar în stânga, respectiv doar în dreapta.

```python
nume_tastat = "   Ana Popescu  "
print("[" + nume_tastat + "]")
print("[" + nume_tastat.strip() + "]")
```

```text
[   Ana Popescu  ]
[Ana Popescu]
```

**Înlocuire:**

```python
pret = "12,50"
print(pret.replace(",", "."))
mesaj = "Ana merge la Cluj. Ana locuiește în Cluj."
print(mesaj.replace("Cluj", "Brașov"))
```

```text
12.50
Ana merge la Brașov. Ana locuiește în Brașov.
```

`replace(vechi, nou)` înlocuiește **toate** aparițiile.

**Spargere și lipire: split() și join()**

```python
nume = "Ana Maria Popescu"
bucati = nume.split()
print(bucati)

data = "29.10.2026"
print(data.split("."))
```

```text
['Ana', 'Maria', 'Popescu']
['29', '10', '2026']
```

`split()` sparge textul într-o **listă** de bucăți. Fără argument, sparge după spații. Cu argument, sparge după textul primit. Parantezele drepte `[...]` arată că rezultatul e o listă, un tip pe care îl vei învăța la lecția 12. Deocamdată reține că bucățile se numără tot de la 0: `data.split(".")[2]` este `"2026"`.

`join()` face invers: lipește bucățile, punând între ele textul pe care apelezi metoda:

```python
bucati = "29.10.2026".split(".")
print("/".join(bucati))
print(" - ".join(["Cluj", "Iași", "Brașov"]))
```

```text
29/10/2026
Cluj - Iași - Brașov
```

**Căutare și numărare:**

```python
propozitie = "Ana are mere și Ana are pere."
print(propozitie.count("Ana"))
print(propozitie.find("mere"))
print(propozitie.find("prune"))
print(propozitie.startswith("Ana"))
print(propozitie.endswith("."))
```

```text
2
8
-1
True
True
```

`find()` întoarce (adică dă ca rezultat) indexul primei apariții sau `-1` dacă textul nu apare. `startswith()` și `endswith()` răspund cu `True` (adevărat) sau `False` (fals), valori pe care le vei studia la lecția 7.

### Ce se întâmplă „pe dedesubt”: stringurile sunt imutabile

Un string **nu se poate modifica** după ce a fost creat. Tipurile de felul ăsta se numesc **imutabile** (în engleză „immutable”). Metodele nu schimbă textul original: creează **un string nou** și îl întorc.

```python
oras = "cluj"
oras.upper()
print(oras)

oras = oras.upper()
print(oras)
```

```text
cluj
CLUJ
```

Pe primul rând cu `upper()`, Python a creat `"CLUJ"`, dar nu l-a legat de niciun nume, așa că s-a pierdut. Ca să păstrezi rezultatul, îl atribui unei variabile, aceeași sau alta.

Din același motiv, metodele se pot înlănțui: fiecare primește stringul nou de la cea dinaintea ei.

```python
nume_tastat = "   aNA popESCU "
print(nume_tastat.strip().lower().title())
```

```text
Ana Popescu
```

## Exemplu complet

Un formular trimite datele Anei așa cum le-a tastat ea, cu spații și litere amestecate. Programul le curăță și construiește un nume de utilizator.

<!-- fisier: formular.py -->
```python
# Datele brute, cum vin din formular
nume_brut = "  ana   POPESCU "
email_brut = " Ana.Popescu@Exemplu.RO  "
telefon_brut = "0722 123 456"

# Curățare
nume = " ".join(nume_brut.split()).title()
email = email_brut.strip().lower()
telefon = telefon_brut.replace(" ", "")

# Nume de utilizator: prima literă din prenume + numele de familie
prenume, nume_familie = nume.split()
utilizator = (prenume[0] + nume_familie).lower()

# Domeniul e partea de după @
domeniu = email[email.find("@") + 1:]

print("Nume:      ", nume)
print("E-mail:    ", email)
print("Domeniu:   ", domeniu)
print("Telefon:   ", telefon[:4] + "***" + telefon[-3:])
print("Utilizator:", utilizator)
```

```text
Nume:       Ana Popescu
E-mail:     ana.popescu@exemplu.ro
Domeniu:    exemplu.ro
Telefon:    0722***456
Utilizator: apopescu
```

Trei trucuri din exemplu:
- `" ".join(nume_brut.split())` sparge textul după oricâte spații, apoi îl lipește la loc cu câte **un singur** spațiu, deci dispar și spațiile duble din interior;
- `email[email.find("@") + 1:]` e un slicing al cărui `start` e calculat: poziția lui `@` plus 1, adică primul caracter de după `@`, până la final;
- `prenume, nume_familie = nume.split()` dă nume celor două bucăți dintr-o dată. Funcționează doar dacă sunt exact două. Se numește **despachetare** și o vei studia la lecția 13.

## Greșeli frecvente

### 1. Așteptarea ca o metodă să modifice stringul

```python
email = "  Ana@Exemplu.ro "
email.strip()
email.lower()
print("[" + email + "]")
```

```text
[  Ana@Exemplu.ro ]
```

Stringurile sunt imutabile: metodele întorc un string nou, iar aici rezultatul s-a pierdut. Corect:

```python
email = "  Ana@Exemplu.ro "
email = email.strip().lower()
print("[" + email + "]")
```

```text
[ana@exemplu.ro]
```

### 2. Încercarea de a schimba un caracter

<!-- fisier: nume.py -->
```python
nume = "ana"
nume[0] = "A"
```

```text
Traceback (most recent call last):
  File "nume.py", line 2, in <module>
    nume[0] = "A"
    ~~~~^^^
TypeError: 'str' object does not support item assignment
```

Nu poți schimba un caracter dintr-un string existent, dar poți construi unul nou:

```python
nume = "ana"
nume = "A" + nume[1:]
print(nume)
```

```text
Ana
```

(Pentru exact acest caz există și `nume.capitalize()`.)

### 3. Index prea mare

<!-- fisier: nume.py -->
```python
oras = "Iași"
print(oras[4])
```

```text
Traceback (most recent call last):
  File "nume.py", line 2, in <module>
    print(oras[4])
          ~~~~^^^
IndexError: string index out of range
```

`"Iași"` are 4 caractere, deci indicii sunt 0, 1, 2 și 3. Ultimul index e mereu `len(text) - 1`. Pentru ultimul caracter, cel mai simplu e `oras[-1]`.

### 4. Lipirea unui string cu un număr

<!-- fisier: nume.py -->
```python
varsta = 25
print("Ana are " + varsta + " de ani.")
```

```text
Traceback (most recent call last):
  File "nume.py", line 2, in <module>
    print("Ana are " + varsta + " de ani.")
          ~~~~~~~~~~~^~~~~~~~
TypeError: can only concatenate str (not "int") to str
```

`+` între un `str` și un `int` nu are sens pentru Python: ar trebui să adune sau să lipească? Deocamdată folosește virgule în `print()`. La lecția 5 vei folosi f-strings, iar la lecția 6 conversia cu `str()`.

```python
varsta = 25
print("Ana are", varsta, "de ani.")
```

### 5. Confuzia dintre stop și ultimul caracter la slicing

```python
data = "29.10.2026"
print(data[0:1])
print(data[0:2])
```

```text
2
29
```

`stop` nu e inclus. Ca să iei primele două caractere, scrii `[0:2]` (sau `[:2]`), nu `[0:1]`. Regula care te ajută: lungimea bucății e `stop - start`.

## Exercițiu

În `capitole/04-stringuri/stringuri.py`, pornește de la variabila:

```python
adresa_bruta = "  str. memorandumului   nr. 28 ,  CLUJ-napoca  "
```

și scrie un program care:

1. curăță adresa: fără spații la margini și fără spații duble în interior;
2. o împarte în stradă și oraș, după virgulă, și curăță fiecare bucată;
3. afișează strada cu fiecare cuvânt începând cu literă mare, iar orașul doar cu litere mari;
4. afișează câte caractere are adresa curățată și pe ce poziție apare `"nr."`;
5. afișează inițialele orașului (de exemplu `C.N.` pentru `CLUJ-NAPOCA`), folosind indexarea pe bucățile obținute cu `split("-")`.

## Pe scurt

- Un string (`str`) e text între ghilimele; `+` lipește stringuri, `*` le repetă, iar `len()` numără caracterele.
- Indexarea începe de la 0: `text[0]` e primul caracter, `text[-1]` ultimul.
- `text[start:stop]` ia caracterele de la `start` până înainte de `stop`; `text[::-1]` inversează textul.
- Metode uzuale: `upper`, `lower`, `title`, `strip`, `replace`, `split`, `join`, `find`, `count`, `startswith`.
- Stringurile sunt imutabile: metodele întorc un string nou, pe care trebuie să-l salvezi într-o variabilă.
- `str + int` dă `TypeError`; un index prea mare dă `IndexError`.
