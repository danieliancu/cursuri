## Ce este

**Autentificarea** înseamnă să afli **cine** e utilizatorul: își spune numele și dovedește, cu parola, că e chiar el. Pe ea se sprijină **autorizarea**: hotărăști **ce are voie** să facă fiecare.

Django are un sistem complet de autentificare, în aplicația `django.contrib.auth`, activată din prima zi a proiectului (lecția 45):
- modelul `User`, cu nume de utilizator, parolă (păstrată niciodată în clar) și e-mail;
- pagini gata făcute pentru **login**, **logout** și schimbarea parolei;
- `request.user` în fiecare view și `user` în fiecare template: utilizatorul cererii curente;
- decoratorul `@login_required`, care oprește vizitatorii neautentificați.

În lecția asta, blogul Anei devine un site cu conturi: doar cine e autentificat poate scrie articole, fiecare articol are un **autor**, și doar autorul își poate edita articolele.

## De ce contează

După lecția 56, oricine putea scrie și edita orice articol din blogul Anei, inclusiv un vizitator rău intenționat. Aproape orice aplicație reală are nevoie de conturi: un magazin (comenzile **tale**), o rețea socială (postările **tale**), o aplicație de note (doar tu le vezi).

Partea de securitate e greu de scris corect de la zero: parolele nu se păstrează niciodată în clar, sesiunile trebuie protejate, iar formularele de login trebuie să reziste la atacuri. Django le are pe toate testate de mii de proiecte. Treaba ta e să le legi în aplicație.

## Cum funcționează

Lucrezi în proiectul PyTutor `blog`, pornind de la starea de la finalul lecției 56. Contul de superuser al Anei există deja din lecția 54.

### 1. Utilizatorii

Tabelul utilizatorilor există de la primul `migrate` (lecția 50). Pe lângă `createsuperuser` (lecția 54), un utilizator obișnuit se creează în cod cu `create_user`, care nu salvează parola ca atare, ci un hash al ei (vezi „pe dedesubt”):

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c '
from django.contrib.auth.models import User

mihai = User.objects.create_user("mihai", "mihai@exemplu.ro", "parola-mihai-2026")
print(mihai.username, mihai.is_staff, mihai.is_superuser)
print([u.username for u in User.objects.order_by("id")])
'
```

```text
mihai False False
['ana', 'mihai']
```

Mihai e un utilizator obișnuit: poate intra pe site, dar nu și în panoul de admin (`is_staff` e `False`).

### 2. Autorul articolului: models.py și o migrare

Fiecare articol primește un autor, adică o legătură spre un utilizator:

<!-- fisier: articole/models.py -->
```python
from datetime import date

from django.conf import settings
from django.db import models
from django.urls import reverse


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
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articole",
    )

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
```

Câmpul nou e `autor`, un `ForeignKey` (lecția 53):
- `settings.AUTH_USER_MODEL` înseamnă „modelul de utilizator al proiectului”. De obicei e `User`, dar un proiect își poate defini propriul model, iar codul scris așa merge cu oricare;
- `null=True`: articolele existente nu au încă autor, iar dacă un cont e șters, articolele rămân (`SET_NULL`), fără autor.

Migrarea, ca la lecția 51:

<!-- ruleaza -->
```bash
python manage.py makemigrations
python manage.py migrate
```

```text
Migrations for 'articole':
  articole/migrations/0004_articol_autor.py
    + Add field autor to articol
Operations to perform:
  Apply all migrations: admin, articole, auth, contenttypes, sessions
Running migrations:
  Applying articole.0004_articol_autor... OK
```

Cele trei articole existente sunt ale Anei:

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c '
from django.contrib.auth.models import User
from articole.models import Articol

print(Articol.objects.update(autor=User.objects.get(username="ana")))
'
```

```text
3
```

`update()` (lecția 52) întoarce numărul de rânduri modificate.

### 3. Paginile de login și logout: blog_proiect/urls.py

Django are view-urile gata făcute. Le legi de o adresă cu `include`:

<!-- fisier: blog_proiect/urls.py -->
```python
"""Adresele proiectului: fiecare cerere e trimisă mai departe după începutul căii."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # login/, logout/, schimbarea parolei: view-urile gata făcute ale Django
    path("conturi/", include("django.contrib.auth.urls")),
    path("", include("articole.urls")),
]
```

Acum există `/conturi/login/` (numele URL `login`), `/conturi/logout/` (`logout`), `/conturi/password_change/` și altele. View-ul de login caută un template cu un nume fix, `registration/login.html`, pe care îl scrii tu:

<!-- fisier: articole/templates/registration/login.html -->
```html
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
```

View-ul Django își numește formularul `form` (nu `formular`, ca la noi). Câmpul ascuns `next` păstrează pagina la care voia să ajungă vizitatorul înainte să fie trimis la login (vezi mai jos).

În `settings.py`, la final, spunem unde e pagina de login și unde ajunge utilizatorul după login și după logout. Valorile sunt nume de URL (lecția 47):

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

# Autentificare: unde trimitem utilizatorul să intre în cont și unde ajunge după login/logout.
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "lista"
LOGOUT_REDIRECT_URL = "lista"
```

Doar ultimele patru rânduri sunt noi.

### 4. Cine are voie: articole/views.py

<!-- fisier: articole/views.py -->
```python
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
```

Ce e nou:
- **`@login_required`** e decoratorul promis la lecția 38. Înainte să ruleze view-ul, verifică `request.user`. Dacă vizitatorul nu e autentificat, răspunde cu o redirecționare spre `LOGIN_URL`, iar adresa cerută o pune în `?next=...`, ca după login să ajungă înapoi acolo;
- **`request.user`** e utilizatorul cererii: un obiect `User` pentru cine e autentificat sau un `AnonymousUser` (cu `is_authenticated` egal cu `False`) pentru ceilalți;
- **autorul** nu vine din formular, ci din cerere: `save(commit=False)` (lecția 56), `articol.autor = request.user`, apoi `save()`. `ArticolForm` are etichete (multi-la-multi), deci după `save()` e nevoie și de `formular.save_m2m()`;
- **doar autorul** editează: dacă `articol.autor` nu e utilizatorul cererii, `raise PermissionDenied(...)` (lecția 25). Django prinde excepția și răspunde `403 Forbidden`;
- **`inregistrare`** folosește `UserCreationForm`, un `ModelForm` gata făcut pentru `User` (nume, parolă, confirmarea parolei, cu toate validările de parolă din `AUTH_PASSWORD_VALIDATORS`). După creare, `login(request, utilizator)` îl autentifică direct, ca să nu mai treacă prin pagina de login.

Adresa paginii de înregistrare și template-ul ei:

<!-- fisier: articole/urls.py -->
```python
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
    path("conturi/inregistrare/", views.inregistrare, name="inregistrare"),
]
```

<!-- fisier: articole/templates/registration/inregistrare.html -->
```html
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
```

### 5. Template-urile se adaptează utilizatorului

În orice template, `user` e utilizatorul cererii. Meniul arată „Scrie un articol” și butonul de ieșire doar celor autentificați, iar celorlalți linkurile de autentificare și de cont nou:

<!-- fisier: articole/templates/articole/base.html -->
```html
{% load static %}
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block titlu %}Blogul Anei{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'articole/stil.css' %}">
</head>
<body>
  <header class="antet">
    <a href="{% url 'lista' %}" class="sigla">Blogul Anei</a>
    <nav>
      <a href="{% url 'lista' %}">Articole</a>
      <a href="{% url 'despre' %}">Despre</a>
      <a href="{% url 'contact' %}">Contact</a>
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
    </nav>
  </header>

  <main>
    {% for mesaj in messages %}
      <p class="mesaj">{{ mesaj }}</p>
    {% endfor %}
    {% block continut %}{% endblock %}
  </main>

  <footer class="subsol">
    <p>Ana Popescu, Cluj · 2026</p>
  </footer>
</body>
</html>
```

Ieșirea din cont e un **formular POST**, nu un link: de la Django 5, logout-ul acceptă doar POST (vezi greșelile frecvente).

Autorul apare lângă dată, în fragmentul comun listei și paginii articolului:

<!-- fisier: articole/templates/articole/_meta.html -->
```html
<p class="meta">
  {{ articol.data_publicarii|date:"j F Y"|lower }}
  {% if articol.categorie %} · <span class="categorie">{{ articol.categorie }}</span>{% endif %}
  {% if articol.autor %} · de {{ articol.autor.username }}{% endif %}
</p>
```

Linkul de editare îl vede doar autorul:

<!-- fisier: articole/templates/articole/detaliu.html -->
```html
{% extends "articole/base.html" %}

{% block titlu %}{{ articol.titlu }} · Blogul Anei{% endblock %}

