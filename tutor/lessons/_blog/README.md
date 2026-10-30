# Blogul Anei — proiectul de referință al lecțiilor Django (45–61)

Folderul `NN/` conține proiectul **complet, așa cum arată după lecția NN**. Lecția NN pornește de la `NN-1/`
(lecția 45 pornește de la un folder gol) și trebuie să ajungă exact la `NN/`:

```text
<!-- proiect: _blog/49 -->          (lipsește la lecția 45)
<!-- proiect-final: _blog/50 -->
<!-- pregatire: python manage.py migrate -v 0 && python manage.py loaddata /lectii/_blog/date/50.json -v 0 -->
```

Orice fișier schimbat se arată în lecție **întreg**, într-un bloc cu `<!-- fisier: cale -->` (căi relative la
rădăcina proiectului, cea cu `manage.py`). Lista exactă a schimbărilor: `python tools/verifica_blog.py NN`.
Comparația finală ignoră `db.sqlite3`, `__pycache__`, `staticfiles/`, data din antetul migrărilor și cheia
`SECRET_KEY` generată de `startproject` (vezi „Probleme cunoscute”).

## Convenții

- Proiect: `blog_proiect` (creat cu `django-admin startproject blog_proiect .`, deci `manage.py` stă în rădăcină).
  Aplicație: `articole`. Python 3.12, Django 5.2.18.
- Template-uri: `articole/templates/articole/` (`base.html`, `lista.html`, `detaliu.html`, `_meta.html` — inclus
  în listă și în detaliu, `despre.html`, `contact.html`, `formular_articol.html`, `confirma_stergere.html`) și
  `articole/templates/registration/` (`login.html`, `inregistrare.html`).
- CSS: `articole/static/articole/stil.css` = CSS-ul din lecția 44, cu o singură diferență: `.formular-comentariu`
  devine `.formular` (îl folosesc toate formularele), plus `.errorlist` și `.mesaj` (folosite de la lecția 55).
- Datele calendaristice: `{{ data|date:"j F Y"|lower }}` — localizarea românească a Django scrie lunile cu
  majusculă („2 Octombrie 2026”), iar `|lower` le face corecte („2 octombrie 2026”).
- Mesajele de confirmare: framework-ul `messages`, afișat în `base.html` (de la 55).
- Comentariile: formularul `ComentariuForm` (câmpuri `autor`, `text`); după salvare, redirect la
  `/articol/<nr>/#comentarii`. Câmpul `autor` al comentariului rămâne text liber și după lecția 57.

### Adrese (după lecția 58)

| Adresă | Nume URL | View | Apare la |
|---|---|---|---|
| `/` | `lista` | `ListaArticole` (`lista` până la 57) | 47 |
| `/articol/<int:nr>/` | `detaliu` | `DetaliuArticol` (`detaliu`) | 47 |
| `/despre/` | `despre` | `Despre` (`despre`) | 48 |
| `/contact/` | `contact` | `Contact` (`contact`) | 55 |
| `/articol/<int:nr>/comentariu/` (POST) | `comentariu` | `adauga_comentariu` (rămâne funcție) | 56 |
| `/articol/nou/` | `articol_nou` | `ArticolNou` (`articol_nou`) | 56 |
| `/articol/<int:nr>/editeaza/` | `articol_editeaza` | `ArticolEditeaza` (`articol_editeaza`) | 56 |
| `/articol/<int:nr>/sterge/` | `articol_sterge` | `ArticolSterge` | 58 |
| `/conturi/login/`, `/conturi/logout/` … | `login`, `logout` … | `django.contrib.auth.urls` | 57 |
| `/conturi/inregistrare/` | `inregistrare` | `inregistrare` (rămâne funcție) | 57 |
| `/api/`, `/api/articole/`, `/api/articole/<id>/` | (router DRF) | `ArticolViewSet` | 60 |
| `/admin/` | — | admin | 45 (folosit la 54) |

URL-urile n-au namespace (`{% url 'detaliu' articol.id %}`, nu `articole:detaliu`).

### Modele (forma finală)

- `Categorie(nume unic)`, `Eticheta(nume unic)` — de la 53, ordonate după nume.
- `Articol(titlu, continut, data_publicarii=date.today, publicat=True, categorie→Categorie (null, SET_NULL,
  related_name="articole"), etichete↔Eticheta (blank, related_name="articole"), autor→User (null, SET_NULL,
  related_name="articole"))`, ordonate descrescător după dată; `__str__` = titlul; `get_absolute_url()` (de la 53).
  Câmpuri pe etape: 50 `titlu`, `continut`, `data_publicarii`; 51 `publicat`; 53 `categorie`, `etichete`; 57 `autor`.
