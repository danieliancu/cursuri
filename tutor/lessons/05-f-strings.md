## Ce este

Un **f-string** („formatted string literal”) este un string care începe cu litera `f` în fața ghilimelelor. În el poți pune variabile și calcule între acolade `{ }`, iar Python le înlocuiește cu valorile lor.

```python
nume = "Ana"
varsta = 25
print(f"{nume} are {varsta} de ani.")
```

```text
Ana are 25 de ani.
```

Tot în lecția asta vei vedea cum controlezi felul în care arată numerele (zecimale, aliniere) și cum scrii caractere speciale, cum ar fi un rând nou.

## De ce contează

În lecțiile trecute ai combinat text cu valori prin `print()` cu virgule sau prin `+`. Ambele au limite. Virgulele pun mereu un spațiu, iar `+` nu merge cu numere și se citește greu. f-strings rezolvă ambele probleme: vezi propoziția exact cum va arăta, cu valorile la locul lor. Sunt metoda recomandată în Python modern și o vei vedea peste tot, inclusiv în codul Django.

## Cum funcționează

### Valori și expresii între acolade

Între acolade poți pune orice **expresie**, adică orice bucată de cod care produce o valoare: o variabilă, un calcul, un apel de metodă.

```python
nume = "ana popescu"
varsta = 25
print(f"Nume: {nume.title()}")
print(f"Peste 5 ani: {varsta + 5} de ani")
print(f"Luni trăite: {varsta * 12}")
print(f"Inițiala: {nume[0].upper()}")
```

```text
Nume: Ana Popescu
Peste 5 ani: 30 de ani
Luni trăite: 300
Inițiala: A
```

Un f-string e tot un `str`, deci îl poți păstra într-o variabilă:

```python
prenume = "Ana"
nume_familie = "Popescu"
nume_complet = f"{prenume} {nume_familie}"
print(nume_complet, len(nume_complet))
```

```text
Ana Popescu 11
```

### Formatarea numerelor

După expresie poți pune `:` și o **specificație de format**, care spune cum să arate valoarea. Cea mai folosită fixează numărul de zecimale:

```python
pret = 12.5
total = 0.1 + 0.2
print(f"{pret:.2f} lei")
print(f"{total:.2f}")
print(f"{3.14159:.3f}")
print(f"{7:.1f}")
```

```text
12.50 lei
0.30
3.142
7.0
```

`.2f` înseamnă „număr cu virgulă (`f` de la float), cu 2 zecimale”. Valoarea se rotunjește doar **la afișare**: variabila rămâne neschimbată. Aceasta e soluția pentru problema `0.30000000000000004` din lecția 3.

Alte formate utile:

```python
populatie = 1250000
procent = 0.157
print(f"{populatie:,}")
print(f"{populatie:_}")
print(f"{procent:.1%}")
print(f"{5:03}")
```

```text
1,250,000
1_250_000
15.7%
005
```

- `,` și `_` separă miile. Python folosește stilul englezesc, cu virgulă; pentru stilul românesc (`1.250.000`) poți face `f"{populatie:,}".replace(",", ".")`;
- `%` înmulțește cu 100 și adaugă semnul procent;
- `03` completează cu zerouri în față, până la 3 cifre (util la numere de ordine: `001`, `002`).

### Alinierea în coloane

Un număr după `:` stabilește **lățimea** minimă, adică pe câte caractere se întinde valoarea (spațiile lipsă se completează automat). Semnele `<`, `>` și `^` aliniază valoarea la stânga, la dreapta sau la centru în acel spațiu:

```python
print(f"[{'Ana':<10}]")
print(f"[{'Ana':>10}]")
print(f"[{'Ana':^10}]")
print(f"[{12.5:>8.2f}]")
```

```text
[Ana       ]
[       Ana]
[   Ana    ]
[   12.50]
```

Textul se aliniază implicit la stânga, iar numerele la dreapta. Ultimul exemplu combină lățimea `8` cu `.2f`. Așa obții coloane de prețuri aliniate, ca pe un bon:

```python
print(f"{'Produs':<12}{'Preț':>8}")
print(f"{'Pâine':<12}{4.5:>8.2f}")
print(f"{'Lapte':<12}{8.99:>8.2f}")
print(f"{'Cafea':<12}{32:>8.2f}")
```

```text
Produs          Preț
Pâine           4.50
Lapte           8.99
Cafea          32.00
```

Observă ghilimelele: în interiorul acoladelor am folosit `'...'`, ca să se vadă clar unde se termină f-string-ul, scris cu `"..."`. (În versiunile de Python mai vechi de 3.12 era chiar obligatoriu.)

### Afișare pentru depanare: {x=}

