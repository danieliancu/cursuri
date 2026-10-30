## Ce este

Un **program** este o listă de instrucțiuni pe care calculatorul le execută una după alta, de sus în jos. În Python, programul e un fișier text obișnuit, cu extensia `.py`.

**Python** este un limbaj de programare: un set de reguli pentru a scrie instrucțiuni pe care atât oamenii, cât și calculatorul le pot citi. Calculatorul nu înțelege direct textul din fișier. Îl citește un alt program, numit **interpretor** (în engleză „interpreter”), care ia fiecare rând și îl execută.

Cel mai simplu program Python are un singur rând:

```python
print("Salut, lume!")
```

```text
Salut, lume!
```

`print()` este o **funcție**: o comandă cu nume, care face ceva. Ce pui între paranteze este ce primește funcția, iar `print()` afișează acel lucru pe ecran.

## De ce contează

Orice program, de la un script de zece rânduri la o aplicație web cu Django, se reduce la același lucru: un fișier pe care interpretorul îl citește de sus în jos. Dacă înțelegi bine cum rulează un fișier simplu, înțelegi și ce se întâmplă mai târziu, când rulezi `python manage.py runserver`.

`print()` va fi și prima ta unealtă de depanare: când nu știi ce face programul, afișezi valori ca să vezi ce se întâmplă.

## Cum funcționează

### Rularea unui fișier

În editor, fișierul capitolului e deja creat. Când apeși **Rulează și verifică** (sau Ctrl+Enter), în terminal apare o comandă de felul acesta (iar la final tutorele se uită la rezultat și îți spune ce a văzut):

```bash
python capitole/01-primul-program/primul_program.py
```

Comanda are două părți:
- `python` pornește interpretorul;
- `capitole/01-primul-program/primul_program.py` îi spune ce fișier să citească.

Interpretorul citește fișierul de la primul rând la ultimul, execută fiecare instrucțiune și se oprește la final. Tot ce afișează programul apare în terminal.

### print()

Textul se scrie între ghilimele. Fără ghilimele, Python ar crede că e numele unui lucru din program (despre asta, la lecția 2).

```python
print("Bună ziua!")
print('Merg și ghilimelele simple.')
print("Ana are", 25, "de ani.")
print()
print("Rândul de mai sus e gol.")
```

```text
Bună ziua!
Merg și ghilimelele simple.
Ana are 25 de ani.

Rândul de mai sus e gol.
```

Ce se vede aici:
- fiecare `print()` afișează un rând nou;
- ghilimelele duble `"` și simple `'` funcționează la fel; important e să deschizi și să închizi cu același fel;
- poți da mai multe lucruri, separate prin virgulă: `print()` le afișează pe același rând, cu câte un spațiu între ele;
- numerele, ca `25`, nu au nevoie de ghilimele;
- `print()` gol afișează un rând gol.

`print()` poate afișa și rezultatul unui calcul:

```python
print(2 + 3)
print("2 + 3")
```

```text
5
2 + 3
```

Fără ghilimele, `2 + 3` e un calcul și se afișează rezultatul. Cu ghilimele, e doar text și se afișează exact cum e scris.

### Comentarii

Tot ce urmează după `#` pe un rând este un **comentariu**: interpretorul îl ignoră. Comentariile sunt pentru oameni: pentru tine peste o lună sau pentru colegul care citește codul.

```python
# Programul ăsta salută utilizatorul.
print("Salut!")  # comentariul poate sta și la final de rând
# print("Rândul ăsta nu rulează.")
```

```text
Salut!
```

Un truc folosit des: pui `#` în fața unui rând de cod ca să-l „oprești” temporar, fără să-l ștergi.

Un comentariu bun explică **de ce** faci ceva, nu repetă ce face codul. `# afișez salutul` deasupra lui `print("Salut!")` nu ajută pe nimeni.

### Indentarea face parte din sintaxă

**Indentarea** înseamnă spațiile de la începutul unui rând. În multe limbaje sunt doar estetică. În Python au sens: arată ce cod aparține de ce bloc (vei vedea blocuri la lecția 8, la `if`).

Până atunci, regula e simplă: **instrucțiunile obișnuite încep de la marginea din stânga**, fără spații în față. Un spațiu în plus produce o eroare, ca în secțiunea „Greșeli frecvente”.

### Ce se întâmplă „pe dedesubt”

Când rulezi fișierul, interpretorul face doi pași:
1. **citește tot fișierul** și verifică dacă e scris corect (sintaxa). Dacă găsește o greșeală de scriere, se oprește înainte să execute ceva și afișează un `SyntaxError`;
2. **execută rândurile pe rând**. Dacă un rând dă eroare la execuție, rândurile de dinainte au rulat deja, iar cele de după nu mai rulează.

```python
print("Rândul 1")
print("Rândul 2")
Print("Rândul 3")
print("Rândul 4")
```

```text
Rândul 1
Rândul 2
Traceback (most recent call last):
  File "program.py", line 3, in <module>
    Print("Rândul 3")
    ^^^^^
NameError: name 'Print' is not defined. Did you mean: 'print'?
```

Primele două rânduri s-au afișat. La rândul 3 programul s-a oprit, iar rândul 4 nu a mai rulat. Mesajul de eroare (un **traceback**) spune exact unde e problema (`line 3`) și, pe ultimul rând, ce s-a întâmplat: `NameError`, adică Python nu cunoaște numele `Print` (vezi greșeala 3 de mai jos). Cum citești un traceback în detaliu vom vedea la lecția 23.