- `Comentariu(articol→Articol (CASCADE, related_name="comentarii"), autor (text), text, data auto_now_add)` — 53.
- Migrări: `0001_initial` (50), `0002_articol_publicat` (51),
  `0003_categorie_eticheta_articol_categorie_comentariu_and_more` (53, numele dat automat de Django),
  `0004_articol_autor` (57). Toate se creează în lecție cu `python manage.py makemigrations` (fără `--name`).

### Datele de test (`date/`)

Încărcate ascuns cu `<!-- pregatire: ... -->`; în afara proiectului, deci nu apar în comparația finală.

| Fișier | Pentru modelele etapelor | Conține |
|---|---|---|
| `date/50.json` | 50–52 | cele 3 articole (fără categorii) |
| `date/53.json` | 53–56 | + categoriile Programare (1), Călătorii (2); etichetele python (1), django (2), cluj (3); 2 comentarii ale lui Mihai (la articolele 2 și 3) |
| `date/57.json` | 57–61 | + utilizatorii `ana` (superuser, parola `parola-ana-2026`) și `mihai` (parola `parola-mihai-2026`); autorul articolelor e `ana` |

Articolele: 1 „Primul meu program în Python” (14.09.2026, Programare, python), 2 „De ce am ales Django”
(02.10.2026, Programare, python+django), 3 „O plimbare prin Cluj” (20.10.2026, Călătorii, cluj).
Comentarii: „Foarte bun articol!” (Mihai, 3 octombrie, la 2), „Și eu iubesc Clujul! Grădina Botanică merită.”
(Mihai, 21 octombrie, la 3).

Ce date se încarcă la începutul fiecărei lecții (starea **de pornire**, nu cea finală):

| Lecția | `pregatire` |
|---|---|
| 45–50 | nimic (la 50 lecția creează modelul și rulează ea `migrate`) |
| 51, 52, 53 | `migrate -v 0 && loaddata /lectii/_blog/date/50.json -v 0` |
| 54, 55, 56, 57 | `migrate -v 0 && loaddata /lectii/_blog/date/53.json -v 0` |
| 58, 59, 60, 61 | `migrate -v 0 && loaddata /lectii/_blog/date/57.json -v 0` |

La 51, 53 și 57 lecția își face singură migrarea nouă (`makemigrations` + `migrate`). La 57, utilizatorii nu
există încă în baza de date: lecția îi creează vizibil (`createsuperuser --noinput` cu
`DJANGO_SUPERUSER_PASSWORD`, sau `User.objects.create_user` în `manage.py shell`).

## Ce vede browserul: `vezi_pagina.py`

```text
<!-- comanda: python /h/vezi_pagina.py /articol/2/ -->
<!-- comanda: python /h/vezi_pagina.py --html / -->
<!-- comanda: python /h/vezi_pagina.py POST /articol/2/comentariu/ autor=Mihai 'text=Bravo!' -->
<!-- comanda: python /h/vezi_pagina.py --user ana /articol/nou/ -->
<!-- comanda: python /h/vezi_pagina.py --follow POST /contact/ nume=Mihai email=mihai@exemplu.ro 'mesaj=Salut, Ana!' -->
```

Prima linie e statusul (`200 OK`, `302 Found` + `Location:`), apoi textul vizibil (câmpurile apar ca
`[câmp: nume]`), sau JSON-ul indentat pentru `/api/`. Atenție:
- clientul de test **nu servește fișiere statice** (`/static/...` dă 404 în vezi_pagina, deși merge cu
  `runserver`); la 49 folosește `python manage.py findstatic articole/stil.css` sau `--html` pentru `<link>`;
- erorile 404/500 cu `DEBUG = True` afișează pagina detaliată a Django, iar Django scrie pe stderr un rând
  `Not Found: /cale/` înaintea răspunsului (apare în output);
- `runserver` nu se poate rula în verificare (nu se oprește): arată-l într-un bloc ```` ```bash ```` nerulat.

## Probleme cunoscute (de rezolvat în unelte, nu în lecții)

- Rezolvate: normalizarea `SECRET_KEY` cu ghilimele duble (`verifica_lectie.py`); rândurile rupte și celulele de
  tabel lipite în `vezi_pagina.py` (celulele apar acum separate prin „ | ”).

## Lecție cu lecție

Fișierele schimbate față de etapa anterioară (+ nou, ~ modificat) și ce merită arătat cu output verificat.

### 45 — Proiect și aplicații
- + toate fișierele din `startproject` și `startapp`; `blog_proiect/settings.py`: `"articole"` adăugat în `INSTALLED_APPS`.
- `ruleaza`: `django-admin startproject blog_proiect .`, `python manage.py startapp articole`, `find . -name "*.py" | sort`, `python manage.py check`.
- `comanda`: `vezi_pagina.py /` → pagina de bun venit a Django („The install worked successfully!”).
- `settings.py` generat are 123 de rânduri; modificarea e un rând în `INSTALLED_APPS`, dar comparația cere fișierul întreg.

### 46 — settings.py
- ~ `blog_proiect/settings.py`: rescris compact, cu comentarii în română; `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` din variabile de mediu (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`); `LANGUAGE_CODE = "ro"`, `TIME_ZONE = "Europe/Bucharest"`; ghilimele duble.
- `ruleaza`: `python manage.py shell -c "from django.conf import settings; print(settings.DEBUG)"`, și cu `DJANGO_DEBUG=0` în față; `python manage.py diffsettings | grep LANGUAGE`.

