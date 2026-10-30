## Ce este

Fiecare pagină a unui site Django are două părți:
- o **adresă** (URL), trecută în lista `urlpatterns` din `urls.py`, cu funcția `path()`;
- un **view**: o funcție Python care primește cererea browserului și întoarce răspunsul, adică pagina.

```python
from django.http import HttpResponse


def lista(request):
    return HttpResponse("<h1>Blogul Anei</h1>")
```

```python
urlpatterns = [
    path("", views.lista, name="lista"),
]
```

Când cineva deschide `/`, Django caută adresa în `urlpatterns`, găsește `views.lista`, o apelează și trimite browserului ce a întors. E exact ce făcea serverul tău din lecția 43 cu `if self.path == "/":`, doar că acum Django face potrivirea pentru tine.

## De ce contează

Adresele sunt „cuprinsul” site-ului: `/` pentru lista de articole, `/articol/2/` pentru un articol anume, mai târziu `/contact/`, `/conturi/login/` și `/api/articole/`. View-urile sunt locul unde scrii logica fiecărei pagini: ce date citești, ce verifici, ce trimiți înapoi.

Tot ce vei face de acum în Django trece pe aici: template-urile (lecția 48) sunt folosite **din** view-uri, modelele (lecția 50) sunt citite **în** view-uri, iar formularele (lecția 55) sunt trimise **la** view-uri.

## Cum funcționează

### Drumul unei cereri

Pentru `GET /articol/2/`:
1. Django citește `ROOT_URLCONF` din setări (lecția 46): `blog_proiect.urls`;
2. parcurge `urlpatterns` de sus în jos și se oprește la **primul** tipar de adresă care se potrivește cu `articol/2/`;
3. din adresă extrage valoarea `nr = 2`;
4. apelează view-ul: `detaliu(request, nr=2)`;
5. view-ul întoarce un `HttpResponse`, iar Django îl trimite browserului.

Dacă nicio adresă nu se potrivește, răspunsul e `404 Not Found` (lecția 43).

### Adresele proiectului și adresele aplicației

Proiectul are un singur `urls.py`, cel principal. Ca să nu ajungă o listă uriașă, fiecare aplicație își ține adresele în propriul `urls.py`, iar cel principal doar le „include”:

```python
path("", include("articole.urls")),
```

`include()` înseamnă: „pentru orice cale care începe cu `""`, adică orice cale, caută mai departe în `articole/urls.py`”. Dacă ai scrie `path("blog/", include("articole.urls"))`, toate paginile aplicației ar începe cu `/blog/`. Adresa `admin/` rămâne în fișierul principal.

### `path()`: tipar, view, nume

```python
path("articol/<int:nr>/", views.detaliu, name="detaliu"),
```

- **tiparul** adresei (în engleză „pattern”), `"articol/<int:nr>/"`, se scrie fără `/` la început și, prin convenție, cu `/` la final;
- `<int:nr>` e un **convertor**: se potrivește cu un număr întreg, pe care îl dă view-ului ca argument cu numele `nr`, deja convertit în `int` (fără `int()` de mâna ta). Alte convertoare: `<str:...>` pentru text fără `/`, `<slug:...>` pentru litere fără diacritice, cifre, cratime și `_`;
- **view-ul** e dat ca funcție, **fără paranteze**: Django îl apelează la fiecare cerere, ca la `key=len` (lecția 17);
- `name="detaliu"` dă adresei un nume. Cu el vei genera linkuri în template-uri, fără să scrii căile de mână (lecția 48).

### View-uri

Un view e o funcție care:
- primește ca **prim argument** cererea, numită prin convenție `request` (un obiect cu metoda, adresa, datele trimise);
- primește apoi valorile extrase din adresă, ca argumente keyword (lecția 19);
- **întoarce** un răspuns: `HttpResponse(text)` pentru o pagină, sau ridică `Http404` pentru „nu există”.

`Http404` e o excepție (lecția 25): o ridici cu `raise`, iar Django o transformă în răspunsul 404.

### Ce se întâmplă „pe dedesubt”

