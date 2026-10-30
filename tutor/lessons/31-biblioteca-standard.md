## Ce este

**Biblioteca standard** e colecția de module care vin odată cu Python: nu instalezi nimic, doar le imporți (lecția 29). Python are sute de astfel de module. Lecția asta le prezintă pe cele pe care le vei folosi cel mai des:
- **`datetime`**: date calendaristice, ore, durate;
- **`random`**: numere și alegeri aleatoare;
- **`math`**: funcții matematice;
- **`os`** și **`pathlib`**: sistemul de fișiere și variabilele de mediu;
- **`collections`**: colecții specializate, ca `Counter` și `defaultdict`.

```python
from datetime import date
import math

azi = date(2026, 10, 29)
print(azi.year, azi.month, azi.day)
print(math.ceil(385.5 / 100), "bancnote de 100 de lei")
```

```text
2026 10 29
4 bancnote de 100 de lei
```

## De ce contează

Multe probleme pe care le-ai rezolva de mână au deja o soluție testată în biblioteca standard. Câte zile sunt până la o dată? Cum alegi un câștigător la întâmplare? Care e cuvântul cel mai des întâlnit într-un text? Fiecare are un răspuns de un rând.

Regula pe care o folosesc programatorii cu experiență: **înainte să scrii ceva general, verifică dacă există deja în biblioteca standard**. Codul de acolo e corect, rapid și cunoscut de toată lumea. În plus, aproape toate modulele de aici apar și în Django: datele calendaristice în modele (lecția 50), variabilele de mediu în `settings.py` (lecția 46), căile cu `pathlib` chiar în primele rânduri ale oricărui proiect nou.

## Cum funcționează

### datetime: date, ore, durate

Modulul `datetime` are trei tipuri principale: `date` (o zi), `datetime` (o zi și o oră) și `timedelta` (o durată).

```python
from datetime import date, datetime, timedelta

ziua_ana = date(2026, 10, 29)
print(ziua_ana)
print(ziua_ana.isoformat())
print(ziua_ana.weekday())          # 0 = luni, ..., 6 = duminică

termen = ziua_ana + timedelta(days=30)
print("Peste 30 de zile:", termen)

craciun = date(2026, 12, 25)
print("Până la Crăciun:", (craciun - ziua_ana).days, "de zile")

intalnire = datetime(2026, 10, 29, 18, 30)
print(intalnire, "->", intalnire + timedelta(hours=2, minutes=15))
```

```text
2026-10-29
2026-10-29
3
Peste 30 de zile: 2026-11-28
Până la Crăciun: 57 de zile
2026-10-29 18:30:00 -> 2026-10-29 20:45:00
```

Operațiile se fac ca la numere: o dată plus o durată dă o dată, iar diferența dintre două date dă o durată (`timedelta`), din care iei numărul de zile cu `.days`. Datele se pot și compara: `craciun > ziua_ana` e `True`.

**Transformarea între date și text** se face cu `fromisoformat()` și `strptime()` (text → dată), respectiv `isoformat()` și `strftime()` (dată → text):

```python
from datetime import date, datetime

data = date.fromisoformat("2026-10-29")       # formatul AAAA-LL-ZZ
print(data.strftime("%d.%m.%Y"))

din_text = datetime.strptime("29.10.2026 18:30", "%d.%m.%Y %H:%M")
print(din_text)
print(f"{din_text:%H:%M, %d.%m}")             # formatul merge și în f-string
```

```text
29.10.2026
2026-10-29 18:30:00
18:30, 29.10
```

Codurile cele mai folosite: `%d` ziua, `%m` luna, `%Y` anul cu 4 cifre, `%H` ora (0–23), `%M` minutul. Formatul ISO, `AAAA-LL-ZZ`, e cel de folosit când **salvezi** date (în JSON sau CSV, lecția 28): e neambiguu și se sortează corect chiar și ca text.

Numele zilelor și lunilor (`%A`, `%B`) sunt în engleză. Pentru română, cel mai simplu e să ai propria listă:

