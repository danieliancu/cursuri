## Ce este

Un **decorator** este o funcție care primește o funcție și întoarce o versiune „împachetată” a ei: aceeași funcție, plus un comportament adăugat **înainte** și/sau **după** rularea ei, fără să-i modifici codul.

```python
def anunta(functie):
    def impachetata():
        print(f"> pornesc {functie.__name__}")
        functie()
        print(f"> am terminat {functie.__name__}")
    return impachetata


@anunta
def inventar():
    print("Număr cărțile de pe rafturi...")


inventar()
```

```text
> pornesc inventar
Număr cărțile de pe rafturi...
> am terminat inventar
```

Rândul `@anunta`, pus deasupra lui `def`, e sintaxa de decorator. Înseamnă exact `inventar = anunta(inventar)`: numele `inventar` arată acum spre funcția împachetată.

## De ce contează

Multe funcții au nevoie de același cod „în jurul” lor: să scrie în jurnal când sunt apelate, să măsoare cât durează, să verifice dacă utilizatorul are voie să le folosească, să păstreze rezultatele deja calculate. Fără decoratori, ai copia aceleași rânduri în fiecare funcție. Cu un decorator, scrii codul o singură dată și îl aplici cu un rând: `@nume`.

Ai folosit deja decoratori: `@property`, `@classmethod` și `@staticmethod` (lecția 33), `@dataclass` (lecția 36), care primește o clasă în loc de o funcție, dar după aceeași idee. În Django îi vei folosi constant: `@login_required` (lecția 57) pus deasupra unui view îl face accesibil doar utilizatorilor autentificați, fără ca view-ul să conțină vreo verificare.

## Cum funcționează

### Ingredientele: funcții ca valori și funcții interioare

Un decorator se bazează pe două lucruri pe care le știi de la lecția 21:
- o funcție e o valoare: o poți da ca argument și o poți întoarce cu `return`;
- o funcție poate fi definită **în interiorul** altei funcții și ține minte variabilele funcției exterioare chiar după ce aceasta s-a terminat: un **closure**, ca `fa_reducere` din lecția 21.

O recapitulare scurtă, pe un exemplu nou:

```python
def creeaza_salut(formula):
    def salut(nume):
        return f"{formula}, {nume}!"
    return salut


buna_ziua = creeaza_salut("Bună ziua")
servus = creeaza_salut("Servus")
print(buna_ziua("Ana"))
print(servus("Mihai"))
```

```text
Bună ziua, Ana!
Servus, Mihai!
```

`creeaza_salut` s-a terminat de mult când apelăm `buna_ziua("Ana")`, dar funcția interioară își amintește `formula`. Un decorator face exact asta, doar că lucrul ținut minte e **o funcție**.

### Un decorator, pas cu pas

```python
def jurnal(functie):
    def impachetata(*args, **kwargs):
        print(f"[jurnal] {functie.__name__}{args}")
        rezultat = functie(*args, **kwargs)
        print(f"[jurnal] {functie.__name__} a întors {rezultat!r}")
        return rezultat
    return impachetata


def imprumuta(titlu, cititor):
    return f"{titlu} -> {cititor}"


imprumuta = jurnal(imprumuta)   # exact ce face @jurnal
print(imprumuta("Ion", "Ana"))
```

```text
[jurnal] imprumuta('Ion', 'Ana')
[jurnal] imprumuta a întors 'Ion -> Ana'
Ion -> Ana
```

Trei detalii fac decoratorul să funcționeze pentru **orice** funcție:
1. `impachetata(*args, **kwargs)` primește orice argumente (lecția 19), poziționale sau cu nume;
2. le transmite mai departe neschimbate: `functie(*args, **kwargs)`;
3. **întoarce rezultatul** funcției originale. Fără `return rezultat`, funcția decorată ar întoarce mereu `None`.

`!r` din f-string (lecția 26) afișează valoarea cu `repr()`, adică stringurile apar cu ghilimele.

### Sintaxa @

În loc de `imprumuta = jurnal(imprumuta)` după definiție, scrii decoratorul deasupra:

```python
def jurnal(functie):
    def impachetata(*args, **kwargs):
        print(f"[jurnal] {functie.__name__}{args}")
        return functie(*args, **kwargs)
    return impachetata


@jurnal
def returneaza(titlu):
    return f"{titlu} e din nou pe raft"


@jurnal
def cauta(autor):
    return ["Ion", "Pădurea spânzuraților"] if autor == "Rebreanu" else []


print(returneaza("Maitreyi"))
print(cauta("Rebreanu"))
```

```text
[jurnal] returneaza('Maitreyi',)
Maitreyi e din nou pe raft
[jurnal] cauta('Rebreanu',)
['Ion', 'Pădurea spânzuraților']
```

