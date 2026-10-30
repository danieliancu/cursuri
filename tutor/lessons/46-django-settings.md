## Ce este

`blog_proiect/settings.py` este fișierul cu **setările** proiectului: ce aplicații sunt active, ce bază de date se folosește, în ce limbă și în ce fus orar lucrează site-ul, dacă afișează pagini de eroare detaliate și multe altele.

E un modul Python obișnuit (lecția 29), plin de **constante**: nume scrise cu majuscule, cum ai învățat la lecția 40.

```python
DEBUG = True
LANGUAGE_CODE = "ro"
INSTALLED_APPS = ["django.contrib.admin", "articole"]
```

Django citește modulul o singură dată, la pornire, și folosește valorile peste tot. Tu le poți citi la rândul tău, în orice fișier al proiectului, cu `from django.conf import settings`.

## De ce contează

Același cod rulează în mai multe locuri: în PyTutor, pe calculatorul altui programator, pe serverul public al blogului. Codul e identic, dar unele setări diferă:
- pe calculatorul tău vrei `DEBUG = True`, cu pagini de eroare detaliate, ca să vezi exact ce s-a stricat;
- pe serverul public, aceleași pagini ar arăta oricui detalii despre codul tău, deci `DEBUG` trebuie să fie oprit;
- **cheia secretă** (`SECRET_KEY`) nu are voie să ajungă în Git (lecția 42), pentru că oricine o știe poate falsifica datele pe care Django le semnează cu ea (de exemplu, linkurile de resetare a parolei).

Soluția obișnuită: valorile care diferă de la un loc la altul vin din **variabile de mediu**, nu sunt scrise în cod. Asta faci în lecția de azi; în plus, treci blogul pe limba română și pe ora României.

## Cum funcționează

### Setările importante

Fișierul generat de `startproject` (lecția 45) are peste 100 de rânduri, dar multe sunt comentarii. Iată setările pe care le vei folosi, pe scurt:

| Setare | Ce stabilește | Unde o folosim |
|---|---|---|
| `BASE_DIR` | folderul proiectului (cel cu `manage.py`), ca `Path` (lecția 27) | căile spre baza de date și fișiere |
| `SECRET_KEY` | cheia cu care Django semnează datele care nu trebuie falsificate (sesiuni, linkuri de resetare a parolei) | lecția 61 |
| `DEBUG` | pagini de eroare detaliate (da/nu) | acum |
| `ALLOWED_HOSTS` | numele de domeniu la care răspunde site-ul | lecția 61 |
| `INSTALLED_APPS` | aplicațiile active | lecția 45 |
| `MIDDLEWARE` | „straturile” prin care trece fiecare cerere (sesiuni, securitate, autentificare) | lecția 57 |
| `ROOT_URLCONF` | modulul cu adresele principale | lecția 47 |
| `TEMPLATES` | unde caută Django șabloanele HTML | lecția 48 |
| `DATABASES` | baza de date: aici, un fișier SQLite, `db.sqlite3` | lecția 50 |
| `LANGUAGE_CODE`, `TIME_ZONE` | limba și fusul orar | acum |
| `STATIC_URL` | adresa fișierelor CSS și a imaginilor | lecția 49 |

### Valori din variabile de mediu

O **variabilă de mediu** e o pereche nume–valoare pe care sistemul de operare o dă fiecărui program pornit. Python le vede în dicționarul `os.environ` (modulul `os`, lecția 31). Cu `get()` (lecția 14) iei valoarea sau, dacă variabila lipsește, o valoare de rezervă:

```python
import os

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
```

Variabilele de mediu sunt întotdeauna **text**, la fel ca rezultatul lui `input()` (lecția 6). De aceea:
- `DEBUG` compară textul cu `"1"`, iar rezultatul e un `bool`: `True` doar dacă textul e exact `"1"`;
- `ALLOWED_HOSTS` sparge textul după virgulă cu `split()` (lecția 4) și obține o listă.