### 47 — URL-uri și view-uri
- ~ `blog_proiect/urls.py` (`include("articole.urls")`), + `articole/urls.py`, ~ `articole/views.py` (lista `ARTICOLE`, funcția `gaseste`, view-urile `lista` și `detaliu` cu `HttpResponse`).
- `comanda`: `/`, `/articol/2/`, `/articol/9/` (404 cu `Http404`), `/articol/abc/` (404: nu se potrivește cu `<int:nr>`).

### 48 — Template-uri
- ~ `views.py` (`render`, + `despre`), ~ `articole/urls.py` (+ `despre/`), + `base.html`, `lista.html`, `_meta.html`, `detaliu.html`, `despre.html`.
- `comanda`: `/` (lista cu date „2 octombrie 2026” și `truncatewords`), `/articol/2/` (`linebreaks` → paragrafe), `/despre/`, `--html /articol/2/` pentru `{% extends %}`. Escaparea automată se poate arăta cu `python manage.py shell -c` și `Template(...).render(...)`.

### 49 — Fișiere statice
- ~ `base.html` (`{% load static %}` + `<link>`), + `articole/static/articole/stil.css`.
- `ruleaza`: `python manage.py findstatic articole/stil.css`; `comanda`: `--html /` (se vede `href="/static/articole/stil.css"`).

### 50 — Modele
- ~ `articole/models.py` (`Articol`: `titlu`, `continut`, `data_publicarii`; `Meta`, `__str__`), + `articole/migrations/0001_initial.py`.
- `ruleaza`: `makemigrations`, `migrate`, `python manage.py shell -c "..."` (creare + `Articol.objects.all()`). View-urile citesc încă din listă.

### 51 — Migrări
- ~ `models.py` (+ `publicat = models.BooleanField(default=True)`), + `0002_articol_publicat.py`.
- `ruleaza`: `showmigrations articole`, `makemigrations`, `sqlmigrate articole 0002`, `migrate`, `showmigrations`; o problemă comună (ex. `makemigrations --check`).

### 52 — Interogări cu ORM
- ~ `views.py` (ORM: `filter(publicat=True)`, `get_object_or_404`; lista `ARTICOLE` dispare).
- `ruleaza`: `manage.py shell -c` cu `all`, `filter`, `get`, `exclude`, `__contains`, `__gte`, `order_by`, `count`, `Articol.DoesNotExist`, `create`/`update`/`delete`, `str(qs.query)` pentru lene; `comanda`: `/`, `/articol/3/`, `/articol/99/` (404).

### 53 — Relații între modele
- ~ `models.py` (+ `Categorie`, `Eticheta`, `Comentariu`; `Articol.categorie`, `Articol.etichete`, `get_absolute_url`), + `0003_…_and_more.py`, ~ `views.py` (`select_related("categorie")`), ~ `detaliu.html` (etichete + secțiunea de comentarii).
- `ruleaza`: crearea categoriilor/etichetelor/comentariilor în shell, `categorie.articole.all()`, `articol.comentarii.count()`; `comanda`: `/articol/2/`. OneToOneField și `prefetch_related` doar explicate.

### 54 — Panoul de admin
- ~ `articole/admin.py` (`ArticolAdmin` cu `list_display`, `list_filter`, `search_fields`, inline de comentarii; `ComentariuAdmin`; `Categorie`, `Eticheta` simplu).
- `ruleaza`: `DJANGO_SUPERUSER_PASSWORD=... python manage.py createsuperuser --noinput --username ana --email ana@exemplu.ro`; `comanda`: `--user ana /admin/articole/articol/`, `--user ana "/admin/articole/articol/?q=Django"`.

### 55 — Formulare
- + `articole/forms.py` (`ContactForm`), ~ `views.py` (+ `contact`, POST-redirect-GET, `messages`), ~ `articole/urls.py` (+ `contact/`), + `contact.html`, ~ `base.html` (link Contact + mesajele).
- `comanda`: `/contact/`; `POST /contact/ nume=Mihai email=gresit mesaj=Hi` (200 cu erori); `--follow POST ...` valid (mesajul „Mulțumim, Mihai! …”).

