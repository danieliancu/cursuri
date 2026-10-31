## Ce este

Patru instrucțiuni îți dau control mai fin asupra buclelor:
- **`break`** oprește bucla imediat; execuția continuă după ea;
- **`continue`** sare peste restul iterației curente și trece la următoarea;
- **`else`** pus după o buclă rulează doar dacă bucla s-a terminat **fără** `break`;
- **`pass`** nu face nimic; ține locul unui bloc care trebuie să existe, dar e încă gol.

```python
for numar in range(1, 10):
    if numar == 6:
        break
    if numar % 2 == 0:
        continue
    print(numar, end=" ")
print("| gata")
```

```text
1 3 5 | gata
```

Numerele pare au fost sărite de `continue`, iar la 6 bucla s-a oprit cu `break`, deci 7, 8 și 9 nu mai sunt verificate.

## De ce contează

În lecțiile 9 și 10 ai văzut că unele bucle devin stângace:
- validarea răspunsului cerea `input()` scris de două ori, o dată înainte de buclă și o dată în ea;
- o căutare („există un cuvânt mai lung de 8 litere?”) ar fi parcurs toată secvența chiar după ce găsea ce căuta;
- o buclă care sare peste unele elemente avea tot blocul indentat într-un `if` mare.

`break` și `continue` rezolvă aceste situații și fac codul mai scurt și mai ușor de citit. Clauza `else` a buclelor e mai rar întâlnită, dar e exact unealta potrivită pentru „am căutat peste tot și n-am găsit”.

## Cum funcționează

### break: ieșirea din buclă

Când Python întâlnește `break`, iese imediat din bucla în care se află. Restul blocului nu mai rulează și nici iterațiile următoare.

Căutarea primului cuvânt lung:

```python
text = "Ana învață programare în fiecare seară"
for cuvant in text.split():
    print(f"verific: {cuvant}")
    if len(cuvant) > 8:
        print(f"Găsit: {cuvant}")
        break
```

```text
verific: Ana
verific: învață
verific: programare
Găsit: programare
```

„în”, „fiecare” și „seară” nu mai sunt verificate, pentru că nu mai e nevoie.

### while True + break

Combinația cea mai des întâlnită: o buclă „infinită”, din care ieși cu `break` când condiția e îndeplinită. Validarea de la lecția 9 devine:

<!-- stdin: douăzeci\n25 -->
```python
while True:
    text = input("Vârsta: ").strip()
    if text.isdigit():
        break
    print("Te rog, scrie un număr întreg.")
varsta = int(text)
print(f"Ai {varsta} de ani.")
```

```text
Vârsta: douăzeci
Te rog, scrie un număr întreg.
Vârsta: 25
Ai 25 de ani.
```

`input()` apare o singură dată, iar ordinea pașilor e cea naturală: întreabă, verifică, ieși sau explică problema. `while True` nu e o greșeală aici: bucla e intenționat „infinită”, iar ieșirea e garantată de `break`.

### continue: treci la iterația următoare

`continue` oprește iterația **curentă** și sare direct la următoarea. În `for`, trece la elementul următor. În `while`, se întoarce la verificarea condiției.

```python
# Suma numerelor naturale (fără semn) dintr-un text
date = "12 -5 7 abc 0 3"
suma = 0
for bucata in date.split():
    if not bucata.isdigit():
        print(f"ignor „{bucata}”")
        continue
    suma += int(bucata)
print(f"Suma: {suma}")
```

```text
ignor „-5”
ignor „abc”
Suma: 22
```

Fără `continue`, ar fi trebuit să pui `suma += ...` și tot restul codului într-un `else`. Cu `continue`, cazurile de exclus sunt tratate sus, iar codul „normal” rămâne la indentarea de bază. Tiparul se numește **gardă** (în engleză „guard clause”).

### else la bucle: „nu am ieșit cu break”

Un `else` pus după `for` sau `while`, la aceeași indentare cu bucla, rulează când bucla se termină **natural**: secvența s-a terminat (`for`) sau condiția a devenit falsă (`while`). **Nu** rulează dacă bucla s-a oprit cu `break`.

```python
email = "ana.popescu@exemplu.ro"
for caracter in email:
    if caracter == " ":
        print("E-mailul conține spații.")
        break
else:
    print("Nu am găsit spații.")
```

```text
Nu am găsit spații.
```

Gândește-te la `else` ca la „altfel decât cu `break`”. Rolul lui principal e în căutări: fie găsești (și ieși cu `break`), fie ajungi la final, iar `else` tratează cazul „nu am găsit”. Fără el, ai avea nevoie de o variabilă în plus:

```python
email = "ana.popescu@exemplu.ro"
gasit = False
for caracter in email:
    if caracter == " ":
        gasit = True
        break
if not gasit:
    print("Nu am găsit spații.")
```

```text
Nu am găsit spații.
```