```python
from datetime import date

ZILE = ["luni", "marți", "miercuri", "joi", "vineri", "sâmbătă", "duminică"]
print(ZILE[date(2026, 10, 29).weekday()])
```

```text
joi
```

Data și ora curentă se obțin cu `date.today()` și `datetime.now()`:

<!-- nu-rula -->
```python
from datetime import date, datetime

print(date.today())     # ziua de azi, de exemplu 2026-10-29
print(datetime.now())   # cu oră, minute, secunde și microsecunde
```

Rezultatul depinde, evident, de momentul în care rulezi.

### random: numere aleatoare

```python
import random

random.seed(42)                                   # vezi explicația de mai jos
print(random.randint(1, 6), random.randint(1, 6), random.randint(1, 6))
print(random.choice(["Ana", "Mihai", "Ioana", "Radu"]))
print(round(random.random(), 4))

cartonase = ["liste", "tupluri", "dicționare", "seturi", "comprehensions"]
random.shuffle(cartonase)
print(cartonase)
print(random.sample(range(1, 50), 6))
print(round(random.uniform(10, 20), 2))
```

```text
6 1 1
Ioana
0.2449
['comprehensions', 'seturi', 'dicționare', 'liste', 'tupluri']
[38, 28, 3, 2, 6, 14]
12.33
```

- `randint(a, b)`: un întreg între `a` și `b`, **inclusiv** `b` (spre deosebire de `range`);
- `choice(secventa)`: un element la întâmplare;
- `random()`: un `float` între 0 (inclusiv) și 1 (exclusiv); `uniform(a, b)`: un `float` între `a` și `b`;
- `shuffle(lista)`: amestecă lista **pe loc** (și întoarce `None`, ca `sort()`, lecția 12);
- `sample(secventa, k)`: `k` elemente diferite, ca la o extragere de loto.

**`random.seed(42)`** fixează punctul de pornire al generatorului. Numerele „aleatoare” ale calculatorului sunt calculate dintr-o valoare inițială. Cu același seed, obții mereu aceeași secvență: de aceea output-ul de mai sus e același la fiecare rulare, iar tu vei vedea exact aceleași valori. E util la teste și la depanare. Fără `seed()`, Python pornește de la o valoare diferită la fiecare rulare. Asta e ce vrei în jocuri, cum e „ghicește numărul” din lecțiile 8–11:

<!-- nu-rula -->
```python
import random

numar_secret = random.randint(1, 100)   # altul la fiecare rulare
```

Pentru parole sau coduri de securitate nu folosi `random`, ci modulul `secrets`, făcut special pentru asta.

### math: funcții matematice

```python
import math

print(math.sqrt(2), math.pi)
print(math.ceil(4.1), math.floor(4.9))
print(math.isclose(0.1 + 0.2, 0.3))

total = 0
for _ in range(10):
    total += 0.1
print(total, math.fsum([0.1] * 10))
print(math.gcd(12, 18), math.factorial(5))
```

```text
1.4142135623730951 3.141592653589793
5 4
True
0.9999999999999999 1.0
6 120
```

- `ceil` rotunjește mereu **în sus**, `floor` mereu **în jos** (spre deosebire de `round`, lecția 3);
- `isclose(a, b)` e felul corect de a compara două `float`-uri (problema din lecția 7);
- `fsum` adună `float`-uri fără să acumuleze erorile de rotunjire, care apar când aduni pas cu pas, cu `+=`. (Din Python 3.12, și `sum()` adună `float`-urile cu aceeași grijă, deci `sum([0.1] * 10)` dă tot `1.0`.)
- `gcd` e cel mai mare divizor comun, iar `factorial(5)` = 1 × 2 × 3 × 4 × 5.

### os și pathlib: sistemul de fișiere și variabilele de mediu

Pentru căi și fișiere, folosește `pathlib` (lecția 27). Modulul `os` e mai vechi și face multe lucruri apropiate de sistemul de operare. Cel mai important pentru tine e accesul la **variabilele de mediu**, setări date programului din afara codului:

```python
import os

moneda = os.environ.get("JURNAL_MONEDA", "lei")
print("Moneda:", moneda)
print("Separatorul de căi pe acest sistem:", repr(os.sep))
```

