## Ce este

Funcția `input()` oprește programul și așteaptă ca utilizatorul să tasteze ceva în terminal și să apese Enter. Ce a tastat devine valoarea întoarsă de `input()`.

<!-- stdin: Ana -->
```python
nume = input("Cum te cheamă? ")
print(f"Salut, {nume}!")
```

```text
Cum te cheamă? Ana
Salut, Ana!
```

Textul dintre paranteze (`"Cum te cheamă? "`) este **mesajul de invitație** (în engleză „prompt”): se afișează înainte ca programul să aștepte răspunsul.

Regula cea mai importantă a lecției: **`input()` întoarce mereu un `str`**, chiar dacă utilizatorul a tastat un număr. Ca să faci calcule cu răspunsul, îl **convertești** în alt tip cu `int()` sau `float()`.

## De ce contează

Până acum, toate datele erau scrise direct în cod. Ca să lucrezi cu vârsta lui Mihai în locul celei a Anei, trebuia să modifici programul. Cu `input()`, același program merge pentru oricine îl folosește.

Lecția mai are o idee care te va urmări tot timpul: **datele care vin din afara programului sunt text**. Asta e valabil pentru tastatură, pentru un fișier (lecția 27), pentru un formular web sau un URL în Django (lecțiile 47 și 55). Va trebui de fiecare dată să le convertești și să te gândești ce faci dacă utilizatorul a scris altceva decât te așteptai.

## Cum funcționează

### input() întoarce text

<!-- stdin: 25 -->
```python
varsta = input("Câți ani ai? ")
print(type(varsta))
print(varsta * 2)
```

```text
Câți ani ai? 25
<class 'str'>
2525
```

Utilizatorul a tastat `25`, dar `varsta` este stringul `"25"`. De aceea `* 2` l-a **repetat** (lecția 4) în loc să-l dubleze.

Când rulezi programul în terminal, cursorul se oprește după mesajul de invitație. Scrii răspunsul direct acolo și apeși Enter. Programul nu continuă până nu primește răspunsul.

### Conversia în număr: int() și float()

`int()` transformă un text într-un număr întreg, iar `float()` într-un număr cu zecimale:

<!-- stdin: 25\n1.68 -->
```python
varsta = int(input("Câți ani ai? "))
inaltime = float(input("Cât de înalt ești (în metri)? "))
print(f"Peste 10 ani vei avea {varsta + 10} de ani.")
print(f"Înălțimea ta în centimetri: {inaltime * 100:.0f}")
```

```text
Câți ani ai? 25
Cât de înalt ești (în metri)? 1.68
Peste 10 ani vei avea 35 de ani.
Înălțimea ta în centimetri: 168
```

Ce se întâmplă pe rândul `int(input(...))`, din interior spre exterior:
1. `input(...)` afișează întrebarea și întoarce textul tastat: `"25"`;
2. `int("25")` transformă textul în numărul `25`;
3. `varsta` e legată de numărul `25`.

Apelurile de funcții „unele în altele” se citesc mereu așa: cel din interior se execută primul, iar rezultatul lui devine **argument** (valoarea primită între paranteze) pentru cel din exterior.

`int()` și `float()` ignoră spațiile de la margini, deci `int(" 25 ")` dă `25`. Ele acceptă însă doar texte care arată exact ca un număr. Orice altceva produce un `ValueError`:

<!-- fisier: varsta.py -->
<!-- stdin: douăzeci și cinci -->
```python
varsta = int(input("Câți ani ai? "))
```

```text
Câți ani ai? douăzeci și cinci
Traceback (most recent call last):
  File "varsta.py", line 1, in <module>
    varsta = int(input("Câți ani ai? "))
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: invalid literal for int() with base 10: 'douăzeci și cinci'
```

Mesajul spune exact ce s-a întâmplat: textul `'douăzeci și cinci'` nu e un număr valid în baza 10 (adică un număr scris cu cifrele obișnuite, de la 0 la 9). Deocamdată programul se oprește aici. La lecția 9 vei vedea cum repeți întrebarea până primești un răspuns bun, iar la lecția 24 cum „prinzi” eroarea cu `try / except`.

