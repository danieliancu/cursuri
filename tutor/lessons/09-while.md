## Ce este

O **buclă** (în engleză „loop”) repetă un bloc de cod. Bucla **`while`** („cât timp”) îl repetă **cât timp** o condiție e adevărată:

```python
numar = 1
while numar <= 5:
    print(numar)
    numar += 1
print("Gata!")
```

```text
1
2
3
4
5
Gata!
```

Seamănă cu `if`: o condiție, două puncte și un bloc indentat. Diferența e că, după ce termină blocul, `while` **se întoarce** și verifică din nou condiția. Fiecare trecere prin bloc se numește **iterație**.

## De ce contează

Multe lucruri nu se fac o singură dată: un joc care primește încercări până ghicești, un meniu afișat până alegi „Ieșire”, o întrebare repetată până primești un răspuns valid, un server care așteaptă cereri până e oprit. Fără bucle, ar trebui să copiezi același cod de câte ori crezi că e nevoie, iar de multe ori nici nu știi dinainte de câte ori.

`while` e potrivit tocmai când **nu știi** dinainte câte repetări vor fi. Când știi (de exemplu „de 10 ori” sau „pentru fiecare literă”), bucla `for` de la lecția 10 e mai simplă.

## Cum funcționează

### Pas cu pas

Pentru exemplul de mai sus, Python face așa:
1. `numar = 1`;
2. verifică `numar <= 5`, adică `1 <= 5`: adevărat, deci execută blocul: afișează `1`, iar `numar` devine 2;
3. se întoarce la condiție: `2 <= 5`, adevărat, afișează `2`, iar `numar` devine 3;
4. ... la fel pentru 3, 4 și 5;
5. după ce afișează `5`, `numar` devine 6; `6 <= 5` e fals, deci bucla se termină;
6. execuția continuă cu primul rând de după bloc: `print("Gata!")`.

O buclă `while` are aproape mereu trei părți:
- **inițializarea**, înainte de buclă: variabila din condiție primește o valoare de pornire;
- **condiția**: cât timp e adevărată, bucla continuă;
- **actualizarea**, în bloc: ceva se schimbă, ca într-o zi condiția să devină falsă.

Dacă o condiție e falsă de la început, blocul nu se execută niciodată:

```python
numar = 10
while numar <= 5:
    print("Nu se afișează niciodată.")
print("Bucla a fost sărită.")
```

```text
Bucla a fost sărită.
```

### Contoare și acumulatori

Un **contor** numără câte ceva, iar un **acumulator** adună (sau combină) valori pe parcurs. Ambii pornesc de la o valoare inițială înainte de buclă:

```python
# Suma numerelor de la 1 la 100
numar = 1
suma = 0
while numar <= 100:
    suma += numar
    numar += 1
print(f"Suma: {suma}")
```

```text
Suma: 5050
```

Iată un caz în care nu știi dinainte câte iterații vor fi: în câți ani se dublează o sumă depusă la bancă cu dobândă de 5% pe an?

```python
suma = 1000.0
ani = 0
while suma < 2000:
    suma *= 1.05  # o creștere de 5% = înmulțire cu 1,05
    ani += 1
print(f"După {ani} ani: {suma:.2f} lei")
```

```text
După 15 ani: 2078.93 lei
```

### Repetare până la un răspuns valid

Cea mai frecventă folosire a lui `while` în programele mici: întrebi din nou cât timp răspunsul nu e bun. Aceasta e soluția anunțată la lecția 6 pentru `ValueError`.

<!-- stdin: douăzeci\n\n25 -->
```python
text = input("Vârsta: ").strip()
while not text.isdigit():
    print("Te rog, scrie un număr întreg.")
    text = input("Vârsta: ").strip()
varsta = int(text)
print(f"Ai {varsta} de ani.")
```

```text
Vârsta: douăzeci
Te rog, scrie un număr întreg.
Vârsta: 
Te rog, scrie un număr întreg.
Vârsta: 25
Ai 25 de ani.
```

Observă că `input()` apare de două ori: o dată **înainte** de buclă, ca să ai ce verifica prima dată, și o dată **în** buclă, ca să primești un răspuns nou. La lecția 11 vei vedea o variantă fără această repetare, cu `while True` și `break`.

### Meniuri: repetare până la „ieșire”

