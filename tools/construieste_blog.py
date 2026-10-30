"""Construiește tutor/lessons/_blog/45 … 61: starea proiectului după fiecare lecție Django.

Fiecare etapă = copia etapei anterioare + fișiere scrise/șterse + (opțional) makemigrations în container.
"""
import shutil
import subprocess
import sys
from pathlib import Path

BLOG = Path(r"C:\_work\pyth\tutor\lessons\_blog")
IMAGE = "pytutor-sandbox:2"


def docker(folder: Path, cmd: str) -> str:
    res = subprocess.run(["docker", "run", "--rm", "-v", f"{folder}:/w", "-w", "/w", IMAGE, "sh", "-c", cmd],
                         capture_output=True, text=True, encoding="utf-8")
    if res.returncode:
        sys.exit(f"EȘEC în {folder.name}: {cmd}\n{res.stdout}\n{res.stderr}")
    return res.stdout


def clean(folder: Path) -> None:
    for p in list(folder.rglob("__pycache__")) + list(folder.rglob("db.sqlite3")):
        shutil.rmtree(p) if p.is_dir() else p.unlink()
    for p in folder.rglob("*"):  # LF peste tot
        if p.is_file() and p.suffix in (".py", ".html", ".css", ".txt", ".md", ".json"):
            data = p.read_bytes().replace(b"\r\n", b"\n")
            p.write_bytes(data)


def stage(nr: int, files: dict[str, str] | None = None, delete: tuple = (), migrate: bool = False) -> None:
    folder = BLOG / str(nr)
    if folder.exists():
        shutil.rmtree(folder)
    shutil.copytree(BLOG / str(nr - 1), folder)
    for path in delete:
        (folder / path).unlink()
    for path, content in (files or {}).items():
        target = folder / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content.lstrip("\n"), encoding="utf-8", newline="\n")
    if migrate:
        print(docker(folder, "python manage.py makemigrations articole"), end="")
    clean(folder)
    print(f"etapa {nr} gata")


# ---------------------------------------------------------------- 45: proiect și aplicație
def stage45() -> None:
    folder = BLOG / "45"
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    docker(folder, "django-admin startproject blog_proiect . && python manage.py startapp articole")
    settings = folder / "blog_proiect" / "settings.py"
    text = settings.read_text(encoding="utf-8")
    old = '    "django.contrib.staticfiles",\n]'
    assert old in text
    settings.write_text(text.replace(old, '    "django.contrib.staticfiles",\n    "articole",\n]'),
                        encoding="utf-8", newline="\n")
    clean(folder)
    print("etapa 45 gata")


# ---------------------------------------------------------------- fișiere comune
SETTINGS_46 = r'''
"""Setările proiectului blog_proiect.

Toate setările posibile: https://docs.djangoproject.com/en/5.2/ref/settings/
"""
import os
from pathlib import Path

# Folderul proiectului (cel cu manage.py); celelalte căi pornesc de aici.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cheia secretă semnează sesiunile și formularele. În producție vine dintr-o variabilă
# de mediu (lecția 61); valoarea de rezervă e bună doar pe calculatorul tău.
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
'''

PROJECT_URLS_47 = r'''
"""Adresele proiectului: fiecare cerere e trimisă mai departe după începutul căii."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("articole.urls")),
]
'''

ARTICOLE_LISTA = r'''
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
'''

VIEWS_47 = r'''
from datetime import date

from django.http import Http404, HttpResponse
''' + ARTICOLE_LISTA + r'''

def lista(request):
    randuri = []
    for a in ARTICOLE:
        data = a["data_publicarii"].strftime("%d.%m.%Y")
        randuri.append(f'<li><a href="/articol/{a["id"]}/">{a["titlu"]}</a> ({data})</li>')
    return HttpResponse("<h1>Blogul Anei</h1><ul>" + "".join(randuri) + "</ul>")


def detaliu(request, nr):
    articol = gaseste(nr)
    return HttpResponse(f"<h1>{articol['titlu']}</h1><p>{articol['continut']}</p>")
'''

APP_URLS_47 = r'''
from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista, name="lista"),
    path("articol/<int:nr>/", views.detaliu, name="detaliu"),
]
'''

VIEWS_48 = r'''
from datetime import date

from django.http import Http404
from django.shortcuts import render
''' + ARTICOLE_LISTA + r'''

def lista(request):
    return render(request, "articole/lista.html", {"articole": ARTICOLE})


def detaliu(request, nr):
    return render(request, "articole/detaliu.html", {"articol": gaseste(nr)})


def despre(request):
    return render(request, "articole/despre.html")
'''

APP_URLS_48 = r'''
from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista, name="lista"),
    path("articol/<int:nr>/", views.detaliu, name="detaliu"),
    path("despre/", views.despre, name="despre"),
]
'''


def base_html(head_extra: str = "", nav: str = "", before_block: str = "") -> str:
    return r'''
{% load static %}
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block titlu %}Blogul Anei{% endblock %}</title>
''' + head_extra + r'''</head>
<body>
  <header class="antet">
    <a href="{% url 'lista' %}" class="sigla">Blogul Anei</a>
    <nav>
      <a href="{% url 'lista' %}">Articole</a>
      <a href="{% url 'despre' %}">Despre</a>
''' + nav + r'''    </nav>
  </header>

  <main>
''' + before_block + r'''    {% block continut %}{% endblock %}
  </main>

  <footer class="subsol">
    <p>Ana Popescu, Cluj · 2026</p>
  </footer>
</body>
</html>
'''


