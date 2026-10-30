## Ce este

O **variabilă** este un nume pe care îl dai unei valori, ca să o poți folosi mai târziu în program.

```python
nume = "Ana Popescu"
varsta = 25
print(nume, "are", varsta, "de ani.")
```

```text
Ana Popescu are 25 de ani.
```

Rândul `nume = "Ana Popescu"` se numește **atribuire** (în engleză „assignment”) și se citește „numele `nume` primește valoarea `"Ana Popescu"`”. Semnul `=` nu înseamnă „egal” ca la matematică. Înseamnă „leagă numele din stânga de valoarea din dreapta”.

## De ce contează

Fără variabile, ar trebui să scrii aceeași valoare de fiecare dată când ai nevoie de ea. În lecția 1, numele Anei apărea scris de mână în fiecare `print()`. Dacă vrei fișa lui Mihai, trebuie să schimbi textul peste tot și e ușor să uiți un loc.

Cu o variabilă, valoarea e scrisă **o singură dată**, iar restul programului folosește numele. Variabilele mai au un rol: păstrează rezultatele intermediare ale unui calcul și dau nume clare lucrurilor din program. `pret_total` spune mult mai mult decât `37.5` scris în mijlocul codului.

## Cum funcționează

### Atribuirea

Forma e mereu aceeași: `nume = valoare`. Python calculează întâi partea din dreapta, apoi leagă numele din stânga de rezultat.

```python
oras = "Cluj"
luni = 25 * 12
print(oras)
print(luni)
```

```text
Cluj
300
```

La `luni = 25 * 12` (`*` înseamnă înmulțire; toți operatorii, la lecția 3), Python face întâi înmulțirea (`300`), apoi leagă `luni` de rezultat. Variabila ține minte valoarea `300`, nu calculul.

Când folosești o variabilă, scrii numele ei **fără ghilimele**. Cu ghilimele, ar fi doar textul format din literele acelea:

```python
oras = "Cluj"
print(oras)
print("oras")
```

```text
Cluj
oras
```

### Reatribuirea

O variabilă poate primi oricând o valoare nouă. Valoarea veche se pierde, iar de acum numele se referă la cea nouă:

```python
oras = "Cluj"
print("Ana locuiește în", oras)
oras = "Brașov"
print("Ana s-a mutat în", oras)
```

```text
Ana locuiește în Cluj
Ana s-a mutat în Brașov
```

Partea din dreapta poate folosi chiar variabila din stânga. Rândul `varsta = varsta + 1` arată ciudat dacă îl citești ca pe o ecuație, dar are sens dacă îl citești ca Python: „calculează `varsta + 1` cu valoarea de acum, apoi leagă `varsta` de rezultat”.

```python
varsta = 25
varsta = varsta + 1
print("La anul, Ana va avea", varsta, "de ani.")
```

```text
La anul, Ana va avea 26 de ani.
```

### Ce se întâmplă „pe dedesubt”: nume și obiecte

În Python, fiecare valoare (`25`, `"Cluj"`) este un **obiect** care stă undeva în memoria calculatorului. O variabilă **nu este o cutie** care conține valoarea. Este mai degrabă o **etichetă** lipită pe obiect.

```python
varsta_ana = 25
varsta_mihai = varsta_ana
varsta_ana = 26
print(varsta_ana, varsta_mihai)
```

```text
26 25
```

Pas cu pas:
1. `varsta_ana = 25`: eticheta `varsta_ana` e lipită pe obiectul `25`;
2. `varsta_mihai = varsta_ana`: eticheta `varsta_mihai` e lipită pe **același** obiect `25`;
3. `varsta_ana = 26`: eticheta `varsta_ana` e mutată pe obiectul `26`. Eticheta `varsta_mihai` rămâne unde era, pe `25`.

Pentru numere și texte, modelul cu etichete și cel cu cutii dau același rezultat. Diferența va conta la liste (lecția 12), unde două nume pot arăta spre același obiect care se modifică.

### Tipul unei valori: type()

Fiecare obiect are un **tip**, care spune ce fel de valoare e și ce poți face cu ea. Funcția `type()` îți arată tipul:

```python
nume = "Ana"
varsta = 25
inaltime = 1.68
print(type(nume))
print(type(varsta))
print(type(inaltime))
```

```text
<class 'str'>
<class 'int'>
<class 'float'>
```

- `str` (de la „string”, șir de caractere) este textul, la lecția 4;
- `int` (de la „integer”) sunt numerele întregi, la lecția 3;
- `float` sunt numerele cu virgulă, tot la lecția 3. În Python, virgula zecimală se scrie cu **punct**: `1.68`.

Tipul ține de **valoare**, nu de variabilă. Aceeași variabilă poate primi pe rând valori de tipuri diferite:

```python
valoare = 25
print(type(valoare))
valoare = "douăzeci și cinci"
print(type(valoare))
```

```text
<class 'int'>
<class 'str'>
```

Python permite asta, dar în practică e o idee proastă: cine citește codul se așteaptă ca `valoare` să fie mereu același fel de lucru.

### Reguli pentru nume

Un nume de variabilă:
- conține doar litere, cifre și `_` (fără spații, cratime sau alte semne);
- **nu începe cu o cifră**: `nota1` e corect, `1nota` nu;
- ține cont de literele mari și mici: `varsta` și `Varsta` sunt două variabile diferite;
- nu poate fi un **cuvânt rezervat** al limbajului, cum ar fi `if`, `for`, `class`, `True` sau `None`.

