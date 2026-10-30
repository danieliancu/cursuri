<!-- proiect: _blog/60 -->
<!-- proiect-final: _blog/61 -->
<!-- pregatire: python manage.py migrate -v 0 && python manage.py loaddata /lectii/_blog/date/57.json -v 0 -->
## Ce este

**Publicarea** (în engleză „deployment”) înseamnă să pui aplicația pe un **server**, un calculator mereu pornit și conectat la internet, ca oricine să deschidă blogul Anei la o adresă ca `https://blogul-anei.ro`.

Codul blogului rămâne același. Se schimbă felul în care rulează:

| | Pe calculatorul tău (dezvoltare) | Pe server (producție) |
|---|---|---|
| `DEBUG` | pornit: pagini de eroare detaliate | **oprit**: vizitatorii nu văd cod și setări |
| `SECRET_KEY` | o valoare scrisă în cod | o valoare lungă, aleatoare, **secretă** |
| `ALLOWED_HOSTS` | `localhost` | domeniul tău, `blogul-anei.ro` |
| Serverul web | `runserver` | **gunicorn** |
| Fișierele statice | servite de `runserver` | adunate cu `collectstatic`, servite de **WhiteNoise** |
| Adresa | `http://` | **`https://`** |
| Baza de date | `db.sqlite3` din proiect | un loc sigur sau **PostgreSQL** |

Toate diferențele vin din **variabile de mediu** (lecția 46): același `settings.py` se comportă diferit pe server, fără ca secretele să apară în cod.

## De ce contează

Un site care rulează doar pe calculatorul tău nu-l vede nimeni. Iar o aplicație publicată greșit e periculoasă: cu `DEBUG` pornit, orice eroare afișează oricui fragmente din cod și din setări; cu cheia secretă din cod (care ajunge pe GitHub, lecția 42), oricine poate falsifica datele pe care Django le semnează cu ea (de exemplu linkurile de resetare a parolei) și poate ajunge să intre în contul Anei. `runserver` e făcut pentru dezvoltare: Django însuși avertizează că nu e potrivit pentru producție.

Vestea bună: Django are o listă de verificare automată pentru producție, iar câteva setări bine alese rezolvă aproape tot. Lecția asta pregătește blogul Anei pentru publicare și îți arată ce se întâmplă pe server.

Lucrezi tot în proiectul PyTutor **`blog`**.

## Cum funcționează

### Lista de verificare: check --deploy

Comanda `check` (pe care o rulează și `runserver`) are o variantă pentru producție. Pe blogul de acum, ea găsește 6 probleme:

<!-- ruleaza -->
```bash
python manage.py check --deploy
```

```text
System check identified some issues:

WARNINGS:
?: (security.W004) You have not set a value for the SECURE_HSTS_SECONDS setting. If your entire site is served only over SSL, you may want to consider setting a value and enabling HTTP Strict Transport Security. Be sure to read the documentation first; enabling HSTS carelessly can cause serious, irreversible problems.
?: (security.W008) Your SECURE_SSL_REDIRECT setting is not set to True. Unless your site should be available over both SSL and non-SSL connections, you may want to either set this setting True or configure a load balancer or reverse-proxy server to redirect all connections to HTTPS.
?: (security.W009) Your SECRET_KEY has less than 50 characters, less than 5 unique characters, or it's prefixed with 'django-insecure-' indicating that it was generated automatically by Django. Please generate a long and random value, otherwise many of Django's security-critical features will be vulnerable to attack.
?: (security.W012) SESSION_COOKIE_SECURE is not set to True. Using a secure-only session cookie makes it more difficult for network traffic sniffers to hijack user sessions.
?: (security.W016) You have 'django.middleware.csrf.CsrfViewMiddleware' in your MIDDLEWARE, but you have not set CSRF_COOKIE_SECURE to True. Using a secure-only CSRF cookie makes it more difficult for network traffic sniffers to steal the CSRF token.
?: (security.W018) You should not have DEBUG set to True in deployment.

System check identified 6 issues (0 silenced).
```

Pe scurt, în română:

- **W004, W008**: site-ul nu obligă browserele să folosească HTTPS (vezi „HTTPS” mai jos);
- **W009**: cheia secretă e cea de dezvoltare, care începe cu `django-insecure-`;
- **W012, W016**: cookie-urile de sesiune și de CSRF (lecțiile 55 și 57) pot fi trimise și prin `http://`, necriptat;
- **W018**: `DEBUG` e pornit.

