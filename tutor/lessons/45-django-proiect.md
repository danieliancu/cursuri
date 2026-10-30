## Ce este

**Django** este un **framework web** pentru Python: o colecție mare de cod gata scris, plus reguli despre cum îți organizezi propriul cod, ca să construiești site-uri fără să pornești de la zero. La lecția 43 ai scris de mână un mic server HTTP, care primea o cerere și trimitea înapoi un răspuns. Django face același lucru, dar îți dă deja tot ce se repetă în orice site: potrivirea adreselor, pagini construite din șabloane, baza de date, formulare, conturi de utilizator, un panou de administrare.

Codul unui site Django se împarte în două niveluri:
- **proiectul**: întregul site, cu setările lui (limba, baza de date, ce aplicații folosește) și adresele principale;
- **aplicațiile** (în engleză „apps”): bucăți de funcționalitate, fiecare într-un folder separat. Blogul nostru va avea aplicația `articole`; un magazin ar putea avea `produse`, `cos` și `comenzi`.

Un proiect conține una sau mai multe aplicații. În lecțiile 45–61 vom construi un singur proiect, **blogul Anei**, pe care l-ai scris de mână în HTML la lecția 44.

## De ce contează

Pagina din lecția 44 era statică: ca să adaugi un articol, copiai HTML-ul și schimbai textul de mână. Un blog adevărat are nevoie de articole salvate într-o bază de date, de o singură „machetă” pentru toate paginile, de formulare pentru comentarii și de autentificare pentru autori. Le poți scrie pe toate singur, dar ar dura luni, iar greșelile de securitate ar fi aproape sigure.

Django e folosit de site-uri foarte mari (Instagram a pornit pe Django), dar e și un instrument excelent de învățat: tot ce ai învățat în cursul de Python (funcții, clase, module, dicționare, decoratori) apare acum în cod real.

Primul pas e mereu același: creezi proiectul, creezi aplicația și o anunți proiectului. Asta facem în lecția de azi.

## Cum funcționează

### Un proiect PyTutor separat: `blog`

Toate lecțiile Django lucrează la **același** blog, care crește de la o lecție la alta. De aceea nu îl scrii în folderul capitolului, ca până acum, ci într-un proiect PyTutor separat:

1. apasă butonul **+** de lângă numele proiectului, sus, și creează proiectul `blog`;
2. lucrează de acum în proiectul `blog` la toate lecțiile Django (45–61).

Terminalul pornește mereu în rădăcina proiectului curent. Toate comenzile din lecții se rulează de acolo, exact cum sunt scrise.

### Crearea proiectului: `django-admin startproject`

Django e deja instalat în terminalul PyTutor. Proiectul se creează cu o singură comandă:

<!-- ruleaza -->
```bash
django-admin startproject blog_proiect .
find . -type f | sort
```

```text
./blog_proiect/__init__.py
./blog_proiect/asgi.py
./blog_proiect/settings.py
./blog_proiect/urls.py
./blog_proiect/wsgi.py
./manage.py
```

`django-admin startproject blog_proiect .` înseamnă: „creează un proiect numit `blog_proiect`, aici”. Punctul de la final e important: pune proiectul în folderul curent, adică în rădăcina proiectului `blog`. A doua comandă, `find`, doar listează fișierele create.

Ce a apărut:
- **`manage.py`**: „telecomanda” proiectului. Toate comenzile Django de acum încolo încep cu `python manage.py ...`;
- **folderul `blog_proiect/`**: configurația proiectului, adică un pachet Python (are `__init__.py`, lecția 29):
  - `settings.py`: setările (lecția 46);
  - `urls.py`: adresele principale ale site-ului (lecția 47);
  - `wsgi.py` și `asgi.py`: punctele de intrare pentru serverele de producție (lecția 61). Deocamdată nu le atingi.

### Crearea aplicației: `startapp`

<!-- ruleaza -->
```bash
python manage.py startapp articole
find articole -type f | sort
```

```text
articole/__init__.py
articole/admin.py
articole/apps.py
articole/migrations/__init__.py
articole/models.py
articole/tests.py
articole/views.py
```

Fiecare fișier are un rol pe care îl vei învăța pe rând:
- `views.py`: funcțiile care primesc o cerere și întorc o pagină (lecția 47);
- `models.py`: forma datelor salvate în baza de date (lecția 50);
- `migrations/`: istoricul schimbărilor din baza de date (lecția 51);
- `admin.py`: panoul de administrare (lecția 54);
- `tests.py`: testele (lecția 59);
- `apps.py`: descrierea aplicației, pentru Django.

Numele aplicației e la plural și descrie ce conține (`articole`), ca orice nume bun de modul.

### Aplicația trebuie anunțată proiectului