`urls.py` și `views.py` sunt module Python obișnuite, importate o singură dată, la pornire. `include("articole.urls")` primește numele modulului ca text, iar Django îl importă singur. `from . import views` din `articole/urls.py` e un import relativ (lecția 29): „modulul `views` din același pachet”.

Datele articolelor sunt deocamdată o listă de dicționare în `views.py`, exact ca la lecția 14. La lecția 52 ele vor veni din baza de date, dar view-urile vor arăta aproape la fel.

## Exemplu complet

Primele două pagini ale blogului: lista de articole și pagina unui articol. Sunt trei fișiere.

Adresele principale ale proiectului, `blog_proiect/urls.py` (înlocuiește tot fișierul generat):

<!-- fisier: blog_proiect/urls.py -->
```python
"""Adresele proiectului: fiecare cerere e trimisă mai departe după începutul căii."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("articole.urls")),
]
```

Adresele aplicației, într-un fișier nou, `articole/urls.py`:

<!-- fisier: articole/urls.py -->
```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista, name="lista"),
    path("articol/<int:nr>/", views.detaliu, name="detaliu"),
]
```

View-urile, în `articole/views.py` (înlocuiește tot fișierul generat):

<!-- fisier: articole/views.py -->
```python
from datetime import date

from django.http import Http404, HttpResponse

# Datele vin deocamdată dintr-o listă Python; la lecția 52 le vom citi din baza de date.
ARTICOLE = [
    {
        "id": 3,
        "titlu": "O plimbare prin Cluj",
        "data_publicarii": date(2026, 10, 20),
        "categorie": "Călătorii",
        "continut": (
            "Duminică am urcat pe dealul Cetățuia, de unde se vede tot Clujul. "
            "Pe drum am trecut prin Piața Unirii și pe lângă Teatrul Național.\n\n"
            "Data viitoare vreau să ajung și în Grădina Botanică."
        ),
    },
    {
        "id": 2,
        "titlu": "De ce am ales Django",
        "data_publicarii": date(2026, 10, 2),
        "categorie": "Programare",
        "continut": (
            "După primele luni cu Python, voiam să fac un site adevărat: cu pagini, "
            "cu bază de date și cu un loc unde să mă autentific.\n\n"
            "Django are toate acestea „din cutie”, iar documentația lui e excelentă."
        ),
    },
    {
        "id": 1,
        "titlu": "Primul meu program în Python",
        "data_publicarii": date(2026, 9, 14),
        "categorie": "Programare",
        "continut": (
            'Totul a început cu un simplu print("Salut, lume!"). '
            "Nu credeam că două cuvinte pe ecran pot să bucure atât de mult.\n\n"
            "Azi știu că a fost primul pas dintr-un drum lung: "
            "variabile, bucle, funcții și clase."
        ),
    },
]


def gaseste(nr):
    """Articolul cu id-ul `nr` sau pagina 404, dacă nu există."""
    for articol in ARTICOLE:
        if articol["id"] == nr:
            return articol
    raise Http404("Articolul nu există.")


def lista(request):
    randuri = []
    for a in ARTICOLE:
        data = a["data_publicarii"].strftime("%d.%m.%Y")
        randuri.append(f'<li><a href="/articol/{a["id"]}/">{a["titlu"]}</a> ({data})</li>')
    return HttpResponse("<h1>Blogul Anei</h1><ul>" + "".join(randuri) + "</ul>")


def detaliu(request, nr):
    articol = gaseste(nr)
    return HttpResponse(f"<h1>{articol['titlu']}</h1><p>{articol['continut']}</p>")
```

Câteva observații despre cod:
- `date` vine din modulul `datetime` (lecția 31), iar `strftime("%d.%m.%Y")` formatează data ca `20.10.2026`;
- `gaseste()` e o funcție ajutătoare, nu un view: nu primește `request` și nu apare în `urls.py`;
- articolele sunt în ordinea în care vrem să le afișăm: cel mai nou primul.

Verifici proiectul și deschizi pagina principală:

<!-- ruleaza -->
```bash
python manage.py check
```

```text
System check identified no issues (0 silenced).
```

<!-- comanda: python /h/vezi_pagina.py / -->
```text
200 OK
Blogul Anei
O plimbare prin Cluj (20.10.2026)
De ce am ales Django (02.10.2026)
Primul meu program în Python (14.09.2026)
```