BASE_48 = base_html().replace("{% load static %}\n", "")
BASE_49 = base_html(head_extra='  <link rel="stylesheet" href="{% static \'articole/stil.css\' %}">\n')
MESAJE = r'''    {% for mesaj in messages %}
      <p class="mesaj">{{ mesaj }}</p>
    {% endfor %}
'''
BASE_55 = base_html(
    head_extra='  <link rel="stylesheet" href="{% static \'articole/stil.css\' %}">\n',
    nav='      <a href="{% url \'contact\' %}">Contact</a>\n',
    before_block=MESAJE,
)
BASE_56 = base_html(
    head_extra='  <link rel="stylesheet" href="{% static \'articole/stil.css\' %}">\n',
    nav='      <a href="{% url \'contact\' %}">Contact</a>\n      <a href="{% url \'articol_nou\' %}">Scrie un articol</a>\n',
    before_block=MESAJE,
)
NAV_57 = r'''      <a href="{% url 'contact' %}">Contact</a>
      {% if user.is_authenticated %}
        <a href="{% url 'articol_nou' %}">Scrie un articol</a>
        <form action="{% url 'logout' %}" method="post" class="iesire">
          {% csrf_token %}
          <button type="submit">Ieși ({{ user.username }})</button>
        </form>
      {% else %}
        <a href="{% url 'login' %}">Autentificare</a>
        <a href="{% url 'inregistrare' %}">Cont nou</a>
      {% endif %}
'''
BASE_57 = base_html(
    head_extra='  <link rel="stylesheet" href="{% static \'articole/stil.css\' %}">\n',
    nav=NAV_57,
    before_block=MESAJE,
)

LISTA_HTML = r'''
{% extends "articole/base.html" %}

{% block continut %}
  <h1>Articole</h1>
  {% for articol in articole %}
    <article class="articol">
      <h2><a href="{% url 'detaliu' articol.id %}">{{ articol.titlu }}</a></h2>
      {% include "articole/_meta.html" %}
      <p>{{ articol.continut|truncatewords:12 }}</p>
    </article>
  {% empty %}
    <p>Încă nu există articole.</p>
  {% endfor %}
{% endblock %}
'''

META_48 = r'''
<p class="meta">
  {{ articol.data_publicarii|date:"j F Y"|lower }}
  {% if articol.categorie %} · <span class="categorie">{{ articol.categorie }}</span>{% endif %}
</p>
'''
META_57 = r'''
<p class="meta">
  {{ articol.data_publicarii|date:"j F Y"|lower }}
  {% if articol.categorie %} · <span class="categorie">{{ articol.categorie }}</span>{% endif %}
  {% if articol.autor %} · de {{ articol.autor.username }}{% endif %}
</p>
'''

DETALIU_48 = r'''
{% extends "articole/base.html" %}

{% block titlu %}{{ articol.titlu }} · Blogul Anei{% endblock %}

{% block continut %}
  <article class="articol">
    <h1>{{ articol.titlu }}</h1>
    {% include "articole/_meta.html" %}
    {{ articol.continut|linebreaks }}
  </article>
{% endblock %}
'''

COMENTARII_53 = r'''
  <section class="comentarii" id="comentarii">
    <h2>Comentarii ({{ articol.comentarii.count }})</h2>
    {% for comentariu in articol.comentarii.all %}
      <div class="comentariu">
        <p class="meta"><strong>{{ comentariu.autor }}</strong> · {{ comentariu.data|date:"j F Y"|lower }}</p>
        <p>{{ comentariu.text }}</p>
      </div>
    {% empty %}
      <p>Niciun comentariu încă.</p>
    {% endfor %}
'''
FORMULAR_COMENTARIU = r'''
    <form action="{% url 'comentariu' articol.id %}" method="post" class="formular">
      <h3>Lasă un comentariu</h3>
      {% csrf_token %}
      {{ formular.as_div }}
      <button type="submit">Trimite comentariul</button>
    </form>
'''


def detaliu_html(etichete: bool, comentarii: bool, formular: bool, actiuni: str = "") -> str:
    text = r'''
{% extends "articole/base.html" %}

{% block titlu %}{{ articol.titlu }} · Blogul Anei{% endblock %}

{% block continut %}
  <article class="articol">
    <h1>{{ articol.titlu }}</h1>
    {% include "articole/_meta.html" %}
    {{ articol.continut|linebreaks }}
'''
    if etichete:
        text += r'''    {% if articol.etichete.all %}
      <p class="meta">Etichete: {{ articol.etichete.all|join:", " }}</p>
    {% endif %}
'''
    text += actiuni
    text += "  </article>\n"
    if comentarii:
        text += COMENTARII_53.lstrip("\n")
        if formular:
            text += FORMULAR_COMENTARIU.lstrip("\n")
        text += "  </section>\n"
    text += "{% endblock %}\n"
    return text


ACTIUNI_56 = r'''    <p><a href="{% url 'articol_editeaza' articol.id %}">Editează articolul</a></p>
'''
ACTIUNI_57 = r'''    {% if user == articol.autor %}
      <p><a href="{% url 'articol_editeaza' articol.id %}">Editează articolul</a></p>
    {% endif %}
'''
ACTIUNI_58 = r'''    {% if user == articol.autor %}
      <p>
        <a href="{% url 'articol_editeaza' articol.id %}">Editează articolul</a> ·
        <a href="{% url 'articol_sterge' articol.id %}">Șterge articolul</a>
      </p>
    {% endif %}
'''

DESPRE_HTML = r'''
{% extends "articole/base.html" %}

{% block titlu %}Despre · Blogul Anei{% endblock %}

{% block continut %}
  <h1>Despre</h1>
  <p>Sunt Ana Popescu, am 25 de ani și locuiesc în Cluj.</p>
  <p>Învăț programare de un an și scriu aici despre ce descopăr: Python, Django și, uneori, călătorii.</p>
{% endblock %}
'''

