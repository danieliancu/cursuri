<!-- proiect: _blog/51 -->
<!-- proiect-final: _blog/52 -->
<!-- pregatire: python manage.py migrate -v 0 && python manage.py loaddata /lectii/_blog/date/50.json -v 0 -->
## Ce este

O **interogare** (în engleză „query”) este o întrebare pusă bazei de date: „dă-mi toate articolele publicate”, „dă-mi articolul cu `id` 3”, „câte articole sunt din octombrie?”. Cu ORM-ul Django, întrebările se scriu în Python, pornind de la managerul modelului, `Articol.objects`:

```python
Articol.objects.all()                      # toate articolele
Articol.objects.filter(publicat=True)      # doar cele publicate
Articol.objects.get(id=3)                  # exact un articol
```

Primele două întorc un **QuerySet**: o colecție de obiecte din baza de date, pe care o poți parcurge cu `for`, ca pe o listă. `get` întoarce un singur obiect.

În lecția asta, view-urile blogului renunță la lista `ARTICOLE` și citesc articolele din baza de date, unde le-ai mutat la lecția 50.

## De ce contează

O aplicație web face interogări la aproape fiecare cerere: lista articolelor, un articol după `id`, comentariile lui, articolele unei categorii, rezultatele unei căutări. Fără ORM, ai scrie SQL ca text, cu grijă la fiecare ghilimea. Cu ORM-ul, scrii Python obișnuit, cu nume de câmpuri pe care editorul le recunoaște, iar Django construiește SQL-ul corect pentru baza ta de date.

Tot aici se ține și promisiunea de la lecțiile 24 și 25: când ceri un articol care nu există, Django ridică excepția `Articol.DoesNotExist`. Vei vedea cum o transformi într-o pagină 404.

## Cum funcționează

### Citire: all, filter, exclude, get

Toate exemplele rulează în `python manage.py shell` (lecția 50), cu cele trei articole ale Anei în baza de date.

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'Articol.objects.all()' 'Articol.objects.filter(publicat=True)' 'Articol.objects.exclude(id=2)' 'Articol.objects.get(id=3)' 'Articol.objects.count()' 'Articol.objects.filter(publicat=True).exclude(id=2).count()'; } | PYTHONPATH=/h python manage.py shell -->
```text
7 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol
>>> Articol.objects.all()
<QuerySet [<Articol: O plimbare prin Cluj>, <Articol: De ce am ales Django>, <Articol: Primul meu program în Python>]>
>>> Articol.objects.filter(publicat=True)
<QuerySet [<Articol: O plimbare prin Cluj>, <Articol: De ce am ales Django>, <Articol: Primul meu program în Python>]>
>>> Articol.objects.exclude(id=2)
<QuerySet [<Articol: O plimbare prin Cluj>, <Articol: Primul meu program în Python>]>
>>> Articol.objects.get(id=3)
<Articol: O plimbare prin Cluj>
>>> Articol.objects.count()
3
>>> Articol.objects.filter(publicat=True).exclude(id=2).count()
2
>>> 
now exiting InteractiveConsole...
```

- `all()` — toate rândurile, în ordinea din `Meta.ordering` (cele mai noi primele);
- `filter(camp=valoare)` — doar rândurile care îndeplinesc condiția; mai multe condiții separate prin virgulă înseamnă „și”;
- `exclude(...)` — opusul lui `filter`: scoate rândurile care îndeplinesc condiția;
- `get(...)` — **exact un** obiect, nu un QuerySet; dacă nu există niciunul sau există mai multe, ridică o excepție (vezi greșelile frecvente);
- `count()` — câte rânduri sunt, calculat direct de baza de date.

Metodele se pot **înlănțui**: fiecare `filter` sau `exclude` întoarce un QuerySet nou, pe care poți apela din nou `filter`, `exclude`, `count` și așa mai departe.

### Lookups: condiții mai complicate decât „egal”