```text
Moneda: lei
Separatorul de căi pe acest sistem: '/'
```

`os.environ` se comportă ca un dicționar (lecția 14), iar `get()` îți dă o valoare implicită dacă variabila nu există. Exact așa vei citi, la lecția 46, cheia secretă și setările bazei de date ale unei aplicații Django: din mediu, nu scrise în cod.

`os.getcwd()` dă folderul curent de lucru (cel de care depind căile relative, lecția 27), iar `Path.cwd()` face același lucru, dar întoarce un `Path`.

### collections: Counter și defaultdict

**`Counter`** numără elementele unei colecții. E tiparul de numărare din lecția 14, `d[x] = d.get(x, 0) + 1`, gata făcut, cu câteva metode în plus:

```python
from collections import Counter

categorii = ["cafea", "benzină", "cafea", "cărți", "cafea", "benzină"]
numarare = Counter(categorii)
print(numarare)
print(numarare["cafea"], numarare["cinema"])
print(numarare.most_common(2))

cuvinte = Counter("ana are mere ana are pere ana".split())
print(cuvinte.most_common(1))
```

```text
Counter({'cafea': 3, 'benzină': 2, 'cărți': 1})
3 0
[('cafea', 3), ('benzină', 2)]
[('ana', 3)]
```

Un `Counter` e un dicționar: are `items()`, `keys()` și tot restul. În plus, o cheie inexistentă dă `0`, nu `KeyError`, iar `most_common(n)` dă cele mai frecvente `n` elemente.

**`defaultdict`** e un dicționar care creează singur o valoare implicită când ceri o cheie inexistentă. Ideal pentru **grupare**:

```python
from collections import defaultdict

cheltuieli = [("2026-10", "cafea", 32), ("2026-10", "benzină", 250), ("2026-11", "cafea", 14.5)]
pe_luni = defaultdict(list)
for luna, categorie, suma in cheltuieli:
    pe_luni[luna].append(suma)          # lista se creează singură la prima folosire

for luna, sume in pe_luni.items():
    print(luna, sume, sum(sume))
```

```text
2026-10 [32, 250] 282
2026-11 [14.5] 14.5
```

Cu un dicționar obișnuit, ar fi trebuit să verifici de fiecare dată `if luna not in pe_luni: pe_luni[luna] = []`. `defaultdict(list)` creează lista goală automat; `defaultdict(int)` ar crea `0`, ca un `Counter`.

### Ce se întâmplă „pe dedesubt”: unde stau modulele standard

Majoritatea modulelor din biblioteca standard sunt fișiere `.py` obișnuite, într-un folder al instalării Python; câteva sunt scrise în C, pentru viteză. Le poți găsi chiar tu:

```python
import json
import random

print(json.__name__, random.__name__)
print(json.__file__.endswith("json/__init__.py"), random.__file__.endswith("random.py"))
```

```text
json random
True True
```

`json` e un pachet (un folder cu `__init__.py`), iar `random` e un singur fișier, `random.py`. Le poți deschide și citi: sunt scrise în Python, cu comentarii. Așa se explică și greșeala 5 din lecția 29: un `random.py` al tău, din folderul scriptului, e găsit **înaintea** acestuia.