STIL_CSS = r'''
body {
  margin: 0;
  font-family: system-ui, sans-serif;
  line-height: 1.6;
  color: #222;
  background-color: #f6f7f9;
}

main {
  max-width: 720px;
  margin: 0 auto;
  padding: 0 16px 32px;
}

.antet {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #1f2937;
}

.antet a {
  color: white;
  text-decoration: none;
  margin-left: 16px;
}

.antet .sigla {
  margin-left: 0;
  font-weight: bold;
  font-size: 20px;
}

.articol {
  background-color: white;
  border: 1px solid #e3e5e8;
  border-radius: 8px;
  padding: 16px 20px;
  margin: 16px 0;
}

.articol h2 a {
  color: #2f6fde;
  text-decoration: none;
}

.articol h2 a:hover {
  text-decoration: underline;
}

.meta {
  color: #6b7280;
  font-size: 14px;
}

.categorie {
  background-color: #e8f0fe;
  color: #2f6fde;
  padding: 2px 8px;
  border-radius: 999px;
}

.comentariu {
  border-left: 3px solid #2f6fde;
  padding-left: 12px;
  margin: 12px 0;
}

/* Toate formularele site-ului: comentarii, contact, articole, autentificare. */
.formular label {
  display: block;
  margin-top: 12px;
  font-weight: bold;
}

.formular input,
.formular textarea,
.formular select {
  width: 100%;
  box-sizing: border-box;
  padding: 8px;
  border: 1px solid #c9ccd1;
  border-radius: 6px;
  font: inherit;
}

.formular button {
  margin-top: 12px;
  padding: 8px 16px;
  border: 0;
  border-radius: 6px;
  background-color: #2f6fde;
  color: white;
  cursor: pointer;
}

/* Erorile de validare (lecția 55) și mesajele de confirmare. */
.errorlist {
  color: #b42318;
  padding-left: 18px;
}

.mesaj {
  background-color: #e7f6ec;
  border: 1px solid #a6dcb6;
  border-radius: 6px;
  padding: 8px 12px;
  margin: 16px 0;
}

.subsol {
  text-align: center;
  color: #6b7280;
  font-size: 14px;
}
'''

# ---------------------------------------------------------------- modele
MODELS_50 = r'''
from datetime import date

from django.db import models


class Articol(models.Model):
    titlu = models.CharField(max_length=200)
    continut = models.TextField()
    data_publicarii = models.DateField(default=date.today)

    class Meta:
        ordering = ["-data_publicarii"]
        verbose_name = "articol"
        verbose_name_plural = "articole"

    def __str__(self):
        return self.titlu
'''

MODELS_51 = MODELS_50.replace(
    "    data_publicarii = models.DateField(default=date.today)\n",
    "    data_publicarii = models.DateField(default=date.today)\n    publicat = models.BooleanField(default=True)\n",
)


def models_53(autor: bool = False) -> str:
    imports = "from datetime import date\n\n"
    if autor:
        imports += "from django.conf import settings\n"
    imports += "from django.db import models\nfrom django.urls import reverse\n"
    autor_field = (
        "    autor = models.ForeignKey(\n"
        "        settings.AUTH_USER_MODEL,\n"
        "        on_delete=models.SET_NULL,\n"
        "        null=True,\n"
        "        blank=True,\n"
        '        related_name="articole",\n'
        "    )\n"
    ) if autor else ""
    return "\n" + imports + r'''

class Categorie(models.Model):
    nume = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["nume"]
        verbose_name = "categorie"
        verbose_name_plural = "categorii"

    def __str__(self):
        return self.nume


class Eticheta(models.Model):
    nume = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ["nume"]
        verbose_name = "etichetă"
        verbose_name_plural = "etichete"

    def __str__(self):
        return self.nume


class Articol(models.Model):
    titlu = models.CharField(max_length=200)
    continut = models.TextField()
    data_publicarii = models.DateField(default=date.today)
    publicat = models.BooleanField(default=True)
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articole",
    )
    etichete = models.ManyToManyField(Eticheta, blank=True, related_name="articole")
''' + autor_field + r'''
    class Meta:
        ordering = ["-data_publicarii"]
        verbose_name = "articol"
        verbose_name_plural = "articole"

    def __str__(self):
        return self.titlu

    def get_absolute_url(self):
        """Adresa paginii articolului; o folosesc redirect() și view-urile generice."""
        return reverse("detaliu", args=[self.id])


class Comentariu(models.Model):
    articol = models.ForeignKey(Articol, on_delete=models.CASCADE, related_name="comentarii")
    autor = models.CharField(max_length=80)
    text = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["data"]
        verbose_name = "comentariu"
        verbose_name_plural = "comentarii"

    def __str__(self):
        return f"{self.autor} despre „{self.articol}”"
'''


VIEWS_52 = r'''
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
'''

VIEWS_53 = VIEWS_52.replace(
    "    articole = Articol.objects.filter(publicat=True)\n",
    '    articole = Articol.objects.filter(publicat=True).select_related("categorie")\n',
)

