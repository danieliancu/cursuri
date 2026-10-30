## Ce este

Un **template** (în română „șablon”) este un fișier HTML cu „găuri” pe care Django le completează cu date. Seamănă cu un f-string (lecția 5), dar pentru o pagină întreagă:

```html
<h1>{{ articol.titlu }}</h1>
<p>{{ articol.continut }}</p>
```

Limbajul de template are două feluri de marcaje:
- **`{{ ... }}`** afișează o valoare: `{{ articol.titlu }}`;
- **`{% ... %}`** e o instrucțiune (un „tag”): o buclă, o condiție, un link, moștenirea unei machete, de exemplu `{% for articol in articole %}`.

View-ul pregătește datele, iar template-ul decide cum arată pagina. Funcția `render()` le pune împreună.

## De ce contează

La lecția 47, HTML-ul era lipit din stringuri în Python. Așa e greu de citit, greu de schimbat și, cum vei vedea, periculos. La lecția 44 aveai altă problemă: antetul, meniul și subsolul erau copiate în fiecare pagină, iar o schimbare în meniu trebuia făcută în trei fișiere.

Template-urile rezolvă ambele probleme:
- HTML-ul stă în fișiere `.html`, separat de Python, exact cum l-ai scrie de mână;
- partea comună (antet, meniu, subsol) stă **o singură dată**, într-o machetă de bază, iar fiecare pagină completează doar ce are diferit (`{% extends %}`);
- tot textul afișat cu `{{ }}` e **escapat automat**, deci un titlu sau un comentariu cu `<script>` nu poate strica pagina (lecția 44).

## Cum funcționează

### Unde stau template-urile

Cu `APP_DIRS = True` în `TEMPLATES` (lecția 46), Django caută template-uri în folderul `templates/` al fiecărei aplicații din `INSTALLED_APPS`. Le punem într-un subfolder cu numele aplicației:

```text
articole/
└── templates/
    └── articole/
        ├── base.html
        ├── lista.html
        ├── _meta.html
        ├── detaliu.html
        └── despre.html
```

Numele „dublat” `templates/articole/` pare ciudat, dar e convenția Django. Toate aplicațiile își pun template-urile în același „spațiu”, deci fără subfolder, un `lista.html` din altă aplicație s-ar putea confunda cu al tău. În view folosești calea de după `templates/`: `"articole/lista.html"`.

### `render()`: view-ul cu template

```python
from django.shortcuts import render


def lista(request):
    return render(request, "articole/lista.html", {"articole": ARTICOLE})
```

`render(request, template, context)`:
- încarcă template-ul;
- îl completează cu **contextul**, un dicționar (lecția 14) ale cărui chei devin nume în template: `articole`;
- întoarce un `HttpResponse` cu HTML-ul rezultat.

### `{{ }}` și filtrele

În template, punctul face mai multe lucruri: `{{ articol.titlu }}` caută întâi cheia `"titlu"` în dicționar, apoi un atribut, apoi un element de listă. Același template merge cu dicționarele de acum și cu obiectele din baza de date de la lecția 52.