## Exemplu complet

Un program care afișează o fișă de prezentare:

<!-- fisier: prezentare.py -->
```python
# Fișa de prezentare a Anei, afișată în terminal.

print("=====================")
print("  FIȘĂ DE PREZENTARE")
print("=====================")
print("Nume:  ", "Ana Popescu")
print("Vârstă:", 25, "de ani")
print("Oraș:  ", "Cluj")
print()
print("Ana învață Python de", 3, "săptămâni.")
print("Până la finalul anului mai are", 52 - 3, "de săptămâni.")
```

```text
=====================
  FIȘĂ DE PREZENTARE
=====================
Nume:   Ana Popescu
Vârstă: 25 de ani
Oraș:   Cluj

Ana învață Python de 3 săptămâni.
Până la finalul anului mai are 49 de săptămâni.
```

Observă cum `print()` pune un spațiu între elemente: după `"Nume:  "` (care are deja două spații) apare încă unul. Spațiile din interiorul ghilimelelor se păstrează exact, așa că le poți folosi ca să aliniezi textul.

## Greșeli frecvente

### 1. Ghilimele neînchise

<!-- fisier: salut.py -->
```python
print("Salut, lume!)
```

```text
  File "salut.py", line 1
    print("Salut, lume!)
          ^
SyntaxError: unterminated string literal (detected at line 1)
```

„Unterminated string literal” înseamnă „text neterminat”: ai deschis ghilimelele, dar nu le-ai închis. Săgeata `^` arată unde începe textul cu probleme.

```python
print("Salut, lume!")
```

### 2. Ghilimele „românești” copiate din Word sau din chat

Editoarele de text obișnuite pun automat ghilimele tipografice („ ”), care pentru Python sunt alte caractere:

<!-- fisier: salut.py -->
```python
print(„Salut!”)
```

```text
  File "salut.py", line 1
    print(„Salut!”)
          ^
SyntaxError: invalid character '„' (U+201E)
```

În cod se folosesc doar ghilimelele drepte, `"` sau `'`. În interiorul textului poți scrie orice: `print("Ea a spus „bună”.")` e corect.

### 3. Print cu literă mare

<!-- fisier: salut.py -->
```python
Print("Salut!")
```

```text
Traceback (most recent call last):
  File "salut.py", line 1, in <module>
    Print("Salut!")
    ^^^^^
NameError: name 'Print' is not defined. Did you mean: 'print'?
```

Python face diferența între litere mari și mici: `Print` și `print` sunt nume diferite, iar `Print` nu există. Python chiar îți sugerează varianta corectă: „Did you mean: 'print'?”.

```python
print("Salut!")
```

### 4. Spații în fața rândului

<!-- fisier: salut.py -->
```python
print("Rândul 1")
 print("Rândul 2")
```

```text
  File "salut.py", line 2
    print("Rândul 2")
IndentationError: unexpected indent
```

„Unexpected indent” înseamnă „indentare neașteptată”: rândul 2 începe cu un spațiu, deși nu se află într-un bloc. Fiindcă e o greșeală de scriere, nici rândul 1 nu a rulat: Python verifică tot fișierul înainte să înceapă.

```python
print("Rândul 1")
print("Rândul 2")
```

### 5. print fără paranteze

Pe internet găsești încă exemple scrise pentru Python 2, o versiune veche, în care `print` nu avea paranteze:

<!-- fisier: salut.py -->
```python
print "Salut!"
```

```text
  File "salut.py", line 1
    print "Salut!"
    ^^^^^^^^^^^^^^
SyntaxError: Missing parentheses in call to 'print'. Did you mean print(...)?
```

În Python 3, `print` e o funcție, deci are mereu paranteze:

```python
print("Salut!")
```

## Exercițiu

În fișierul capitolului, `capitole/01-primul-program/primul_program.py`, scrie un program care afișează fișa ta de prezentare:

1. un titlu încadrat de două rânduri de `=` sau `-`;
2. numele, vârsta și orașul tău, pe rânduri separate, aliniate ca în exemplu;
3. un rând gol;
4. un rând care conține un calcul făcut de Python, de exemplu câte luni ai trăit (vârsta înmulțită cu 12, cu `*`);
5. cel puțin un comentariu care explică ce face programul.

Rulează programul și asigură-te că afișează ce trebuie. Abia apoi strică-l intenționat, câte o greșeală pe rând (scoate o ghilimea, scrie `Print`, pune un spațiu în fața unui rând), citește ce eroare primești și repară-l la loc înainte de următoarea.

## Pe scurt

- Un program Python e un fișier `.py` pe care interpretorul îl citește și îl execută de sus în jos.
- `print()` afișează în terminal tot ce primește; mai multe valori separate prin virgulă apar pe același rând, cu spațiu între ele.
- Textul stă între ghilimele drepte (`"` sau `'`); numerele și calculele nu au nevoie de ghilimele.
- Tot ce e după `#` e comentariu și nu se execută.
- Instrucțiunile obișnuite încep de la marginea din stânga; spațiile în plus dau `IndentationError`.
- Greșelile de scriere (`SyntaxError`) opresc programul înainte de primul rând; erorile de execuție îl opresc la rândul cu problema.