ADMIN_54 = r'''
from django.contrib import admin

from .models import Articol, Categorie, Comentariu, Eticheta


class ComentariuInline(admin.TabularInline):
    model = Comentariu
    extra = 0


@admin.register(Articol)
class ArticolAdmin(admin.ModelAdmin):
    list_display = ["titlu", "categorie", "data_publicarii", "publicat"]
    list_filter = ["publicat", "categorie"]
    search_fields = ["titlu", "continut"]
    inlines = [ComentariuInline]


@admin.register(Comentariu)
class ComentariuAdmin(admin.ModelAdmin):
    list_display = ["autor", "articol", "data"]
    search_fields = ["autor", "text"]


admin.site.register(Categorie)
admin.site.register(Eticheta)
'''
ADMIN_57 = ADMIN_54.replace(
    'list_display = ["titlu", "categorie", "data_publicarii", "publicat"]',
    'list_display = ["titlu", "autor", "categorie", "data_publicarii", "publicat"]',
).replace('list_filter = ["publicat", "categorie"]', 'list_filter = ["publicat", "categorie", "autor"]')

# ---------------------------------------------------------------- formulare
FORMS_55 = r'''
from django import forms


class ContactForm(forms.Form):
    nume = forms.CharField(max_length=80)
    email = forms.EmailField()
    mesaj = forms.CharField(widget=forms.Textarea, min_length=10)
'''

FORMS_56 = FORMS_55.replace("from django import forms\n", "from django import forms\n\nfrom .models import Articol, Comentariu\n") + r'''

class ComentariuForm(forms.ModelForm):
    class Meta:
        model = Comentariu
        fields = ["autor", "text"]
        labels = {"autor": "Numele tău", "text": "Comentariu"}
        widgets = {"text": forms.Textarea(attrs={"rows": 4})}


class ArticolForm(forms.ModelForm):
    class Meta:
        model = Articol
        fields = ["titlu", "continut", "categorie", "etichete", "data_publicarii", "publicat"]
        labels = {"continut": "Conținut", "data_publicarii": "Data publicării"}

    def clean_titlu(self):
        """Validare proprie: titlul nu e scris numai cu majuscule."""
        titlu = self.cleaned_data["titlu"].strip()
        if titlu.isupper():
            raise forms.ValidationError("Nu scrie titlul numai cu majuscule.")
        return titlu
'''

CONTACT_HTML = r'''
{% extends "articole/base.html" %}

{% block titlu %}Contact · Blogul Anei{% endblock %}

{% block continut %}
  <h1>Contact</h1>
  <form method="post" class="formular">
    {% csrf_token %}
    {{ formular.as_div }}
    <button type="submit">Trimite mesajul</button>
  </form>
{% endblock %}
'''

FORMULAR_ARTICOL_HTML = r'''
{% extends "articole/base.html" %}

{% block titlu %}{{ titlu }} · Blogul Anei{% endblock %}

{% block continut %}
  <h1>{{ titlu }}</h1>
  <form method="post" class="formular">
    {% csrf_token %}
    {{ formular.as_div }}
    <button type="submit">Salvează</button>
  </form>
{% endblock %}
'''

VIEWS_55 = r'''
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm
from .models import Articol


def lista(request):
    articole = Articol.objects.filter(publicat=True).select_related("categorie")
    return render(request, "articole/lista.html", {"articole": articole})


def detaliu(request, nr):
    articol = get_object_or_404(Articol, id=nr, publicat=True)
    return render(request, "articole/detaliu.html", {"articol": articol})


def despre(request):
    return render(request, "articole/despre.html")


def contact(request):
    if request.method == "POST":
        formular = ContactForm(request.POST)
        if formular.is_valid():
            nume = formular.cleaned_data["nume"]
            messages.success(request, f"Mulțumim, {nume}! Ana îți va răspunde în curând.")
            return redirect("contact")
    else:
        formular = ContactForm()
    return render(request, "articole/contact.html", {"formular": formular})
'''

VIEWS_56 = r'''
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ArticolForm, ComentariuForm, ContactForm
from .models import Articol


def lista(request):
    articole = Articol.objects.filter(publicat=True).select_related("categorie")
    return render(request, "articole/lista.html", {"articole": articole})


def detaliu(request, nr):
    articol = get_object_or_404(Articol, id=nr, publicat=True)
    context = {"articol": articol, "formular": ComentariuForm()}
    return render(request, "articole/detaliu.html", context)


@require_POST
def adauga_comentariu(request, nr):
    articol = get_object_or_404(Articol, id=nr, publicat=True)
    formular = ComentariuForm(request.POST)
    if formular.is_valid():
        comentariu = formular.save(commit=False)
        comentariu.articol = articol
        comentariu.save()
        return redirect(articol.get_absolute_url() + "#comentarii")
    return render(request, "articole/detaliu.html", {"articol": articol, "formular": formular})


def articol_nou(request):
    if request.method == "POST":
        formular = ArticolForm(request.POST)
        if formular.is_valid():
            articol = formular.save()
            messages.success(request, "Articolul a fost salvat.")
            return redirect(articol)
    else:
        formular = ArticolForm()
    context = {"formular": formular, "titlu": "Articol nou"}
    return render(request, "articole/formular_articol.html", context)


def articol_editeaza(request, nr):
    articol = get_object_or_404(Articol, id=nr)
    if request.method == "POST":
        formular = ArticolForm(request.POST, instance=articol)
        if formular.is_valid():
            formular.save()
            messages.success(request, "Modificările au fost salvate.")
            return redirect(articol)
    else:
        formular = ArticolForm(instance=articol)
    context = {"formular": formular, "titlu": f"Editează: {articol.titlu}"}
    return render(request, "articole/formular_articol.html", context)


def despre(request):
    return render(request, "articole/despre.html")


def contact(request):
    if request.method == "POST":
        formular = ContactForm(request.POST)
        if formular.is_valid():
            nume = formular.cleaned_data["nume"]
            messages.success(request, f"Mulțumim, {nume}! Ana îți va răspunde în curând.")
            return redirect("contact")
    else:
        formular = ContactForm()
    return render(request, "articole/contact.html", {"formular": formular})
'''