Pe lângă reguli, există și **convenții**, adică obiceiuri pe care le respectă toată lumea:
- **snake_case**: litere mici, cuvinte despărțite prin `_`, ca `pret_total` sau `data_nasterii`;
- **nume care spun ce conțin**: `varsta`, nu `v` sau `x1`;
- **fără diacritice**. Python le acceptă (`vârstă = 25` funcționează), dar ele creează probleme pe tastaturi și în unelte diferite. În cod scrii `varsta`, iar diacriticele le păstrezi pentru textul dintre ghilimele.

```python
# Corect și ușor de citit
pret_unitar = 12
cantitate = 3
pret_total = pret_unitar * cantitate
print("Total:", pret_total, "lei")
```

```text
Total: 36 lei
```

## Exemplu complet

Fișa din lecția 1, rescrisă cu variabile. Ca să afișezi fișa altcuiva, schimbi doar cele trei rânduri cu datele persoanei.

<!-- fisier: fisa.py -->
```python
# Datele persoanei: singurul loc unde le schimbi.
nume = "Mihai Ionescu"
varsta = 31
oras = "Iași"

# Calcule pe baza datelor
luni_traite = varsta * 12
varsta_peste_10_ani = varsta + 10

print("=====================")
print("  FIȘĂ DE PREZENTARE")
print("=====================")
print("Nume:  ", nume)
print("Vârstă:", varsta, "de ani")
print("Oraș:  ", oras)
print()
print(nume, "a trăit aproximativ", luni_traite, "de luni.")
print("Peste 10 ani va avea", varsta_peste_10_ani, "de ani.")
```

```text
=====================
  FIȘĂ DE PREZENTARE
=====================
Nume:   Mihai Ionescu
Vârstă: 31 de ani
Oraș:   Iași

Mihai Ionescu a trăit aproximativ 372 de luni.
Peste 10 ani va avea 41 de ani.
```

## Greșeli frecvente

### 1. Folosirea unei variabile înainte să existe

Python execută rândurile în ordine, deci o variabilă există abia după rândul în care primește o valoare.

<!-- fisier: fisa.py -->
```python
print(oras)
oras = "Cluj"
```

```text
Traceback (most recent call last):
  File "fisa.py", line 1, in <module>
    print(oras)
          ^^^^
NameError: name 'oras' is not defined
```

Atribuirea trebuie să vină înaintea folosirii:

```python
oras = "Cluj"
print(oras)
```

### 2. O greșeală de tastare în nume

<!-- fisier: fisa.py -->
```python
varsta = 25
print(varsat)
```

```text
Traceback (most recent call last):
  File "fisa.py", line 2, in <module>
    print(varsat)
          ^^^^^^
NameError: name 'varsat' is not defined. Did you mean: 'varsta'?
```

Pentru Python, `varsat` e un nume complet nou. Mesajul „Did you mean: 'varsta'?” te ajută să vezi greșeala. Același lucru se întâmplă cu `Varsta` în loc de `varsta`.

### 3. Nume care încep cu cifră sau conțin spații

<!-- fisier: fisa.py -->
```python
2nume = "Ana Maria"
```

```text
  File "fisa.py", line 1
    2nume = "Ana Maria"
    ^
SyntaxError: invalid decimal literal
```

Python vede `2` și crede că urmează un număr, dar găsește litere. Cu spații, eroarea e alta:

<!-- fisier: fisa.py -->
```python
al doilea nume = "Maria"
```

```text
  File "fisa.py", line 1
    al doilea nume = "Maria"
       ^^^^^^
SyntaxError: invalid syntax
```

Varianta corectă folosește `_`, iar cifra vine la final:

```python
al_doilea_nume = "Maria"
nume2 = "Ana Maria"
```

### 4. Un cuvânt rezervat ca nume

<!-- fisier: fisa.py -->
```python
class = "a XII-a"
```

```text
  File "fisa.py", line 1
    class = "a XII-a"
          ^
SyntaxError: invalid syntax
```

`class` e cuvânt rezervat (îl vei folosi la lecția 32). Alege alt nume:

```python
clasa = "a XII-a"
```

### 5. Ghilimele puse din greșeală în jurul variabilei

Greșeala asta nu dă nicio eroare, deci e ușor să treacă neobservată:

```python
nume = "Ana"
print("Salut,", "nume")
```

```text
Salut, nume
```

Cu ghilimele, `"nume"` e un text, nu variabila. Corect:

```python
nume = "Ana"
print("Salut,", nume)
```

```text
Salut, Ana
```

## Exercițiu

În `capitole/02-variabile/variabile.py`, scrie un program pentru un bon de cumpărături:

1. creează variabile pentru numele clientului și pentru trei produse: pentru fiecare, prețul pe bucată și cantitatea (de exemplu `pret_paine`, `cantitate_paine`);
2. calculează totalul pe fiecare produs și totalul general, fiecare într-o variabilă cu nume clar;
3. afișează bonul: numele clientului, apoi câte un rând pe produs și la final totalul;
4. la final, schimbă prețul unui produs, prin **reatribuire** după calcul, și afișează din nou variabila cu totalul general, fără să refaci calculul. Se schimbă totalul? De ce?

Folosește `type()` ca să verifici tipul a două dintre variabile.

## Pe scurt

- O variabilă e un nume legat de o valoare; `=` înseamnă atribuire, nu egalitate.
- Python calculează întâi partea din dreapta a lui `=`, apoi leagă numele de rezultat; `x = x + 1` e perfect valid.
- O variabilă poate primi oricând o valoare nouă, iar cea veche se pierde.
- Variabilele sunt etichete pe obiecte, iar fiecare obiect are un tip (`str`, `int`, `float`), pe care îl vezi cu `type()`.
- Numele conțin litere, cifre și `_`, nu încep cu cifră și nu sunt cuvinte rezervate; prin convenție se scriu în snake_case, fără diacritice.
- O variabilă folosită înainte de atribuire, sau scrisă greșit, dă `NameError`.
