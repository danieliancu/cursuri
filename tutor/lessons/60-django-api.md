<!-- proiect: _blog/59 -->
<!-- proiect-final: _blog/60 -->
<!-- pregatire: python manage.py migrate -v 0 && python manage.py loaddata /lectii/_blog/date/57.json -v 0 -->
## Ce este

Până acum, blogul Anei răspunde cu **pagini HTML**, făcute pentru oameni. Un **API** (Application Programming Interface) răspunde cu **date**, făcute pentru alte programe: o aplicație de telefon, o pagină scrisă în JavaScript, un script Python al lui Mihai care vrea lista articolelor.

Formatul obișnuit al datelor e **JSON** (lecția 28). Aceeași informație, în cele două forme:

```text
HTML (pentru oameni):    <h1>De ce am ales Django</h1> <p class="meta">2 octombrie 2026 · Programare</p>
JSON (pentru programe):  {"id": 2, "titlu": "De ce am ales Django", "data_publicarii": "2026-10-02", ...}
```

Un **API REST** organizează datele ca **resurse** cu adrese (`/api/articole/`, `/api/articole/2/`), iar ce faci cu ele spune **metoda HTTP** (lecția 43). **Django REST Framework** (DRF) e pachetul cu care se scriu aproape toate API-urile în Django.

## De ce contează

Un site modern rar are un singur „client”. Aceleași articole pot fi citite de browser, de o aplicație mobilă, de un alt site care afișează ultimele postări ale Anei sau de un program care face statistici. În loc să scrie câte o variantă pentru fiecare, Ana publică datele o dată, printr-un API, iar fiecare client le afișează cum vrea.

Ce ai învățat deja se refolosește aproape în întregime: modelele, permisiunile și validarea. DRF adaugă doar stratul care transformă obiectele Python în JSON și invers. Vei recunoaște multe idei din formularele de la lecțiile 55–56 și din class-based views (lecția 58).

Lucrezi tot în proiectul PyTutor **`blog`**.

## Cum funcționează

### REST pe scurt

| Metodă | Adresă | Ce face | Răspuns obișnuit |
|---|---|---|---|
| `GET` | `/api/articole/` | lista articolelor | `200 OK` |
| `POST` | `/api/articole/` | creează un articol | `201 Created` |
| `GET` | `/api/articole/2/` | un articol | `200 OK` sau `404 Not Found` |
| `PUT` / `PATCH` | `/api/articole/2/` | îl modifică (complet / doar unele câmpuri) | `200 OK` |
| `DELETE` | `/api/articole/2/` | îl șterge | `204 No Content` |

Când ceva nu e în regulă, codul de status spune ce: `400 Bad Request` (date greșite), `403 Forbidden` (n-ai voie), `404 Not Found` (nu există).

### Instalarea

În afara PyTutor, DRF se instalează cu pip (lecția 30):

```bash
pip install djangorestframework
```

În terminalul din PyTutor e deja instalat. Ca orice aplicație Django, trebuie adăugat în `INSTALLED_APPS`. Singura schimbare din `blog_proiect/settings.py` e rândul `"rest_framework"`:

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
    "rest_framework",
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

### Serializerul: din obiect în JSON și înapoi

Un **serializer** face pentru JSON ce face un `ModelForm` pentru HTML (lecția 56): știe ce câmpuri are un articol, le transformă în valori simple pentru JSON și, în sens invers, validează datele primite înainte să fie salvate. Fișier nou, `articole/serializers.py`:

<!-- fisier: articole/serializers.py -->
```python
from rest_framework import serializers

from .models import Articol


class ArticolSerializer(serializers.ModelSerializer):
    """Cum arată un articol în JSON: câmpurile alese și cum se transformă."""

    autor = serializers.ReadOnlyField(source="autor.username")
    categorie = serializers.StringRelatedField()

    class Meta:
        model = Articol
        fields = ["id", "titlu", "continut", "data_publicarii", "categorie", "autor"]
```

- **`ModelSerializer`** citește câmpurile din model, la fel ca `ModelForm`; în `Meta.fields` alegi exact ce câmpuri apar în JSON;
- **`autor`**: în model e o legătură spre un `User`. Fără nimic special, JSON-ul ar conține doar id-ul utilizatorului (`1`). `ReadOnlyField(source="autor.username")` pune în schimb numele de utilizator și îl face doar de citit: autorul nu se trimite, îl stabilește serverul;
- **`categorie`**: `StringRelatedField` pune textul dat de `__str__` al categoriei (`"Programare"`), tot doar de citit.

