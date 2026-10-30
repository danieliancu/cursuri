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

# Autentificare: unde trimitem utilizatorul să intre în cont și unde ajunge după login/logout.
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "lista"
LOGOUT_REDIRECT_URL = "lista"