VIEWS_57 = r'''
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ArticolForm, ComentariuForm, ContactForm
from .models import Articol


def lista(request):
    articole = Articol.objects.filter(publicat=True).select_related("categorie", "autor")
    return render(request, "articole/lista.html", {"articole": articole})


def detaliu(request, nr):
    articol = get_object_or_404(Articol, id=nr, publicat=True)
    context = {"articol": articol, "formular": ComentariuForm()}
    return render(request, "articole/detaliu.html", context)


@require_POST
def adauga_comentariu(request, nr):
    articol = get_object_or_404(Articol, id=nr, publicat=True)
    formular = ComentariuForm(request.POST)
    if formular.is_valid():
        comentariu = formular.save(commit=False)
        comentariu.articol = articol
        comentariu.save()
        return redirect(articol.get_absolute_url() + "#comentarii")
    return render(request, "articole/detaliu.html", {"articol": articol, "formular": formular})


@login_required
def articol_nou(request):
    if request.method == "POST":
        formular = ArticolForm(request.POST)
        if formular.is_valid():
            articol = formular.save(commit=False)
            articol.autor = request.user
            articol.save()
            formular.save_m2m()  # etichetele se salvează după articol
            messages.success(request, "Articolul a fost salvat.")
            return redirect(articol)
    else:
        formular = ArticolForm()
    context = {"formular": formular, "titlu": "Articol nou"}
    return render(request, "articole/formular_articol.html", context)


@login_required
def articol_editeaza(request, nr):
    articol = get_object_or_404(Articol, id=nr)
    if articol.autor != request.user:
        raise PermissionDenied("Doar autorul poate edita articolul.")
    if request.method == "POST":
        formular = ArticolForm(request.POST, instance=articol)
        if formular.is_valid():
            formular.save()
            messages.success(request, "Modificările au fost salvate.")
            return redirect(articol)
    else:
        formular = ArticolForm(instance=articol)
    context = {"formular": formular, "titlu": f"Editează: {articol.titlu}"}
    return render(request, "articole/formular_articol.html", context)


def inregistrare(request):
    if request.method == "POST":
        formular = UserCreationForm(request.POST)
        if formular.is_valid():
            utilizator = formular.save()
            login(request, utilizator)
            messages.success(request, f"Bun venit, {utilizator.username}!")
            return redirect("lista")
    else:
        formular = UserCreationForm()
    return render(request, "registration/inregistrare.html", {"formular": formular})


def despre(request):
    return render(request, "articole/despre.html")


def contact(request):
    if request.method == "POST":
        formular = ContactForm(request.POST)
        if formular.is_valid():
            nume = formular.cleaned_data["nume"]
            messages.success(request, f"Mulțumim, {nume}! Ana îți va răspunde în curând.")
            return redirect("contact")
    else:
        formular = ContactForm()
    return render(request, "articole/contact.html", {"formular": formular})
'''

VIEWS_58 = r'''
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import ArticolForm, ComentariuForm, ContactForm
from .models import Articol


class ListaArticole(ListView):
    queryset = Articol.objects.filter(publicat=True).select_related("categorie", "autor")
    template_name = "articole/lista.html"
    context_object_name = "articole"


class DetaliuArticol(DetailView):
    queryset = Articol.objects.filter(publicat=True)
    template_name = "articole/detaliu.html"
    context_object_name = "articol"
    pk_url_kwarg = "nr"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formular"] = ComentariuForm()
        return context


class ArticolNou(LoginRequiredMixin, CreateView):
    model = Articol
    form_class = ArticolForm
    template_name = "articole/formular_articol.html"
    extra_context = {"titlu": "Articol nou"}

    def form_valid(self, form):
        form.instance.autor = self.request.user
        messages.success(self.request, "Articolul a fost salvat.")
        return super().form_valid(form)


class DoarAutorul(UserPassesTestMixin):
    """Lasă mai departe doar autorul articolului; ceilalți primesc 403."""

    def test_func(self):
        return self.get_object().autor == self.request.user


class ArticolEditeaza(LoginRequiredMixin, DoarAutorul, UpdateView):
    model = Articol
    form_class = ArticolForm
    template_name = "articole/formular_articol.html"
    pk_url_kwarg = "nr"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titlu"] = f"Editează: {self.object.titlu}"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Modificările au fost salvate.")
        return super().form_valid(form)


class ArticolSterge(LoginRequiredMixin, DoarAutorul, DeleteView):
    model = Articol
    template_name = "articole/confirma_stergere.html"
    pk_url_kwarg = "nr"
    success_url = reverse_lazy("lista")


class Despre(TemplateView):
    template_name = "articole/despre.html"


class Contact(FormView):
    form_class = ContactForm
    template_name = "articole/contact.html"
    success_url = reverse_lazy("contact")

    def form_valid(self, form):
        nume = form.cleaned_data["nume"]
        messages.success(self.request, f"Mulțumim, {nume}! Ana îți va răspunde în curând.")
        return super().form_valid(form)


@require_POST
def adauga_comentariu(request, nr):
    articol = get_object_or_404(Articol, id=nr, publicat=True)
    formular = ComentariuForm(request.POST)
    if formular.is_valid():
        comentariu = formular.save(commit=False)
        comentariu.articol = articol
        comentariu.save()
        return redirect(articol.get_absolute_url() + "#comentarii")
    return render(request, "articole/detaliu.html", {"articol": articol, "formular": formular})


def inregistrare(request):
    if request.method == "POST":
        formular = UserCreationForm(request.POST)
        if formular.is_valid():
            utilizator = formular.save()
            login(request, utilizator)
            messages.success(request, f"Bun venit, {utilizator.username}!")
            return redirect("lista")
    else:
        formular = UserCreationForm()
    return render(request, "registration/inregistrare.html", {"formular": formular})
'''

