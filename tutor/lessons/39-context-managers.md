## Ce este

Un **context manager** este un obiect care știe să facă ceva **la intrarea** într-un bloc de cod și ceva **la ieșirea** din el, garantat, chiar dacă blocul se termină cu o eroare. Îl folosești cu instrucțiunea **`with`**, pe care o știi de la fișiere (lecția 27):

```python
with open("catalog.txt", "w", encoding="utf-8") as fisier:
    fisier.write("Ion\nMaitreyi\n")
print(fisier.closed)
```

```text
True
```

`open()` întoarce un context manager. La intrarea în `with`, fișierul e deschis și legat de numele `fisier`. La ieșire, indiferent cum se iese, fișierul e **închis automat**.

Poți scrie propriii context manageri, fie ca o clasă cu metodele speciale `__enter__` și `__exit__`, fie, mai simplu, ca o funcție generator cu decoratorul `@contextmanager`.

## De ce contează

Multe resurse trebuie „eliberate” după folosire: un fișier deschis trebuie închis, o conexiune la baza de date trebuie închisă, un lacăt trebuie deblocat, o modificare temporară (de exemplu, folderul de lucru) trebuie anulată. Dacă uiți, sau dacă o eroare sare peste codul de eliberare, apar probleme greu de depistat: fișiere neterminate, conexiuni rămase deschise, date blocate.

`with` mută responsabilitatea de pe umerii tăi pe obiect: tu scrii doar ce faci **în** bloc, iar curățenia se face singură. În Django, de exemplu, `transaction.atomic()` e un context manager: tot ce faci în blocul `with` se salvează în baza de date împreună sau, dacă apare o eroare, nu se salvează nimic.

## Cum funcționează

### Problema pe care o rezolvă

Fără `with`, garanția se obține cu `try / finally` (lecția 24):

```python
fisier = open("catalog.txt", "w", encoding="utf-8")
try:
    fisier.write("Ion\n")
    fisier.write("Maitreyi\n")
finally:
    fisier.close()
print(fisier.closed)
```

```text
True
```

`finally` rulează și când blocul `try` se termină normal, și când apare o excepție. E corect, dar trebuie scris de fiecare dată, iar dacă îl uiți o singură dată, ai o resursă rămasă deschisă. `with` face exact acest `try / finally`, ascuns în obiect.

### Protocolul: __enter__ și __exit__

Un obiect e context manager dacă are două metode speciale (lecția 35):
- `__enter__(self)` rulează la intrarea în `with`; ce **întoarce** ea primește numele de după `as`;
- `__exit__(self, tip, eroare, traceback)` rulează la ieșire, mereu. Dacă blocul s-a terminat normal, cele trei argumente sunt `None`; dacă a apărut o excepție, ele descriu excepția.

```python
class Raft:
    def __init__(self, nume):
        self.nume = nume
        self.carti = []

    def __enter__(self):
        print(f"[deschid raftul {self.nume}]")
        return self

    def __exit__(self, tip, eroare, traceback):
        print(f"[închid raftul {self.nume}: {len(self.carti)} cărți]")
        return False


with Raft("A") as raft:
    raft.carti.append("Ion")
    raft.carti.append("Baltagul")
    print("lucrez în bloc")
print("după with")
```

```text
[deschid raftul A]
lucrez în bloc
[închid raftul A: 2 cărți]
după with
```

`return self` din `__enter__` face ca `raft` să fie chiar obiectul `Raft`. Valoarea întoarsă de `__exit__` contează doar când apare o excepție (vezi mai jos); `False` înseamnă „las excepția să meargă mai departe”.

### Ce se întâmplă când apare o eroare

`__exit__` rulează și dacă blocul se oprește cu o excepție. Apoi, dacă `__exit__` nu întoarce `True`, excepția continuă normal, ca și cum `with` n-ar fi existat:

```python
class Raft:
    def __init__(self, nume):
        self.nume = nume

    def __enter__(self):
        print(f"[deschid raftul {self.nume}]")
        return self

    def __exit__(self, tip, eroare, traceback):
        if tip is not None:
            print(f"[eroare în bloc: {tip.__name__}: {eroare}]")
        print(f"[închid raftul {self.nume}]")
        return False


try:
    with Raft("B"):
        print("caut cartea...")
        raise LookupError("cartea nu e pe raft")
        print("nu ajung aici")
except LookupError as e:
    print("prins în afara lui with:", e)
```