Le rezolvăm pe toate în `settings.py`.

### Fișierele statice: collectstatic

Cu `DEBUG` pornit, `runserver` găsește CSS-ul în folderul `static/` al fiecărei aplicații (lecția 49). În producție, fișierele statice se **adună** într-un singur folder cu comanda `collectstatic`, ca serverul să le servească repede. Încearcă acum:

<!-- ruleaza -->
```bash
python manage.py collectstatic --noinput
```

```text
Traceback (most recent call last):
django.core.exceptions.ImproperlyConfigured: You're using the staticfiles app without having set the STATIC_ROOT setting to a filesystem path.
```

(Am scurtat tracebackul.) Django nu știe **unde** să le adune: lipsește setarea `STATIC_ROOT`.

### settings.py pentru producție

Iată `blog_proiect/settings.py` complet, gata de publicare. Noutățile sunt explicate după el.

<!-- fisier: blog_proiect/settings.py -->
```python
"""Setările proiectului blog_proiect.

Toate setările posibile: https://docs.djangoproject.com/en/5.2/ref/settings/
Pe server, valorile sensibile vin din variabile de mediu:
DJANGO_SECRET_KEY, DJANGO_DEBUG=0, DJANGO_ALLOWED_HOSTS, DJANGO_CSRF_TRUSTED_ORIGINS,
DJANGO_DB_PATH.
"""
import os
from pathlib import Path

# Folderul proiectului (cel cu manage.py); celelalte căi pornesc de aici.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cheia secretă semnează sesiunile și alte date care nu trebuie falsificate. Pe server vine din
# DJANGO_SECRET_KEY; valoarea de rezervă e bună doar pe calculatorul tău.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-doar-pentru-dezvoltare-locala")

# DEBUG pornit afișează pagini de eroare detaliate. Pe server: DJANGO_DEBUG=0.
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# Numele de domeniu la care răspunde site-ul, separate prin virgulă.
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Adresele (cu https://) de pe care se pot trimite formulare, separate prin virgulă.
ORIGINI = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o for o in ORIGINI.split(",") if o]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "articole",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise servește fișierele statice direct din aplicație, fără un server separat.
    "whitenoise.middleware.WhiteNoiseMiddleware",
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

# Baza de date: SQLite. Pe server, fișierul stă într-un loc care nu se șterge
# când publici o versiune nouă.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DJANGO_DB_PATH", BASE_DIR / "db.sqlite3"),
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

# Fișierele statice: STATIC_URL e adresa lor, STATIC_ROOT e folderul
# în care le adună `collectstatic`.
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Autentificare: unde trimitem utilizatorul să intre în cont și unde ajunge după login/logout.
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "lista"
LOGOUT_REDIRECT_URL = "lista"

# Producție: doar HTTPS, cookie-uri trimise doar prin HTTPS și HSTS
# (browserul ține minte să folosească HTTPS).
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # HSTS: o oră la început; crește (DJANGO_HSTS_SECONDS) când HTTPS merge peste tot
    SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_HSTS_SECONDS", 60 * 60))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # preload (lista din browsere) e o decizie separată, greu de retras: nu o activăm aici
    SILENCED_SYSTEM_CHECKS = ["security.W021"]
```

Ce e nou:

- **`CSRF_TRUSTED_ORIGINS`**: lista adreselor de pe care se pot trimite formulare, de exemplu `https://blogul-anei.ro`. Django verifică de unde vine fiecare formular (protecția CSRF, lecția 55). De obicei își recunoaște singur domeniul, dar în spatele unui proxy (vezi „HTTPS”) verificarea poate da greș, iar multe platforme de publicare cer de aceea lista explicit. Rândul `[o for o in ORIGINI.split(",") if o]` (lecția 16) transformă textul variabilei într-o listă și sare peste valorile goale;
- **WhiteNoise**, pus imediat după `SecurityMiddleware`: servește fișierele statice direct din aplicația Django, deci nu mai e nevoie de un server separat pentru CSS și imagini. La lecția 49 am spus că fișierele statice sunt servite de obicei de un program specializat (ca nginx); pentru un blog mic, WhiteNoise e mai simplu și suficient de rapid;
- **`DJANGO_DB_PATH`**: pe server, fișierul bazei de date stă într-un folder care nu se șterge când publici o versiune nouă a codului; pe calculatorul tău rămâne `db.sqlite3`;
- **`STATIC_ROOT`**: folderul `staticfiles/` în care `collectstatic` adună totul. **`STORAGES`** îi spune lui WhiteNoise să păstreze și versiuni comprimate ale fișierelor, ca să ajungă mai repede la browser;
- **blocul `if not DEBUG:`** se aplică doar în producție: trimite orice cerere `http://` spre `https://`, trimite cookie-urile doar prin HTTPS și pornește **HSTS** (explicat la „HTTPS”).