APP_URLS_55 = r'''
from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista, name="lista"),
    path("articol/<int:nr>/", views.detaliu, name="detaliu"),
    path("despre/", views.despre, name="despre"),
    path("contact/", views.contact, name="contact"),
]
'''

APP_URLS_56 = r'''
from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista, name="lista"),
    path("articol/<int:nr>/", views.detaliu, name="detaliu"),
    path("articol/<int:nr>/comentariu/", views.adauga_comentariu, name="comentariu"),
    path("articol/nou/", views.articol_nou, name="articol_nou"),
    path("articol/<int:nr>/editeaza/", views.articol_editeaza, name="articol_editeaza"),
    path("despre/", views.despre, name="despre"),
    path("contact/", views.contact, name="contact"),
]
'''

APP_URLS_57 = APP_URLS_56.replace(
    '    path("contact/", views.contact, name="contact"),\n',
    '    path("contact/", views.contact, name="contact"),\n'
    '    path("conturi/inregistrare/", views.inregistrare, name="inregistrare"),\n',
)

APP_URLS_58 = r'''
from django.urls import path

from . import views

urlpatterns = [
    path("", views.ListaArticole.as_view(), name="lista"),
    path("articol/<int:nr>/", views.DetaliuArticol.as_view(), name="detaliu"),
    path("articol/<int:nr>/comentariu/", views.adauga_comentariu, name="comentariu"),
    path("articol/nou/", views.ArticolNou.as_view(), name="articol_nou"),
    path("articol/<int:nr>/editeaza/", views.ArticolEditeaza.as_view(), name="articol_editeaza"),
    path("articol/<int:nr>/sterge/", views.ArticolSterge.as_view(), name="articol_sterge"),
    path("despre/", views.Despre.as_view(), name="despre"),
    path("contact/", views.Contact.as_view(), name="contact"),
    path("conturi/inregistrare/", views.inregistrare, name="inregistrare"),
]
'''

APP_URLS_60 = r'''
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

# Routerul creează singur adresele API-ului: /api/articole/ și /api/articole/<id>/.
router = DefaultRouter()
router.register("articole", api.ArticolViewSet)

urlpatterns = [
    path("", views.ListaArticole.as_view(), name="lista"),
    path("articol/<int:nr>/", views.DetaliuArticol.as_view(), name="detaliu"),
    path("articol/<int:nr>/comentariu/", views.adauga_comentariu, name="comentariu"),
    path("articol/nou/", views.ArticolNou.as_view(), name="articol_nou"),
    path("articol/<int:nr>/editeaza/", views.ArticolEditeaza.as_view(), name="articol_editeaza"),
    path("articol/<int:nr>/sterge/", views.ArticolSterge.as_view(), name="articol_sterge"),
    path("despre/", views.Despre.as_view(), name="despre"),
    path("contact/", views.Contact.as_view(), name="contact"),
    path("conturi/inregistrare/", views.inregistrare, name="inregistrare"),
    path("api/", include(router.urls)),
]
'''

PROJECT_URLS_57 = r'''
"""Adresele proiectului: fiecare cerere e trimisă mai departe după începutul căii."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # login/, logout/, schimbarea parolei: view-urile gata făcute ale Django
    path("conturi/", include("django.contrib.auth.urls")),
    path("", include("articole.urls")),
]
'''

LOGIN_HTML = r'''
{% extends "articole/base.html" %}

{% block titlu %}Autentificare · Blogul Anei{% endblock %}

{% block continut %}
  <h1>Autentificare</h1>
  <form method="post" class="formular">
    {% csrf_token %}
    {{ form.as_div }}
    <input type="hidden" name="next" value="{{ next }}">
    <button type="submit">Intră în cont</button>
  </form>
  <p>Nu ai cont? <a href="{% url 'inregistrare' %}">Creează unul</a>.</p>
{% endblock %}
'''

INREGISTRARE_HTML = r'''
{% extends "articole/base.html" %}

{% block titlu %}Cont nou · Blogul Anei{% endblock %}

{% block continut %}
  <h1>Cont nou</h1>
  <form method="post" class="formular">
    {% csrf_token %}
    {{ formular.as_div }}
    <button type="submit">Creează contul</button>
  </form>
{% endblock %}
'''

CONFIRMA_STERGERE_HTML = r'''
{% extends "articole/base.html" %}

{% block titlu %}Șterge articolul · Blogul Anei{% endblock %}

{% block continut %}
  <h1>Ștergi articolul „{{ articol.titlu }}”?</h1>
  <p>Comentariile lui se șterg și ele. Operația nu se poate anula.</p>
  <form method="post" class="formular">
    {% csrf_token %}
    <button type="submit">Da, șterge</button>
    <a href="{{ articol.get_absolute_url }}">Renunță</a>
  </form>
{% endblock %}
'''

SETTINGS_57 = SETTINGS_46.rstrip("\n") + r'''

# Autentificare: unde trimitem utilizatorul să intre în cont și unde ajunge după login/logout.
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "lista"
LOGOUT_REDIRECT_URL = "lista"
'''

SETTINGS_60 = SETTINGS_57.replace('    "articole",\n]', '    "rest_framework",\n    "articole",\n]')