{% block continut %}
  <article class="articol">
    <h1>{{ articol.titlu }}</h1>
    {% include "articole/_meta.html" %}
    {{ articol.continut|linebreaks }}
    {% if articol.etichete.all %}
      <p class="meta">Etichete: {{ articol.etichete.all|join:", " }}</p>
    {% endif %}
    {% if user == articol.autor %}
      <p><a href="{% url 'articol_editeaza' articol.id %}">Editează articolul</a></p>
    {% endif %}
  </article>
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
    <form action="{% url 'comentariu' articol.id %}" method="post" class="formular">
      <h3>Lasă un comentariu</h3>
      {% csrf_token %}
      {{ formular.as_div }}
      <button type="submit">Trimite comentariul</button>
    </form>
  </section>
{% endblock %}
```

În panoul de admin, autorul apare în listă și ca filtru:

<!-- fisier: articole/admin.py -->
```python
from django.contrib import admin

from .models import Articol, Categorie, Comentariu, Eticheta


class ComentariuInline(admin.TabularInline):
    model = Comentariu
    extra = 0


@admin.register(Articol)
class ArticolAdmin(admin.ModelAdmin):
    list_display = ["titlu", "autor", "categorie", "data_publicarii", "publicat"]
    list_filter = ["publicat", "categorie", "autor"]
    search_fields = ["titlu", "continut"]
    inlines = [ComentariuInline]


@admin.register(Comentariu)
class ComentariuAdmin(admin.ModelAdmin):
    list_display = ["autor", "articol", "data"]
    search_fields = ["autor", "text"]


admin.site.register(Categorie)
admin.site.register(Eticheta)
```

### Încearcă

Un vizitator neautentificat care vrea să scrie un articol e trimis la login, cu adresa cerută în `next`:

<!-- comanda: python /h/vezi_pagina.py /articol/nou/ -->
```text
302 Found
Location: /conturi/login/?next=/articol/nou/
```

Pagina de autentificare:

<!-- comanda: python /h/vezi_pagina.py /conturi/login/ | sed -n '/^Autentificare$/,$p' -->
```text
Autentificare
Nume utilizator:
[câmp: username]
Parolă:
[câmp: password]
Intră în cont
Nu ai cont? Creează unul.
Ana Popescu, Cluj · 2026
```

O parolă greșită:

<!-- comanda: python /h/vezi_pagina.py POST /conturi/login/ username=ana password=gresita | sed -n '/^Autentificare$/,/^Nume/p' -->
```text
Autentificare
Introduceți vă rog un nume utilizator corect și o parolă. Reţineţi că ambele câmpuri pot fi sensibile la litere mari şi mici.
Nume utilizator:
```

(Traducerea e cea a Django, cu diacriticele ei vechi, „ţ” și „ş”.) Mesajul nu spune care dintre cele două e greșit, intenționat: altfel un atacator ar afla ce nume de utilizator există. Cu parola corectă, Ana ajunge unde voia, la pagina „Articol nou”:

<!-- comanda: python /h/vezi_pagina.py POST /conturi/login/ username=ana password=parola-ana-2026 next=/articol/nou/ -->
```text
302 Found
Location: /articol/nou/
```

De aici încolo, browserul trimite la fiecare cerere cookie-ul de sesiune (vezi „pe dedesubt”), iar Django știe că e Ana. Unealta noastră simulează asta cu `--user ana`. Ana vede meniul cu „Scrie un articol”, butonul de ieșire și linkul de editare la propriul articol:

<!-- comanda: python /h/vezi_pagina.py --user ana /articol/2/ | sed -n '1,/^Editează/p' -->
```text
200 OK
Blogul Anei
Articole Despre Contact Scrie un articol
Ieși (ana)
De ce am ales Django
2 octombrie 2026 · Programare · de ana
După primele luni cu Python, voiam să fac un site adevărat: cu pagini, cu bază de date și cu un loc unde să mă autentific.
Django are toate acestea „din cutie”, iar documentația lui e excelentă.
Etichete: django, python
Editează articolul
```

Mihai e autentificat, dar articolul nu e al lui. Linkul de editare nu apare, iar dacă scrie adresa de mână, primește `403`:

<!-- comanda: python /h/vezi_pagina.py --user mihai /articol/2/editeaza/ 2>&1 | tail -n 3 -->
```text
django.core.exceptions.PermissionDenied: Doar autorul poate edita articolul.
403 Forbidden
403 Forbidden
```

Primul rând e finalul unui traceback pe care Django îl scrie în terminalul serverului, ca să știi ce s-a întâmplat. Vizitatorul vede doar pagina „403 Forbidden”.

Un vizitator nou își face cont. `UserCreationForm` cere parola de două ori:

<!-- comanda: python /h/vezi_pagina.py POST /conturi/inregistrare/ username=ioana password1=Clujul-meu-2026 password2=Clujul-meu-2026 -->
```text
302 Found
Location: /
```

### Ce se întâmplă „pe dedesubt”: cookie-uri și sesiuni

HTTP nu ține minte nimic între cereri (lecția 43): fiecare cerere vine „de la zero”. Cum știe atunci serverul că a doua cerere vine tot de la Ana?

1. La login reușit, Django creează o **sesiune**: un rând în tabelul `django_session`, cu o cheie lungă și aleatoare și datele utilizatorului (id-ul lui).
2. În răspuns, serverul trimite un **cookie** (un mic text pe care browserul îl păstrează pentru acel site): `sessionid=<cheia>`.
3. La fiecare cerere următoare, browserul trimite singur cookie-ul înapoi. Middleware-ul de sesiuni găsește rândul după cheie, iar cel de autentificare pune utilizatorul în `request.user`.
4. La logout, rândul sesiunii se șterge, deci cheia din cookie nu mai valorează nimic.

Le poți vedea cu clientul de test, care se poartă ca un browser:

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c '
from django.contrib.sessions.models import Session
from django.test import Client
from django.test.utils import setup_test_environment

setup_test_environment()
browser = Client()
browser.post("/conturi/login/", {"username": "ana", "password": "parola-ana-2026"})
print(sorted(browser.cookies))
sesiune = Session.objects.get(session_key=browser.cookies["sessionid"].value)
print(sorted(sesiune.get_decoded()))
print(sesiune.get_decoded()["_auth_user_id"])
'
```