După numele câmpului poți pune `__` (două liniuțe de jos) și un **lookup**, care spune ce fel de comparație vrei:

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'Articol.objects.filter(titlu__icontains="python")' 'Articol.objects.filter(titlu__startswith="De ce")' 'Articol.objects.filter(data_publicarii__gte="2026-10-01").count()' 'Articol.objects.filter(data_publicarii__month=10, publicat=True)' 'Articol.objects.filter(id__in=[1, 3])' 'Articol.objects.filter(titlu__startswith="Z").exists()'; } | PYTHONPATH=/h python manage.py shell -->
```text
7 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol
>>> Articol.objects.filter(titlu__icontains="python")
<QuerySet [<Articol: Primul meu program în Python>]>
>>> Articol.objects.filter(titlu__startswith="De ce")
<QuerySet [<Articol: De ce am ales Django>]>
>>> Articol.objects.filter(data_publicarii__gte="2026-10-01").count()
2
>>> Articol.objects.filter(data_publicarii__month=10, publicat=True)
<QuerySet [<Articol: O plimbare prin Cluj>, <Articol: De ce am ales Django>]>
>>> Articol.objects.filter(id__in=[1, 3])
<QuerySet [<Articol: O plimbare prin Cluj>, <Articol: Primul meu program în Python>]>
>>> Articol.objects.filter(titlu__startswith="Z").exists()
False
>>> 
now exiting InteractiveConsole...
```

| Lookup | Înseamnă | Exemplu |
|---|---|---|
| `__contains` / `__icontains` | conține textul (`i` = fără să conteze literele mari) | `titlu__icontains="python"` |
| `__startswith`, `__endswith` | începe / se termină cu | `titlu__startswith="De ce"` |
| `__gt`, `__gte`, `__lt`, `__lte` | mai mare, mai mare sau egal, mai mic... | `data_publicarii__gte="2026-10-01"` |
| `__in` | este unul dintre | `id__in=[1, 3]` |
| `__year`, `__month`, `__day` | o parte dintr-o dată | `data_publicarii__month=10` |

Atenție, pe SQLite: `contains` nu face diferența între litere mari și mici la literele fără diacritice, iar nici `icontains` nu o face pentru ă, â, î, ș, ț (`"ș"` nu găsește `"Ș"`). Pe PostgreSQL (lecția 61), `contains` ține cont de litere mari.

`exists()` răspunde doar „există măcar unul?”, fără să aducă articolele; e mai rapid decât să verifici dacă un QuerySet e gol.

### Ordine, primul, ultimul, doar unele câmpuri

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'Articol.objects.order_by("titlu")' 'Articol.objects.order_by("titlu").first()' 'Articol.objects.order_by("data_publicarii").last()' 'Articol.objects.values_list("id", "titlu")'; } | PYTHONPATH=/h python manage.py shell -->
```text
7 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol
>>> Articol.objects.order_by("titlu")
<QuerySet [<Articol: De ce am ales Django>, <Articol: O plimbare prin Cluj>, <Articol: Primul meu program în Python>]>
>>> Articol.objects.order_by("titlu").first()
<Articol: De ce am ales Django>
>>> Articol.objects.order_by("data_publicarii").last()
<Articol: O plimbare prin Cluj>
>>> Articol.objects.values_list("id", "titlu")
<QuerySet [(3, 'O plimbare prin Cluj'), (2, 'De ce am ales Django'), (1, 'Primul meu program în Python')]>
>>> 
now exiting InteractiveConsole...
```

`order_by("camp")` ordonează crescător, iar `order_by("-camp")` descrescător (ca `ordering` din `Meta`). `first()` și `last()` dau primul și ultimul element sau `None` dacă nu există niciunul: spre deosebire de `get`, nu ridică excepții. `values_list` aduce doar câmpurile cerute, ca tupluri (lecția 13).

### Scriere: create, update, delete

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'nou = Articol.objects.create(titlu="Ciornă", continut="De terminat.", publicat=False)' 'nou.id' 'Articol.objects.filter(publicat=True).count()' 'Articol.objects.filter(id=nou.id).update(titlu="Ciornă despre Iași")' 'Articol.objects.get(id=nou.id).titlu' 'Articol.objects.filter(publicat=False).delete()' 'Articol.objects.count()'; } | PYTHONPATH=/h python manage.py shell -->
```text
7 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol
>>> nou = Articol.objects.create(titlu="Ciornă", continut="De terminat.", publicat=False)
>>> nou.id
4
>>> Articol.objects.filter(publicat=True).count()
3
>>> Articol.objects.filter(id=nou.id).update(titlu="Ciornă despre Iași")
1
>>> Articol.objects.get(id=nou.id).titlu
'Ciornă despre Iași'
>>> Articol.objects.filter(publicat=False).delete()
(1, {'articole.Articol': 1})
>>> Articol.objects.count()
3
>>> 
now exiting InteractiveConsole...
```