### Conversii între numere

`int()` și `float()` funcționează și pe numere:

```python
print(int(3.99))
print(int(-3.99))
print(float(7))
print(round(3.99))
```

```text
3
-3
7.0
4
```

`int()` aplicat unui `float` **taie** zecimalele (spre zero), nu rotunjește. Dacă vrei rotunjire, folosește `round()` (lecția 3). Acum poți repara și `10.0` din exemplul cu bancnotele din lecția 3: `int(pe_persoana // 10) + 1` dă `10`.

### Conversia în text: str()

`str()` transformă orice valoare în text. Cu el poți lipi numere în stringuri folosind `+`:

```python
varsta = 25
mesaj = "Ana are " + str(varsta) + " de ani."
print(mesaj)
print(len(str(1250000)))
```

```text
Ana are 25 de ani.
7
```

Pentru afișare, f-strings rămân mai comode. `str()` e util atunci când chiar ai nevoie de text, de exemplu ca să numeri cifrele unui număr, ca mai sus.

### Ce se întâmplă „pe dedesubt”: conversia creează un obiect nou

`int("25")` nu „schimbă tipul” stringului `"25"`. Stringurile sunt imutabile (lecția 4). Funcția citește textul și **creează un obiect nou**, numărul `25`. Textul original rămâne neschimbat:

```python
text = "25"
numar = int(text)
print(text, type(text))
print(numar, type(numar))
```

```text
25 <class 'str'>
25 <class 'int'>
```

Când scrii `varsta = int(varsta)`, eticheta `varsta` se mută pe obiectul nou, iar stringul vechi nu mai e folosit.

## Exemplu complet

Un calculator de consum la benzinărie. Utilizatorul introduce datele, iar programul calculează costul.

<!-- fisier: benzina.py -->
<!-- stdin: Ana\n450\n6.5\n7,45 -->
```python
print("=== Calculator de drum ===")
nume = input("Numele tău: ").strip().title()
distanta = int(input("Distanța (km): "))
consum = float(input("Consum (litri la 100 km): "))
# Mulți scriu prețul cu virgulă; o înlocuim cu punct înainte de conversie.
pret_litru = float(input("Prețul unui litru (lei): ").replace(",", "."))

litri = distanta * consum / 100
cost = litri * pret_litru

print()
print(f"{nume}, pentru {distanta} km ai nevoie de {litri:.1f} litri.")
print(f"Costul drumului: {cost:.2f} lei.")
print(f"Adică {cost / distanta:.2f} lei pe kilometru.")
```

```text
=== Calculator de drum ===
Numele tău: Ana
Distanța (km): 450
Consum (litri la 100 km): 6.5
Prețul unui litru (lei): 7,45

Ana, pentru 450 km ai nevoie de 29.2 litri.
Costul drumului: 217.91 lei.
Adică 0.48 lei pe kilometru.
```

Observă:
- metodele de string se pot aplica direct pe rezultatul lui `input()`: `input(...).strip().title()`;
- `replace(",", ".")` se face **înainte** de `float()`, cât valoarea e încă text;
- distanța e convertită cu `int()`, pentru că ne așteptăm la kilometri întregi, iar consumul și prețul cu `float()`.

## Greșeli frecvente

### 1. Calcule cu rezultatul lui input(), fără conversie

<!-- fisier: varsta.py -->
<!-- stdin: 25 -->
```python
varsta = input("Câți ani ai? ")
print(f"La anul vei avea {varsta + 1} de ani.")
```

```text
Câți ani ai? 25
Traceback (most recent call last):
  File "varsta.py", line 2, in <module>
    print(f"La anul vei avea {varsta + 1} de ani.")
                              ~~~~~~~^~~
TypeError: can only concatenate str (not "int") to str
```