Dacă pui `=` după expresie, Python afișează și expresia, nu doar valoarea. E foarte comod când verifici ce conține o variabilă:

```python
varsta = 25
oras = "Cluj"
print(f"{varsta=}, {oras=}")
print(f"{varsta * 12=}")
```

```text
varsta=25, oras='Cluj'
varsta * 12=300
```

### Acolade în text

Ca să scrii o acoladă propriu-zisă într-un f-string, o dublezi:

```python
nume = "Ana"
print(f"{{nume}} se înlocuiește cu {nume}")
```

```text
{nume} se înlocuiește cu Ana
```

### Caractere speciale: \n, \t, \\

În orice string (nu doar în f-strings), backslash-ul `\` începe o **secvență de evadare**: un mod de a scrie caractere care nu se pot tasta direct într-un string (un rând nou, un tab) sau care altfel ar avea alt rol (backslash-ul însuși, ghilimelele):

| Secvență | Înseamnă |
|---|---|
| `\n` | rând nou („newline”) |
| `\t` | tab |
| `\\` | un backslash |
| `\"` și `\'` | ghilimele în interiorul unor ghilimele de același fel |

```python
print("Ana\nMihai")
print("Nume:\tAna")
print("C:\\Users\\ana")
print("Ea a spus \"bună\".")
```

```text
Ana
Mihai
Nume:	Ana
C:\Users\ana
Ea a spus "bună".
```

`len("Ana\nMihai")` este 9: `\n` e scris cu două caractere în cod, dar e **un singur** caracter în text.

### Text pe mai multe rânduri

Cu trei ghilimele, `"""` sau `'''`, un string poate continua pe mai multe rânduri, iar rândurile noi se păstrează. Poate fi și f-string:

```python
nume = "Ana Popescu"
oras = "Cluj"
mesaj = f"""Bună ziua, {nume}!

Comanda dumneavoastră a fost trimisă în {oras}.
Mulțumim!"""
print(mesaj)
```

```text
Bună ziua, Ana Popescu!

Comanda dumneavoastră a fost trimisă în Cluj.
Mulțumim!
```

### sep și end la print()

Acum că știi de `\n`, poți înțelege două opțiuni ale lui `print()`: `sep` (ce se pune între valori, implicit un spațiu) și `end` (ce se pune la final, implicit `"\n"`).

```python
print("29", "10", "2026", sep=".")
print("Se încarcă", end="")
print("...", end=" ")
print("gata")
```

```text
29.10.2026
Se încarcă... gata
```

## Exemplu complet

Bonul fiscal al Anei, cu coloane aliniate și totaluri cu două zecimale:

<!-- fisier: bon.py -->
```python
client = "Ana Popescu"
numar_bon = 42

pret_paine, cant_paine = 4.5, 2
pret_lapte, cant_lapte = 8.99, 3
pret_cafea, cant_cafea = 32.0, 1

total_paine = pret_paine * cant_paine
total_lapte = pret_lapte * cant_lapte
total_cafea = pret_cafea * cant_cafea
total = total_paine + total_lapte + total_cafea
tva = total * 0.11 / 1.11  # TVA de 11% (cota redusă, la alimente), inclus în preț

latime = 32
print("=" * latime)
print(f"{'BON FISCAL':^{latime}}")
print(f"{'nr. ' + f'{numar_bon:04}':^{latime}}")
print("=" * latime)
print(f"{'Produs':<12}{'Cant.':>6}{'Total':>14}")
print("-" * latime)
print(f"{'Pâine':<12}{cant_paine:>6}{total_paine:>14.2f}")
print(f"{'Lapte':<12}{cant_lapte:>6}{total_lapte:>14.2f}")
print(f"{'Cafea':<12}{cant_cafea:>6}{total_cafea:>14.2f}")
print("-" * latime)
print(f"{'TOTAL':<18}{total:>14.2f}")
print(f"{'din care TVA':<18}{tva:>14.2f}")
print("=" * latime)
print(f"Client: {client}\nMulțumim!")
```

```text
================================
           BON FISCAL
            nr. 0042
================================
Produs       Cant.         Total
--------------------------------
Pâine            2          9.00
Lapte            3         26.97
Cafea            1         32.00
--------------------------------
TOTAL                      67.97
din care TVA                6.74
================================
Client: Ana Popescu
Mulțumim!
```

Lucruri noi în exemplu:
- `pret_paine, cant_paine = 4.5, 2` atribuie două valori dintr-o dată (detalii la lecția 13);
- `{'BON FISCAL':^{latime}}` ia lățimea dintr-o variabilă, pusă tot între acolade. Dacă schimbi `latime`, se recentrează tot;
- rândul cu numărul bonului pune un f-string în altul: întâi `f'{numar_bon:04}'` dă `"0042"`, apoi textul `"nr. 0042"` e centrat pe lățimea `latime`;
- prețurile conțin deja TVA-ul, așa că partea de TVA se scoate din total cu `total * 0.11 / 1.11`.