- `create(...)` creează și salvează un rând (lecția 50);
- `filter(...).update(...)` modifică dintr-o dată toate rândurile găsite, direct în baza de date, și spune câte au fost modificate. Pentru un singur obiect deja citit, merge și varianta de la lecția 51: schimbi atributul și apelezi `save()`;
- `filter(...).delete()` șterge toate rândurile găsite. Fii atent la filtru: `Articol.objects.all().delete()` golește tabelul.

### Ce se întâmplă „pe dedesubt”: QuerySet-urile sunt leneșe

Când scrii `Articol.objects.filter(publicat=True)`, Django **nu** întreabă încă baza de date. Construiește doar întrebarea. O poți vedea, ca SQL:

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'qs = Articol.objects.filter(publicat=True).order_by("titlu")' 'print(qs.query)' 'for a in qs:' '    print(a.id, a)' ''; } | PYTHONPATH=/h python manage.py shell -->
```text
7 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol
>>> qs = Articol.objects.filter(publicat=True).order_by("titlu")
>>> print(qs.query)
SELECT "articole_articol"."id", "articole_articol"."titlu", "articole_articol"."continut", "articole_articol"."data_publicarii", "articole_articol"."publicat" FROM "articole_articol" WHERE "articole_articol"."publicat" ORDER BY "articole_articol"."titlu" ASC
>>> for a in qs:
...     print(a.id, a)
... 
2 De ce am ales Django
3 O plimbare prin Cluj
1 Primul meu program în Python
>>> 
now exiting InteractiveConsole...
```

Interogarea pleacă spre baza de date abia când ai nevoie de rezultate: când parcurgi QuerySet-ul cu `for`, îl afișezi, apelezi `list()`, `len()` sau îl folosești într-un `if`. E aceeași idee ca la generatoarele din lecția 37: munca se face „la cerere”. Avantajul: poți construi interogarea în pași (`filter`, apoi `exclude`, apoi `order_by`), iar Django trimite un singur SQL, la final. După prima evaluare, QuerySet-ul ține minte rezultatele, deci un al doilea `for` pe același `qs` nu mai întreabă baza de date.

### Când articolul nu există: DoesNotExist și get_object_or_404

`get` ridică `Articol.DoesNotExist` dacă nu găsește nimic. Fiecare model are propria clasă de excepție cu acest nume. Într-un view, ai putea scrie (lecția 24):

```python
from django.http import Http404


def detaliu(request, nr):
    try:
        articol = Articol.objects.get(id=nr, publicat=True)
    except Articol.DoesNotExist:
        raise Http404("Articolul nu există.")
    return render(request, "articole/detaliu.html", {"articol": articol})
```

Tiparul e atât de des întâlnit, încât Django are o scurtătură, `get_object_or_404(Model, conditii)`: face `get` și, dacă obiectul lipsește, ridică `Http404`. Cu ea, view-urile blogului devin:

<!-- fisier: articole/views.py -->
```python
from django.shortcuts import get_object_or_404, render

from .models import Articol


def lista(request):
    articole = Articol.objects.filter(publicat=True)
    return render(request, "articole/lista.html", {"articole": articole})


def detaliu(request, nr):
    articol = get_object_or_404(Articol, id=nr, publicat=True)
    return render(request, "articole/detaliu.html", {"articol": articol})


def despre(request):
    return render(request, "articole/despre.html")
```

Lista `ARTICOLE` și funcția `gaseste` au dispărut: datele vin acum din baza de date. Template-urile rămân neschimbate, pentru că obiectele `Articol` au aceleași nume de câmpuri ca dicționarele de dinainte (`articol.titlu`, `articol.data_publicarii`, `articol.continut`). În template, `{{ articol.titlu }}` funcționează la fel pentru un dicționar și pentru un obiect. O singură diferență se vede: categoria nu mai apare lângă dată, pentru că modelul nu are (încă) un câmp `categorie`, iar `{% if articol.categorie %}` din `_meta.html` e fals. O aducem înapoi la lecția 53.

## Exemplu complet

Paginile blogului, servite acum din baza de date. Lista:

<!-- comanda: python /h/vezi_pagina.py / -->
```text
200 OK
Blogul Anei
Articole Despre
Articole
O plimbare prin Cluj
20 octombrie 2026
Duminică am urcat pe dealul Cetățuia, de unde se vede tot Clujul. …
De ce am ales Django
2 octombrie 2026
După primele luni cu Python, voiam să fac un site adevărat: cu …
Primul meu program în Python
14 septembrie 2026
Totul a început cu un simplu print("Salut, lume!"). Nu credeam că două …
Ana Popescu, Cluj · 2026
```

Un articol:

<!-- comanda: python /h/vezi_pagina.py /articol/3/ -->
```text
200 OK
Blogul Anei
Articole Despre
O plimbare prin Cluj
20 octombrie 2026
Duminică am urcat pe dealul Cetățuia, de unde se vede tot Clujul. Pe drum am trecut prin Piața Unirii și pe lângă Teatrul Național.
Data viitoare vreau să ajung și în Grădina Botanică.
Ana Popescu, Cluj · 2026
```

Un articol care nu există:

<!-- comanda: python /h/vezi_pagina.py /articol/99/ -->
```text
Not Found: /articol/99/
404 Not Found
Page not found (404)
No Articol matches the given query.
Request Method: | GET
Request URL: | http://testserver/articol/99/
Raised by: | articole.views.detaliu
Using the URLconf defined in blog_proiect.urls, Django tried these URL patterns, in this order:
admin/
[name='lista']
articol/<int:nr>/ [name='detaliu']
The current path, articol/99/, matched the last one.
You’re seeing this error because you have DEBUG = True in your Django settings file. Change that to False, and Django will display a standard 404 page.
```

Mesajul „No Articol matches the given query” vine de la `get_object_or_404`, iar „Raised by: articole.views.detaliu” arată view-ul care a ridicat `Http404`. Cu `DEBUG = False` (lecția 61), vizitatorul ar vedea doar o pagină 404 simplă.

Acum, adevăratul câștig: Ana ascunde articolul despre Cluj din shell, fără să schimbe vreun fișier.

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'Articol.objects.filter(id=3).update(publicat=False)'; } | PYTHONPATH=/h python manage.py shell -->
```text
7 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol
>>> Articol.objects.filter(id=3).update(publicat=False)
1
>>> 
now exiting InteractiveConsole...
```

<!-- comanda: python /h/vezi_pagina.py / -->
```text
200 OK
Blogul Anei
Articole Despre
Articole
De ce am ales Django
2 octombrie 2026
După primele luni cu Python, voiam să fac un site adevărat: cu …
Primul meu program în Python
14 septembrie 2026
Totul a început cu un simplu print("Salut, lume!"). Nu credeam că două …
Ana Popescu, Cluj · 2026
```

Articolul a dispărut din listă, iar `/articol/3/` dă acum 404, pentru că ambele view-uri cer `publicat=True`. Îl publici la loc cu `update(publicat=True)`.

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'Articol.objects.filter(id=3).update(publicat=True)'; } | PYTHONPATH=/h python manage.py shell -->
```text
7 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol
>>> Articol.objects.filter(id=3).update(publicat=True)
1
>>> 
now exiting InteractiveConsole...
```

## Greșeli frecvente

### 1. get pentru un obiect care nu există

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'Articol.objects.get(id=99)'; } | PYTHONPATH=/h python manage.py shell -->
```text
>>> Articol.objects.get(id=99)
Traceback (most recent call last):
  File "<console>", line 1, in <module>
articole.models.Articol.DoesNotExist: Articol matching query does not exist.
>>> 
now exiting InteractiveConsole...
```

(Aici și la greșelile 2–4 am păstrat doar rândurile de la comanda greșită încolo și am scurtat tracebackurile.) Într-un view, o astfel de excepție neprinsă devine o eroare 500, „eroare de server”, deși problema e doar o adresă greșită. Folosește `get_object_or_404`, sau `try / except Articol.DoesNotExist`, sau `filter(...).first()`, care dă `None` în loc de excepție.

### 2. get care găsește mai multe obiecte

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'Articol.objects.get(publicat=True)'; } | PYTHONPATH=/h python manage.py shell -->
```text
>>> Articol.objects.get(publicat=True)
Traceback (most recent call last):
  File "<console>", line 1, in <module>
articole.models.Articol.MultipleObjectsReturned: get() returned more than one Articol -- it returned 3!
>>> 
now exiting InteractiveConsole...
```