Acum `collectstatic` știe unde să adune fișierele:

<!-- ruleaza -->
```bash
python manage.py collectstatic --noinput
```

```text

155 static files copied to 'staticfiles', 146 post-processed.
```

155 de fișiere: CSS-ul blogului, plus fișierele panoului de admin și ale API-ului navigabil (lecția 60). La tine, mesajul arată calea completă a folderului `staticfiles`. Folderul se generează, deci nu se pune în git: adaugă `staticfiles/` în `.gitignore` (lecția 42), împreună cu `db.sqlite3`.

### Variabilele de mediu

Setările citesc valorile din variabile de mediu. Pe server, ele se configurează o singură dată (în panoul platformei sau în fișierul de pornire al serviciului). În terminal, le poți da chiar înaintea comenzii, pe același rând:

<!-- ruleaza -->
```bash
DJANGO_DEBUG=0 DJANGO_SECRET_KEY=o-cheie-lunga-si-aleatoare-de-cel-putin-cincizeci-de-caractere-0123456789 DJANGO_ALLOWED_HOSTS=blogul-anei.ro python manage.py check --deploy
```

```text
System check identified no issues (1 silenced).
```

Nicio problemă. Cheia de mai sus e doar un exemplu: o cheie adevărată o generezi cu Django și n-o scrii nicăieri în cod:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Rezultatul e diferit la fiecare rulare, de exemplu `r9$k0w...` (50 de caractere aleatoare). Cheia conține semne ca `$`, `&` sau `(`, pe care terminalul le interpretează, așa că, scrisă înaintea unei comenzi, o pui între apostrofuri: `DJANGO_SECRET_KEY='r9$k0w...'`.

### requirements.txt

Serverul trebuie să instaleze exact pachetele cu care ai lucrat. Lista lor stă într-un fișier `requirements.txt` (lecția 30). Versiunile instalate le afli cu `pip freeze`:

<!-- ruleaza -->
```bash
pip freeze | grep -i -E "^(django|djangorestframework|gunicorn|whitenoise)=="
pip freeze | wc -l
```

```text
Django==5.2.18
djangorestframework==3.18.3
gunicorn==23.0.0
whitenoise==6.12.0
21
```

`pip freeze` listează 21 de pachete: în terminalul PyTutor sunt instalate și uneltele din lecțiile 40–41 (black, ruff, mypy, pytest), de care blogul nu are nevoie pe server. De aceea scriem lista de mână, doar cu ce folosește blogul, la versiunile exacte (`==`). Fișier nou, `requirements.txt`, în rădăcina proiectului:

<!-- fisier: requirements.txt -->
```txt
Django==5.2.18
djangorestframework==3.18.3
gunicorn==23.0.0
whitenoise==6.12.0
```

Dependențele lor (de exemplu `asgiref` și `sqlparse`, cerute de Django) sunt instalate automat de `pip install -r requirements.txt`.

### gunicorn

`runserver` e un server de dezvoltare: simplu, cu repornire automată, dar lent și netestat pentru atacuri. În producție rulează **gunicorn**, un server WSGI. **WSGI** e regula după care un server web vorbește cu o aplicație Python: fișierul `blog_proiect/wsgi.py`, creat de `startproject` la lecția 45, conține obiectul `application` pe care gunicorn îl pornește. Pe server, comanda arată cam așa (ilustrativ, nu rulează în verificarea lecției):

```bash
gunicorn blog_proiect.wsgi --bind 0.0.0.0:8000 --workers 3
```

`--workers 3` pornește 3 procese, care răspund în paralel la mai mulți vizitatori. gunicorn rulează pe Linux și macOS (deci pe servere și în terminalul PyTutor), nu și direct pe Windows. Fără să pornească serverul, poți verifica măcar că gunicorn găsește aplicația:

<!-- ruleaza -->
```bash
gunicorn --check-config blog_proiect.wsgi && echo "gunicorn: configurația e în regulă"
```