<!-- stdin: 1\n3\n2\n0 -->
```python
sold = 100
optiune = ""
while optiune != "0":
    print(f"\nSold: {sold} lei. 1 = depune 10, 2 = retrage 10, 0 = ieșire")
    optiune = input("Alege: ").strip()
    if optiune == "1":
        sold += 10
    elif optiune == "2":
        sold -= 10
    elif optiune != "0":
        print("Opțiune necunoscută.")
print(f"La revedere! Sold final: {sold} lei.")
```

```text

Sold: 100 lei. 1 = depune 10, 2 = retrage 10, 0 = ieșire
Alege: 1

Sold: 110 lei. 1 = depune 10, 2 = retrage 10, 0 = ieșire
Alege: 3
Opțiune necunoscută.

Sold: 110 lei. 1 = depune 10, 2 = retrage 10, 0 = ieșire
Alege: 2

Sold: 100 lei. 1 = depune 10, 2 = retrage 10, 0 = ieșire
Alege: 0
La revedere! Sold final: 100 lei.
```

`optiune` e inițializată cu `""` doar ca bucla să înceapă: `"" != "0"` e adevărat. Rândul gol dinaintea fiecărui meniu vine de la `\n` de la începutul f-string-ului.

### Bucle infinite

Dacă condiția nu devine niciodată falsă, bucla nu se oprește. Programul rămâne „blocat”: afișează la nesfârșit sau așteaptă fără să se întâmple nimic.

<!-- nu-rula -->
```python
numar = 1
while numar <= 5:
    print(numar)
    # lipsește numar += 1, deci numar rămâne 1 pentru totdeauna
```

Ca să oprești un program blocat, apasă **Oprește** în bara terminalului sau **Ctrl+C** în terminal. În afara aplicației, Ctrl+C funcționează în orice terminal. Python se oprește cu un `KeyboardInterrupt`, care e normal în situația asta.

Când o buclă nu se termină, verifică cele trei părți: are variabila o valoare de pornire? Se schimbă în bloc? Se schimbă **în direcția bună** (de exemplu, crește când condiția e `numar <= 5`)?

Uneori o buclă infinită e voită: un server web rulează „la nesfârșit”, până îl oprești. Vei vedea `while True` la lecția 11.

### Ce se întâmplă „pe dedesubt”: condiția se verifică doar la începutul iterației

Condiția nu e urmărită „tot timpul”. Se verifică **doar** când bucla ajunge din nou la început. Dacă în mijlocul blocului condiția devine falsă, restul blocului se execută oricum:

```python
numar = 3
while numar > 0:
    numar -= 1
    print(f"numar = {numar}")
```

```text
numar = 2
numar = 1
numar = 0
```

În ultima iterație, `numar` devine 0, deci condiția e deja falsă, dar `print` se execută totuși. Bucla se oprește abia la verificarea următoare.

## Exemplu complet

A doua versiune a jocului „Ghicește numărul”: încercări nelimitate, cu indicii și cu numărarea încercărilor. Răspunsurile care nu sunt numere nu opresc jocul.

<!-- fisier: ghiceste.py -->
<!-- stdin: 50\nabc\n25\n37 -->
```python
numar_secret = 37
incercari = 0
incercare = 0  # orice valoare diferită de numar_secret, ca bucla să înceapă

print("Ghicește numărul (între 1 și 100)!")
while incercare != numar_secret:
    text = input("Încercarea ta: ").strip()
    while not text.isdigit():
        print("Scrie un număr întreg.")
        text = input("Încercarea ta: ").strip()

    incercare = int(text)
    incercari += 1

    if incercare < numar_secret:
        print("Prea mic.")
    elif incercare > numar_secret:
        print("Prea mare.")

cuvant = "încercare" if incercari == 1 else "încercări"
print(f"Bravo! Ai ghicit numărul {numar_secret} din {incercari} {cuvant}.")
```

```text
Ghicește numărul (între 1 și 100)!
Încercarea ta: 50
Prea mare.
Încercarea ta: abc
Scrie un număr întreg.
Încercarea ta: 25
Prea mic.
Încercarea ta: 37
Bravo! Ai ghicit numărul 37 din 3 încercări.
```

Ce e nou față de lecția 8:
- bucla exterioară se repetă până la răspunsul corect, iar în ea, o buclă **imbricată** repetă întrebarea până primește cifre;
- `incercari` e un contor, crescut doar pentru răspunsurile valide, deci `abc` nu se pune la socoteală;
- mesajul de felicitare e după buclă: se ajunge acolo doar când `incercare == numar_secret`.