Același decorator, aplicat pe două funcții diferite, fără nicio modificare în corpul lor. (`('Maitreyi',)` are virgulă pentru că `args` e un tuplu cu un element, lecția 13.)

### functools.wraps: păstrarea identității funcției

Funcția decorată e, de fapt, `impachetata`. De aceea și-a pierdut numele și docstring-ul (lecția 22):

```python
def jurnal(functie):
    def impachetata(*args, **kwargs):
        return functie(*args, **kwargs)
    return impachetata


@jurnal
def imprumuta(titlu):
    """Împrumută o carte."""


print(imprumuta.__name__, imprumuta.__doc__)
```

```text
impachetata None
```

Pentru unelte de depanare și pentru mesajele de eroare, care afișează numele funcțiilor, asta e o problemă. Soluția e decoratorul `functools.wraps`, pus pe funcția interioară: copiază numele, docstring-ul și celelalte informații ale funcției originale.

```python
from functools import wraps


def jurnal(functie):
    @wraps(functie)
    def impachetata(*args, **kwargs):
        return functie(*args, **kwargs)
    return impachetata


@jurnal
def imprumuta(titlu):
    """Împrumută o carte."""


print(imprumuta.__name__, imprumuta.__doc__)
```

```text
imprumuta Împrumută o carte.
```

Regula practică: **orice decorator pe care îl scrii are `@wraps(functie)`** pe funcția interioară.

### Decoratori cu argumente

Uneori decoratorul are nevoie de setări: `@repeta(3)`, `@necesita_rol("bibliotecar")`. Pentru asta ai nevoie de încă un nivel: o funcție care primește setările și **întoarce decoratorul**.

```python
from functools import wraps


def repeta(de_cate_ori):
    def decorator(functie):
        @wraps(functie)
        def impachetata(*args, **kwargs):
            for _ in range(de_cate_ori):
                rezultat = functie(*args, **kwargs)
            return rezultat
        return impachetata
    return decorator


@repeta(3)
def suna(cititor):
    print(f"Sun la {cititor}...")


suna("Mihai")
```

```text
Sun la Mihai...
Sun la Mihai...
Sun la Mihai...
```

Citește `@repeta(3)` în doi pași: întâi se apelează `repeta(3)`, care întoarce `decorator`; apoi `decorator` e aplicat pe `suna`, ca un decorator obișnuit.

### Mai mulți decoratori pe aceeași funcție

Decoratorii se aplică **de jos în sus**: cel mai apropiat de `def` împachetează primul, iar cel de sus împachetează rezultatul.

```python
from functools import wraps


def cu_litere_mari(functie):
    @wraps(functie)
    def impachetata(*args, **kwargs):
        return functie(*args, **kwargs).upper()
    return impachetata


def cu_ghilimele(functie):
    @wraps(functie)
    def impachetata(*args, **kwargs):
        return f"„{functie(*args, **kwargs)}”"
    return impachetata


@cu_ghilimele
@cu_litere_mari
def titlu_carte():
    return "Enigma Otiliei"


print(titlu_carte())
```

```text
„ENIGMA OTILIEI”
```

E echivalent cu `titlu_carte = cu_ghilimele(cu_litere_mari(titlu_carte))`. Contează ordinea: dacă le-ai inversa, `upper()` ar fi aplicat și pe ghilimele (care nu se schimbă), dar în alte cazuri rezultatul poate fi complet diferit.

### Un exemplu clasic: măsurarea timpului

Un decorator care afișează cât a durat o funcție:

<!-- nu-rula -->
```python
import time
from functools import wraps


def cronometreaza(functie):
    @wraps(functie)
    def impachetata(*args, **kwargs):
        inceput = time.perf_counter()
        rezultat = functie(*args, **kwargs)
        durata = time.perf_counter() - inceput
        print(f"{functie.__name__} a durat {durata:.4f} secunde")
        return rezultat
    return impachetata


@cronometreaza
def numara_cuvinte(text):
    return len(text.split())


numara_cuvinte("Ana are mere " * 100_000)
```

`time.perf_counter()` dă un moment de timp foarte precis; diferența dintre două momente e durata. Output-ul arată de forma `numara_cuvinte a durat 0.0123 secunde`, iar numărul diferă la fiecare rulare, în funcție de calculator.

### Ce se întâmplă „pe dedesubt”: decoratorul rulează o singură dată, la definire

Decoratorul se execută **când e definită funcția**, nu când e apelată. La apeluri rulează doar funcția împachetată.