Pagina de bun venit a dispărut: acum `/` are propriul view. HTML-ul trimis browserului e exact textul construit în `lista()`:

<!-- comanda: python /h/vezi_pagina.py --html / -->
```text
200 OK
<h1>Blogul Anei</h1><ul><li><a href="/articol/3/">O plimbare prin Cluj</a> (20.10.2026)</li><li><a href="/articol/2/">De ce am ales Django</a> (02.10.2026)</li><li><a href="/articol/1/">Primul meu program în Python</a> (14.09.2026)</li></ul>
```

Un clic pe al doilea titlu deschide `/articol/2/`:

<!-- comanda: python /h/vezi_pagina.py /articol/2/ -->
```text
200 OK
De ce am ales Django
După primele luni cu Python, voiam să fac un site adevărat: cu pagini, cu bază de date și cu un loc unde să mă autentific. Django are toate acestea „din cutie”, iar documentația lui e excelentă.
```

Un articol care nu există:

<!-- comanda: python /h/vezi_pagina.py /articol/9/ -->
```text
Not Found: /articol/9/
404 Not Found
Page not found (404)
Articolul nu există.
Request Method: | GET
Request URL: | http://testserver/articol/9/
Raised by: | articole.views.detaliu
Using the URLconf defined in blog_proiect.urls, Django tried these URL patterns, in this order:
admin/
[name='lista']
articol/<int:nr>/ [name='detaliu']
The current path, articol/9/, matched the last one.
You’re seeing this error because you have DEBUG = True in your Django settings file. Change that to False, and Django will display a standard 404 page.
```

Pagina de depanare (lecția 46) spune multe: adresa s-a potrivit cu `articol/<int:nr>/` („matched the last one”), dar view-ul `detaliu` a ridicat `Http404` cu mesajul „Articolul nu există.”.

Dar `/articol/abc/` nu ajunge deloc la view: `abc` nu e un număr, deci convertorul `<int:nr>` nu se potrivește („didn’t match any of these”):

<!-- comanda: python /h/vezi_pagina.py /articol/abc/ -->
```text
Not Found: /articol/abc/
404 Not Found
Page not found (404)
Request Method: | GET
Request URL: | http://testserver/articol/abc/
Using the URLconf defined in blog_proiect.urls, Django tried these URL patterns, in this order:
admin/
[name='lista']
articol/<int:nr>/ [name='detaliu']
The current path, articol/abc/, didn’t match any of these.
You’re seeing this error because you have DEBUG = True in your Django settings file. Change that to False, and Django will display a standard 404 page.
```

Încă un detaliu: adresele noastre se termină cu `/`. Dacă cineva scrie `/articol/2`, fără bară, Django nu dă 404, ci îl trimite la adresa corectă:

<!-- comanda: python /h/vezi_pagina.py /articol/2 -->
```text
301 Moved Permanently
Location: /articol/2/
```

E o redirecționare permanentă (lecția 43). Setarea `APPEND_SLASH`, activă implicit, face asta. Browserul urmează redirecționarea singur, deci vizitatorul nici nu observă.

Ai observat că paginile sunt doar text simplu, fără antetul, meniul și stilul din lecția 44? Construirea HTML-ului din stringuri în Python e incomodă și, cum vei vedea, chiar periculoasă. Lecția 48 rezolvă asta cu template-uri.

## Greșeli frecvente

### 1. View-ul nu întoarce nimic

Ai uitat `return` în fața lui `HttpResponse(...)` din `lista()`:

<!-- comanda: cp -r . /tmp/p && cd /tmp/p && sed -i "s/    return HttpResponse(\"<h1>Blogul Anei/    HttpResponse(\"<h1>Blogul Anei/" articole/views.py && python /h/vezi_pagina.py / -->
```text
Traceback (most recent call last):
ValueError: The view articole.views.lista didn't return an HttpResponse object. It returned None instead.
```

O funcție fără `return` întoarce `None` (lecția 18). Fiecare view trebuie să întoarcă un răspuns (sau să ridice o excepție ca `Http404`).