## Greșeli frecvente

### 1. Variabila din condiție nu e inițializată

<!-- fisier: joc.py -->
```python
while incercari < 3:
    print("Încă o încercare")
    incercari += 1
```

```text
Traceback (most recent call last):
  File "joc.py", line 1, in <module>
    while incercari < 3:
          ^^^^^^^^^
NameError: name 'incercari' is not defined
```

Condiția se calculează înainte de prima iterație, deci variabila trebuie să existe deja:

```python
incercari = 0
while incercari < 3:
    print("Încă o încercare")
    incercari += 1
```

### 2. Inițializarea pusă în interiorul buclei

Vrem suma numerelor de la 1 la 3:

```python
numar = 1
while numar <= 3:
    suma = 0  # greșit: se resetează la fiecare iterație
    suma += numar
    numar += 1
print(suma)
```

```text
3
```

Nu apare nicio eroare, dar `suma` redevine 0 la fiecare trecere, așa că la final rămâne doar ultimul număr.

Contoarele și acumulatorii se inițializează **înainte** de buclă:

```python
numar = 1
suma = 0
while numar <= 3:
    suma += numar
    numar += 1
print(suma)
```

```text
6
```

### 3. Uitarea actualizării: buclă infinită

<!-- nu-rula -->
```python
parola = input("Parola: ")
while len(parola) < 8:
    print("Parola e prea scurtă.")
```

Dacă parola e scurtă, mesajul se afișează la nesfârșit, pentru că `parola` nu se mai schimbă niciodată. Lipsește un nou `input()` în buclă:

<!-- stdin: abc\nparolabuna -->
```python
parola = input("Parola: ")
while len(parola) < 8:
    print("Parola e prea scurtă.")
    parola = input("Parola: ")
print("Parolă acceptată.")
```

```text
Parola: abc
Parola e prea scurtă.
Parola: parolabuna
Parolă acceptată.
```

### 4. Compararea textului cu un număr în condiție

<!-- nu-rula -->
```python
raspuns = ""
while raspuns != 37:
    raspuns = input("Ghicește: ")
```

`input()` întoarce text, iar `"37" != 37` e mereu adevărat (lecția 7), așa că bucla nu se termină niciodată, chiar dacă scrii `37`. Compară text cu text (`raspuns != "37"`) sau convertește întâi cu `int()`, ca în exemplul complet.

### 5. Greșeala de o unitate („off-by-one”)

```python
# Vrem numerele de la 1 la 5
numar = 1
while numar < 5:
    print(numar, end=" ")
    numar += 1
```

```text
1 2 3 4 
```

Cu `<`, valoarea 5 nu mai trece. Greșelile de felul ăsta, cu o iterație în plus sau în minus, sunt atât de frecvente încât au și nume: „off-by-one”. Verifică mereu prima și ultima valoare: ce se întâmplă când `numar` e exact 5? Aici trebuia `numar <= 5`.

## Exercițiu

În `capitole/09-while/while_exercitii.py` (fișierul se numește așa, și nu `while.py`, pentru că `while` e cuvânt rezervat), scrie un program care urmărește economiile puse într-o **pușculiță**:

1. cere suma țintă (un număr întreg pozitiv); repetă întrebarea cât timp răspunsul nu e valid;
2. apoi, într-o buclă, cere sume depuse (numere întregi), una câte una, până se atinge sau se depășește ținta; după fiecare depunere afișează cât s-a strâns și cât mai lipsește;
3. un răspuns gol sau invalid la depunere afișează un mesaj și nu se numără;
4. la final, afișează câte depuneri valide au fost, suma totală și media pe depunere, cu 2 zecimale;
5. bonus: dacă utilizatorul scrie `stop` la o depunere, programul se termină înainte de țintă, cu un mesaj potrivit (fără `break`: folosește o variabilă și condiția buclei).

## Pe scurt

- `while conditie:` repetă blocul cât timp condiția e adevărată; condiția se verifică înaintea fiecărei iterații.
- O buclă `while` are inițializare (înainte), condiție și actualizare (în bloc); fără actualizare, bucla e infinită.
- Contoarele și acumulatorii se inițializează **înainte** de buclă.
- `while not text.isdigit():` repetă întrebarea până primești un răspuns valid.
- Un program blocat se oprește cu **Oprește** sau Ctrl+C.
- `while` e potrivit când nu știi câte repetări vor fi; verifică mereu prima și ultima iterație (greșelile „off-by-one”).