Îl poți încerca în `python manage.py shell`:

```python
import json

from articole.models import Articol
from articole.serializers import ArticolSerializer

articol = Articol.objects.get(id=2)
rezultat = ArticolSerializer(articol).data
print(json.dumps(rezultat, ensure_ascii=False, indent=2))
```

<!-- comanda: python manage.py shell -v 0 -c "import json; from articole.models import Articol; from articole.serializers import ArticolSerializer; articol = Articol.objects.get(id=2); rezultat = ArticolSerializer(articol).data; print(json.dumps(rezultat, ensure_ascii=False, indent=2))" -->
```text
{
  "id": 2,
  "titlu": "De ce am ales Django",
  "continut": "După primele luni cu Python, voiam să fac un site adevărat: cu pagini, cu bază de date și cu un loc unde să mă autentific.\n\nDjango are toate acestea „din cutie”, iar documentația lui e excelentă.",
  "data_publicarii": "2026-10-02",
  "categorie": "Programare",
  "autor": "ana"
}
```

`.data` e un dicționar cu valori simple (datele calendaristice au devenit texte în formatul `AAAA-LL-ZZ`), iar `json.dumps` îl transformă în JSON. Exact asta va trimite API-ul.

În sens invers, serializerul validează, ca un formular: `is_valid()` și `errors`.

```python
serializer = ArticolSerializer(data={"titlu": "Nou", "data_publicarii": "29.10.2026"})
print(serializer.is_valid())
print(json.dumps(serializer.errors, ensure_ascii=False, indent=2))
```

<!-- comanda: python manage.py shell -v 0 -c "import json; from articole.serializers import ArticolSerializer; serializer = ArticolSerializer(data={'titlu': 'Nou', 'data_publicarii': '29.10.2026'}); print(serializer.is_valid()); print(json.dumps(serializer.errors, ensure_ascii=False, indent=2))" -->
```text
False
{
  "continut": [
    "Acest câmp este obligatoriu."
  ],
  "data_publicarii": [
    "Data are formatul greșit. Utilizați unul dintre aceste formate în loc: YYYY-MM-DD."
  ]
}
```

Mesajele sunt în română pentru că proiectul are `LANGUAGE_CODE = "ro"` (lecția 46). În JSON, datele calendaristice se scriu mereu `AAAA-LL-ZZ` (`"2026-10-29"`), nu în formatul românesc.

### ViewSet-ul: toate operațiile într-o clasă

La lecția 58 ai scris câte o clasă pentru listă, detaliu, creare, editare și ștergere. Un **ViewSet** din DRF le grupează pe toate pentru o resursă. Fișier nou, `articole/api.py`:

<!-- fisier: articole/api.py -->
```python
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
```

- **`ModelViewSet`** oferă toate operațiile din tabelul REST: listă, detaliu, creare, modificare, ștergere;
- **`queryset`**: ce articole vede API-ul. Ca pe site, doar cele publicate; `select_related` (lecția 53) aduce categoria și autorul în aceeași interogare;
- **`permission_classes`**: `IsAuthenticatedOrReadOnly` lasă pe oricine să citească, dar cere cont pentru scriere. `EsteAutorulSauDoarCitire` e o permisiune scrisă de noi: metodele „sigure” (`SAFE_METHODS`: `GET`, `HEAD`, `OPTIONS`) sunt permise oricui, celelalte doar autorului. E aceeași regulă ca la editarea articolelor pe site (lecția 58);
- **`perform_create`** rulează la `POST`, după ce datele au trecut validarea, și face salvarea: `serializer.save(autor=...)` pune ca autor al articolului nou utilizatorul care a trimis cererea, ca la `ArticolNou` din lecția 58.

### Routerul: adresele

Un **router** creează singur adresele pentru un ViewSet. În `articole/urls.py`, routerul se înregistrează și apoi se include sub `api/`:

<!-- fisier: articole/urls.py -->
```python
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
```

Gata. API-ul răspunde. Rădăcina lui, `/api/`, arată ce resurse există:

<!-- comanda: python /h/vezi_pagina.py /api/ -->
```text
200 OK
{
  "articole": "http://testserver/api/articole/"
}
```

(`testserver` e numele folosit de verificare; pe calculatorul tău apare adresa reală a serverului.) Lista articolelor:

<!-- comanda: python /h/vezi_pagina.py /api/articole/ -->
```text
200 OK
[
  {
    "id": 3,
    "titlu": "O plimbare prin Cluj",
    "continut": "Duminică am urcat pe dealul Cetățuia, de unde se vede tot Clujul. Pe drum am trecut prin Piața Unirii și pe lângă Teatrul Național.\n\nData viitoare vreau să ajung și în Grădina Botanică.",
    "data_publicarii": "2026-10-20",
    "categorie": "Călătorii",
    "autor": "ana"
  },
  {
    "id": 2,
    "titlu": "De ce am ales Django",
    "continut": "După primele luni cu Python, voiam să fac un site adevărat: cu pagini, cu bază de date și cu un loc unde să mă autentific.\n\nDjango are toate acestea „din cutie”, iar documentația lui e excelentă.",
    "data_publicarii": "2026-10-02",
    "categorie": "Programare",
    "autor": "ana"
  },
  {
    "id": 1,
    "titlu": "Primul meu program în Python",
    "continut": "Totul a început cu un simplu print(\"Salut, lume!\"). Nu credeam că două cuvinte pe ecran pot să bucure atât de mult.\n\nAzi știu că a fost primul pas dintr-un drum lung: variabile, bucle, funcții și clase.",
    "data_publicarii": "2026-09-14",
    "categorie": "Programare",
    "autor": "ana"
  }
]
```

Și un singur articol, după id:

<!-- comanda: python /h/vezi_pagina.py /api/articole/2/ -->
```text
200 OK
{
  "id": 2,
  "titlu": "De ce am ales Django",
  "continut": "După primele luni cu Python, voiam să fac un site adevărat: cu pagini, cu bază de date și cu un loc unde să mă autentific.\n\nDjango are toate acestea „din cutie”, iar documentația lui e excelentă.",
  "data_publicarii": "2026-10-02",
  "categorie": "Programare",
  "autor": "ana"
}
```

Pornește serverul (`python manage.py runserver 0.0.0.0:8000`) și deschide `/api/articole/` în browser, la adresa din bara terminalului. Vei vedea o pagină HTML cu același JSON, plus formulare pentru încercat cererile: e **API-ul navigabil** al DRF, foarte util cât timp scrii API-ul.

### Ce se întâmplă „pe dedesubt”: ce a creat routerul

Routerul a adăugat adrese pe care nu le-ai scris tu:

```python
from articole.urls import router

print(*router.urls, sep="\n")
```

<!-- comanda: python manage.py shell -v 0 -c "from articole.urls import router; print(*router.urls, sep=chr(10))" -->
```text
<URLPattern '^articole/$' [name='articol-list']>
<URLPattern '^articole\.(?P<format>[a-z0-9]+)/?$' [name='articol-list']>
<URLPattern '^articole/(?P<pk>[^/.]+)/$' [name='articol-detail']>
<URLPattern '^articole/(?P<pk>[^/.]+)\.(?P<format>[a-z0-9]+)/?$' [name='articol-detail']>
<URLPattern '' [name='api-root']>
<URLPattern '<drf_format_suffix:format>' [name='api-root']>
```

- `articole/` (numele `articol-list`) primește `GET` (lista) și `POST` (creare); ViewSet-ul le trimite metodelor `list` și `create`;
- `articole/<pk>/` (`articol-detail`) primește `GET`, `PUT`, `PATCH` și `DELETE`, trimise la `retrieve`, `update`, `partial_update` și `destroy`;
- variantele cu `format` permit adrese ca `/api/articole.json`; ultimele două sunt rădăcina `/api/`.

De unde știe DRF să dea JSON unui program și o pagină HTML browserului? Din headerul `Accept` al cererii (lecția 43). Browserul cere `text/html`, deci primește API-ul navigabil; un program care cere `application/json`, sau nu cere nimic anume, primește JSON. Mecanismul se numește **negocierea conținutului** (în engleză „content negotiation”).

## Exemplu complet

Scrierea prin API. Fără cont, un `POST` e refuzat:

<!-- comanda: python /h/vezi_pagina.py POST /api/articole/ titlu=Nou continut=Text -->
```text
Forbidden: /api/articole/
403 Forbidden
{
  "detail": "Datele de autentificare nu au fost furnizate."
}
```

(Primul rând e mesajul scris de Django în terminalul serverului la fiecare răspuns cu eroare; clientul primește doar statusul și JSON-ul.) Autentificat ca Mihai, articolul e creat, iar autorul e pus de server:

<!-- comanda: python /h/vezi_pagina.py --user mihai POST /api/articole/ 'titlu=Salut din API' 'continut=Primul meu articol trimis prin API.' data_publicarii=2026-10-29 -->
```text
201 Created
{
  "id": 4,
  "titlu": "Salut din API",
  "continut": "Primul meu articol trimis prin API.",
  "data_publicarii": "2026-10-29",
  "categorie": null,
  "autor": "mihai"
}
```

Răspunsul `201 Created` conține articolul salvat, cu id-ul primit de la baza de date. `categorie` e `null` (echivalentul lui `None` în JSON), pentru că serializerul o tratează ca doar de citit.

Un program real ar trimite datele ca JSON și s-ar autentifica, de exemplu cu numele și parola (autentificarea „Basic”, pe care DRF o acceptă implicit). Cu serverul pornit, într-un al doilea terminal, cererea ar arăta cam așa (exemplu ilustrativ, nerulat aici):

```bash
curl -u mihai:parola-mihai-2026 -H "Content-Type: application/json" \
     -d '{"titlu": "Salut", "continut": "Din curl.", "data_publicarii": "2026-10-30"}' \
     http://localhost:8000/api/articole/
```

Cu autentificarea „Basic”, parola călătorește în fiecare cerere, doar codificată, nu criptată: pe un server real se folosește numai prin HTTPS (lecția 61). În aplicațiile reale se folosesc de obicei **token-uri** în loc de parolă, tot printr-un header; DRF le oferă prin `rest_framework.authtoken`.

Ca orice parte a site-ului, API-ul are testele lui. DRF oferă `APITestCase`, cu un client care știe JSON și cu `force_authenticate` (echivalentul lui `force_login` din lecția 59). Fișier nou, `articole/tests_api.py`:

<!-- fisier: articole/tests_api.py -->
```python
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
```

Numele fișierului începe cu `test`, deci `manage.py test` îl găsește singur, alături de `tests.py`:

<!-- ruleaza -->
```bash
python manage.py test
```

```text
Found 17 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.................
----------------------------------------------------------------------
Ran 17 tests in 1.000s

OK
Destroying test database for alias 'default'...
```

Cele 13 teste ale site-ului și cele 4 ale API-ului trec. (Dacă ai făcut exercițiul din lecția 59, la tine numărul e mai mare, cu testele adăugate de tine.) Ultimul test verifică permisiunea noastră: Mihai e autentificat, dar articolul e al Anei, deci `PATCH` primește 403.

## Greșeli frecvente

Pentru greșelile 3 și 4 folosim un fișier de încercare, `articole/serializers_incercare.py`, pe care îl ștergem la final.

### 1. POST la o adresă fără / la final

<!-- comanda: python /h/vezi_pagina.py --user mihai POST /api/articole titlu=Nou continut=Text -->
```text
Internal Server Error: /api/articole
Traceback (most recent call last):
RuntimeError: You called this URL via POST, but the URL doesn't end in a slash and you have APPEND_SLASH set. Django can't redirect to the slash URL while maintaining POST data. Change your form to point to testserver/api/articole/ (note the trailing slash), or set APPEND_SLASH=False in your Django settings.
```

(Tracebackul complet e mult mai lung.) La un `GET` fără `/`, Django redirecționează singur spre adresa cu `/` (`301`). La `POST` nu poate, pentru că datele trimise s-ar pierde la redirecționare, așa că se oprește cu eroare. Adresele API-ului se termină mereu cu `/`: `/api/articole/`.

### 2. Date lipsă sau în alt format

<!-- comanda: python /h/vezi_pagina.py --user mihai POST /api/articole/ titlu=Nou -->
```text
Bad Request: /api/articole/
400 Bad Request
{
  "continut": [
    "Acest câmp este obligatoriu."
  ]
}
```

`400 Bad Request` cu erorile pe câmpuri, ca un formular reafișat (lecția 55). Clientul trebuie să citească răspunsul și să corecteze datele. Atenție și la formatul datelor calendaristice: JSON-ul folosește `"2026-10-29"`, iar `"29.10.2026"` e respins (vezi „Serializerul”).

### 3. fields = "__all__"

<!-- fisier: articole/serializers_incercare.py -->
```python
from rest_framework import serializers

from .models import Articol


class TotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articol
        fields = "__all__"


class GresitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articol
        fields = ["id", "titlul"]
```

