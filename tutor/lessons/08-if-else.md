## Ce este

Până acum, programele tale rulau toate rândurile, de sus în jos, de fiecare dată. Instrucțiunea **`if`** („dacă”) îi permite programului să **decidă**: un bloc de cod rulează doar dacă o condiție e adevărată.

<!-- stdin: 25 -->
```python
varsta = int(input("Câți ani ai? "))
if varsta >= 18:
    print("Ești major.")
print("Gata.")
```

```text
Câți ani ai? 25
Ești major.
Gata.
```

Cu un răspuns de `15`, Python ar fi sărit peste rândul „Ești major.”, iar „Gata.” s-ar afișa oricum, pentru că nu face parte din `if`.

Condiția e o expresie care dă `True` sau `False`, adică exact ce ai învățat la lecția 7. Lângă `if` pot apărea **`elif`** („altfel, dacă”) și **`else`** („altfel”), ca programul să aleagă între mai multe drumuri.

## De ce contează

Fără decizii, un program poate doar să calculeze. Cu decizii, poate reacționa: să refuze o parolă greșită, să aplice o reducere doar peste o anumită sumă, să afișeze „coșul e gol” în loc de un tabel gol, să trimită utilizatorul neautentificat la pagina de autentificare. Și în Django, aproape fiecare view (funcția care construiește o pagină, lecția 47) are un `if` (de exemplu, „a trimis formularul?”).

## Cum funcționează

### Sintaxa și blocurile

```python
if conditie:
    # blocul lui if: rulează doar dacă conditie e adevărată
    print("primul rând din bloc")
    print("al doilea rând din bloc")
# aici blocul s-a terminat
```

Trei reguli de sintaxă:
1. după condiție urmează **două puncte** `:`;
2. rândurile din bloc sunt **indentate** (împinse spre dreapta). Convenția e de **4 spații**, iar editorul le pune automat după `:`;
3. blocul se termină la primul rând care revine la indentarea lui `if`.

Aici apare ce anunțam la lecția 1: în Python, indentarea face parte din sintaxă. Ea arată ce cod aparține de `if`.

### else: cele două drumuri

<!-- stdin: Mihai -->
```python
nume = input("Numele: ")
if nume == "Ana":
    print("Bine ai revenit, Ana!")
else:
    print(f"Salut, {nume}! E prima ta vizită?")
```

```text
Numele: Mihai
Salut, Mihai! E prima ta vizită?
```

Exact unul dintre cele două blocuri rulează. `else` nu are condiție: prinde tot ce nu a prins `if`.

### elif: mai multe variante

Când ai mai mult de două cazuri, folosești `elif`. Fiecare bloc (`if`, `elif`, `else`) se numește **ramură**. Python verifică ramurile **de sus în jos** și o execută doar pe **prima** a cărei condiție e adevărată. Restul nu mai sunt verificate.

<!-- stdin: 7.5 -->
```python
nota = float(input("Nota: "))
if nota >= 9:
    calificativ = "Foarte bine"
elif nota >= 7:
    calificativ = "Bine"
elif nota >= 5:
    calificativ = "Suficient"
else:
    calificativ = "Insuficient"
print(f"Calificativ: {calificativ}")
```

```text
Nota: 7.5
Calificativ: Bine
```

Pentru `7.5`: `nota >= 9` e fals, deci se trece mai departe. `nota >= 7` e adevărat, se execută ramura asta și gata. Faptul că și `nota >= 5` e adevărat nu mai contează. Din același motiv nu a fost nevoie să scriem `elif 7 <= nota < 9`: dacă am ajuns la a doua ramură, știm deja că nota e sub 9.

Poți avea oricâte `elif`-uri, iar `else` e opțional.

### Condiții compuse

Tot ce ai învățat la lecția 7 funcționează în `if`: `and`, `or`, `not`, comparații înlănțuite, `in`.

<!-- stdin: 34\nda -->
```python
varsta = int(input("Vârsta: "))
student = input("Ești student? (da/nu) ").strip().lower() == "da"

if varsta < 7 or varsta >= 70:
    pret = 0
elif student or 7 <= varsta < 18:
    pret = 10
else:
    pret = 25
print(f"Biletul costă {pret} lei.")
```

```text
Vârsta: 34
Ești student? (da/nu) da
Biletul costă 10 lei.
```

Variabila `student` păstrează direct rezultatul comparației cu `"da"`, adică `True` sau `False` (ca `este_cluj` din lecția 7), așa că o poți folosi singură în condiție.

### Truthiness în if

