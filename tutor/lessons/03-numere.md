## Ce este

Python are două tipuri de numere pe care le vei folosi aproape tot timpul:
- **`int`** (de la „integer”): numere întregi, ca `25`, `-3` sau `0`;
- **`float`** (de la „floating point”, virgulă mobilă): numere cu zecimale, ca `1.68`, `-0.5` sau `3.0`.

Cu ele faci calcule folosind **operatori**, adică semne precum `+`, `-`, `*` și `/`.

```python
print(7 + 3)
print(7 / 2)
print(type(7), type(3.5))
```

```text
10
3.5
<class 'int'> <class 'float'>
```

## De ce contează

Aproape orice program calculează ceva: totalul unui coș de cumpărături, media unor note, câte zile sunt între două date calendaristice, câte pagini are o listă cu 95 de articole afișate câte 10 pe pagină. Trebuie să știi ce operator să folosești și în ce ordine se fac operațiile. Mai trebuie să știi de ce `0.1 + 0.2` nu dă exact `0.3`, ca să nu te surprindă când lucrezi cu prețuri.

## Cum funcționează

### Scrierea numerelor

```python
varsta = 25            # int
inaltime = 1.68        # float: zecimalele se scriu cu punct
temperatura = -4       # numerele negative au minus în față
populatie = 1_250_000  # _ separă cifrele, ca să le citești ușor
print(populatie)
```

```text
1250000
```

Underscore-ul `_` din `1_250_000` e doar pentru ochii tăi. Python îl ignoră.

Un `int` poate fi oricât de mare: Python nu are o limită, cum au alte limbaje.

```python
print(2 ** 100)
```

```text
1267650600228229401496703205376
```

### Operatorii aritmetici

| Operator | Ce face | Exemplu | Rezultat |
|---|---|---|---|
| `+` | adunare | `7 + 3` | `10` |
| `-` | scădere | `7 - 3` | `4` |
| `*` | înmulțire | `7 * 3` | `21` |
| `/` | împărțire | `7 / 2` | `3.5` |
| `//` | împărțire întreagă | `7 // 2` | `3` |
| `%` | restul împărțirii (modulo) | `7 % 2` | `1` |
| `**` | ridicare la putere | `7 ** 2` | `49` |

Trei dintre ei merită explicați.

**`/` dă mereu un `float`**, chiar dacă împărțirea „iese exact”:

```python
print(10 / 2)
print(type(10 / 2))
```

```text
5.0
<class 'float'>
```

**`//` și `%` merg împreună.** `//` spune de câte ori încape un număr în altul, iar `%` spune cât rămâne. Sunt foarte utile când împarți lucruri în grupuri:

```python
minute = 135
ore = minute // 60
rest_minute = minute % 60
print(minute, "de minute înseamnă", ore, "ore și", rest_minute, "minute.")
```

```text
135 de minute înseamnă 2 ore și 15 minute.
```

`%` mai are o folosire clasică: un număr e par dacă `numar % 2` este `0`.

**`**` ridică la putere**: `2 ** 3` înseamnă 2 × 2 × 2 = 8. Cu `0.5` ca putere obții rădăcina pătrată: `9 ** 0.5` dă `3.0`.

### Ordinea operațiilor

Python respectă ordinea de la matematică:
1. parantezele `( )`;
2. puterea `**`;
3. `*`, `/`, `//`, `%`;
4. `+`, `-`.

Operatorii de același nivel se calculează de la stânga la dreapta.

```python
print(2 + 3 * 4)
print((2 + 3) * 4)
print(10 - 4 - 3)
print(-2 ** 2)
print((-2) ** 2)
```

```text
14
20
3
-4
4
```

`-2 ** 2` dă `-4` pentru că puterea se face înaintea minusului: e `-(2 ** 2)`. Când nu ești sigur de ordine, **pune paranteze**. Nu costă nimic și codul devine mai clar.

### int și float împreună

Dacă într-o operație apare măcar un `float`, rezultatul e `float`:

```python
print(3 + 2)
print(3 + 2.0)
print(2 * 1.5)
```