Fără nicio variabilă setată, primești valorile de rezervă, potrivite pentru dezvoltare. Pe server (lecția 61) setezi variabilele și obții setările de producție, fără să schimbi codul. Tot acolo vom lua din mediu și calea bazei de date.

### Setările blogului, rescrise

Rescriem acum `settings.py` mai scurt, cu comentarii în română, cu valorile sensibile luate din variabile de mediu și cu limba română și ora României. Restul setărilor rămân la fel ca în fișierul generat.

<!-- fisier: blog_proiect/settings.py -->
```python
"""Setările proiectului blog_proiect.

Toate setările posibile: https://docs.djangoproject.com/en/5.2/ref/settings/
"""
import os
from pathlib import Path

# Folderul proiectului (cel cu manage.py); celelalte căi pornesc de aici.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cheia secretă semnează sesiunile și alte date care nu trebuie falsificate. În producție vine
# dintr-o variabilă de mediu (lecția 61); valoarea de rezervă e bună doar pe calculatorul tău.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-doar-pentru-dezvoltare-locala")

# DEBUG pornit afișează pagini de eroare detaliate. DJANGO_DEBUG=0 îl oprește.
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# Numele de domeniu la care răspunde site-ul, separate prin virgulă.
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "articole",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "blog_proiect.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "blog_proiect.wsgi.application"

# Baza de date: un singur fișier SQLite, potrivit pentru dezvoltare.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Limba și fusul orar: datele și mesajele generate de Django apar în română.
LANGUAGE_CODE = "ro"
TIME_ZONE = "Europe/Bucharest"
USE_I18N = True
USE_TZ = True

# Fișierele statice (CSS, imagini) sunt servite de la această adresă.
STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

### Setarea unei variabile în terminal

În terminal, scrii variabila **în fața comenzii**, iar ea există doar pentru acea comandă:

```bash
DJANGO_DEBUG=0 python manage.py check
```

### Citirea setărilor din cod

Orice parte a proiectului citește setările prin `django.conf.settings`, niciodată importând direct `blog_proiect.settings`. Ca să încerci rapid, `python manage.py shell -c "..."` rulează câteva rânduri de Python în proiect (`-v 0` ascunde mesajele lui Django despre ce a importat):

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c "from django.conf import settings; print(settings.DEBUG)"
DJANGO_DEBUG=0 python manage.py shell -v 0 -c "from django.conf import settings; print(settings.DEBUG)"
```

```text
True
False
```

Aceeași linie de cod, două rezultate, în funcție de mediu.

### Fișierul `.env`

La lecția 42 ai pus `.env` în `.gitignore`: e fișierul în care mulți programatori își țin variabilele de mediu locale. Atenție însă: **Django nu citește singur fișierul `.env`**. Există pachete care fac asta (de exemplu `python-dotenv`), iar platformele de găzduire îți dau o pagină unde setezi variabilele (lecția 61). În PyTutor nu ai nevoie de el: valorile de rezervă din `settings.py` sunt cele pentru dezvoltare.

### `DEBUG`: două pagini de eroare

Cu `DEBUG` pornit, o adresă inexistentă arată o pagină detaliată, cu lista adreselor încercate:

<!-- comanda: python /h/vezi_pagina.py /nu-exista/ -->
```text
Not Found: /nu-exista/
404 Not Found
Page not found (404)
Request Method: | GET
Request URL: | http://testserver/nu-exista/
Using the URLconf defined in blog_proiect.urls, Django tried these URL patterns, in this order:
admin/
The current path, nu-exista/, didn’t match any of these.
You’re seeing this error because you have DEBUG = True in your Django settings file. Change that to False, and Django will display a standard 404 page.
```

(Primul rând, `Not Found: /nu-exista/`, e mesajul pe care serverul îl scrie în terminal, nu face parte din pagină. În restul textului, „ | ” desparte celulele unui rând de tabel: în browser, „Request Method:” și „GET” stau în coloane alăturate.)