```text
['csrftoken', 'sessionid']
['_auth_user_backend', '_auth_user_hash', '_auth_user_id']
1
```

În cookie e doar cheia. Datele (id-ul 1, al Anei) stau pe server, unde vizitatorul nu le poate modifica. Al doilea cookie, `csrftoken`, e cel din lecția 55.

**Parolele** nu se păstrează niciodată în clar. Django salvează un **hash**: rezultatul unei funcții care se calculează ușor într-un sens, dar nu se poate inversa. La login, se calculează hash-ul parolei introduse și se compară cu cel salvat:

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c '
from django.contrib.auth.models import User

ana = User.objects.get(username="ana")
print(ana.password.split("$")[:2])
print(ana.check_password("parola-ana-2026"), ana.check_password("parola"))
'
```

```text
['pbkdf2_sha256', '1000000']
True False
```

Algoritmul e `pbkdf2_sha256`, aplicat de un milion de ori, ca ghicirea parolelor prin încercări să fie foarte lentă.

## Exemplu complet

| Fișier | Ce s-a schimbat |
|---|---|
| `articole/models.py` | + `Articol.autor` (legătură spre utilizator) |
| `articole/migrations/0004_articol_autor.py` | nou, creat de `makemigrations` |
| `blog_proiect/urls.py` | + `conturi/` → `django.contrib.auth.urls` |
| `blog_proiect/settings.py` | + `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` |
| `articole/views.py` | `@login_required`, autorul din `request.user`, `PermissionDenied`, + `inregistrare` |
| `articole/urls.py` | + `conturi/inregistrare/` |
| `articole/templates/registration/login.html`, `inregistrare.html` | noi |
| `articole/templates/articole/base.html` | meniul după `user.is_authenticated`, logout prin POST |
| `articole/templates/articole/_meta.html`, `detaliu.html` | autorul; editare doar pentru autor |
| `articole/admin.py` | autorul în listă și în filtre |

Un articol nou scris de Mihai are automat autorul `mihai`, fără niciun câmp „autor” în formular:

<!-- comanda: python /h/vezi_pagina.py --user mihai --follow POST /articol/nou/ "titlu=Weekend la Iași" "continut=Palatul Culturii merită văzut." data_publicarii=2026-10-29 publicat=on | sed -n '/^Articolul/,/^Palatul/p' -->
```text
Articolul a fost salvat.
Weekend la Iași
29 octombrie 2026 · de mihai
Palatul Culturii merită văzut.
```

<!-- ruleaza -->
```bash
python manage.py check
```

```text
System check identified no issues (0 silenced).
```

## Greșeli frecvente

### 1. Logout printr-un link

```html
<a href="{% url 'logout' %}">Ieși</a>
```

Un link face o cerere GET, iar de la Django 5 logout-ul acceptă doar POST:

<!-- comanda: python /h/vezi_pagina.py --user ana /conturi/logout/ -->
```text
Method Not Allowed (GET): /conturi/logout/
405 Method Not Allowed
```

Motivul e de securitate: un link spre logout pus pe orice alt site (de exemplu, ca imagine) te-ar scoate din cont fără să vrei. Folosește un formular POST cu `{% csrf_token %}`, ca în `base.html`.

### 2. Lipsește LOGIN_URL

Fără `LOGIN_URL` în `settings.py`, `@login_required` trimite vizitatorul la adresa implicită, `/accounts/login/`. Blogul are login-ul la `/conturi/login/`, deci vizitatorul primește `404 Page not found`. Dacă pui view-urile de autentificare la altă adresă decât `accounts/`, setează `LOGIN_URL`.

### 3. Verificarea doar în template

Ascunderea linkului cu `{% if user == articol.autor %}` **nu** protejează nimic: oricine poate scrie adresa `/articol/2/editeaza/` în browser. Template-ul doar arată sau ascunde. Verificarea adevărată e în view (`@login_required`, `raise PermissionDenied`), cum ai văzut la Mihai, care a primit `403`.

### 4. commit=False fără save_m2m()

```python
articol = formular.save(commit=False)
articol.autor = request.user
articol.save()
# lipsește formular.save_m2m()
```

Articolul se salvează, dar **fără etichete**, iar nicio eroare nu te avertizează. Cu `commit=False`, formularul nu poate salva relațiile multi-la-multi (articolul nu avea încă `id`), așa că le păstrează până apelezi `formular.save_m2m()`.

### 5. Template-ul de login lipsește

Dacă `registration/login.html` nu există, pagina `/conturi/login/` dă eroare: `TemplateDoesNotExist at /conturi/login/` cu numele `registration/login.html`. View-urile din `django.contrib.auth.urls` caută template-uri cu nume fixe (`registration/login.html`, `registration/password_change_form.html` etc.), în orice folder `templates/` al aplicațiilor.

## Exercițiu

Lucrezi în proiectul PyTutor `blog`. La lecția 58 vei înlocui `views.py`, `urls.py`, `detaliu.html` și `formular_articol.html` cu versiunile din lecție, deci păstrează-ți adăugirile.

1. Pagina „Articolele mele”, la `/conturi/articolele-mele/`, cu `@login_required`: lista articolelor utilizatorului (`request.user.articole.all()`, grație `related_name="articole"`), inclusiv cele nepublicate.
2. Dacă utilizatorul e autentificat, precompletează câmpul `autor` al formularului de comentariu cu numele lui (indiciu: în `detaliu`, `ComentariuForm(initial={"autor": request.user.username})`).
3. Creează în panoul de admin grupul „Redactori” (Grupuri → Adaugă), pune-l pe Mihai în el (Utilizatori → mihai → Grupuri) și lasă-l să editeze orice articol dacă e în acest grup: `request.user.groups.filter(name="Redactori").exists()`.
4. Creează un cont nou din site, ieși din cont și intră din nou. Urmărește cookie-ul `sessionid` în instrumentele de dezvoltare ale browserului (F12 → Application → Cookies).

## Pe scurt

- `django.contrib.auth` dă modelul `User`, paginile de login/logout (`include("django.contrib.auth.urls")`) și `request.user` / `user` în view-uri și template-uri.
- `@login_required` trimite vizitatorii neautentificați la `LOGIN_URL`, cu `?next=` pentru întoarcere; `raise PermissionDenied` dă `403`.
- Verificarea drepturilor se face în view; template-ul doar ascunde linkuri.
- Autorul vine din `request.user`, nu din formular: `save(commit=False)`, completezi, `save()` și `save_m2m()`.
- Sesiunea ține minte utilizatorul: în cookie e doar cheia (`sessionid`), datele stau pe server; parolele se păstrează doar ca hash. Logout-ul se face prin POST.

<!-- proiect: _blog/56 -->
<!-- proiect-final: _blog/57 -->
<!-- pregatire: python manage.py migrate -v 0 && python manage.py loaddata /lectii/_blog/date/53.json -v 0 -->
<!-- pregatire: DJANGO_SUPERUSER_PASSWORD=parola-ana-2026 python manage.py createsuperuser --noinput --username ana --email ana@exemplu.ro > /dev/null -->