**Filtrele** transformă o valoare înainte de afișare și se scriu după `|`:

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c "from django.template import Template, Context; print(Template('{{ titlu|upper }} | {{ lista|length }} | {{ lipsa }} | {{ text|truncatewords:3 }}').render(Context({'titlu': 'Blogul Anei', 'lista': [1, 2, 3], 'text': 'unu doi trei patru cinci'})))"
```

```text
BLOGUL ANEI | 3 |  | unu doi trei …
```

(Am folosit `shell -c` ca să încercăm un template mic, direct din terminal.) Observă că `{{ lipsa }}`, o variabilă care nu există, **nu afișează nimic** și nu dă nicio eroare.

Filtrele din blog:
- `{{ data|date:"j F Y" }}` formatează o dată: `2 Octombrie 2026`. Traducerea românească a Django scrie lunile cu majusculă, de aceea adăugăm `|lower`;
- `{{ text|truncatewords:12 }}` păstrează primele 12 cuvinte;
- `{{ text|linebreaks }}` transformă rândurile goale din text în paragrafe `<p>`.

### Tag-urile: `for`, `if`, `url`

```html
{% for articol in articole %}
  <h2><a href="{% url 'detaliu' articol.id %}">{{ articol.titlu }}</a></h2>
{% empty %}
  <p>Încă nu există articole.</p>
{% endfor %}
```

- `{% for %}` ... `{% endfor %}` repetă conținutul pentru fiecare element, ca în Python (lecția 10). `{% empty %}` se afișează dacă lista e goală;
- `{% if %}` ... `{% endif %}` afișează ceva doar dacă o condiție e adevărată;
- `{% url 'detaliu' articol.id %}` construiește adresa din **numele** dat în `urls.py` (lecția 47): `/articol/2/`. Dacă mâine schimbi adresa în `urls.py`, toate linkurile se schimbă singure.

Spre deosebire de Python, blocurile nu se marchează prin indentare, ci se închid explicit: `{% endfor %}`, `{% endif %}`, `{% endblock %}`.

### Moștenirea: `{% extends %}` și `{% block %}`

Antetul și subsolul stau o singură dată, în `base.html`, care definește **blocuri** cu nume, adică locuri goale pe care paginile le completează:

```html
<title>{% block titlu %}Blogul Anei{% endblock %}</title>
...
<main>
  {% block continut %}{% endblock %}
</main>
```

O pagină anume începe cu `{% extends "articole/base.html" %}` și completează doar blocurile:

```html
{% extends "articole/base.html" %}

{% block continut %}
  <h1>Despre</h1>
{% endblock %}
```

Tot ce nu e în blocuri vine din `base.html`. Ideea e cea a moștenirii claselor (lecția 34): pagina „moștenește” macheta și „suprascrie” blocurile.

`{% include "articole/_meta.html" %}` inserează un template mic în altul. Rândul cu data și categoria apare și în listă, și pe pagina articolului, așa că îl scriem o dată. Liniuța de jos din nume (`_meta.html`) arată, prin convenție, că nu e o pagină completă.

### Escaparea automată

Ce se întâmplă dacă un titlu conține HTML, de exemplu un comentariu răutăcios cu `<script>`?

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c "from django.template import Template, Context; t = Template('<p>{{ text }}</p>'); print(t.render(Context({'text': '<script>alert(1)</script>'})))"
```

```text
<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>
```

Django a înlocuit `<` și `>` cu `&lt;` și `&gt;`, exact ce făcea `html.escape` la lecția 44. Browserul afișează textul `<script>alert(1)</script>` ca text, nu îl execută. Escaparea e automată pentru tot ce afișezi cu `{{ }}`, deci nu o poți uita. View-urile din lecția 47, care lipeau HTML din stringuri, nu aveau această protecție.

### Ce se întâmplă „pe dedesubt”

La `render()`, Django găsește fișierul, îl „compilează” într-o listă de bucăți (text simplu, variabile, tag-uri) și o parcurge, completând fiecare bucată din context. Pentru `{% extends %}`, întâi încarcă `base.html`, apoi înlocuiește fiecare `{% block %}` cu varianta paginii.

Limbajul de template e intenționat limitat: nu poți apela funcții cu argumente și nu poți scrie Python. Logica stă în view, iar template-ul doar afișează. Așa, cineva care știe doar HTML poate lucra la template-uri fără să strice logica.

## Exemplu complet

Blogul cu template-uri: aceleași date ca la lecția 47, dar cu macheta din lecția 44 și cu o pagină nouă, „Despre”.

View-urile, `articole/views.py` (lista de articole rămâne neschimbată; `HttpResponse` e înlocuit de `render`):