Cu `DEBUG` oprit, vizitatorul vede doar un mesaj scurt, fără niciun detaliu despre cod:

<!-- comanda: DJANGO_DEBUG=0 python /h/vezi_pagina.py /nu-exista/ -->
```text
404 Not Found
Not Found
The requested resource was not found on this server.
```

Pagina detaliată e foarte utilă pentru tine și periculoasă pe un site public. De aceea `DEBUG` vine dintr-o variabilă de mediu.

### Ce se întâmplă „pe dedesubt”

`manage.py` setează variabila de mediu `DJANGO_SETTINGS_MODULE = "blog_proiect.settings"`. La pornire, Django importă acel modul și păstrează toate numele scrise **cu majuscule** ca setări. Restul (`os`, `Path`, variabilele cu litere mici) sunt ignorate.

Setările se citesc o singură dată. Dacă modifici `settings.py` cu serverul pornit, `runserver` observă schimbarea și se repornește singur. Pentru variabilele de mediu, însă, trebuie să oprești serverul și să-l pornești din nou cu noile valori.

Django are valori implicite pentru sute de setări. Comanda `diffsettings` îți arată doar ce ai schimbat tu față de ele.

## Exemplu complet

Cu noul `settings.py` (din „Cum funcționează”), verifici proiectul și ce ai schimbat față de valorile implicite ale Django:

<!-- ruleaza -->
```bash
python manage.py check
python manage.py diffsettings | grep -E "^(DEBUG|ALLOWED_HOSTS|LANGUAGE_CODE|TIME_ZONE)"
DJANGO_DEBUG=0 DJANGO_ALLOWED_HOSTS=blogul-anei.ro python manage.py diffsettings | grep -E "^(DEBUG|ALLOWED_HOSTS)"
```

```text
System check identified no issues (0 silenced).
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
DEBUG = True
LANGUAGE_CODE = 'ro'
TIME_ZONE = 'Europe/Bucharest'
ALLOWED_HOSTS = ['blogul-anei.ro']
```

(`grep -E` păstrează doar rândurile care încep cu numele date, ca output-ul să fie scurt.)

La a doua rulare, `DEBUG` nu mai apare deloc: `False` e chiar valoarea implicită a Django, iar `diffsettings` arată doar ce diferă de ea.

Și pagina de bun venit e acum în română:

<!-- comanda: python /h/vezi_pagina.py / -->
```text
200 OK
Instalarea a funcționat cu succes! Felicitări!
Vezi notele de lansare pentru Django 5.2
Vedeți această pagină deoarece DEBUG=True este în fișierul de setări și nu ați configurat niciun URL.
Django
Documentația Django.
Topics, references, & how-to’s
Tutorial: O aplicație de votare.
Începeți cu Django
Comunitatea Django.
Conectați-vă, obțineți ajutor sau contribuiți
```

Traducerea vine chiar din Django; câteva texte nu sunt încă traduse, de aceea un rând a rămas în engleză.

## Greșeli frecvente

### 1. O virgulă lipsă în `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    "django.contrib.staticfiles"
    "articole",
]
```

Python lipește automat două stringuri scrise unul lângă altul, fără virgulă între ele. Lista conține astfel un singur nume, inexistent:

<!-- comanda: cp -r . /tmp/p && cd /tmp/p && sed -i "s/\"django.contrib.staticfiles\",/\"django.contrib.staticfiles\"/" blog_proiect/settings.py && python manage.py check -->
```text
Traceback (most recent call last):
ModuleNotFoundError: No module named 'django.contrib.staticfilesarticole'
```

Am scurtat tracebackul: la tine are vreo 20 de rânduri, aproape toate din codul Django (lecția 23). Ultimul rând spune tot: numele modulului e cele două nume lipite. Pune virgula și obișnuiește-te să o pui și după ultimul element al listei.

### 2. `DEBUG` citit ca text

```python
import os