## Greșeli frecvente

### 1. Uitarea literei f

```python
nume = "Ana"
print("Salut, {nume}!")
```

```text
Salut, {nume}!
```

Fără `f`, acoladele sunt text obișnuit. Nu apare nicio eroare, doar un rezultat greșit. Corect:

```python
nume = "Ana"
print(f"Salut, {nume}!")
```

```text
Salut, Ana!
```

### 2. Format numeric aplicat pe un text

<!-- fisier: pret.py -->
```python
pret = "12.5"
print(f"{pret:.2f} lei")
```

```text
Traceback (most recent call last):
  File "pret.py", line 2, in <module>
    print(f"{pret:.2f} lei")
            ^^^^^^^^^^
ValueError: Unknown format code 'f' for object of type 'str'
```

`pret` e un string (are ghilimele), iar `.2f` funcționează doar pe numere. Problema apare des cu valorile citite de la tastatură. Soluția, conversia cu `float()`, e la lecția 6.

```python
pret = 12.5
print(f"{pret:.2f} lei")
```

### 3. Acoladă neînchisă

<!-- fisier: pret.py -->
```python
nume = "Ana"
print(f"Salut, {nume!")
```

```text
  File "pret.py", line 2
    print(f"Salut, {nume!")
                         ^
SyntaxError: f-string: expecting '}'
```

„Expecting '}'” înseamnă că Python a ajuns la finalul f-string-ului și încă așteaptă acolada de închidere. Când vezi `SyntaxError: f-string: ...`, verifică întâi dacă fiecare `{` are perechea ei `}`.

```python
nume = "Ana"
print(f"Salut, {nume}!")
```

### 4. Backslash-ul din căile Windows

```python
cale = "C:\nou\tabel.txt"
print(cale)
```

```text
C:
ou	abel.txt
```

`\n` și `\t` au fost interpretate ca rând nou și tab. Ai două soluții: dublezi backslash-urile sau pui `r` în fața stringului (string „raw”, în care `\` nu are rol special):

```python
print("C:\\nou\\tabel.txt")
print(r"C:\nou\tabel.txt")
```

```text
C:\nou\tabel.txt
C:\nou\tabel.txt
```

Și mai simplu: Python acceptă `/` în căi și pe Windows. Despre căi vei afla mai multe la lecția 27.

### 5. Rotunjire „de două ori”

```python
pret = 2.675
print(f"{round(pret, 2):.3f}")
print(f"{pret:.2f}")
```

```text
2.670
2.67
```

Nu e nevoie de `round()` și `.2f` împreună: specificația de format rotunjește singură. Mai mult, ce ai pierdut rotunjind dinainte nu se mai întoarce: pe primul rând, `.3f` afișează `2.670`, deși prețul era `2.675`. Păstrează calculele cu valoarea completă și formatează doar la afișare.

## Exercițiu

În `capitole/05-f-strings/f_strings.py`, scrie un program care afișează **situația școlară** a lui Andrei, fratele mai mic al Anei, la trei materii:

1. pentru fiecare materie, variabile cu numele materiei și trei note (pot fi `int` sau `float`);
2. calculează media fiecărei materii și media generală;
3. afișează un tabel cu coloanele „Materie” (aliniată la stânga, lățime 15), cele trei note (aliniate la dreapta, lățime 5) și „Media” (aliniată la dreapta, 2 zecimale);
4. sub tabel, o linie de separare și media generală, aliniată sub coloana mediilor;
5. un titlu centrat deasupra tabelului, care conține numele elevului, cu lățimea tabelului ținută într-o variabilă (ca în exemplu).

## Pe scurt

- Un f-string (`f"..."`) înlocuiește tot ce e între `{ }` cu valoarea expresiei.
- După `:` urmează formatul: `.2f` pentru zecimale, `,` pentru separatorul de mii, `.1%` pentru procente, `03` pentru zerouri în față.
- Lățimea și alinierea (`<`, `>`, `^`) fac coloane drepte: `{pret:>8.2f}`.
- `{x=}` afișează și expresia scrisă, nu doar valoarea; e util la depanare.
- `\n` e rând nou, `\t` e tab, `\\` e un backslash; `r"..."` dezactivează secvențele, iar `"""..."""` permite text pe mai multe rânduri.
- Formatarea rotunjește doar la afișare; nu o combina cu `round()` și nu o aplica pe stringuri.