```text
[deschid raftul B]
caut cartea...
[eroare în bloc: LookupError: cartea nu e pe raft]
[închid raftul B]
prins în afara lui with: cartea nu e pe raft
```

Dacă `__exit__` ar întoarce `True`, excepția ar fi **înghițită**: programul ar continua după `with` ca și cum nimic nu s-ar fi întâmplat. Fă asta doar intenționat, pentru excepții anume (vezi greșeala 4).

### @contextmanager: un context manager dintr-un generator

Scrierea unei clase întregi e mult pentru ceva simplu. Modulul `contextlib` are decoratorul `@contextmanager` (decoratorii sunt la lecția 38), care transformă o funcție generator (lecția 37) într-un context manager:
- codul de **dinainte** de `yield` e intrarea (ca `__enter__`);
- valoarea dată de `yield` ajunge la `as`;
- codul de **după** `yield` e ieșirea (ca `__exit__`).

```python
from contextlib import contextmanager


@contextmanager
def raft(nume):
    print(f"[deschid raftul {nume}]")
    carti = []
    try:
        yield carti
    finally:
        print(f"[închid raftul {nume}: {len(carti)} cărți]")


with raft("C") as carti:
    carti.append("Maitreyi")
    carti.append("Moromeții")
print("după with")
```

```text
[deschid raftul C]
[închid raftul C: 2 cărți]
după with
```

`try / finally` din jurul lui `yield` e esențial: dacă blocul `with` aruncă o excepție, ea apare **în generator, exact la `yield`**. Fără `finally`, codul de ieșire n-ar mai rula (vezi greșeala 3).

### Mai mulți context manageri deodată

Poți deschide mai multe resurse în același `with`, separate prin virgulă. Când rândul devine prea lung, le pui între paranteze, câte una pe rând (posibil din Python 3.10). Se închid în ordine inversă deschiderii:

```python
with open("intrare.txt", "w", encoding="utf-8") as f:
    f.write("ion\nmaitreyi\n")

with (
    open("intrare.txt", encoding="utf-8") as sursa,
    open("iesire.txt", "w", encoding="utf-8") as destinatie,
):
    for linie in sursa:
        destinatie.write(linie.title())

with open("iesire.txt", encoding="utf-8") as f:
    print(f.read(), end="")
```

```text
Ion
Maitreyi
```

### Context manageri gata făcuți

Biblioteca standard are mulți. Doi utili din `contextlib`:
- `suppress(TipEroare)` ignoră intenționat o anumită excepție în bloc;
- `redirect_stdout(fisier)` trimite tot ce afișează `print()` în alt loc, de exemplu într-un fișier.

```python
from contextlib import suppress, redirect_stdout
from pathlib import Path

with suppress(FileNotFoundError):
    Path("nu_exista.txt").unlink()  # unlink() șterge fișierul
print("ștergerea a fost încercată, fără eroare")

with open("raport.txt", "w", encoding="utf-8") as f:
    with redirect_stdout(f):
        print("Raport: 3 cărți împrumutate")

with open("raport.txt", encoding="utf-8") as f:
    print("în fișier:", f.read().strip())
```

```text
ștergerea a fost încercată, fără eroare
în fișier: Raport: 3 cărți împrumutate
```

`suppress(FileNotFoundError)` e echivalentul scurt pentru `try: ... except FileNotFoundError: pass`.

### Ce se întâmplă „pe dedesubt”: ce face with, pas cu pas

Instrucțiunea:

<!-- nu-rula -->
```python
with expresie as nume:
    bloc
```

face, aproximativ:

<!-- nu-rula -->
```python
manager = expresie
nume = manager.__enter__()
try:
    bloc
except BaseException as e:
    if not manager.__exit__(type(e), e, e.__traceback__):
        raise
else:
    manager.__exit__(None, None, None)
```

Trei lucruri reies de aici:
- `as nume` primește ce întoarce `__enter__`, **nu** obiectul `manager` (de obicei sunt același lucru, pentru că `__enter__` face `return self`, dar nu e obligatoriu);
- `__exit__` se apelează pe ambele drumuri, cu sau fără eroare;
- excepția e ridicată din nou (`raise`) doar dacă `__exit__` nu întoarce o valoare adevărată.

Variabila de după `as` **rămâne** după bloc (așa am putut verifica `fisier.closed` la început), dar resursa ei a fost deja eliberată.

## Exemplu complet