`if` acceptă orice valoare, nu doar `True` și `False`, și o tratează după regulile de truthiness din lecția 7. De aceea poți verifica scurt dacă un text e gol:

<!-- stdin: \n -->
```python
nume = input("Numele: ").strip()
if nume:
    print(f"Salut, {nume}!")
else:
    print("N-ai scris niciun nume.")
```

```text
Numele: 
N-ai scris niciun nume.
```

`if nume:` se citește „dacă numele nu e gol”. E forma preferată în Python, în loc de `if nume != "":` sau `if len(nume) > 0:`.

### if imbricat

Un bloc poate conține alt `if`. Fiecare nivel adaugă 4 spații:

<!-- stdin: ana\nparola12 -->
```python
utilizator = input("Utilizator: ")
parola = input("Parola: ")

if utilizator == "ana":
    if parola == "Secret2026":
        print("Autentificare reușită.")
    else:
        print("Parolă greșită.")
else:
    print("Utilizator necunoscut.")
```

```text
Utilizator: ana
Parola: parola12
Parolă greșită.
```

Imbricarea e utilă când al doilea test are sens doar după primul. Nu exagera totuși: mai mult de două-trei niveluri se citesc greu. Adesea, un `and` sau un `elif` face același lucru mai clar.

### Expresia condițională

Când vrei doar să alegi **o valoare** din două, există o formă pe un singur rând:

```python
varsta = 25
categorie = "adult" if varsta >= 18 else "minor"
print(categorie)

numar = 7
print(f"{numar} este {'par' if numar % 2 == 0 else 'impar'}.")
```

```text
adult
7 este impar.
```

Se citește „`"adult"` dacă vârsta e cel puțin 18, altfel `"minor"`”. E bună pentru alegeri simple între două valori. Pentru orice altceva, folosește `if` normal.

### Ce se întâmplă „pe dedesubt”: Python nu verifică ce nu execută

Ramurile care nu sunt alese **nu se execută deloc**, deci nici erorile din ele nu apar:

```python
are_cont = False
if are_cont:
    print(sold_cont)  # sold_cont nu există, dar rândul nu rulează
else:
    print("Nu ai cont.")
```

```text
Nu ai cont.
```

Python verifică doar **sintaxa** întregului fișier, înainte de pornire. Erorile de execuție, ca `NameError` aici, apar abia când se ajunge la rândul respectiv. O greșeală dintr-o ramură rar folosită poate sta ascunsă mult timp. De aceea, când testezi un program, încearcă intrări care trec prin **fiecare** ramură.

## Exemplu complet

Prima versiune a jocului „Ghicește numărul”, pe care îl vom construi în tot modulul. Deocamdată jucătorul are o singură încercare. Numărul secret e fix. La lecția 31 îl vom alege la întâmplare, cu modulul `random`.

<!-- fisier: ghiceste.py -->
<!-- stdin: 30 -->
```python
numar_secret = 37

print("Ghicește numărul (între 1 și 100)!")
text = input("Încercarea ta: ").strip()

if not text.isdigit():
    print(f"„{text}” nu e un număr întreg pozitiv.")
else:
    incercare = int(text)
    diferenta = abs(incercare - numar_secret)

    if incercare < 1 or incercare > 100:
        print("Numărul trebuie să fie între 1 și 100.")
    elif incercare == numar_secret:
        print("Bravo, ai ghicit din prima!")
    else:
        directie = "mic" if incercare < numar_secret else "mare"
        if diferenta <= 5:
            print(f"Foarte aproape, dar e puțin prea {directie}.")
        else:
            print(f"Prea {directie}.")
        print(f"Numărul era {numar_secret}.")
```

```text
Ghicește numărul (între 1 și 100)!
Încercarea ta: 30
Prea mic.
Numărul era 37.
```

Metoda `isdigit()` e nouă: întoarce `True` dacă textul are cel puțin un caracter și e format numai din cifre. O folosim **înainte** de `int()`, ca să evităm `ValueError`-ul de la lecția 6. Rulează programul cu `35`, `37`, `120` și `abc` ca să treci prin toate ramurile.

## Greșeli frecvente

### 1. Lipsesc cele două puncte

<!-- fisier: varsta.py -->
```python
varsta = 25
if varsta >= 18
    print("Major")
```

```text
  File "varsta.py", line 2
    if varsta >= 18
                   ^
SyntaxError: expected ':'
```

Orice `if`, `elif` și `else` se termină cu `:`.

### 2. Blocul nu e indentat

<!-- fisier: varsta.py -->
```python
varsta = 25
if varsta >= 18:
print("Major")
```