`get` e pentru condiții care identifică **un singur** rând, de obicei `id`-ul sau un câmp `unique`. Pentru „toate cele care...” folosește `filter`.

### 3. Lookup scris greșit

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'Articol.objects.filter(titlu__contine="Django")'; } | PYTHONPATH=/h python manage.py shell -->
```text
>>> Articol.objects.filter(titlu__contine="Django")
Traceback (most recent call last):
  File "<console>", line 1, in <module>
django.core.exceptions.FieldError: Unsupported lookup 'contine' for CharField or join on the field not permitted, perhaps you meant contains or icontains?
>>> 
now exiting InteractiveConsole...
```

Lookup-urile au nume englezești fixe (`contains`, nu `contine`). Aceeași familie de erori, `FieldError`, apare și când scrii greșit numele unui câmp (`titul=...`): Django îți listează atunci câmpurile disponibile. Atenție și la o singură liniuță: `titlu_contains` ar fi căutat un câmp numit chiar așa.

### 4. Atribute cerute unui QuerySet, nu unui obiect

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'rezultat = Articol.objects.filter(id=3)' 'rezultat.titlu' 'rezultat.first().titlu'; } | PYTHONPATH=/h python manage.py shell -->
```text
>>> rezultat = Articol.objects.filter(id=3)
>>> rezultat.titlu
Traceback (most recent call last):
  File "<console>", line 1, in <module>
AttributeError: 'QuerySet' object has no attribute 'titlu'
>>> rezultat.first().titlu
'O plimbare prin Cluj'
>>> 
now exiting InteractiveConsole...
```

`filter` întoarce mereu o colecție, chiar dacă are un singur element. Ca să ajungi la obiect: `get(...)`, `first()` sau un `for`.

### 5. „Am schimbat articolul, dar nu s-a salvat”

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'Articol.objects.get(id=1).titlu = "Titlu nou"' 'Articol.objects.get(id=1).titlu'; } | PYTHONPATH=/h python manage.py shell -->
```text
7 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol
>>> Articol.objects.get(id=1).titlu = "Titlu nou"
>>> Articol.objects.get(id=1).titlu
'Primul meu program în Python'
>>> 
now exiting InteractiveConsole...
```

Primul rând a modificat un obiect din memorie, care a dispărut imediat, fără `save()`. Al doilea `get` citește din nou din baza de date, unde nu s-a schimbat nimic. Corect: păstrezi obiectul într-o variabilă, schimbi atributul, apoi `save()`; sau folosești `filter(id=1).update(titlu="Titlu nou")`.

## Exercițiu

Lucrezi în proiectul PyTutor `blog`. Înlocuiește `articole/views.py` cu varianta din lecție, care citește din baza de date, și verifică paginile cu `python manage.py runserver 0.0.0.0:8000`. Apoi, în `python manage.py shell`, scrie câte o interogare pentru:

1. articolele care conțin cuvântul „Cluj” în titlu sau în conținut (două interogări separate, apoi gândește-te cum le-ai combina; indiciu: `|` între două QuerySet-uri face uniunea, ca la seturi, lecția 15);
2. câte articole au fost publicate în septembrie 2026;
3. titlurile tuturor articolelor, în ordine alfabetică, ca listă de stringuri (`values_list("titlu", flat=True)` și `list()`);
4. articolul cel mai vechi, cu `order_by` și `first()`;
5. ascunde, cu `update`, toate articolele din octombrie, verifică în browser lista și pagina unui articol ascuns, apoi publică-le la loc.

Nu modifica modelul: lecția 53 pornește de la el.

## Pe scurt

- `Articol.objects` e punctul de pornire: `all()`, `filter()`, `exclude()` întorc QuerySet-uri; `get()` întoarce un singur obiect.
- Lookup-urile se scriu cu `__`: `titlu__icontains`, `data_publicarii__gte`, `id__in`, `data_publicarii__month`.
- `order_by("-camp")`, `first()`, `last()`, `count()`, `exists()`, `values_list()`; scrierea: `create()`, `update()`, `delete()`.
- QuerySet-urile sunt leneșe: SQL-ul pleacă abia când ai nevoie de rezultate; `print(qs.query)` îl arată.
- `get` ridică `Model.DoesNotExist` sau `MultipleObjectsReturned`; în view-uri folosește `get_object_or_404`.
- Modificarea unui obiect se salvează doar cu `save()` (sau direct cu `update()`).
