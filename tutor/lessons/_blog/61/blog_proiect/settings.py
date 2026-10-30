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