```python
articol = Articol.objects.get(id=2)
print(json.dumps(TotSerializer(articol).data, ensure_ascii=False, indent=2))
```

<!-- comanda: python manage.py shell -v 0 -c "import json; from articole.models import Articol; from articole.serializers_incercare import TotSerializer; articol = Articol.objects.get(id=2); print(json.dumps(TotSerializer(articol).data, ensure_ascii=False, indent=2))" -->
```text
{
  "id": 2,
  "titlu": "De ce am ales Django",
  "continut": "După primele luni cu Python, voiam să fac un site adevărat: cu pagini, cu bază de date și cu un loc unde să mă autentific.\n\nDjango are toate acestea „din cutie”, iar documentația lui e excelentă.",
  "data_publicarii": "2026-10-02",
  "publicat": true,
  "categorie": 1,
  "autor": 1,
  "etichete": [
    2,
    1
  ]
}
```

Funcționează, dar trimite **tot** ce are modelul: câmpul intern `publicat`, id-uri (`1`, `[2, 1]`) care nu spun nimic clientului și, mai grav, orice câmp adăugat pe viitor în model, inclusiv unul care n-ar trebui să fie public. Scrie lista câmpurilor explicit, ca în `ArticolSerializer`.

### 4. Un câmp care nu există

```python
print(GresitSerializer(articol).data)
```

<!-- comanda: python manage.py shell -v 0 -c "from articole.models import Articol; from articole.serializers_incercare import GresitSerializer; articol = Articol.objects.get(id=2); print(GresitSerializer(articol).data)" -->
```text
Traceback (most recent call last):
django.core.exceptions.ImproperlyConfigured: Field name `titlul` is not valid for model `Articol` in `articole.serializers_incercare.GresitSerializer`.
```

O greșeală de tastare în `fields` (`titlul` în loc de `titlu`) apare abia când serializerul e folosit prima dată. Mesajul numește câmpul, modelul și serializerul. Testele API-ului (care folosesc serializerul) prind astfel de greșeli înainte să ajungă la clienți.

După încercări, șterge fișierul și rulează din nou testele:

<!-- ruleaza -->
```bash
rm articole/serializers_incercare.py
python manage.py test
```

```text
Found 17 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.................
----------------------------------------------------------------------
Ran 17 tests in 1.000s

OK
Destroying test database for alias 'default'...
```

## Exercițiu

În proiectul PyTutor **`blog`** (fișierul capitolului, `capitole/60-django-api/django_api.py`, poate rămâne pentru notițe):

1. adaugă în `ArticolSerializer` câmpul `etichete`, ca listă de **nume** (nu de id-uri): `serializers.SlugRelatedField(many=True, read_only=True, slug_field="nume")`, și pune-l în `fields`. Verifică `/api/articole/2/`: trebuie să apară `"etichete": ["django", "python"]`;
2. creează un `CategorieSerializer` (câmpurile `id` și `nume`) și un `CategorieViewSet` derivat din `viewsets.ReadOnlyModelViewSet` (doar citire), înregistrat în router la `"categorii"`. Verifică `/api/` și `/api/categorii/`;
3. în `tests_api.py`, adaugă un test că `/api/categorii/` răspunde cu 200 și un test că un `POST` la `/api/categorii/` e refuzat, chiar și pentru un utilizator autentificat (codul e `405 Method Not Allowed`: metoda nu există pentru această resursă);
4. rulează `python manage.py test` până trec toate testele.

## Pe scurt

- Un API trimite date (JSON) pentru programe; REST organizează datele ca resurse cu adrese, iar metoda HTTP spune operația (`GET`, `POST`, `PUT`/`PATCH`, `DELETE`).
- Django REST Framework se adaugă în `INSTALLED_APPS` ca `"rest_framework"`.
- Un **serializer** (`ModelSerializer`) transformă obiecte în JSON și validează datele primite, ca un `ModelForm`; scrie explicit lista `fields`.
- Un **ViewSet** (`ModelViewSet`) grupează toate operațiile; `permission_classes` și `perform_create` controlează cine scrie și ce se salvează.
- Un **router** creează adresele (`/api/articole/`, `/api/articole/<id>/`); adresele se termină cu `/`.
- Codurile de status spun rezultatul: 200, 201, 400 (date greșite), 403 (fără drept), 404; API-ul se testează cu `APITestCase`.