```text
gunicorn: configurația e în regulă
```

### Baza de date în producție

Pentru un blog mic, SQLite e suficient, cu condiția ca fișierul să stea într-un loc sigur (`DJANGO_DB_PATH`) și să faci copii de siguranță. Atenție: pe multe platforme de publicare, fișierele aplicației se șterg la fiecare publicare sau repornire; acolo SQLite merge doar pe un disc păstrat separat (un „volum” persistent), altfel ai nevoie de PostgreSQL. Când mulți utilizatori scriu în același timp, se folosește un server de baze de date, de obicei **PostgreSQL**. Codul și modelele rămân aceleași; se schimbă doar `DATABASES` (exemplu ilustrativ, nefolosit în blog):

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NUME"],
        "USER": os.environ["DB_UTILIZATOR"],
        "PASSWORD": os.environ["DB_PAROLA"],
        "HOST": os.environ["DB_SERVER"],
        "PORT": "5432",
    }
}
```

Pentru PostgreSQL se mai instalează pachetul `psycopg`. Oricare ar fi baza de date, pe server rulezi `python manage.py migrate` după fiecare versiune nouă a codului, ca tabelele să fie la zi (lecția 51).

### HTTPS

La lecția 43 ai văzut că HTTP trimite totul ca text. **HTTPS** e același HTTP, dar **criptat**: nimeni de pe drum (rețeaua Wi-Fi a cafenelei, de exemplu) nu poate citi parolele sau cookie-urile. Pentru HTTPS, serverul are nevoie de un **certificat** pentru domeniul lui. Certificatele gratuite, reînnoite automat (de exemplu prin Let's Encrypt), sunt standardul azi, iar platformele de publicare le configurează de obicei singure.

De obicei, criptarea o face un program aflat **în fața** lui gunicorn (un „reverse proxy”, ca nginx, sau platforma însăși). El primește cererea HTTPS și o trimite mai departe lui gunicorn, cu headerul `X-Forwarded-Proto: https`. De aici vin setările din blocul `if not DEBUG:`:

- `SECURE_PROXY_SSL_HEADER` îi spune lui Django să creadă acel header, ca să știe că cererea originală a fost HTTPS (fără el, Django ar crede că toate cererile vin prin `http://`, iar `SECURE_SSL_REDIRECT` ar redirecționa la nesfârșit). Folosește-l doar dacă proxy-ul tău scrie singur headerul și îl înlocuiește pe cel venit de la vizitator; altfel oricine l-ar putea falsifica;
- `SECURE_SSL_REDIRECT` trimite orice cerere `http://` spre `https://`;
- **HSTS** (`SECURE_HSTS_SECONDS`, o oră aici, configurabilă prin `DJANGO_HSTS_SECONDS`) îi cere browserului să folosească **numai** HTTPS pentru domeniu, chiar dacă cineva scrie `http://`. `SECURE_HSTS_INCLUDE_SUBDOMAINS` extinde regula la toate subdomeniile (`www.`, `api.` ...), iar `SECURE_HSTS_PRELOAD` (pe care nu-l activăm; de aceea avertismentul W021 e oprit cu `SILENCED_SYSTEM_CHECKS`) ar permite înscrierea domeniului în lista încorporată în browsere (doar dacă o ceri explicit, pe hstspreload.org, și cu o durată de cel puțin un an). Atenție: browserul ține minte regula pe toată durata setată și n-o poți retrage de pe server, deci pornește HSTS doar când HTTPS funcționează sigur pe domeniu și pe toate subdomeniile. Documentația Django recomandă să începi cu o durată mică (o oră) și s-o mărești treptat.

### Unde publici

Variantele uzuale:

- **o platformă de publicare** („Platform as a Service”): îi dai codul (de obicei dintr-un repository git, lecția 42) și variabilele de mediu, iar ea instalează pachetele, rulează comenzile de pornire și se ocupă de HTTPS;
- **un server virtual** (VPS) pe care îl administrezi tu: instalezi Python, configurezi nginx, gunicorn ca serviciu al sistemului și certificatul. Mai multă muncă, dar și control complet.

În ambele cazuri, pașii sunt cei din exemplul complet de mai jos.

### Ce se întâmplă „pe dedesubt”: drumul unei cereri în producție

Pe server, o cerere trece pe aici:

```text
browser ──HTTPS──▶ proxy (nginx sau platforma) ──HTTP + X-Forwarded-Proto──▶ gunicorn
        ──▶ blog_proiect.wsgi.application ──▶ middleware ──▶ view
```

Poți simula modul de producție chiar acum, cu clientul de test din lecția 59, pornind `python manage.py shell` cu variabilele de producție (`DJANGO_DEBUG=0 DJANGO_SECRET_KEY=... DJANGO_ALLOWED_HOSTS=blogul-anei.ro python manage.py shell`):

```python
from django.test import Client

client = Client(HTTP_HOST="blogul-anei.ro")
raspuns = client.get("/")
print(raspuns.status_code, raspuns["Location"])
print(client.get("/", secure=True).status_code)
css = client.get("/static/articole/stil.css", secure=True)
print(css.status_code, css["Content-Type"])
```

<!-- comanda: DJANGO_DEBUG=0 DJANGO_SECRET_KEY=x DJANGO_ALLOWED_HOSTS=blogul-anei.ro python manage.py shell -v 0 -c "from django.test import Client; client = Client(HTTP_HOST='blogul-anei.ro'); raspuns = client.get('/'); print(raspuns.status_code, raspuns['Location']); print(client.get('/', secure=True).status_code); css = client.get('/static/articole/stil.css', secure=True); print(css.status_code, css['Content-Type'])" -->
```text
301 https://blogul-anei.ro/
200
200 text/css; charset="utf-8"
```

- cererea `http://` primește `301` spre adresa `https://` (`SecurityMiddleware`, datorită lui `SECURE_SSL_REDIRECT`);
- cererea HTTPS (`secure=True` simulează ce ar spune proxy-ul) ajunge la view: `200`;
- CSS-ul e servit de **WhiteNoise**, din `staticfiles/`, înainte să ajungă cererea la vreun view. Cu `DEBUG` oprit, `runserver` n-ar mai servi fișierele statice; WhiteNoise o face și în producție.

## Exemplu complet

O repetiție generală a publicării: pașii pe care îi face serverul (sau îi faci tu pe server), cu setările de producție. Variabilele se dau o singură dată, cu `export`, la începutul scriptului, iar baza de date de producție e un fișier separat (`/tmp/blog.sqlite3`), ca să nu atingem baza de dezvoltare:

<!-- ruleaza -->
```bash
export DJANGO_DEBUG=0
export DJANGO_SECRET_KEY=o-cheie-lunga-si-aleatoare-de-cel-putin-cincizeci-de-caractere-0123456789
export DJANGO_ALLOWED_HOSTS=blogul-anei.ro
export DJANGO_CSRF_TRUSTED_ORIGINS=https://blogul-anei.ro
export DJANGO_DB_PATH=/tmp/blog.sqlite3
python manage.py check --deploy
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn --check-config blog_proiect.wsgi && echo "gunicorn: configurația e în regulă"
```

```text
System check identified no issues (1 silenced).
Operations to perform:
  Apply all migrations: admin, articole, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying articole.0001_initial... OK
  Applying articole.0002_articol_publicat... OK
  Applying articole.0003_categorie_eticheta_articol_categorie_comentariu_and_more... OK
  Applying articole.0004_articol_autor... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK

0 static files copied to 'staticfiles', 155 unmodified, 146 post-processed.
gunicorn: configurația e în regulă
```

Pe rând:

1. `check --deploy` nu mai găsește nicio problemă;
2. `migrate` creează tabelele în baza de date de producție, goală la prima publicare;
3. `collectstatic` nu mai copiază nimic („0 copied, 155 unmodified”), pentru că fișierele sunt deja adunate și nu s-au schimbat;
4. gunicorn găsește aplicația.

Pe server, după acești pași urmează pornirea propriu-zisă (`gunicorn blog_proiect.wsgi ...`), apoi crearea contului Anei în baza de producție, cu `python manage.py createsuperuser` (lecția 54). La fiecare versiune nouă: rulezi întâi testele (lecția 59), pe calculatorul tău, apoi, pe server, aduci codul nou (de exemplu cu git), `pip install -r requirements.txt`, `migrate`, `collectstatic` și repornești gunicorn. În proiectele reale, testele rulează automat la fiecare `git push`, iar codul ajunge pe server doar dacă trec (așa-numita „integrare continuă”, în engleză „continuous integration”, CI).