os.environ["DJANGO_DEBUG"] = "0"
DEBUG = os.environ.get("DJANGO_DEBUG", True)
print(repr(DEBUG), bool(DEBUG))
```

<!-- comanda: python -c 'import os; os.environ["DJANGO_DEBUG"] = "0"; DEBUG = os.environ.get("DJANGO_DEBUG", True); print(repr(DEBUG), bool(DEBUG))' -->
```text
'0' True
```

Variabila e setată la `"0"`, dar `DEBUG` primește **textul** `"0"`, care nu e gol, deci e considerat adevărat (lecția 7). Site-ul ar rula cu `DEBUG` pornit tocmai pe server. Compară explicit: `os.environ.get("DJANGO_DEBUG", "1") == "1"`.

### 3. Numele unei setări scris greșit

Dacă scrii `LANGUAGE_COD = "ro"` în loc de `LANGUAGE_CODE`, Django nu dă nicio eroare:

<!-- comanda: cp -r . /tmp/p && cd /tmp/p && sed -i "s/^LANGUAGE_CODE/LANGUAGE_COD/" blog_proiect/settings.py && python manage.py check && python /h/vezi_pagina.py / | sed -n 1,2p -->
```text
System check identified no issues (0 silenced).
200 OK
The install worked successfully! Congratulations!
```

`LANGUAGE_COD` e doar o constantă în plus, pe care Django nu o folosește, iar `LANGUAGE_CODE` rămâne la valoarea implicită, engleza. Când o setare „nu are efect”, verifică întâi numele cu `diffsettings`.

### 4. Așteptarea ca `.env` să fie citit automat

Ai creat un fișier `.env` cu rândul `DJANGO_DEBUG=0`, dar:

<!-- comanda: cp -r . /tmp/p && cd /tmp/p && echo DJANGO_DEBUG=0 > .env && python manage.py shell -v 0 -c "from django.conf import settings; print(settings.DEBUG)" -->
```text
True
```

Django nu știe de fișierul `.env`. Variabila trebuie setată în mediu: în fața comenzii (`DJANGO_DEBUG=0 python manage.py ...`), în setările serverului (lecția 61) sau cu un pachet ca `python-dotenv`.

## Exercițiu

În proiectul PyTutor `blog`, înlocuiește `settings.py` cu varianta din secțiunea „Setările blogului, rescrise”, apoi:

1. rulează `python manage.py check` și `python manage.py diffsettings`; numără câte setări ai schimbat față de valorile implicite;
2. pornește serverul și verifică pagina de bun venit în română; deschide apoi o adresă inexistentă, de exemplu `/nimic/`, și citește pagina de eroare;
3. oprește serverul și pornește-l din nou cu `DJANGO_DEBUG=0 python manage.py runserver 0.0.0.0:8000`; deschide aceeași adresă. Ce s-a schimbat? (La `/` vei primi tot o eroare 404: pagina de bun venit apare doar cu `DEBUG` pornit.)
4. cu `python manage.py shell -v 0 -c "..."`, afișează `settings.BASE_DIR` și `settings.TIME_ZONE`.

Lecția 47 adaugă primele pagini ale blogului.

## Pe scurt

- `settings.py` e un modul Python; Django folosește ca setări doar numele scrise cu majuscule.
- În cod citești setările cu `from django.conf import settings`.
- Valorile care diferă între calculatorul tău și server (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`) vin din variabile de mediu: `os.environ.get("NUME", "rezervă")`, iar valoarea e mereu text.
- O variabilă de mediu se setează în fața comenzii: `DJANGO_DEBUG=0 python manage.py ...`; Django nu citește singur fișierul `.env`.
- `DEBUG` pornit afișează pagini de eroare detaliate, bune pentru tine și periculoase pe un site public.
- `python manage.py diffsettings` arată ce ai schimbat față de valorile implicite; o setare cu nume greșit e ignorată fără eroare.

<!-- proiect: _blog/45 -->
<!-- proiect-final: _blog/46 -->