<!-- fisier: articole/views.py -->
```python
from datetime import date

from django.http import Http404
from django.shortcuts import render

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


def lista(request):
    return render(request, "articole/lista.html", {"articole": ARTICOLE})


def detaliu(request, nr):
    return render(request, "articole/detaliu.html", {"articol": gaseste(nr)})


def despre(request):
    return render(request, "articole/despre.html")
```

Adresa nouă, în `articole/urls.py`:

<!-- fisier: articole/urls.py -->
```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista, name="lista"),
    path("articol/<int:nr>/", views.detaliu, name="detaliu"),
    path("despre/", views.despre, name="despre"),
]
```

Macheta comună, `articole/templates/articole/base.html`:

<!-- fisier: articole/templates/articole/base.html -->
```html
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block titlu %}Blogul Anei{% endblock %}</title>
</head>
<body>
  <header class="antet">
    <a href="{% url 'lista' %}" class="sigla">Blogul Anei</a>
    <nav>
      <a href="{% url 'lista' %}">Articole</a>
      <a href="{% url 'despre' %}">Despre</a>
    </nav>
  </header>

  <main>
    {% block continut %}{% endblock %}
  </main>

  <footer class="subsol">
    <p>Ana Popescu, Cluj · 2026</p>
  </footer>
</body>
</html>
```

Rândul cu data și categoria, `articole/templates/articole/_meta.html`:

<!-- fisier: articole/templates/articole/_meta.html -->
```html
<p class="meta">
  {{ articol.data_publicarii|date:"j F Y"|lower }}
  {% if articol.categorie %} · <span class="categorie">{{ articol.categorie }}</span>{% endif %}
</p>
```

Lista de articole, `articole/templates/articole/lista.html`:

<!-- fisier: articole/templates/articole/lista.html -->
```html
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
```

Pagina unui articol, `articole/templates/articole/detaliu.html`:

<!-- fisier: articole/templates/articole/detaliu.html -->
```html
{% extends "articole/base.html" %}

{% block titlu %}{{ articol.titlu }} · Blogul Anei{% endblock %}

{% block continut %}
  <article class="articol">
    <h1>{{ articol.titlu }}</h1>
    {% include "articole/_meta.html" %}
    {{ articol.continut|linebreaks }}
  </article>
{% endblock %}
```

Pagina „Despre”, `articole/templates/articole/despre.html`:

<!-- fisier: articole/templates/articole/despre.html -->
```html
{% extends "articole/base.html" %}

{% block titlu %}Despre · Blogul Anei{% endblock %}

{% block continut %}
  <h1>Despre</h1>
  <p>Sunt Ana Popescu, am 25 de ani și locuiesc în Cluj.</p>
  <p>Învăț programare de un an și scriu aici despre ce descopăr: Python, Django și, uneori, călătorii.</p>
{% endblock %}
```

Pagina principală are acum antetul, meniul, data în cuvinte, categoria și începutul fiecărui articol:

<!-- comanda: python /h/vezi_pagina.py / -->
```text
200 OK
Blogul Anei
Articole Despre
Articole
O plimbare prin Cluj
20 octombrie 2026 · Călătorii
Duminică am urcat pe dealul Cetățuia, de unde se vede tot Clujul. …
De ce am ales Django
2 octombrie 2026 · Programare
După primele luni cu Python, voiam să fac un site adevărat: cu …
Primul meu program în Python
14 septembrie 2026 · Programare
Totul a început cu un simplu print("Salut, lume!"). Nu credeam că două …
Ana Popescu, Cluj · 2026
```

Pagina unui articol, cu cele două paragrafe produse de `linebreaks`:

<!-- comanda: python /h/vezi_pagina.py /articol/2/ -->
```text
200 OK
Blogul Anei
Articole Despre
De ce am ales Django
2 octombrie 2026 · Programare
După primele luni cu Python, voiam să fac un site adevărat: cu pagini, cu bază de date și cu un loc unde să mă autentific.
Django are toate acestea „din cutie”, iar documentația lui e excelentă.
Ana Popescu, Cluj · 2026
```