În terminalul PyTutor, fiecare comandă rulează separat, deci `export` nu se păstrează de la un rând la altul. Acolo scrie variabilele pe același rând cu comanda, ca în secțiunea „Variabilele de mediu”.

## Greșeli frecvente

### 1. Domeniul lipsește din ALLOWED_HOSTS

Blogul e configurat pentru `blogul-anei.ro`, dar cineva îl deschide la `www.blogul-anei.ro`:

```python
from django.test import Client

raspuns = Client(HTTP_HOST="www.blogul-anei.ro").get("/", secure=True)
print(raspuns.status_code)
```

<!-- comanda: DJANGO_DEBUG=0 DJANGO_SECRET_KEY=x DJANGO_ALLOWED_HOSTS=blogul-anei.ro python manage.py shell -v 0 -c "from django.test import Client; raspuns = Client(HTTP_HOST='www.blogul-anei.ro').get('/', secure=True); print(raspuns.status_code)" -->
```text
400
```

`400 Bad Request`: Django refuză orice cerere al cărei domeniu nu e în `ALLOWED_HOSTS`, ca protecție împotriva unor atacuri care falsifică adresa. Pune toate variantele: `DJANGO_ALLOWED_HOSTS=blogul-anei.ro,www.blogul-anei.ro` (și pe ambele în `DJANGO_CSRF_TRUSTED_ORIGINS`, cu `https://`).

### 2. Cheia secretă de dezvoltare, pe server

<!-- ruleaza -->
```bash
DJANGO_DEBUG=0 DJANGO_ALLOWED_HOSTS=blogul-anei.ro python manage.py check --deploy
```

```text
System check identified some issues:

WARNINGS:
?: (security.W009) Your SECRET_KEY has less than 50 characters, less than 5 unique characters, or it's prefixed with 'django-insecure-' indicating that it was generated automatically by Django. Please generate a long and random value, otherwise many of Django's security-critical features will be vulnerable to attack.

System check identified 1 issue (1 silenced).
```

Fără `DJANGO_SECRET_KEY`, setările folosesc valoarea de rezervă din cod, care e publică (e în repository). Cu ea, oricine poate falsifica datele semnate de site. Generează o cheie pentru server (secțiunea „Variabilele de mediu”) și n-o pune niciodată în git. Dacă o cheie a ajuns publică, schimb-o: toate sesiunile vechi devin invalide, iar utilizatorii trebuie să se autentifice din nou.

### 3. Ai uitat DJANGO_DEBUG=0

<!-- ruleaza -->
```bash
DJANGO_SECRET_KEY=o-cheie-lunga-si-aleatoare-de-cel-putin-cincizeci-de-caractere-0123456789 DJANGO_ALLOWED_HOSTS=blogul-anei.ro python manage.py check --deploy
```

```text
System check identified some issues:

WARNINGS:
?: (security.W004) You have not set a value for the SECURE_HSTS_SECONDS setting. If your entire site is served only over SSL, you may want to consider setting a value and enabling HTTP Strict Transport Security. Be sure to read the documentation first; enabling HSTS carelessly can cause serious, irreversible problems.
?: (security.W008) Your SECURE_SSL_REDIRECT setting is not set to True. Unless your site should be available over both SSL and non-SSL connections, you may want to either set this setting True or configure a load balancer or reverse-proxy server to redirect all connections to HTTPS.
?: (security.W012) SESSION_COOKIE_SECURE is not set to True. Using a secure-only session cookie makes it more difficult for network traffic sniffers to hijack user sessions.
?: (security.W016) You have 'django.middleware.csrf.CsrfViewMiddleware' in your MIDDLEWARE, but you have not set CSRF_COOKIE_SECURE to True. Using a secure-only CSRF cookie makes it more difficult for network traffic sniffers to steal the CSRF token.
?: (security.W018) You should not have DEBUG set to True in deployment.

System check identified 5 issues (0 silenced).
```

O singură variabilă uitată aduce 5 probleme: `DEBUG` rămâne pornit (implicit e `"1"`), iar blocul `if not DEBUG:` nu se mai aplică deloc. Cu `DEBUG` pornit, orice eroare afișează oricui pagina detaliată pe care o știi din lecția 47. Rulează `check --deploy` pe server, cu variabilele reale, la fiecare publicare.

### 4. Fișierele statice nu au fost adunate

Dacă folderul `staticfiles/` lipsește (ai uitat `collectstatic`, sau publicarea l-a șters), site-ul merge, dar fără CSS:

```bash
rm -r staticfiles
```

```python
css = Client(HTTP_HOST="blogul-anei.ro").get("/static/articole/stil.css", secure=True)
print(css.status_code)
```

<!-- comanda: rm -r staticfiles && DJANGO_DEBUG=0 DJANGO_SECRET_KEY=x DJANGO_ALLOWED_HOSTS=blogul-anei.ro python manage.py shell -v 0 -c "from django.test import Client; css = Client(HTTP_HOST='blogul-anei.ro').get('/static/articole/stil.css', secure=True); print(css.status_code)" -->
```text
/opt/venv/lib/python3.12/site-packages/django/core/handlers/base.py:61: UserWarning: No directory at: staticfiles/
  mw_instance = middleware(adapted_handler)
404
```

WhiteNoise avertizează că nu găsește folderul `staticfiles/`, iar CSS-ul primește 404. Pe calculatorul tău, cu `DEBUG` pornit, CSS-ul s-ar fi văzut totuși, așa că greșeala apare abia pe server. `collectstatic` face parte din pașii fiecărei publicări:

<!-- ruleaza -->
```bash
python manage.py collectstatic --noinput
```

```text

155 static files copied to 'staticfiles', 146 post-processed.
```

## Exercițiu

În proiectul PyTutor **`blog`** (fișierul capitolului, `capitole/61-django-deploy/django_deploy.py`, poate rămâne pentru notițe):

1. generează o cheie secretă cu `get_random_secret_key()` și rulează `check --deploy` cu ea, cu `DJANGO_DEBUG=0` și cu `DJANGO_ALLOWED_HOSTS` setat la două domenii (unul cu `www.`), până nu mai apare nicio problemă;
2. adaugă `staticfiles/` și `db.sqlite3` în `.gitignore` și verifică cu `git status` că nu mai apar (lecția 42; dacă proiectul `blog` nu e încă un repository, creează-l întâi cu `git init` și `git config core.fileMode false`);
3. pornește blogul cu gunicorn în loc de `runserver`: `gunicorn blog_proiect.wsgi --bind 0.0.0.0:8000` (fără variabilele de producție, deci cu `DEBUG` pornit) și deschide adresa serverului din bara terminalului. Verifică faptul că paginile și CSS-ul merg, apoi oprește-l cu **Oprește**;
4. scrie în notițe lista pașilor de publicare pentru o versiune nouă a blogului, în ordine, și explică într-o propoziție de ce e necesar fiecare.

## Pe scurt

- În producție: `DEBUG` oprit, cheie secretă lungă și secretă, `ALLOWED_HOSTS` și `CSRF_TRUSTED_ORIGINS` cu domeniul tău, toate din variabile de mediu.
- `python manage.py check --deploy` e lista de verificare automată: rulează-l cu variabilele reale la fiecare publicare.
- Fișierele statice se adună cu `collectstatic` în `STATIC_ROOT` și sunt servite de WhiteNoise.
- `requirements.txt` fixează versiunile pachetelor; pe server rulează gunicorn (WSGI), nu `runserver`.
- HTTPS criptează traficul; `SECURE_SSL_REDIRECT`, cookie-urile `SECURE` și HSTS obligă la folosirea lui.
- La fiecare versiune nouă: testele trec, apoi pe server cod nou, `pip install -r requirements.txt`, `migrate`, `collectstatic`, repornirea lui gunicorn.

### Drumul de până aici

Ai pornit de la `print("Salut, lume!")` și ai ajuns la o aplicație web publicabilă: variabile, decizii și bucle (modulele 1–2), colecții și funcții (3–4), erori, fișiere și module (5–6), clase (7), unelte de Python intermediar (8), cod de calitate cu teste și git (9), web-ul (10), apoi blogul Anei, construit pas cu pas cu Django (11–14).

Ce poți face mai departe:

- **publică blogul** pe o platformă reală și folosește-l: e cel mai bun test;
- **construiește un proiect al tău** de la zero (o listă de sarcini, un jurnal de cheltuieli pe web, un site pentru un hobby), folosind lecțiile ca referință;
- **aprofundează**: documentația oficială Django (are și un tutorial excelent), PostgreSQL, JavaScript pentru pagini interactive, autentificarea cu token-uri în API-uri;
- **citește cod scris de alții**: proiecte open-source pe GitHub, începând cu cele mici.