```python
from functools import wraps


def inregistreaza(functie):
    print(f"(înregistrez {functie.__name__})")

    @wraps(functie)
    def impachetata(*args, **kwargs):
        return functie(*args, **kwargs)
    return impachetata


print("înainte de def")


@inregistreaza
def raport():
    return "raport gata"


print("după def")
print(raport())
print(raport())
```

```text
înainte de def
(înregistrez raport)
după def
raport gata
raport gata
```

Pe asta se bazează multe framework-uri: un decorator poate **înregistra** funcția undeva (de exemplu, într-un dicționar de comenzi sau de rute URL) chiar în momentul definirii. Codul din afara lui `impachetata` rulează o dată; codul din interior, la fiecare apel.

## Exemplu complet

Biblioteca primește trei decoratori: unul care scrie în jurnal fiecare operație, unul care verifică dacă cititorul are permisul activ (ca `@login_required` din Django) și unul care numără apelurile.

<!-- fisier: biblioteca.py -->
```python
from functools import wraps

PERMISE_ACTIVE = {"Ana Popescu", "Mihai Ionescu"}
JURNAL = []


def in_jurnal(functie):
    @wraps(functie)
    def impachetata(*args, **kwargs):
        rezultat = functie(*args, **kwargs)
        JURNAL.append(f"{functie.__name__}{args} -> {rezultat}")
        return rezultat
    return impachetata


def necesita_permis(functie):
    """Primul argument al funcției trebuie să fie cititorul."""
    @wraps(functie)
    def impachetata(cititor, *args, **kwargs):
        if cititor not in PERMISE_ACTIVE:
            raise PermissionError(f"{cititor} nu are permis activ")
        return functie(cititor, *args, **kwargs)
    return impachetata


def numara_apeluri(functie):
    @wraps(functie)
    def impachetata(*args, **kwargs):
        impachetata.apeluri += 1
        return functie(*args, **kwargs)
    impachetata.apeluri = 0
    return impachetata


@numara_apeluri
@in_jurnal
@necesita_permis
def imprumuta(cititor, titlu):
    return f"{titlu} împrumutată de {cititor}"


@in_jurnal
def cauta(titlu):
    return titlu in {"Ion", "Maitreyi", "Baltagul"}


print(imprumuta("Ana Popescu", "Ion"))
print(cauta("Moromeții"))
print(imprumuta("Mihai Ionescu", "Maitreyi"))

try:
    imprumuta("Radu Pop", "Baltagul")
except PermissionError as eroare:
    print("Refuzat:", eroare)

print(f"\nimprumuta a fost apelată de {imprumuta.apeluri} ori")
print("Jurnal:")
for intrare in JURNAL:
    print(" ", intrare)
```

```text
Ion împrumutată de Ana Popescu
False
Maitreyi împrumutată de Mihai Ionescu
Refuzat: Radu Pop nu are permis activ

imprumuta a fost apelată de 3 ori
Jurnal:
  imprumuta('Ana Popescu', 'Ion') -> Ion împrumutată de Ana Popescu
  cauta('Moromeții',) -> False
  imprumuta('Mihai Ionescu', 'Maitreyi') -> Maitreyi împrumutată de Mihai Ionescu
```

Observă:
- `imprumuta` nu conține nicio verificare de permis și nicio scriere în jurnal: logica ei a rămas un singur rând;
- încercarea lui Radu a fost **numărată** (`@numara_apeluri` e cel mai de sus, deci rulează primul), dar **nu apare în jurnal**: `@necesita_permis` a ridicat excepția înainte ca `@in_jurnal` să ajungă la `JURNAL.append`. Ordinea decoratorilor schimbă comportamentul;
- `impachetata.apeluri` e un atribut pus direct pe funcție: funcțiile sunt obiecte (lecția 21) și pot avea atribute.

## Greșeli frecvente

### 1. Funcția împachetată nu întoarce rezultatul

```python
def jurnal(functie):
    def impachetata(*args, **kwargs):
        print(f"apelez {functie.__name__}")
        functie(*args, **kwargs)
    return impachetata


@jurnal
def numar_carti():
    return 120


print(numar_carti())
```

```text
apelez numar_carti
None
```

Funcția originală a întors 120, dar `impachetata` nu l-a dat mai departe, așa că a întors implicit `None` (lecția 18). Scrie mereu `return functie(*args, **kwargs)` sau salvează rezultatul și întoarce-l la final.

### 2. Funcția împachetată nu primește argumente

<!-- fisier: decorator.py -->
```python
def jurnal(functie):
    def impachetata():
        print("apel")
        return functie()
    return impachetata


@jurnal
def cauta(titlu):
    return titlu


cauta("Ion")
```

```text
Traceback (most recent call last):
  File "decorator.py", line 13, in <module>
    cauta("Ion")
TypeError: jurnal.<locals>.impachetata() takes 0 positional arguments but 1 was given
```