TESTS_59 = r'''
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import ArticolForm
from .models import Articol, Categorie, Comentariu


class DateDeTest(TestCase):
    """Datele comune: creat o singură dată pentru toată clasa, refăcute pentru fiecare test."""

    @classmethod
    def setUpTestData(cls):
        cls.ana = User.objects.create_user("ana", password="parola-ana-2026")
        cls.mihai = User.objects.create_user("mihai", password="parola-mihai-2026")
        programare = Categorie.objects.create(nume="Programare")
        cls.articol = Articol.objects.create(
            titlu="De ce am ales Django",
            continut="Django are toate acestea „din cutie”.",
            data_publicarii=date(2026, 10, 2),
            categorie=programare,
            autor=cls.ana,
        )
        cls.ciorna = Articol.objects.create(
            titlu="Ciornă", continut="Încă lucrez la el.", publicat=False
        )


class ModelTests(DateDeTest):
    def test_str_e_titlul(self):
        self.assertEqual(str(self.articol), "De ce am ales Django")

    def test_adresa_articolului(self):
        self.assertEqual(self.articol.get_absolute_url(), f"/articol/{self.articol.id}/")


class ListaTests(DateDeTest):
    def test_arata_doar_articolele_publicate(self):
        raspuns = self.client.get(reverse("lista"))
        self.assertEqual(raspuns.status_code, 200)
        self.assertContains(raspuns, "De ce am ales Django")
        self.assertNotContains(raspuns, "Ciornă")


class DetaliuTests(DateDeTest):
    def test_articol_existent(self):
        raspuns = self.client.get(self.articol.get_absolute_url())
        self.assertContains(raspuns, "<h1>De ce am ales Django</h1>", html=True)

    def test_articol_inexistent_da_404(self):
        raspuns = self.client.get("/articol/999/")
        self.assertEqual(raspuns.status_code, 404)

    def test_ciorna_nu_se_vede(self):
        raspuns = self.client.get(self.ciorna.get_absolute_url())
        self.assertEqual(raspuns.status_code, 404)


class ComentariuTests(DateDeTest):
    def test_comentariu_valid_e_salvat_si_redirectionat(self):
        adresa = reverse("comentariu", args=[self.articol.id])
        raspuns = self.client.post(adresa, {"autor": "Mihai", "text": "Foarte bun articol!"})
        self.assertRedirects(raspuns, self.articol.get_absolute_url() + "#comentarii")
        self.assertEqual(Comentariu.objects.get().text, "Foarte bun articol!")

    def test_comentariu_fara_text_nu_e_salvat(self):
        adresa = reverse("comentariu", args=[self.articol.id])
        raspuns = self.client.post(adresa, {"autor": "Mihai", "text": ""})
        self.assertEqual(raspuns.status_code, 200)
        self.assertFalse(Comentariu.objects.exists())


class ArticolNouTests(DateDeTest):
    def test_cere_autentificare(self):
        raspuns = self.client.get(reverse("articol_nou"))
        self.assertRedirects(raspuns, "/conturi/login/?next=/articol/nou/")

    def test_autorul_e_utilizatorul_logat(self):
        self.client.force_login(self.ana)
        date_formular = {
            "titlu": "Un articol nou",
            "continut": "Text.",
            "data_publicarii": "2026-10-29",
            "publicat": "on",
        }
        self.client.post(reverse("articol_nou"), date_formular)
        self.assertEqual(Articol.objects.get(titlu="Un articol nou").autor, self.ana)


class EditareTests(DateDeTest):
    def test_alt_utilizator_primeste_403(self):
        self.client.force_login(self.mihai)
        raspuns = self.client.get(reverse("articol_editeaza", args=[self.articol.id]))
        self.assertEqual(raspuns.status_code, 403)

    def test_autorul_poate_edita(self):
        self.client.force_login(self.ana)
        raspuns = self.client.get(reverse("articol_editeaza", args=[self.articol.id]))
        self.assertEqual(raspuns.status_code, 200)


class ArticolFormTests(TestCase):
    def test_titlu_numai_cu_majuscule_e_respins(self):
        date_formular = {"titlu": "TITLU", "continut": "Text.", "data_publicarii": "2026-10-29"}
        formular = ArticolForm(data=date_formular)
        self.assertFalse(formular.is_valid())
        self.assertEqual(formular.errors["titlu"], ["Nu scrie titlul numai cu majuscule."])
'''

SERIALIZERS_60 = r'''
from rest_framework import serializers

from .models import Articol


class ArticolSerializer(serializers.ModelSerializer):
    """Cum arată un articol în JSON: câmpurile alese și cum se transformă."""

    autor = serializers.ReadOnlyField(source="autor.username")
    categorie = serializers.StringRelatedField()

    class Meta:
        model = Articol
        fields = ["id", "titlu", "continut", "data_publicarii", "categorie", "autor"]
'''

API_60 = r'''
from rest_framework import permissions, viewsets

from .models import Articol
from .serializers import ArticolSerializer


class EsteAutorulSauDoarCitire(permissions.BasePermission):
    """Oricine poate citi; doar autorul poate modifica sau șterge un articol."""

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.autor == request.user


class ArticolViewSet(viewsets.ModelViewSet):
    queryset = Articol.objects.filter(publicat=True).select_related("categorie", "autor")
    serializer_class = ArticolSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, EsteAutorulSauDoarCitire]

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)
'''