### 2. Numele parametrului diferă de cel din adresă

În `urls.py` scrie `<int:nr>`, dar view-ul a fost definit `def detaliu(request, numar):`:

<!-- comanda: cp -r . /tmp/p && cd /tmp/p && sed -i "s/def detaliu(request, nr):/def detaliu(request, numar):/; s/gaseste(nr)/gaseste(numar)/" articole/views.py && python /h/vezi_pagina.py /articol/2/ -->
```text
Traceback (most recent call last):
TypeError: detaliu() got an unexpected keyword argument 'nr'
```

Django apelează `detaliu(request, nr=2)`, cu numele din adresă (argument keyword, lecția 19). Numele din `<int:...>` și numele parametrului trebuie să fie identice.

### 3. `include` folosit fără import

Ai adăugat `path("", include("articole.urls"))`, dar ai păstrat importul generat, `from django.urls import path`:

<!-- comanda: cp -r . /tmp/p && cd /tmp/p && sed -i "s/from django.urls import include, path/from django.urls import path/" blog_proiect/urls.py && python manage.py check -->
```text
Traceback (most recent call last):
  File "/tmp/p/blog_proiect/urls.py", line 7, in <module>
    path("", include("articole.urls")),
             ^^^^^^^
NameError: name 'include' is not defined
```

(La tine calea din traceback începe cu folderul proiectului `blog`.) Corect: `from django.urls import include, path`. `check` e o metodă rapidă de a prinde astfel de greșeli înainte să deschizi browserul.

### 4. Paranteze după numele view-ului

```python
path("", views.lista(), name="lista"),
```

<!-- comanda: cp -r . /tmp/p && cd /tmp/p && sed -i "s/views.lista, name/views.lista(), name/" articole/urls.py && python manage.py check -->
```text
Traceback (most recent call last):
  File "/tmp/p/articole/urls.py", line 6, in <module>
    path("", views.lista(), name="lista"),
             ^^^^^^^^^^^^^
TypeError: lista() missing 1 required positional argument: 'request'
```

Cu paranteze, Python apelează `lista()` chiar în momentul în care citește `urls.py`, fără argumentul `request`, deci eroarea apare încă de la pornire. În `path()` dai **funcția**, ca s-o apeleze Django la fiecare cerere: `views.lista`.

## Exercițiu

În proiectul PyTutor `blog`, după ce ai scris cele trei fișiere din lecție și ai verificat paginile `/`, `/articol/2/` și `/articol/9/` în browser:

1. adaugă un al patrulea articol în lista `ARTICOLE`, cu `id` 4, la începutul listei (e cel mai nou); verifică lista și pagina lui;
2. adaugă pagina `/salut/<str:nume>/`, cu view-ul `salut`, care afișează „Salut, Mihai! Bine ai venit pe blogul Anei.” pentru `/salut/Mihai/`;
3. adaugă pagina `/an/<int:an>/`, care listează doar articolele publicate în acel an, sau mesajul „Niciun articol în 2025.” (folosește `data_publicarii.year`).

Al patrulea articol și paginile de la punctele 2 și 3 sunt doar exerciții: lecțiile următoare nu le folosesc, iar la lecția 48 vei înlocui `views.py` și `articole/urls.py` cu variantele noi, care au tot cele trei articole (dacă vrei să păstrezi paginile tale, adaugă-le din nou la final).

## Pe scurt

- O pagină = o adresă în `urlpatterns` (`path(tipar, view, name=...)`) + un view, adică o funcție care primește `request` și întoarce un `HttpResponse`.
- Adresele aplicației stau în `articole/urls.py`; `urls.py`-ul principal le adaugă cu `include("articole.urls")`.
- `<int:nr>` extrage un număr din adresă și îl dă view-ului ca argument `nr`; textul care nu e număr nu se potrivește (404).
- `raise Http404("...")` răspunde cu „pagina nu există”.
- În `path()` se dă funcția fără paranteze; numele parametrului view-ului e cel din adresă.
- Fără `/` la final, Django redirecționează (301) spre adresa cu `/`.

<!-- proiect: _blog/46 -->
<!-- proiect-final: _blog/47 -->