Și noua pagină, care a primit antetul și subsolul fără să le scrie:

<!-- comanda: python /h/vezi_pagina.py /despre/ -->
```text
200 OK
Blogul Anei
Articole Despre
Despre
Sunt Ana Popescu, am 25 de ani și locuiesc în Cluj.
Învăț programare de un an și scriu aici despre ce descopăr: Python, Django și, uneori, călătorii.
Ana Popescu, Cluj · 2026
```

HTML-ul complet trimis browserului pentru `/articol/2/` arată cum s-au combinat `base.html`, `detaliu.html` și `_meta.html`. Linkurile `{% url %}` au devenit adrese reale, iar blocul `titlu` a fost înlocuit:

<!-- comanda: python /h/vezi_pagina.py --html /articol/2/ -->
```text
200 OK
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>De ce am ales Django · Blogul Anei</title>
</head>
<body>
  <header class="antet">
    <a href="/" class="sigla">Blogul Anei</a>
    <nav>
      <a href="/">Articole</a>
      <a href="/despre/">Despre</a>
    </nav>
  </header>

  <main>

  <article class="articol">
    <h1>De ce am ales Django</h1>
    <p class="meta">
  2 octombrie 2026
   · <span class="categorie">Programare</span>
</p>

    <p>După primele luni cu Python, voiam să fac un site adevărat: cu pagini, cu bază de date și cu un loc unde să mă autentific.</p>

<p>Django are toate acestea „din cutie”, iar documentația lui e excelentă.</p>
  </article>

  </main>

  <footer class="subsol">
    <p>Ana Popescu, Cluj · 2026</p>
  </footer>
</body>
</html>
```

Spațiile și rândurile goale în plus nu contează pentru browser. Paginile nu au încă stilul din lecția 44: CSS-ul vine la lecția 49.

## Greșeli frecvente

### 1. Calea template-ului fără folderul aplicației

În view ai scris `render(request, "lista.html", ...)`:

<!-- comanda: cp -r . /tmp/p && cd /tmp/p && sed -i "s#\"articole/lista.html\"#\"lista.html\"#" articole/views.py && python /h/vezi_pagina.py / -->
```text
Traceback (most recent call last):
django.template.exceptions.TemplateDoesNotExist: lista.html
```

Calea se scrie de la `templates/`: `"articole/lista.html"`. Aceeași eroare apare dacă aplicația lipsește din `INSTALLED_APPS` (lecția 45) sau dacă folderul se numește `template`, fără „s”. Cu `DEBUG` pornit, pagina de eroare arată toate locurile în care a căutat Django.

### 2. Numele unei adrese scris greșit în `{% url %}`

În `lista.html` ai scris `{% url 'detalii' articol.id %}`:

<!-- comanda: cp -r . /tmp/p && cd /tmp/p && sed -i "s/url .detaliu. articol.id/url \x27detalii\x27 articol.id/" articole/templates/articole/lista.html && python /h/vezi_pagina.py / -->
```text
Traceback (most recent call last):
django.urls.exceptions.NoReverseMatch: Reverse for 'detalii' not found. 'detalii' is not a valid view function or pattern name.
```

`NoReverseMatch` înseamnă că Django nu poate construi adresa: numele din `{% url %}` trebuie să fie exact cel din `name=` din `urls.py`.

### 3. `{% url %}` fără argumentul adresei

Ai scris `{% url 'detaliu' %}`, fără `articol.id`:

<!-- comanda: cp -r . /tmp/p && cd /tmp/p && sed -i "s/url .detaliu. articol.id/url \x27detaliu\x27/" articole/templates/articole/lista.html && python /h/vezi_pagina.py / -->
```text
Traceback (most recent call last):
django.urls.exceptions.NoReverseMatch: Reverse for 'detaliu' with no arguments not found. 1 pattern(s) tried: ['articol/(?P<nr>[0-9]+)/\\Z']
```