TESTS_API_60 = r'''
from datetime import date

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Articol


class ArticolApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = User.objects.create_user("ana", password="parola-ana-2026")
        cls.mihai = User.objects.create_user("mihai", password="parola-mihai-2026")
        cls.articol = Articol.objects.create(
            titlu="De ce am ales Django",
            continut="Text.",
            data_publicarii=date(2026, 10, 2),
            autor=cls.ana,
        )

    def test_lista_e_publica(self):
        raspuns = self.client.get("/api/articole/")
        self.assertEqual(raspuns.status_code, 200)
        self.assertEqual(raspuns.json()[0]["titlu"], "De ce am ales Django")

    def test_fara_cont_nu_poti_scrie(self):
        raspuns = self.client.post("/api/articole/", {"titlu": "Nou", "continut": "Text."})
        self.assertEqual(raspuns.status_code, 403)

    def test_autorul_e_utilizatorul_logat(self):
        self.client.force_authenticate(self.mihai)
        raspuns = self.client.post("/api/articole/", {"titlu": "Nou", "continut": "Text."})
        self.assertEqual(raspuns.status_code, 201)
        self.assertEqual(raspuns.json()["autor"], "mihai")

    def test_doar_autorul_poate_modifica(self):
        self.client.force_authenticate(self.mihai)
        raspuns = self.client.patch(f"/api/articole/{self.articol.id}/", {"titlu": "Altul"})
        self.assertEqual(raspuns.status_code, 403)
'''

SETTINGS_61 = r'''
"""Setările proiectului blog_proiect.

Toate setările posibile: https://docs.djangoproject.com/en/5.2/ref/settings/
Pe server, valorile sensibile vin din variabile de mediu (lecția 61):
DJANGO_SECRET_KEY, DJANGO_DEBUG=0, DJANGO_ALLOWED_HOSTS, DJANGO_CSRF_TRUSTED_ORIGINS,
DJANGO_DB_PATH.
"""
import os
from pathlib import Path

# Folderul proiectului (cel cu manage.py); celelalte căi pornesc de aici.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cheia secretă semnează sesiunile și formularele. Pe server vine din DJANGO_SECRET_KEY;
# valoarea de rezervă e bună doar pe calculatorul tău.
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
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
'''

REQUIREMENTS_61 = r'''
Django==5.2.18
djangorestframework==3.18.3
gunicorn==23.0.0
whitenoise==6.12.0
'''


def build(upto: int = 61) -> None:
    stage45()
    stages = {
        46: dict(files={"blog_proiect/settings.py": SETTINGS_46}),
        47: dict(files={"blog_proiect/urls.py": PROJECT_URLS_47, "articole/urls.py": APP_URLS_47,
                        "articole/views.py": VIEWS_47}),
        48: dict(files={"articole/views.py": VIEWS_48, "articole/urls.py": APP_URLS_48,
                        "articole/templates/articole/base.html": BASE_48,
                        "articole/templates/articole/lista.html": LISTA_HTML,
                        "articole/templates/articole/_meta.html": META_48,
                        "articole/templates/articole/detaliu.html": DETALIU_48,
                        "articole/templates/articole/despre.html": DESPRE_HTML}),
        49: dict(files={"articole/templates/articole/base.html": BASE_49, "articole/static/articole/stil.css": STIL_CSS}),
        50: dict(files={"articole/models.py": MODELS_50}, migrate=True),
        51: dict(files={"articole/models.py": MODELS_51}, migrate=True),
        52: dict(files={"articole/views.py": VIEWS_52}),
        53: dict(files={"articole/models.py": models_53(), "articole/views.py": VIEWS_53,
                        "articole/templates/articole/detaliu.html": detaliu_html(True, True, False)}, migrate=True),
        54: dict(files={"articole/admin.py": ADMIN_54}),
        55: dict(files={"articole/forms.py": FORMS_55, "articole/views.py": VIEWS_55, "articole/urls.py": APP_URLS_55,
                        "articole/templates/articole/contact.html": CONTACT_HTML,
                        "articole/templates/articole/base.html": BASE_55}),
        56: dict(files={"articole/forms.py": FORMS_56, "articole/views.py": VIEWS_56, "articole/urls.py": APP_URLS_56,
                        "articole/templates/articole/base.html": BASE_56,
                        "articole/templates/articole/detaliu.html": detaliu_html(True, True, True, ACTIUNI_56),
                        "articole/templates/articole/formular_articol.html": FORMULAR_ARTICOL_HTML}),
        57: dict(files={"articole/models.py": models_53(autor=True), "articole/views.py": VIEWS_57,
                        "articole/urls.py": APP_URLS_57, "articole/admin.py": ADMIN_57,
                        "blog_proiect/urls.py": PROJECT_URLS_57, "blog_proiect/settings.py": SETTINGS_57,
                        "articole/templates/articole/base.html": BASE_57,
                        "articole/templates/articole/_meta.html": META_57,
                        "articole/templates/articole/detaliu.html": detaliu_html(True, True, True, ACTIUNI_57),
                        "articole/templates/registration/login.html": LOGIN_HTML,
                        "articole/templates/registration/inregistrare.html": INREGISTRARE_HTML}, migrate=True),
        58: dict(files={"articole/views.py": VIEWS_58, "articole/urls.py": APP_URLS_58,
                        "articole/templates/articole/detaliu.html": detaliu_html(True, True, True, ACTIUNI_58),
                        "articole/templates/articole/confirma_stergere.html": CONFIRMA_STERGERE_HTML}),
        59: dict(files={"articole/tests.py": TESTS_59}),
        60: dict(files={"articole/serializers.py": SERIALIZERS_60, "articole/api.py": API_60,
                        "articole/urls.py": APP_URLS_60, "articole/tests_api.py": TESTS_API_60,
                        "blog_proiect/settings.py": SETTINGS_60}),
        61: dict(files={"blog_proiect/settings.py": SETTINGS_61, "requirements.txt": REQUIREMENTS_61}),
    }
    for nr in range(46, upto + 1):
        stage(nr, **stages[nr])


if __name__ == "__main__":
    build(int(sys.argv[1]) if len(sys.argv) > 1 else 61)