Numele din mesaj, `jurnal.<locals>.impachetata`, arată că eroarea vine din funcția interioară a decoratorului, nu din `cauta`. Folosește `*args, **kwargs` atât la primire, cât și la transmitere.

### 3. Paranteze la un decorator fără argumente

<!-- fisier: decorator.py -->
```python
from functools import wraps


def jurnal(functie):
    @wraps(functie)
    def impachetata(*args, **kwargs):
        return functie(*args, **kwargs)
    return impachetata


@jurnal()
def cauta(titlu):
    return titlu
```

```text
Traceback (most recent call last):
  File "decorator.py", line 11, in <module>
    @jurnal()
     ^^^^^^^^
TypeError: jurnal() missing 1 required positional argument: 'functie'
```

`@jurnal()` înseamnă „apelează `jurnal` fără argumente, iar rezultatul e decoratorul”. Dar `jurnal` așteaptă funcția. Parantezele se pun doar la decoratorii cu argumente, ca `@repeta(3)`.

### 4. Lipsesc parantezele la un decorator cu argumente

<!-- fisier: decorator.py -->
```python
from functools import wraps


def repeta(de_cate_ori):
    def decorator(functie):
        @wraps(functie)
        def impachetata(*args, **kwargs):
            for _ in range(de_cate_ori):
                functie(*args, **kwargs)
        return impachetata
    return decorator


@repeta
def suna():
    print("Sun...")


suna()
```

```text
Traceback (most recent call last):
  File "decorator.py", line 19, in <module>
    suna()
TypeError: repeta.<locals>.decorator() missing 1 required positional argument: 'functie'
```

Fără paranteze, Python a făcut `suna = repeta(suna)`: `de_cate_ori` a primit funcția, iar `suna` a devenit `decorator`, care așteaptă o funcție. Eroarea apare abia la apel, departe de cauza ei. Corect: `@repeta(3)`.

### 5. Uitarea lui @wraps

```python
def jurnal(functie):
    def impachetata(*args, **kwargs):
        return functie(*args, **kwargs)
    return impachetata


@jurnal
def imprumuta():
    pass


@jurnal
def returneaza():
    pass


print(imprumuta.__name__, returneaza.__name__)
```

```text
impachetata impachetata
```

Ambele funcții par să se numească la fel. Pentru jurnale, mesaje de eroare și unelte de depanare sau testare, care afișează numele funcțiilor, asta produce confuzii greu de depistat. Pune `@wraps(functie)` pe funcția interioară.

## Exercițiu

În `capitole/38-decoratori/decoratori.py`:

1. scrie decoratorul `valideaza_titlu`, care verifică dacă primul argument al funcției e un text nevid (după `strip()`); dacă nu e, ridică `ValueError("Titlul nu poate fi gol")`, iar dacă e, apelează funcția cu titlul curățat;
2. scrie decoratorul cu argument `limita_imprumuturi(maxim)`, care ține minte, într-un dicționar pus ca atribut pe funcția împachetată, câte cărți a împrumutat fiecare cititor (al doilea argument) și ridică `PermissionError` când un cititor depășește `maxim`;
3. scrie decoratorul `memoreaza`, care ține un dicționar `argumente -> rezultat` și, dacă funcția a mai fost apelată cu aceleași argumente poziționale, întoarce rezultatul salvat fără s-o mai apeleze; testează-l pe o funcție care afișează „calculez...” înainte de a întoarce rezultatul, ca să vezi când rulează cu adevărat;
4. aplică primii doi decoratori pe o funcție `imprumuta(titlu, cititor)` și testează: un titlu gol, trei împrumuturi permise pentru Ana și un al patrulea refuzat (cu `maxim=3`), prinzând erorile cu `try / except`;
5. folosește `@wraps` peste tot și afișează `imprumuta.__name__` ca să verifici.

## Pe scurt

- Un decorator e o funcție care primește o funcție și întoarce alta, care o împachetează; `@decorator` deasupra lui `def` înseamnă `f = decorator(f)`.
- Funcția interioară primește `*args, **kwargs`, apelează funcția originală cu ele și **întoarce rezultatul**.
- Pune mereu `@functools.wraps(functie)` pe funcția interioară, ca să păstreze numele și docstring-ul.
- Un decorator cu argumente are trei niveluri: `repeta(3)` întoarce decoratorul, care întoarce funcția împachetată.
- Mai mulți decoratori se aplică de jos în sus, iar ordinea lor contează.
- Decoratorul rulează o dată, la definire; funcția împachetată rulează la fiecare apel. Exemple pe care le vei folosi: `@property`, `@dataclass`, `@login_required`.