Un folder creat cu `startapp` nu e folosit automat. Proiectul are în `settings.py` lista `INSTALLED_APPS`, cu toate aplicațiile active. Primele șase sunt aplicațiile incluse în Django (administrare, autentificare, tipuri de conținut, sesiuni, mesaje, fișiere statice). La finalul listei adaugi aplicația ta:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "articole",
]
```

Fără acest rând, Django nu găsește template-urile, modelele și migrările aplicației. Erorile apar abia mai târziu și par fără legătură, de aceea e bine să-l adaugi imediat. Fișierul complet, cu singura modificare (rândul `"articole"`), e în exemplul complet.

### `python manage.py check`

`check` verifică proiectul fără să-l pornească: setările, aplicațiile, adresele. E primul lucru pe care îl rulezi când ceva nu merge:

<!-- ruleaza -->
```bash
python manage.py check
```

```text
System check identified no issues (0 silenced).
```

Mesajele lui Django sunt în engleză: „verificarea sistemului nu a găsit nicio problemă”. La lecția 46 vom trece site-ul pe limba română, dar comenzile din terminal rămân în engleză.

### Pornirea serverului: `runserver`

Serverul de dezvoltare pornește cu:

```bash
python manage.py runserver 0.0.0.0:8000
```

```text
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
October 29, 2026 - 14:05:12
Django version 5.2.18, using settings 'blog_proiect.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.