```text
5
5.0
3.0
```

### Operatori de atribuire scurtă

Modificarea unei variabile pe baza valorii ei e atât de des întâlnită, încât are o scriere scurtă:

```python
puncte = 10
puncte += 5    # la fel ca: puncte = puncte + 5
puncte -= 2    # puncte = puncte - 2
puncte *= 3    # puncte = puncte * 3
print(puncte)
```

```text
39
```

Există și `/=`, `//=`, `%=` și `**=`, care funcționează la fel.

### Funcții utile: round(), abs(), min(), max()

```python
print(round(3.14159, 2))  # rotunjire la 2 zecimale
print(round(3.7))         # fără al doilea argument: la cel mai apropiat întreg
print(abs(-12))           # valoarea absolută (fără semn)
print(min(4, 9, 2))       # cel mai mic
print(max(4, 9, 2))       # cel mai mare
```

```text
3.14
4
12
2
9
```

### Ce se întâmplă „pe dedesubt”: de ce float nu e exact

Calculatorul ține numerele în **binar** (cu cifre de 0 și 1). Unele numere zecimale simple, cum e `0.1`, nu pot fi scrise exact în binar, la fel cum 1/3 nu poate fi scris exact în zecimal (0,3333...). Python păstrează cea mai apropiată valoare posibilă, iar diferențele mici ies uneori la suprafață:

```python
print(0.1 + 0.2)
print(1.1 * 3)
```

```text
0.30000000000000004
3.3000000000000003
```

Nu e o greșeală a lui Python: așa funcționează numerele `float` în aproape toate limbajele. Ce poți face:
- **la afișare**, rotunjești cu `round()` sau, mai bine, cu formatarea pe care o vei învăța la lecția 5;
- **pentru bani**, unde fiecare ban contează, folosești bani întregi (calculezi în bani, nu în lei: `1250` în loc de `12.50`) sau modulul `decimal` din biblioteca standard.

## Exemplu complet

Ana și trei prieteni ies la restaurant și împart nota, plus bacșișul.

<!-- fisier: nota.py -->
```python
# Împărțirea notei de la restaurant
nota = 347.50
bacsis_procent = 10
persoane = 4

bacsis = nota * bacsis_procent / 100
total = nota + bacsis
pe_persoana = total / persoane

print("Nota:", nota, "lei")
print("Bacșiș:", bacsis, "lei")
print("Total:", total, "lei")
print("De plată de fiecare:", round(pe_persoana, 2), "lei")
print()

# Dacă plătesc doar în bancnote de 10 lei: câte bancnote
# încap întregi în sumă (//), plus una pentru rest.
bancnote = pe_persoana // 10 + 1
print("Fiecare dă", bancnote, "bancnote de 10 lei.")
rest = bancnote * 10 * persoane - total
print("Rămân", round(rest, 2), "lei în plus pentru chelner.")
```

```text
Nota: 347.5 lei
Bacșiș: 34.75 lei
Total: 382.25 lei
De plată de fiecare: 95.56 lei

Fiecare dă 10.0 bancnote de 10 lei.
Rămân 17.75 lei în plus pentru chelner.
```

Observă `10.0` la numărul de bancnote: `pe_persoana` e `float`, deci și `pe_persoana // 10` e `float`. Rezultatul e corect, doar arată ciudat. Cum transformi `10.0` în `10` vei vedea la lecția 6, la `int()`.

## Greșeli frecvente

### 1. Împărțirea la zero

<!-- fisier: medie.py -->
```python
suma_notelor = 0
numar_note = 0
media = suma_notelor / numar_note
```

```text
Traceback (most recent call last):
  File "medie.py", line 3, in <module>
    media = suma_notelor / numar_note
            ~~~~~~~~~~~~~^~~~~~~~~~~~
ZeroDivisionError: division by zero
```

Același lucru se întâmplă cu `//` și `%`. Când împărțitorul vine dintr-un calcul sau de la utilizator, trebuie să verifici dacă e zero. Cum faci verificarea, la lecția 8 (`if`).