Adresa `articol/<int:nr>/` are nevoie de un număr. Mesajul arată și tiparul de adresă încercat, scris ca „expresie regulată”: `[0-9]+` înseamnă „una sau mai multe cifre”.

### 4. O variabilă scrisă greșit nu dă eroare

În `lista.html` ai scris `{{ articol.titlul }}` în loc de `{{ articol.titlu }}`:

<!-- comanda: cp -r . /tmp/p && cd /tmp/p && sed -i "s/{{ articol.titlu }}<\/a>/{{ articol.titlul }}<\/a>/" articole/templates/articole/lista.html && python /h/vezi_pagina.py / | sed -n 1,6p -->
```text
200 OK
Blogul Anei
Articole Despre
Articole
20 octombrie 2026 · Călătorii
Duminică am urcat pe dealul Cetățuia, de unde se vede tot Clujul. …
```

Titlurile au dispărut în tăcere, iar linkurile spre articole au rămas goale. Template-urile ignoră variabilele care nu există, ca o pagină să nu cadă din cauza unei date lipsă. Când ceva „nu apare”, verifică întâi numele.

### 5. Un tag neînchis

Ai șters, din greșeală, `{% endfor %}` din `lista.html`:

<!-- comanda: cp -r . /tmp/p && cd /tmp/p && sed -i "/{% endfor %}/d" articole/templates/articole/lista.html && python /h/vezi_pagina.py / -->
```text
Traceback (most recent call last):
django.template.exceptions.TemplateSyntaxError: Invalid block tag on line 13: 'endblock', expected 'endfor'. Did you forget to register or load this tag?
```

Django a ajuns la `{% endblock %}` de pe rândul 13 când încă aștepta `{% endfor %}`. Fiecare `{% for %}`, `{% if %}` și `{% block %}` are nevoie de tag-ul lui de închidere.

## Exercițiu

În proiectul PyTutor `blog`, scrie fișierele din exemplul complet și verifică cele trei pagini în browser. Apoi:

1. adaugă în `base.html`, în meniu, un al treilea link, „Acasă”, spre `{% url 'lista' %}`; observă că apare pe toate paginile;
2. pe pagina unui articol, adaugă la final un link „← Înapoi la articole”;
3. în `lista.html`, afișează sub titlul „Articole” numărul lor: „3 articole” (filtrul `length`);
4. în lista `ARTICOLE` din `views.py`, schimbă temporar titlul unui articol într-unul care conține `<b>` (de exemplu `"<b>Important</b>"`) și verifică în browser că apare ca text, nu îngroșat (apoi scoate-l).

Modificările tale în template-uri sunt pentru exersare: lecțiile următoare vor da fișierele întregi, iar `base.html` se schimbă din nou la lecția 49.

## Pe scurt

- Un template e HTML cu `{{ valoare }}` și `{% tag %}`; view-ul îl completează cu `render(request, "articole/lista.html", context)`.
- Template-urile aplicației stau în `articole/templates/articole/`, iar calea se scrie de la `templates/`.
- Filtrele (`|date`, `|lower`, `|truncatewords`, `|linebreaks`, `|length`) transformă valoarea la afișare.
- `{% for %}`, `{% if %}` și `{% block %}` se închid explicit; `{% url 'nume' argument %}` construiește adrese din numele din `urls.py`.
- `{% extends "articole/base.html" %}` și `{% block %}` țin antetul și subsolul într-un singur loc; `{% include %}` reutilizează bucăți mici.
- Tot ce afișezi cu `{{ }}` e escapat automat; o variabilă inexistentă nu dă eroare, ci nu afișează nimic.

<!-- proiect: _blog/47 -->
<!-- proiect-final: _blog/48 -->