WARNING: This is a development server. Do not use it in a production setting. Use a production WSGI or ASGI server instead.
For more information on production servers see: https://docs.djangoproject.com/en/5.2/howto/deployment/
```

În PyTutor:
- `0.0.0.0:8000` înseamnă „ascultă pe portul 8000, accesibil și din afara mediului izolat”. Adresa la care deschizi site-ul în browser e cea din bara terminalului („server: localhost:…”), nu `127.0.0.1:8000`, unde rulează chiar PyTutor;
- serverul rulează până îl oprești cu **Oprește** sau Ctrl+C, la fel ca serverul din lecția 43;
- avertismentul despre migrări e normal deocamdată: tabelele bazei de date le creăm la lecțiile 50–51;
- avertismentul de la final („WARNING”) spune că `runserver` e doar un server de dezvoltare, nu unul pentru un site public. Pentru învățat e exact ce trebuie; serverul de producție vine la lecția 61.

Un lucru foarte comod: serverul **se repornește singur** când salvezi un fișier `.py` („Watching for file changes”). Îl lași pornit și doar reîncarci pagina în browser.

### Ce se întâmplă „pe dedesubt”

`manage.py` e un program Python obișnuit, de câteva rânduri. El îi spune lui Django unde sunt setările (prin variabila de mediu `DJANGO_SETTINGS_MODULE = "blog_proiect.settings"`), apoi rulează comanda cerută. Fiind un fișier ca oricare altul, `python manage.py` îl caută în folderul curent: de aceea comenzile merg doar din folderul care conține `manage.py`.

Când browserul cere o pagină, drumul e același ca la serverul tău din lecția 43, doar că fiecare pas e făcut de Django:
1. serverul primește cererea HTTP;
2. Django caută adresa în `urls.py` (lecția 47);
3. apelează funcția potrivită din `views.py`, care construiește răspunsul;
4. serverul trimite răspunsul înapoi browserului.

Deocamdată `urls.py` conține doar adresa `admin/`. Când nu ai definit nicio altă adresă și `DEBUG` e pornit, Django afișează la `/` o pagină de bun venit.

## Exemplu complet

Proiectul și aplicația sunt create. Rămâne să anunți aplicația în `settings.py`. Iată fișierul complet, așa cum l-a generat `startproject`, cu singurul rând adăugat de tine (`"articole"`, la finalul lui `INSTALLED_APPS`). Nu trebuie să-l înțelegi tot acum: lecția 46 îl ia pe rând.

<details>
<summary>Fișierul complet <code>blog_proiect/settings.py</code></summary>

<!-- fisier: blog_proiect/settings.py -->
```python
"""
Django settings for blog_proiect project.

Generated by 'django-admin startproject' using Django 5.2.18.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-oq()!xicd=9+*7$f0k)vjm28@ne_cz#$rt-8w+^@-zbev_7)k2"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

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


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

</details>

`SECRET_KEY` e generată la întâmplare de `startproject`, deci la tine are altă valoare. E normal.

Verifici din nou proiectul:

<!-- ruleaza -->
```bash
python manage.py check
```

```text
System check identified no issues (0 silenced).
```

Pornești serverul (`python manage.py runserver 0.0.0.0:8000`) și deschizi adresa din bara terminalului. Browserul arată pagina de bun venit a Django:

<!-- comanda: python /h/vezi_pagina.py / -->
```text
200 OK
The install worked successfully! Congratulations!
View release notes for Django 5.2
You are seeing this page because DEBUG=True is in your settings file and you have not configured any URLs.
Django
Django Documentation.
Topics, references, & how-to’s
Tutorial: A Polling App.
Get started with Django
Django Community.
Connect, get help, or contribute
```

`200 OK` e codul de status HTTP din lecția 43: cererea a reușit. Pagina spune exact ce am discutat: `DEBUG` e pornit și n-ai configurat încă nicio adresă. Asta schimbăm la lecția 47.

## Greșeli frecvente

### 1. Nume de proiect sau de aplicație cu cratimă

<!-- ruleaza -->
```bash
django-admin startproject blog-proiect
```

```text
CommandError: 'blog-proiect' is not a valid project name. Please make sure the name is a valid identifier.
```

Proiectul și aplicațiile devin pachete Python, deci numele lor trebuie să fie nume valide de variabilă (lecția 2): litere, cifre și `_`, fără cratime și spații. Același lucru pentru `startapp`: `pagini-noi` e refuzat, `pagini_noi` e corect.

### 2. Uitarea punctului de la `startproject`

Fără `.`, Django creează un folder nou cu numele proiectului și pune totul în el, inclusiv `manage.py`:

<!-- ruleaza -->
```bash
cd /tmp && django-admin startproject blog_proiect && find blog_proiect -type f | sort
```

```text
blog_proiect/blog_proiect/__init__.py
blog_proiect/blog_proiect/asgi.py
blog_proiect/blog_proiect/settings.py
blog_proiect/blog_proiect/urls.py
blog_proiect/blog_proiect/wsgi.py
blog_proiect/manage.py
```

Proiectul merge și așa, dar `manage.py` nu mai e în rădăcină. În PyTutor, unde terminalul pornește mereu din rădăcină, fiecare comandă ar deveni `python blog_proiect/manage.py ...`. Dacă ți s-a întâmplat, șterge folderul creat și rulează din nou comanda, cu punct.

### 3. Comanda rulată de două ori

<!-- ruleaza -->
```bash
django-admin startproject blog_proiect .
```

```text
CommandError: manage.py already exists. Overlaying a project into an existing directory won't replace conflicting files.
```

Proiectul există deja, iar Django refuză să-ți suprascrie fișierele. La fel, `python manage.py startapp articole` a doua oară spune că numele „intră în conflict cu un modul Python existent”: chiar folderul `articole`, creat prima dată. Nu e nimic de reparat: proiectul și aplicația sunt deja create.

### 4. `manage.py` rulat din alt folder

<!-- ruleaza -->
```bash
cd articole && python manage.py check
```

```text
python: can't open file 'articole/manage.py': [Errno 2] No such file or directory
```

Python caută `manage.py` în folderul curent. În PyTutor eroarea apare de obicei când ești în alt proiect decât `blog`: verifică numele proiectului din bara de sus.

### 5. O comandă scrisă greșit

<!-- ruleaza -->
```bash
python manage.py runsrever
```

```text
Unknown command: 'runsrever'. Did you mean runserver?
Type 'manage.py help' for usage.
```

Ca la `NameError` (lecția 2), Django îți sugerează comanda corectă. Lista tuturor comenzilor o vezi cu `python manage.py help`.

## Exercițiu

În proiectul PyTutor `blog`:

1. creează proiectul și aplicația ca în lecție, adaugă `"articole"` în `INSTALLED_APPS` și rulează `python manage.py check`;
2. pornește serverul și deschide pagina de bun venit de la adresa din bara terminalului; oprește-l apoi cu **Oprește**;
3. rulează `python manage.py help` și găsește în listă trei comenzi pe care le-ai întâlnit în lecție;
4. exersează `startapp`: creează o a doua aplicație, `pagini`, adaug-o în `INSTALLED_APPS` și verifică totul cu `check`. La final, șterge-o (folderul `pagini` și rândul din `INSTALLED_APPS`): lecțiile următoare nu o folosesc, iar la lecția 46 vei înlocui oricum tot `settings.py`.

Scrie-i apoi tutorelui, cu cuvintele tale, diferența dintre proiect și aplicație.

## Pe scurt

- Django e un framework web: îți dă gata făcute adresele, șabloanele, baza de date, formularele și conturile.
- Un **proiect** (`django-admin startproject blog_proiect .`) conține setările și adresele site-ului; o **aplicație** (`python manage.py startapp articole`) e o parte din funcționalitate.
- Aplicația devine activă doar după ce o adaugi în `INSTALLED_APPS` din `settings.py`.
- `python manage.py check` verifică proiectul; `python manage.py runserver 0.0.0.0:8000` îl pornește, iar în PyTutor îl deschizi la adresa din bara terminalului.
- Toate comenzile `manage.py` se rulează din folderul cu `manage.py`, adică din rădăcina proiectului `blog`.
- Numele de proiecte și aplicații trebuie să fie nume valide în Python, fără cratime.

<!-- proiect-final: _blog/45 -->