`varsta` e `"25"`, deci `+ 1` încearcă să lipească un număr la un text. Convertește imediat ce citești:

```python
varsta = int(input("Câți ani ai? "))
```

### 2. int() pe un număr cu zecimale

<!-- fisier: varsta.py -->
<!-- stdin: 1.68 -->
```python
inaltime = int(input("Înălțimea (m): "))
```

```text
Înălțimea (m): 1.68
Traceback (most recent call last):
  File "varsta.py", line 1, in <module>
    inaltime = int(input("Înălțimea (m): "))
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: invalid literal for int() with base 10: '1.68'
```

`int()` aplicat pe un **text** acceptă doar cifre (eventual cu semn în față), fără punct. (Aplicat pe un **număr** `float`, taie zecimalele; aici însă e text.) Pentru valori care pot avea zecimale, folosește `float()`.

### 3. Virgula zecimală românească

<!-- fisier: varsta.py -->
<!-- stdin: 7,45 -->
```python
pret = float(input("Preț: "))
```

```text
Preț: 7,45
Traceback (most recent call last):
  File "varsta.py", line 1, in <module>
    pret = float(input("Preț: "))
           ^^^^^^^^^^^^^^^^^^^^^^
ValueError: could not convert string to float: '7,45'
```

Python acceptă doar punctul ca separator zecimal. Utilizatorii români vor scrie des cu virgulă, așa că o înlocuiești înainte de conversie:

```python
pret = float(input("Preț: ").replace(",", "."))
```

### 4. Răspuns gol

Utilizatorul apasă Enter fără să scrie nimic:

<!-- fisier: varsta.py -->
<!-- stdin: \n -->
```python
varsta = int(input("Câți ani ai? "))
```

```text
Câți ani ai? 
Traceback (most recent call last):
  File "varsta.py", line 1, in <module>
    varsta = int(input("Câți ani ai? "))
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: invalid literal for int() with base 10: ''
```

`''` din mesaj e stringul gol. Un program real trebuie să trateze și cazul ăsta, cu instrumentele pe care le vei vedea la lecțiile 8, 9 și 24.

### 5. Uitarea spațiului din mesajul de invitație

<!-- stdin: Ana -->
```python
nume = input("Cum te cheamă?")
```

```text
Cum te cheamă?Ana
```

Nu e o eroare, dar răspunsul se lipește de întrebare. Pune un spațiu la finalul mesajului:

```python
nume = input("Cum te cheamă? ")
```

## Exercițiu

În `capitole/06-input-conversii/input_conversii.py`, scrie un convertor de temperatură și de timp:

1. cere numele utilizatorului și curăță-l (`strip()`, `title()`);
2. cere o temperatură în grade Celsius, care poate avea zecimale și poate fi scrisă cu virgulă, și afișeaz-o în Fahrenheit (`F = C * 9 / 5 + 32`) cu o zecimală;
3. cere un număr întreg de secunde și afișează-l ca „X ore, Y minute și Z secunde” (cu `//` și `%`, ca în lecția 3; indiciu: o oră are 3600 de secunde, iar ce rămâne după ore se împarte apoi la 60);
4. afișează câte cifre are numărul de secunde introdus, folosind `str()` și `len()`;
5. rulează programul de mai multe ori și încearcă intenționat răspunsuri greșite (text, gol, `12.5` la secunde). Notează ce eroare dă fiecare.

## Pe scurt

- `input("mesaj ")` afișează mesajul, așteaptă Enter și întoarce **mereu** un `str`.
- `int()` și `float()` transformă textul în număr; `str()` transformă orice valoare în text.
- Un text care nu arată exact ca un număr dă `ValueError`: litere, gol, virgulă zecimală sau `"1.68"` la `int()`.
- `int()` aplicat unui `float` taie zecimalele; pentru rotunjire folosește `round()`.
- Curăță textul (`strip()`, `replace(",", ".")`) **înainte** de conversie.
- Datele din afara programului (tastatură, fișiere, web) vin ca text și trebuie convertite.