Documentația completă a fiecărui modul e la [docs.python.org](https://docs.python.org/3/library/), în secțiunea „The Python Standard Library”.

## Exemplu complet

Statistica jurnalului de cheltuieli al Anei: cheltuielile sunt pe mai multe luni, cu date în format ISO, iar programul folosește toate modulele din lecție.

<!-- fisier: statistica.py -->
```python
import math
import random
from collections import Counter, defaultdict
from datetime import date, timedelta

ZILE = ["luni", "marți", "miercuri", "joi", "vineri", "sâmbătă", "duminică"]
BUGET_LUNAR = 1200

cheltuieli = [
    ("2026-10-03", "cafea", 14.5), ("2026-10-03", "cărți", 89),
    ("2026-10-10", "benzină", 250), ("2026-10-17", "cafea", 32),
    ("2026-10-24", "cinema", 45), ("2026-10-24", "cafea", 14.5),
    ("2026-10-29", "chirie", 900), ("2026-11-01", "cafea", 16),
]

pe_luni = defaultdict(float)
pe_zile_saptamana = Counter()
categorii = Counter()
for text_data, categorie, suma in cheltuieli:
    data = date.fromisoformat(text_data)
    pe_luni[f"{data:%Y-%m}"] += suma
    pe_zile_saptamana[ZILE[data.weekday()]] += 1
    categorii[categorie] += 1

for luna, total in pe_luni.items():
    procent = total / BUGET_LUNAR
    stare = "depășit!" if total > BUGET_LUNAR else "ok"
    print(f"{luna}: {total:8.2f} lei ({procent:.0%} din buget, {stare})")

zi, cate = pe_zile_saptamana.most_common(1)[0]
print(f"Ziua cu cele mai multe cheltuieli: {zi} ({cate})")
print("Cele mai dese categorii:", ", ".join(c for c, _ in categorii.most_common(2)))

ultima_chirie = max(date.fromisoformat(d) for d, c, _ in cheltuieli if c == "chirie")
urmatoarea_plata = ultima_chirie + timedelta(days=30)
zile = (urmatoarea_plata - ultima_chirie).days
print(f"Următoarea chirie: {urmatoarea_plata:%d.%m.%Y}, peste {zile} de zile")

economie = pe_luni["2026-10"] * 0.10
bancnote = math.ceil(economie / 50)
print(f"Ca să economisești 10%, pune deoparte {bancnote} bancnote de 50 de lei")

random.seed(7)
sfaturi = [
    "fă cafeaua acasă",
    "mergi pe jos o dată pe săptămână",
    "împrumută cărți de la bibliotecă",
]
print("Sfatul zilei:", random.choice(sfaturi))
```

```text
2026-10:  1345.00 lei (112% din buget, depășit!)
2026-11:    16.00 lei (1% din buget, ok)
Ziua cu cele mai multe cheltuieli: sâmbătă (6)
Cele mai dese categorii: cafea, cărți
Următoarea chirie: 28.11.2026, peste 30 de zile
Ca să economisești 10%, pune deoparte 3 bancnote de 50 de lei
Sfatul zilei: mergi pe jos o dată pe săptămână
```

Observă:
- `defaultdict(float)` pornește fiecare lună de la `0.0`, iar `Counter()` gol numără orice cheie nouă de la 0;
- `f"{data:%Y-%m}"` grupează pe luni folosind formatul datei direct în f-string;
- „următoarea chirie” e calculată de la data ultimei chirii plătite, plus 30 de zile; e un exemplu de calcul cu `timedelta`, nu o regulă de contabilitate;
- `random.seed(7)` face ca „sfatul zilei” să fie același la fiecare rulare a exemplului. Scoate rândul cu `seed`, ca sfatul să se schimbe.

## Greșeli frecvente

### 1. Modulul datetime și tipul datetime

<!-- fisier: data.py -->
```python
import datetime

print(datetime.now())
```

```text
Traceback (most recent call last):
  File "data.py", line 3, in <module>
    print(datetime.now())
          ^^^^^^^^^^^^
AttributeError: module 'datetime' has no attribute 'now'
```

Modulul `datetime` conține un tip care se numește tot `datetime`. Cu `import datetime`, scrii `datetime.datetime.now()`. Mai simplu: `from datetime import datetime`, apoi `datetime.now()`. Alege una dintre variante și folosește-o consecvent în tot proiectul.

### 2. Compararea unei date cu un text

<!-- fisier: data.py -->
```python
from datetime import date

termen = date(2026, 10, 29)
print(termen > "2026-10-01")
```

```text
Traceback (most recent call last):
  File "data.py", line 4, in <module>
    print(termen > "2026-10-01")
          ^^^^^^^^^^^^^^^^^^^^^
TypeError: '>' not supported between instances of 'datetime.date' and 'str'
```

O dată citită dintr-un fișier sau de la tastatură e text (lecțiile 6 și 27). Convertește-o întâi: `termen > date.fromisoformat("2026-10-01")`.

### 3. O dată care nu există

<!-- fisier: data.py -->
```python
from datetime import date

print(date(2026, 2, 30))
```

```text
Traceback (most recent call last):
  File "data.py", line 3, in <module>
    print(date(2026, 2, 30))
          ^^^^^^^^^^^^^^^^^
ValueError: day is out of range for month
```

`date` verifică dacă ziua există. Avantajul e că o dată invalidă nu trece neobservată, dar trebuie să tratezi eroarea când data vine de la utilizator (`try / except ValueError`, lecția 24). Tot de aici rezultă că nu poți aduna „o lună”: `timedelta` are zile, ore, minute, secunde și săptămâni, dar nu luni sau ani, pentru că lunile au lungimi diferite.

### 4. randint versus randrange

```python
import random

zaruri = {random.randint(1, 3) for _ in range(1000)}
intervale = {random.randrange(1, 3) for _ in range(1000)}
print(sorted(zaruri), sorted(intervale))
```

```text
[1, 2, 3] [1, 2]
```

`randint(1, 3)` poate da și 3. `randrange(1, 3)` urmează regula lui `range` (lecția 10), deci nu dă niciodată 3. Un zar e `randint(1, 6)` sau `randrange(1, 7)`.

### 5. Counter pe un text, nu pe cuvinte

```python
from collections import Counter

print(Counter("ana are mere").most_common(3))
print(Counter("ana are mere".split()).most_common(1))
```

```text
[('a', 3), ('e', 3), (' ', 2)]
[('ana', 1)]
```

Un string e o secvență de **caractere**, deci `Counter("...")` numără litere, inclusiv spațiile. Pentru cuvinte, dă-i lista de cuvinte: `Counter(text.split())`.

## Exercițiu

În `capitole/31-biblioteca-standard/biblioteca_standard.py`, scrie un **planificator de studiu** pentru cursul tău de Python:

1. data de început e `date(2026, 10, 1)`; ai de parcurs lecțiile 1–61, câte una la fiecare 2 zile: lecția 1 se face chiar pe 1 octombrie, iar lecția n în ziua `start + timedelta(days=2 * (n - 1))`; calculează și afișează data de terminare și ziua săptămânii, în română;
2. afișează câte zile mai sunt de la `date(2026, 10, 29)` până la terminare și ce procent din curs ar trebui să fie gata la acea dată: numărul de lecții terminate până atunci e `math.floor(zile_trecute / 2) + 1`, unde `zile_trecute` sunt zilele de la început până la 29 octombrie;
3. generează un **test-surpriză**: alege, cu `random.sample`, 5 lecții diferite dintre cele terminate până la 29 octombrie; folosește `random.seed(2026)` ca rezultatul să fie același la fiecare rulare, apoi scoate `seed` și observă diferența;
4. pornind de la o listă de tupluri `(data, lectie, minute_de_studiu)` scrisă de tine, grupează minutele pe săptămâni (`date.isocalendar().week` dă numărul săptămânii) cu un `defaultdict(int)` și afișează săptămâna cu cele mai multe minute, folosind un `Counter`;
5. citește numele tău din variabila de mediu `ELEV` cu `os.environ.get("ELEV", "elev")` și folosește-l în titlul raportului.

## Pe scurt

- Biblioteca standard vine cu Python; înainte să scrii ceva general, verifică dacă există deja acolo.
- `datetime`: `date`, `datetime`, `timedelta`; text ↔ dată cu `fromisoformat`/`isoformat` și `strptime`/`strftime`; salvează datele în format ISO.
- `random`: `randint` (inclusiv capătul), `choice`, `shuffle`, `sample`; `seed()` face rezultatele reproductibile.
- `math`: `sqrt`, `ceil`, `floor`, `isclose` pentru `float`-uri, `fsum` pentru sume exacte.
- `os.environ.get("NUME", implicit)` citește setări din mediu; pentru fișiere și căi, `pathlib`.
- `Counter` numără și dă `most_common()`; `defaultdict(list)` grupează fără verificări.