O sesiune de împrumut la bibliotecă: cititorul ia mai multe cărți, iar dacă apare o problemă în mijlocul sesiunii, **toate** împrumuturile din sesiune se anulează, ca stocul să nu rămână pe jumătate modificat. Ideea e aceeași cu `transaction.atomic()` din Django.

<!-- fisier: sesiune.py -->
```python
from contextlib import contextmanager

stoc = {"Ion": 2, "Maitreyi": 1, "Baltagul": 1}


@contextmanager
def sesiune_imprumut(cititor):
    copie = dict(stoc)          # starea de dinainte, pentru anulare
    imprumutate = []
    print(f"--- Sesiune pentru {cititor} ---")
    try:
        yield imprumutate
    except Exception as eroare:
        stoc.clear()
        stoc.update(copie)      # anulăm tot ce s-a făcut în sesiune
        print(f"Sesiune anulată ({eroare}); stocul a fost refăcut.")
    else:
        print(f"Sesiune încheiată: {', '.join(imprumutate) or 'nimic'}.")


def imprumuta(titlu, lista):
    if stoc.get(titlu, 0) == 0:
        raise LookupError(f"„{titlu}” nu e disponibilă")
    stoc[titlu] -= 1
    lista.append(titlu)


with sesiune_imprumut("Ana Popescu") as carti:
    imprumuta("Ion", carti)
    imprumuta("Maitreyi", carti)
print("Stoc:", stoc)

with sesiune_imprumut("Mihai Ionescu") as carti:
    imprumuta("Ion", carti)
    imprumuta("Maitreyi", carti)    # nu mai e: toată sesiunea se anulează
    imprumuta("Baltagul", carti)
print("Stoc:", stoc)
```

```text
--- Sesiune pentru Ana Popescu ---
Sesiune încheiată: Ion, Maitreyi.
Stoc: {'Ion': 1, 'Maitreyi': 0, 'Baltagul': 1}
--- Sesiune pentru Mihai Ionescu ---
Sesiune anulată („Maitreyi” nu e disponibilă); stocul a fost refăcut.
Stoc: {'Ion': 1, 'Maitreyi': 0, 'Baltagul': 1}
```

Observă:
- în sesiunea lui Mihai, „Ion” fusese deja scăzut din stoc când a apărut eroarea; anularea l-a pus la loc, așa că stocul e exact cel de dinainte de sesiune;
- excepția a fost **prinsă în context manager** (`except` în jurul lui `yield`) și nu a mai ajuns în afară, de aceea programul a continuat. E o alegere de design: aici o sesiune eșuată e un caz normal. Dacă vrei ca apelantul să afle de eroare, pune `raise` la finalul lui `except`;
- `else` de la `try` rulează doar când blocul `with` s-a terminat fără eroare.

## Greșeli frecvente

### 1. Folosirea resursei după ce blocul with s-a terminat

<!-- fisier: cm.py -->
```python
with open("catalog.txt", "w", encoding="utf-8") as fisier:
    fisier.write("Ion\n")
fisier.write("Maitreyi\n")
```

```text
Traceback (most recent call last):
  File "cm.py", line 3, in <module>
    fisier.write("Maitreyi\n")
ValueError: I/O operation on closed file.
```

Variabila `fisier` există încă, dar fișierul a fost închis la ieșirea din `with`. Tot ce lucrează cu resursa trebuie să fie **în** bloc (indentat).

### 2. __enter__ care nu întoarce nimic

<!-- fisier: cm.py -->
```python
class Raft:
    def __init__(self):
        self.carti = []

    def __enter__(self):
        print("[deschid]")

    def __exit__(self, tip, eroare, traceback):
        print("[închid]")


with Raft() as raft:
    raft.carti.append("Ion")
```

```text
[deschid]
[închid]
Traceback (most recent call last):
  File "cm.py", line 13, in <module>
    raft.carti.append("Ion")
    ^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'carti'
```

`as raft` primește valoarea întoarsă de `__enter__`, iar o funcție fără `return` întoarce `None`. Observă că `[închid]` s-a afișat **înainte** de traceback: `__exit__` a rulat chiar și la eroare. Adaugă `return self` în `__enter__`.

### 3. @contextmanager fără try / finally

```python
from contextlib import contextmanager


@contextmanager
def raft(nume):
    print(f"[deschid {nume}]")
    yield
    print(f"[închid {nume}]")


try:
    with raft("D"):
        raise LookupError("carte lipsă")
except LookupError:
    print("eroare prinsă")
```