Ambele variante sunt corecte. Mulți programatori preferă varianta cu variabilă, pentru că `else` la bucle e neobișnuit și poate fi citit greșit. Important e să-l recunoști când îl întâlnești.

### pass: un bloc care nu face nimic

Python cere ca după `:` să urmeze un bloc. Dacă încă nu știi ce va conține, pui `pass`:

```python
varsta = 25
if varsta < 18:
    pass  # TODO: mesaj pentru minori
else:
    print("Acces permis.")
```

```text
Acces permis.
```

`pass` e util când schițezi structura unui program și completezi mai târziu. Comentariul `TODO` (din engleză, „de făcut”) e un semn folosit de toți programatorii pentru locurile încă neterminate. Îl vei revedea la funcții (lecția 18) și la clase (lecția 32).

### Ce se întâmplă „pe dedesubt”: break și continue afectează doar bucla cea mai apropiată

În buclele imbricate, `break` și `continue` acționează doar asupra buclei **interioare** în care se află:

```python
for rand in range(1, 4):
    for coloana in range(1, 4):
        if coloana == 2:
            break
        print(f"({rand},{coloana})", end=" ")
    print("<- sfârșit de rând")
```

```text
(1,1) <- sfârșit de rând
(2,1) <- sfârșit de rând
(3,1) <- sfârșit de rând
```

`break` a oprit doar bucla `coloana`, iar bucla `rand` a continuat normal. Pentru a ieși din ambele bucle, obișnuit e să pui codul într-o funcție și să folosești `return` (lecția 18).

## Exemplu complet

Versiunea finală a jocului „Ghicește numărul”: jucătorul are 7 încercări. Cu `for` limitezi numărul de încercări, `break` oprește jocul la răspunsul corect, `else` anunță pierderea, `while True` validează fiecare răspuns, iar `continue` ignoră un număr deja încercat.

<!-- fisier: ghiceste.py -->
<!-- stdin: 50\n25\n25\n37 -->
```python
numar_secret = 37
max_incercari = 7
incercate = " "  # numerele încercate, separate prin spații

print(f"Ghicește numărul (între 1 și 100). Ai {max_incercari} încercări.")

for incercare_nr in range(1, max_incercari + 1):
    while True:
        text = input(f"[{incercare_nr}/{max_incercari}] Numărul: ").strip()
        if text.isdigit() and 1 <= int(text) <= 100:
            break
        print("Scrie un număr întreg între 1 și 100.")
    numar = int(text)

    if f" {numar} " in incercate:
        print(f"Ai mai încercat {numar}. Încercarea nu se pune.")
        continue  # trec la iterația următoare, dar numărul ei crește oricum
    incercate += f"{numar} "

    if numar == numar_secret:
        cuvant = "încercare" if incercare_nr == 1 else "încercări"
        print(f"Bravo! Ai ghicit din {incercare_nr} {cuvant}.")
        break
    print("Prea mic." if numar < numar_secret else "Prea mare.")
else:
    print(f"Ai rămas fără încercări. Numărul era {numar_secret}.")

print(f"Numere încercate:{incercate}")
```

```text
Ghicește numărul (între 1 și 100). Ai 7 încercări.
[1/7] Numărul: 50
Prea mare.
[2/7] Numărul: 25
Prea mic.
[3/7] Numărul: 25
Ai mai încercat 25. Încercarea nu se pune.
[4/7] Numărul: 37
Bravo! Ai ghicit din 4 încercări.
Numere încercate: 50 25 37 
```

Ai observat contradicția? Mesajul spune „încercarea nu se pune”, dar contorul a sărit totuși de la 3 la 4: `for` trece la elementul următor din `range` chiar și după `continue`. E un exemplu bun pentru greșeala 5 de mai jos. Cum o repari: cu un `while` și un contor pe care îl crești doar pentru încercările noi. Încearcă la exercițiu.

În condiția `text.isdigit() and 1 <= int(text) <= 100`, `and` se oprește dacă prima parte e falsă (lecția 7), deci `int(text)` nu se calculează niciodată pe un text care nu e număr.

Notă: ținem numerele încercate într-un text, cu spații pe margini, ca `" 25 "` să nu se potrivească în `" 125 "`. La lecția 12 vei folosi o listă, iar la lecția 15 un set, care sunt mult mai potrivite pentru asta.

## Greșeli frecvente

### 1. break în afara unei bucle

<!-- fisier: joc.py -->
```python
varsta = 15
if varsta < 18:
    print("Acces interzis.")
    break
```

```text
  File "joc.py", line 4
    break
    ^^^^^
SyntaxError: 'break' outside loop
```

`break` și `continue` funcționează doar în bucle. Ca să oprești un **program** întreg, există `exit()`, dar de obicei e mai bine să organizezi codul cu `if / else` (iar la lecția 18 cu funcții și `return`).

### 2. Așteptarea ca break să iasă din toate buclele