### 56 — ModelForm
- ~ `forms.py` (+ `ComentariuForm`, `ArticolForm` cu `clean_titlu`), ~ `views.py` (+ `adauga_comentariu`, `articol_nou`, `articol_editeaza`), ~ `urls.py`, ~ `base.html` (link „Scrie un articol”), ~ `detaliu.html` (formularul de comentariu, link de editare), + `formular_articol.html`.
- `comanda`: `POST /articol/2/comentariu/ autor=Mihai 'text=...'` (302 → `/articol/2/#comentarii`), apoi `/articol/2/`; comentariu gol (200 cu erori); `POST /articol/nou/` cu titlu numai majuscule (eroarea proprie); editare.

### 57 — Autentificare
- ~ `models.py` (+ `Articol.autor`), + `0004_articol_autor.py`, ~ `views.py` (`@login_required`, autorul = `request.user`, `PermissionDenied`, + `inregistrare` cu `UserCreationForm` și `login()`), ~ `articole/urls.py` (+ `conturi/inregistrare/`), ~ `admin.py` (autor în listă și filtre), ~ `blog_proiect/urls.py` (+ `conturi/` → `django.contrib.auth.urls`), ~ `settings.py` (+ `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`), ~ `base.html` (meniu după `user.is_authenticated`, logout prin POST), ~ `_meta.html` (autorul), ~ `detaliu.html` (editare doar pentru autor), + `registration/login.html`, `registration/inregistrare.html`.
- `comanda`: `/articol/nou/` fără cont (302 → `/conturi/login/?next=/articol/nou/`), `--user ana /articol/nou/`, `--user mihai /articol/1/editeaza/` (403), `POST /conturi/login/ username=ana password=...` (302); cookie-urile/sesiunea explicate.

### 58 — Class-based views
- ~ `views.py` (rescris: `ListaArticole`, `DetaliuArticol`, `ArticolNou`, `ArticolEditeaza`, `ArticolSterge`, `Despre`, `Contact`; mixin propriu `DoarAutorul`; `adauga_comentariu` și `inregistrare` rămân funcții), ~ `urls.py` (`.as_view()`, + `sterge/`), ~ `detaliu.html` (+ link de ștergere), + `confirma_stergere.html`. Template-urile existente rămân neschimbate (`template_name`, `context_object_name`, `pk_url_kwarg = "nr"`).
- `comanda`: aceleași pagini ca înainte (același rezultat), `--user ana /articol/1/sterge/`, `--user mihai /articol/1/sterge/` (403).

### 59 — Testarea în Django
- ~ `articole/tests.py` (13 teste: modele, listă, detaliu, comentarii, autentificare, editare, formular), cu `setUpTestData`.
- `ruleaza`: `python manage.py test`, `python manage.py test articole.tests.ListaTests -v 2`, un test stricat intenționat (output de eșec). Fixture-urile (`fixtures = [...]`) doar explicate.

### 60 — API-uri cu Django REST Framework
- + `articole/serializers.py`, + `articole/api.py` (`ArticolViewSet`, permisiunea `EsteAutorulSauDoarCitire`), ~ `urls.py` (`DefaultRouter`, `api/`), + `articole/tests_api.py` (4 teste; `manage.py test` rulează acum 17), ~ `settings.py` (+ `"rest_framework"`).
- `comanda`: `/api/articole/`, `/api/articole/2/`, `POST /api/articole/ titlu=Nou continut=Text` (403), `--user mihai POST ...` (201, `"autor": "mihai"`); `ruleaza`: `python manage.py test`.

### 61 — Publicarea aplicației
- ~ `settings.py` (`CSRF_TRUSTED_ORIGINS`, WhiteNoise în `MIDDLEWARE`, `STATIC_ROOT`, `STORAGES`, `DJANGO_DB_PATH`, blocul `if not DEBUG:` cu HTTPS/HSTS/cookie-uri sigure), + `requirements.txt`.
- `ruleaza`: `python manage.py check --deploy` fără variabile (avertismente) și cu `DJANGO_DEBUG=0 DJANGO_SECRET_KEY=... DJANGO_ALLOWED_HOSTS=blogul-anei.ro` (fără probleme); `collectstatic --noinput`; `gunicorn --check-config blog_proiect.wsgi`. Pornirea reală a lui `gunicorn` și HTTPS doar ilustrative.

## Verificare

```bash
python tools/verifica_blog.py          # toate etapele: check, makemigrations --check, migrate, date, teste, pagini
python tools/verifica_blog.py 57 58    # doar unele
```