### 2. Virgula în loc de punct la zecimale

Greșeala asta nu dă eroare, ceea ce o face periculoasă:

```python
pret = 3,5
print(pret)
print(type(pret))
```

```text
(3, 5)
<class 'tuple'>
```

Pentru Python, virgula separă **două valori**: `3` și `5`. Rezultatul e un tuplu (lecția 13), nu un număr. Corect:

```python
pret = 3.5
```

### 3. Uitarea ordinii operațiilor

Media a două note, scrisă greșit:

```python
nota1 = 8
nota2 = 10
media = nota1 + nota2 / 2
print(media)
```

```text
13.0
```

Împărțirea se face înaintea adunării, deci s-a calculat `8 + 5`. Cu paranteze:

```python
nota1 = 8
nota2 = 10
media = (nota1 + nota2) / 2
print(media)
```

```text
9.0
```

### 4. Așteptarea ca round() să rotunjească mereu în sus la ,5

```python
print(round(2.5))
print(round(3.5))
print(round(2.675, 2))
```

```text
2
4
2.67
```

`round()` duce valorile aflate exact la jumătate spre numărul **par** cel mai apropiat (`2.5` → `2`, `3.5` → `4`). Regula se numește „rotunjirea bancherului” și reduce erorile când aduni multe valori rotunjite. Iar `2.675` dă `2.67` pentru că, în binar, numărul e de fapt puțin mai mic decât 2.675 (vezi „pe dedesubt”). Nu e o eroare. Dacă ai nevoie de o regulă exactă de rotunjire, de exemplu pentru facturi, folosești modulul `decimal` din biblioteca standard.

### 5. Adunarea unui număr cu un text

<!-- fisier: varsta.py -->
```python
varsta = "25"
print(varsta + 1)
```

```text
Traceback (most recent call last):
  File "varsta.py", line 2, in <module>
    print(varsta + 1)
          ~~~~~~~^~~
TypeError: can only concatenate str (not "int") to str
```

`"25"` între ghilimele e text, nu număr, chiar dacă arată ca un număr. Mesajul spune că `+` poate doar să „lipească” (în engleză „concatenate”) un text de alt text (lecția 4), nu un număr de un text. Python nu ghicește ce ai vrut. Greșeala apare des când valoarea vine de la tastatură. La lecția 6 vei vedea cum transformi textul în număr. Până atunci: numerele se scriu fără ghilimele.

```python
varsta = 25
print(varsta + 1)
```

## Exercițiu

În `capitole/03-numere/numere.py`, scrie un calculator de călătorie:

1. variabile pentru distanța în km (`450`), consumul mașinii în litri la 100 km (`6.5`), prețul unui litru de benzină (`7.45`) și numărul de persoane care împart costul (`3`); folosește exact aceste valori, ca **Rulează și verifică** să-ți poată confirma rezultatele;
2. calculează câți litri se consumă, costul total și costul pe persoană, rotunjit la 2 zecimale;
3. viteza medie e de 80 km/h: calculează durata drumului în minute, rotunjită la minute întregi cu `round()`, apoi afișeaz-o ca „X ore și Y minute”, cu `//` și `%`;
4. afișează rezultatele cu `print()`, fiecare pe un rând, cu text explicativ.

Verifică „de mână” măcar unul dintre rezultate.

## Pe scurt

- `int` sunt numerele întregi, `float` cele cu zecimale, scrise cu **punct**.
- Operatori: `+ - * /`, plus `//` (împărțire întreagă), `%` (rest) și `**` (putere); `/` dă mereu `float`.
- Ordinea e cea de la matematică: paranteze, putere, înmulțiri și împărțiri, adunări și scăderi. Când ai dubii, pune paranteze.
- `x += 1` e scrierea scurtă pentru `x = x + 1`.
- Valorile `float` nu sunt exacte (`0.1 + 0.2` dă `0.30000000000000004`): rotunjește la afișare și ai grijă la bani.
- `round()` duce valorile de la jumătate spre numărul par; împărțirea la zero dă `ZeroDivisionError`.