```text
  File "varsta.py", line 3
    print("Major")
    ^^^^^
IndentationError: expected an indented block after 'if' statement on line 2
```

Mesajul e foarte clar: după `if`-ul de pe rândul 2 trebuia să urmeze un bloc indentat. Pune 4 spații în fața lui `print`.

Varianta inversă e la fel de periculoasă, dar nu dă eroare: un rând **neindentat** din greșeală iese din bloc și rulează mereu.

```python
varsta = 15
if varsta >= 18:
    print("Major")
print("Poți cumpăra bilet la filmul 18+.")
```

```text
Poți cumpăra bilet la filmul 18+.
```

Al doilea `print` trebuia să fie în bloc, cu 4 spații în față.

### 3. = în loc de == în condiție

<!-- fisier: varsta.py -->
```python
oras = "Cluj"
if oras = "Cluj":
    print("Bun venit în Cluj!")
```

```text
  File "varsta.py", line 2
    if oras = "Cluj":
       ^^^^^^^^^^^^^
SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?
```

Python îți sugerează chiar soluția: `==`. (`:=` e un operator mai avansat, de care nu ai nevoie acum.)

### 4. Ordinea greșită a ramurilor elif

```python
nota = 9.5
if nota >= 5:
    calificativ = "Suficient"
elif nota >= 7:
    calificativ = "Bine"
elif nota >= 9:
    calificativ = "Foarte bine"
print(calificativ)
```

```text
Suficient
```

Nu apare nicio eroare, dar rezultatul e greșit. Prima ramură adevărată câștigă, iar `9.5 >= 5` e adevărat, așa că celelalte nici nu se mai verifică. Când condițiile se suprapun, pune-o **pe cea mai strictă prima** (`>= 9`, apoi `>= 7`, apoi `>= 5`), ca în exemplul din „Cum funcționează”.

### 5. Indentare inconsecventă

<!-- fisier: varsta.py -->
```python
varsta = 25
if varsta >= 18:
    print("Major")
  print("Poți vota.")
```

```text
  File "varsta.py", line 4
    print("Poți vota.")
                       ^
IndentationError: unindent does not match any outer indentation level
```

Rândul 4 are 2 spații: nu e nici în bloc (4 spații), nici în afara lui (0 spații). Toate rândurile unui bloc trebuie să aibă **exact aceeași** indentare. Folosește mereu 4 spații, pe care editorul le pune singur la Tab, și nu amesteca spațiile cu caracterul Tab.

## Exercițiu

În `capitole/08-if-else/if_else.py`, scrie un calculator de reducere pentru un magazin online:

1. cere valoarea coșului (poate avea zecimale și virgulă; dacă textul nu e un număr valid, afișează un mesaj prietenos și nu mai calcula nimic, fără eroare: pune restul programului pe ramura `else`, ca în exemplul complet);
2. cere un cod de reducere, care poate fi gol;
3. regulile (pragurile se verifică pe valoarea coșului **înainte** de reducere, iar ambele coduri se acceptă cu orice combinație de litere mari și mici):
   - sub 100 lei: transport 15 lei, de la 100 lei în sus: transport gratuit;
   - codul `"STUDENT"` dă 10% reducere;
   - codul `"VARA2026"` dă 20 lei reducere, dar numai pentru coșuri de cel puțin 150 lei; altfel afișează de ce nu se aplică;
   - un cod gol nu dă reducere și nici mesaj; orice alt cod afișează „Cod necunoscut”;
4. afișează la final valoarea coșului, reducerea, transportul și totalul, cu 2 zecimale.

Indiciu pentru validare: după ce ai înlocuit virgula cu punct, `"12.5".replace(".", "", 1).isdigit()` e `True`, pentru că scoate un singur punct (al treilea argument, `1`, înseamnă „cel mult o înlocuire”) înainte de verificare. Testează cu valori care trec prin **fiecare** ramură.

## Pe scurt

- `if conditie:` rulează blocul indentat doar dacă condiția e adevărată; `elif` adaugă variante, iar `else` prinde restul.
- Din tot lanțul `if / elif / else` se execută cel mult o ramură: prima adevărată, de sus în jos.
- Blocurile se marchează prin indentare de 4 spații, după `:`; rândurile unui bloc au toate aceeași indentare.
- În condiții poți folosi `and`, `or`, `not`, `in`, comparații înlănțuite și truthiness (`if nume:`).
- `valoare1 if conditie else valoare2` alege între două valori pe un singur rând.
- Ramurile neexecutate nu dau erori de execuție, așa că testează fiecare ramură.