```text
[deschid D]
eroare prinsă
```

`[închid D]` nu s-a afișat: excepția a apărut la `yield` și a ieșit din generator înainte de codul de după el. Exact garanția pentru care folosești `with` s-a pierdut. Pune `yield` într-un `try` și codul de ieșire în `finally`, ca în lecție.

### 4. __exit__ care întoarce True și ascunde erorile

```python
class Liniste:
    def __enter__(self):
        return self

    def __exit__(self, tip, eroare, traceback):
        return True


with Liniste():
    stoc = {"Ion": 2}
    print(stoc["Maitreyi"])
print("programul continuă, ca și cum totul ar fi fost bine")
```

```text
programul continuă, ca și cum totul ar fi fost bine
```

`KeyError`-ul a dispărut fără urmă: `return True` înseamnă „am tratat eu excepția”. Un astfel de context manager ascunde orice greșeală din bloc. Întoarce `True` doar pentru excepții anume, pe care chiar vrei să le ignori (de exemplu, `return tip is FileNotFoundError`), sau folosește `contextlib.suppress`.

### 5. Funcție generator fără @contextmanager

<!-- fisier: cm.py -->
```python
def raft(nume):
    print(f"[deschid {nume}]")
    try:
        yield nume
    finally:
        print(f"[închid {nume}]")


with raft("E") as r:
    print(r)
```

```text
Traceback (most recent call last):
  File "cm.py", line 9, in <module>
    with raft("E") as r:
TypeError: 'generator' object does not support the context manager protocol
```

Fără decorator, `raft("E")` e doar un generator, care nu are `__enter__` și `__exit__`. Pune `@contextmanager` deasupra lui `def` (și `from contextlib import contextmanager` sus în fișier).

## Exercițiu

În `capitole/39-context-managers/context_managers.py`:

1. scrie clasa `Cronometru`, un context manager care, la intrare, ține minte momentul curent cu `time.perf_counter()` și, la ieșire, salvează durata în atributul `self.durata`; după bloc, afișează durata rotunjită la 3 zecimale (valoarea va diferi la fiecare rulare, e normal);
2. scrie, cu `@contextmanager`, funcția `fisier_sigur(cale)`, care deschide pentru scriere fișierul temporar `cale + ".tmp"` și dă blocului (`yield`) fișierul deschis. După bloc, **închide** fișierul și abia apoi, **doar dacă blocul s-a terminat fără eroare**, îl redenumește în `cale` cu `os.replace(sursa, destinatie)` (din modulul `os`: redenumește fișierul și îl înlocuiește pe cel vechi, dacă există; pe Windows nu merge pe un fișier încă deschis). Dacă apare o eroare, închide și șterge fișierul temporar (`Path(cale + ".tmp").unlink()`) și lasă excepția să meargă mai departe (`raise`). Așa, fișierul final nu rămâne niciodată scris pe jumătate;
3. testează `fisier_sigur` de două ori: o dată cu un bloc care scrie trei titluri de cărți, o dată cu un bloc care scrie un titlu și apoi ridică `ValueError` (prinsă cu `try / except` în afara lui `with`); după fiecare test, afișează dacă există fișierul final și dacă există fișierul `.tmp` (`Path(cale).exists()`, lecția 27);
4. folosește în același `with` atât `Cronometru()`, cât și `fisier_sigur(...)`, ca să măsori cât durează scrierea a 10 000 de rânduri;
5. în comentarii, explică în 2–3 propoziții ce s-ar întâmpla cu fișierul final dacă ai scrie direct în el și programul s-ar opri cu o eroare la jumătate.

## Pe scurt

- `with obiect as nume:` rulează codul de intrare, blocul și apoi, garantat, codul de ieșire, chiar și la eroare.
- Un context manager are `__enter__` (ce întoarce ajunge la `as`) și `__exit__(tip, eroare, traceback)`, apelat mereu la ieșire.
- Dacă `__exit__` întoarce `True`, excepția din bloc e înghițită; altfel, merge mai departe.
- `@contextmanager` transformă o funcție generator într-un context manager: înainte de `yield` e intrarea, după `yield` (în `finally`) e ieșirea.
- Mai multe resurse se deschid în același `with`, separate prin virgulă; `contextlib.suppress` și `redirect_stdout` sunt context manageri gata făcuți.
- Resursa nu mai poate fi folosită după bloc, iar `__enter__` trebuie să întoarcă obiectul (de obicei `self`).