```python
for rand in range(3):
    for coloana in range(3):
        if rand == 1 and coloana == 1:
            print("Găsit (1, 1), mă opresc.")
            break
    print(f"terminat rândul {rand}")
```

```text
terminat rândul 0
Găsit (1, 1), mă opresc.
terminat rândul 1
terminat rândul 2
```

`break` a ieșit doar din bucla interioară. Bucla exterioară a continuat cu rândul 2. Dacă trebuie oprite ambele, folosește o variabilă verificată și în bucla exterioară, sau o funcție cu `return` (lecția 18).

### 3. continue înainte de actualizarea contorului într-un while

<!-- nu-rula -->
```python
numar = 0
while numar < 10:
    if numar % 2 == 0:
        continue
    print(numar)
    numar += 1
```

Programul se blochează. Pentru `numar = 0`, `continue` sare peste `numar += 1`, condiția se verifică din nou cu același 0, și tot așa la nesfârșit. Într-un `while`, actualizarea trebuie să aibă loc **înainte** de orice `continue`:

```python
numar = 0
while numar < 10:
    numar += 1
    if numar % 2 == 0:
        continue
    print(numar, end=" ")
```

```text
1 3 5 7 9 
```

(Problema nu există în `for`, unde trecerea la elementul următor e automată.)

### 4. else pus la indentarea greșită

```python
text = "Ana are mere"
for cuvant in text.split():
    if cuvant == "pere":
        print("Am găsit pere.")
        break
    else:
        print("Nu am găsit pere.")
```

```text
Nu am găsit pere.
Nu am găsit pere.
Nu am găsit pere.
```

Aici `else` aparține lui `if`, deci se execută la fiecare cuvânt care nu e „pere”. Pentru „nu am găsit nicăieri”, `else` trebuie aliniat cu `for`:

```python
text = "Ana are mere"
for cuvant in text.split():
    if cuvant == "pere":
        print("Am găsit pere.")
        break
else:
    print("Nu am găsit pere.")
```

```text
Nu am găsit pere.
```

### 5. Așteptarea ca continue să „anuleze” o iterație din for

```python
incercari_valide = 0
for incercare in range(1, 4):
    if incercare == 2:
        continue  # vrem ca a doua să „nu se pună”
    incercari_valide += 1
print(f"Iterații: 3, încercări numărate: {incercari_valide}")
```

```text
Iterații: 3, încercări numărate: 2
```

`continue` doar sare peste restul blocului. Nu dă înapoi iterația. Bucla `for` tot face exact atâtea iterații câte elemente are secvența. Dacă unele iterații nu trebuie să se pună, ține un contor separat sau folosește `while`.

## Exercițiu

În `capitole/11-break-continue/break_continue.py` scrie cele trei părți una după alta, în ordinea de mai jos (programul le rulează pe rând):

1. **Repară jocul.** Pornește de la exemplul complet (numărul secret 37, 7 încercări) și rescrie-l cu un `while` și un contor de încercări, astfel încât un număr deja încercat să **nu** consume o încercare. Păstrează mesajul de pierdere, cu numărul secret în el (îl poți scrie cu `else` la `while` sau cu o variabilă).
2. **Meniu cu while True.** Scrie un meniu de conversii: `1` = Celsius → Fahrenheit, `2` = km → mile (1 km = 0.621371 mile), `0` = ieșire. Folosește `while True` și `break` pentru ieșire, iar pentru o opțiune necunoscută afișează un mesaj și treci la iterația următoare cu `continue`. Valorile se validează ca în exemplul complet de la lecția 10 (`replace(",", ".")` și `replace(".", "", 1).isdigit()`); pentru temperaturi negative, dacă textul începe cu `-` (`text.startswith("-")`), verifică doar restul lui (`text[1:]`), dar convertește cu `float()` textul întreg, cu minus cu tot.
3. **Căutare cu else.** Cere un cuvânt și verifică dacă are măcar o literă dublă alăturată (ca „ii” în „copii” sau „ee” în „idee”). Afișează prima pereche găsită sau, cu `else` la `for`, „Nicio literă dublă”. Indiciu: parcurge pozițiile cu `range(len(cuvant) - 1)` și compară `cuvant[i]` cu `cuvant[i + 1]`.

## Pe scurt

- `break` iese imediat din bucla curentă; `continue` sare la iterația următoare.
- `while True:` cu `break` e tiparul standard pentru „repetă până reușește” (de exemplu, validarea unui răspuns).
- `else` după o buclă rulează doar dacă bucla s-a terminat fără `break`: util pentru „am căutat și n-am găsit”.
- `pass` ține locul unui bloc gol.
- În buclele imbricate, `break` și `continue` afectează doar bucla cea mai apropiată.
- Într-un `while`, actualizează contorul înainte de `continue`; în `for`, `continue` nu „anulează” iterația.
