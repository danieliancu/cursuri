## Ce este

Un **formular Django** este o clasă Python care descrie câmpurile unui formular HTML: ce câmpuri are, ce fel de valori acceptă fiecare și ce înseamnă o valoare corectă. Din aceeași clasă, Django face trei lucruri:

1. **afișează** formularul ca HTML (etichete, câmpuri, mesaje de eroare);
2. **validează** datele trimise de utilizator (un e-mail e cu adevărat e-mail? mesajul e destul de lung?);
3. **convertește** datele în valori Python curate, pe care le găsești în `cleaned_data`.

```python
from django import forms


class ContactForm(forms.Form):
    nume = forms.CharField(max_length=80)
    email = forms.EmailField()
    mesaj = forms.CharField(widget=forms.Textarea, min_length=10)
```

În lecția asta, blogul Anei primește o pagină de **contact**: vizitatorul scrie numele, adresa de e-mail și un mesaj, iar Django verifică datele și confirmă primirea.

## De ce contează

La lecția 43 ai văzut că un formular HTML trimite o cerere `POST`, iar la lecția 44 ai scris de mână formularul de comentariu. Ce rămânea nerezolvat era partea de server: cine verifică datele? Ce se întâmplă dacă e-mailul e greșit sau câmpul e gol? Cum îi arăți utilizatorului ce a greșit, fără să-i pierzi ce a scris deja?

Toate acestea le-ai putea scrie de mână cu `request.POST["email"]` și zeci de `if`-uri, ca în validările din lecțiile 8–11. Clasa `forms.Form` le face într-un loc, la fel pentru orice formular: contact, comentarii, autentificare, înregistrare. Aproape fiecare aplicație web are formulare, iar datele care vin de la utilizator nu sunt niciodată de încredere până nu le-ai verificat.

## Cum funcționează

### Proiectul blog

Lucrezi în proiectul PyTutor `blog`, cel din lecțiile 45–54. Pornești de la starea lui de la finalul lecției 54: articole, categorii, comentarii și panoul de admin.

### 1. Clasa formularului: articole/forms.py

Formularele stau, prin convenție, într-un fișier nou al aplicației, `forms.py`:

<!-- fisier: articole/forms.py -->
```python
from django import forms


class ContactForm(forms.Form):
    nume = forms.CharField(max_length=80)
    email = forms.EmailField()
    mesaj = forms.CharField(widget=forms.Textarea, min_length=10)
```

Seamănă cu un model (lecția 50), dar nu are nimic de-a face cu baza de date: e doar descrierea unui formular.
- fiecare atribut e un **câmp** (`CharField`, `EmailField`, `IntegerField`, `DateField` și multe altele); tipul câmpului hotărăște ce valori sunt acceptate;
- argumentele adaugă reguli: `max_length=80`, `min_length=10`; implicit, toate câmpurile sunt **obligatorii** (`required=True`);
- `widget` alege cum arată câmpul în HTML: `forms.Textarea` dă un `<textarea>` cu mai multe rânduri, în loc de un `<input>` pe un rând.

### 2. View-ul: GET afișează, POST verifică

<!-- fisier: articole/views.py -->
```python
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
```

Doar funcția `contact` e nouă, plus două importuri (`messages`, `redirect`) și importul formularului. Pas cu pas:

1. **Prima vizită** e o cerere `GET`: se creează un formular **gol** (`ContactForm()`) și se afișează.
2. Când utilizatorul apasă butonul, browserul trimite o cerere `POST` cu datele. `request.POST` se folosește ca un dicționar (lecția 14) cu ce a scris. Formularul creat din el se numește formular **legat** („bound”): are date de verificat.
3. `formular.is_valid()` rulează toate verificările și întoarce `True` sau `False`.
4. **Date corecte:** valorile curate sunt în `formular.cleaned_data` (un dicționar). Aici doar mulțumim. Un site real ar trimite un e-mail sau ar salva mesajul. Apoi **redirecționăm**: `redirect("contact")` întoarce un răspuns `302` către adresa cu numele `contact` (lecția 47).
5. **Date greșite:** nu se redirecționează. Execuția ajunge la ultimul `render`, cu formularul legat, care știe acum ce erori are și ce scrisese utilizatorul. Pagina se reafișează cu erorile, iar câmpurile rămân completate.

### POST-redirect-GET

La pasul 4, de ce `redirect` și nu direct `render` cu un mesaj de mulțumire? La lecția 43 ai văzut pe scurt tiparul; acum îl folosim în Django.

Dacă după un POST reușit răspunzi direct cu o pagină, ultima cerere din browser rămâne acel POST. Când utilizatorul apasă **Reîncarcă** (F5), browserul îl întreabă „Retrimiteți formularul?”, iar la „Da” mesajul pleacă de două ori. La un comentariu sau la o comandă dintr-un magazin, asta înseamnă dubluri.

Cu redirecționare, pașii sunt:
1. `POST /contact/` → serverul validează, procesează și răspunde `302 Found`, cu `Location: /contact/`;
2. browserul face singur `GET /contact/` și afișează pagina.

Acum ultima cerere e un GET, deci reîncărcarea paginii e inofensivă. Tiparul se numește **POST-redirect-GET** și se folosește după orice POST reușit.

### Mesajele de confirmare

Mesajul de mulțumire trebuie să ajungă pe pagina de **după** redirecționare, adică într-o altă cerere. Pentru asta, Django are framework-ul `messages`: `messages.success(request, "...")` păstrează mesajul (într-un cookie sau în sesiune; despre amândouă afli la lecția 57) până la următoarea pagină afișată, care îl scoate și îl arată o singură dată. E deja activat în `settings.py` (`django.contrib.messages`, lecția 46).

Mesajele se afișează în `base.html`, ca să apară pe orice pagină. Tot aici adăugăm și linkul spre Contact:

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

Clasa CSS `mesaj` (o bandă verde) există deja în `stil.css`.

### 3. Template-ul: csrf_token și formularul

<!-- fisier: articole/templates/articole/contact.html -->
```html
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
```

- `<form method="post">`: fără `action`, formularul se trimite la aceeași adresă (`/contact/`), deci la același view;
- `{{ formular.as_div }}` scrie, pentru fiecare câmp, eticheta (`<label>`), câmpul și eventualele erori, fiecare într-un `<div>`. Există și `{{ formular.nume }}`, `{{ formular.nume.errors }}` etc., când vrei să aranjezi câmpurile de mână;
- `{% csrf_token %}` adaugă un câmp ascuns cu un cod secret. E obligatoriu în orice formular POST (vezi „pe dedesubt”).

### 4. Adresa: articole/urls.py

<!-- fisier: articole/urls.py -->
```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista, name="lista"),
    path("articol/<int:nr>/", views.detaliu, name="detaliu"),
    path("despre/", views.despre, name="despre"),
    path("contact/", views.contact, name="contact"),
]
```

### Încearcă formularul

Pornește serverul (`python manage.py runserver 0.0.0.0:8000`) și deschide `/contact/` la adresa din bara terminalului. Mai jos e ce vede browserul, ca text: fără stiluri, cu fiecare câmp scris ca `[câmp: nume]`.

<!-- comanda: python /h/vezi_pagina.py /contact/ -->
```text
200 OK
Blogul Anei
Articole Despre Contact
Contact
Nume:
[câmp: nume]
Email:
[câmp: email]
Mesaj:
[câmp: mesaj]
Trimite mesajul
Ana Popescu, Cluj · 2026
```

Etichetele („Nume:”, „Email:”) sunt făcute automat din numele câmpurilor.

Mihai trimite formularul cu un e-mail greșit și un mesaj prea scurt:

<!-- comanda: python /h/vezi_pagina.py POST /contact/ nume=Mihai email=gresit mesaj=Salut -->
```text
200 OK
Blogul Anei
Articole Despre Contact
Contact
Nume:
[câmp: nume]
Email:
Introduceți o adresă de email validă.
[câmp: email]
Mesaj:
Asigurați-vă că această valoare are cel puțin 10 caractere (are 5).
[câmp: mesaj] Salut
Trimite mesajul
Ana Popescu, Cluj · 2026
```

Răspunsul e `200`, nu `302`: formularul nu e valid, deci pagina se reafișează cu erorile lângă câmpuri. Mesajele sunt în română, pentru că `LANGUAGE_CODE = "ro"` (lecția 46). Câmpurile păstrează ce scrisese Mihai: textul „Salut” e încă în căsuța mesajului, iar în HTML apar `value="Mihai"` și `value="gresit"`.

Acum cu date corecte:

<!-- comanda: python /h/vezi_pagina.py POST /contact/ nume=Mihai email=mihai@exemplu.ro "mesaj=Salut, Ana! Mi-a plăcut articolul despre Cluj." -->
```text
302 Found
Location: /contact/
```

Serverul răspunde cu redirecționarea, fără nicio pagină. Browserul urmează singur `Location`, iar pe pagina nouă apare mesajul (cu `--follow`, unealta urmează și ea redirecționarea):

<!-- comanda: python /h/vezi_pagina.py --follow POST /contact/ nume=Mihai email=mihai@exemplu.ro "mesaj=Salut, Ana! Mi-a plăcut articolul despre Cluj." -->
```text
200 OK
Blogul Anei
Articole Despre Contact
Mulțumim, Mihai! Ana îți va răspunde în curând.
Contact
Nume:
[câmp: nume]
Email:
[câmp: email]
Mesaj:
[câmp: mesaj]
Trimite mesajul
Ana Popescu, Cluj · 2026
```

Formularul e din nou gol: e o cerere GET nouă. Dacă reîncarci pagina, mesajul dispare (a fost afișat o dată), iar nimic nu se retrimite.

### Ce se întâmplă „pe dedesubt”

**Validarea, pas cu pas.** `is_valid()` ia fiecare câmp și:
1. îl **convertește** din text (tot ce vine din browser e text, ca la `input()`, lecția 6) în valoarea Python potrivită: `IntegerField` dă un `int`, `DateField` un `date`;
2. îl **verifică** după regulile lui (obligatoriu, lungime, format de e-mail);
3. apelează metoda `clean_<camp>()`, dacă ai scris una în clasă, pentru reguli proprii.

Când o regulă nu e respectată, se ridică o excepție **`ValidationError`**, exact mecanismul `raise` din lecția 25. Formularul o prinde (lecția 24) și pune mesajul ei în `formular.errors`, în dreptul câmpului. Poți vedea totul direct în `manage.py shell` (`-c` rulează codul dat, iar `-v 0` ascunde mesajul despre importurile automate):

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c '
from articole.forms import ContactForm

formular = ContactForm({"nume": "Mihai", "email": "gresit", "mesaj": "Salut"})
print(formular.is_bound, formular.is_valid())
print(formular.errors.as_text())

formular = ContactForm({"nume": " Mihai ", "email": "MIHAI@exemplu.ro", "mesaj": "Salut, Ana! Ce mai faci?"})
print(formular.is_valid())
print(formular.cleaned_data)
'
```

```text
True False
* email
  * Introduceți o adresă de email validă.
* mesaj
  * Asigurați-vă că această valoare are cel puțin 10 caractere (are 5).
True
{'nume': 'Mihai', 'email': 'MIHAI@exemplu.ro', 'mesaj': 'Salut, Ana! Ce mai faci?'}
```

Observă că `cleaned_data` a scos spațiile din jurul numelui: `CharField` face `strip()` automat.

O regulă proprie se scrie ca metodă `clean_<camp>`, care întoarce valoarea curată sau ridică `ValidationError`. De exemplu, un filtru simplu împotriva mesajelor publicitare:

```python
from django import forms


class ContactForm(forms.Form):
    nume = forms.CharField(max_length=80)
    email = forms.EmailField()
    mesaj = forms.CharField(widget=forms.Textarea, min_length=10)

    def clean_mesaj(self):
        mesaj = self.cleaned_data["mesaj"]
        if "http" in mesaj.lower():
            raise forms.ValidationError("Te rog, fără linkuri în mesaj.")
        return mesaj
```

(Nu-l adăugăm în proiect; e tema exercițiului.)

**CSRF.** Fără protecție, orice alt site ar putea conține un formular ascuns care trimite un POST spre blogul Anei, cu cookie-urile vizitatorului (lecția 43). Atacul se numește **CSRF** („Cross-Site Request Forgery”, falsificarea cererilor între site-uri). Django îl oprește așa: `{% csrf_token %}` pune în formular un cod secret, legat de un cookie al vizitatorului. La fiecare POST, middleware-ul `CsrfViewMiddleware` (din `MIDDLEWARE`, lecția 46) verifică dacă cele două se potrivesc. Un site străin nu poate ști codul, deci cererea lui e respinsă cu `403 Forbidden`.

## Exemplu complet

Tot ce s-a schimbat în proiect în lecția asta:

| Fișier | Ce s-a schimbat |
|---|---|
| `articole/forms.py` | nou: `ContactForm` |
| `articole/views.py` | + view-ul `contact` (POST-redirect-GET, `messages`) |
| `articole/urls.py` | + `contact/` |
| `articole/templates/articole/contact.html` | nou: formularul cu `{% csrf_token %}` |
| `articole/templates/articole/base.html` | + linkul Contact și afișarea mesajelor |

Tot ce a trimis Mihai a trecut prin același drum: `request.POST` → `ContactForm(...)` → `is_valid()` → fie `cleaned_data` și redirecționare, fie aceeași pagină, cu erori. Orice formular din lecțiile următoare (comentarii, articole noi, autentificare) urmează exact acest tipar.

Verificarea de sistem confirmă că totul e legat corect:

<!-- ruleaza -->
```bash
python manage.py check
```

```text
System check identified no issues (0 silenced).
```

## Greșeli frecvente

### 1. Lipsește {% csrf_token %}

Dacă uiți `{% csrf_token %}` din `<form method="post">`, la trimitere browserul primește:

```text
Interzis (403)
Verificarea CSRF nereușită. Cerere eșuată.
```

Clientul de test folosit mai sus (`vezi_pagina`) **sare** intenționat peste verificarea CSRF, ca testele să fie simple. Ca să vezi verificarea reală, pornești un client care o face, cu `enforce_csrf_checks=True`. Trimite un POST fără cod, exact ce ar face un formular fără `{% csrf_token %}`:

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c '
from django.test import Client
from django.test.utils import setup_test_environment

setup_test_environment()
browser = Client(enforce_csrf_checks=True)
raspuns = browser.post("/contact/", {"nume": "Mihai", "email": "mihai@exemplu.ro", "mesaj": "Salut, Ana!!"})
print(raspuns.status_code)
'
```

```text
Forbidden (CSRF cookie not set.): /contact/
403
```

Primul rând e scris de Django în jurnalul serverului: cererea a fost respinsă pentru că lipsește cookie-ul CSRF (și, odată cu el, codul din formular). Soluția: `{% csrf_token %}` imediat după `<form method="post">`, în **orice** formular POST.

### 2. Răspuns direct după POST, fără redirecționare

```python
def contact(request):
    if request.method == "POST":
        formular = ContactForm(request.POST)
        if formular.is_valid():
            return render(request, "articole/multumim.html")  # greșit
    ...
```

Funcționează la prima vedere, dar reîncărcarea paginii retrimite mesajul (vezi POST-redirect-GET). După un POST **reușit**, răspunde mereu cu `redirect(...)`. Doar când formularul are erori răspunzi direct cu `render`, ca utilizatorul să-și vadă greșelile.

### 3. cleaned_data citit înainte de is_valid()

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c '
from articole.forms import ContactForm

formular = ContactForm({"nume": "Mihai", "email": "mihai@exemplu.ro", "mesaj": "Salut, Ana!!"})
print(formular.cleaned_data["nume"])
'
```

```text
Traceback (most recent call last):
  File "manage.py", line 22, in <module>
    main()
  File "<string>", line 5, in <module>
AttributeError: 'ContactForm' object has no attribute 'cleaned_data'. Did you mean: 'changed_data'?
```

(Tracebackul e scurtat: între cele două cadre mai apar câteva, din `manage.py` și din interiorul Django. Rândul `File "<string>", line 5` e codul tău, cel dat cu `-c`.) Sugestia „Did you mean” nu ajută aici.

`cleaned_data` apare abia după validare. Apelează întâi `is_valid()` și citește datele doar dacă a întors `True`. Nu folosi nici `request.POST["nume"]` direct: acolo e textul neverificat.

### 4. Formularul nou creat și la POST

```python
def contact(request):
    formular = ContactForm()  # greșit: mereu gol
    if request.method == "POST" and ContactForm(request.POST).is_valid():
        ...
    return render(request, "articole/contact.html", {"formular": formular})
```

Dacă datele sunt greșite, pagina se reafișează cu un formular **gol**: fără erori și fără ce scrisese utilizatorul. La POST trebuie trimis în template exact formularul legat, cel pe care s-a apelat `is_valid()`, ca în view-ul din lecție.

### 5. redirect() cu o adresă care nu există

```python
def contact(request):
    ...
    return redirect("multumesc")
```

Dacă nu există niciun URL cu numele `multumesc`, Django nu poate construi adresa și ridică `NoReverseMatch: Reverse for 'multumesc' not found.` Verifică numele din `urls.py` (`name="contact"`).

## Exercițiu

Lucrezi în proiectul PyTutor `blog`. Modificările tale sunt o extindere: la lecția următoare, când înlocuiești fișiere întregi cu cele din lecție, păstrează-ți adăugirile.

1. Adaugă în `ContactForm` metoda `clean_mesaj` de mai sus, care respinge mesajele cu linkuri. Verifică în browser că eroarea apare lângă câmpul „Mesaj”.
2. Adaugă un câmp opțional `telefon` (`forms.CharField(max_length=20, required=False)`) și o metodă `clean_telefon` care acceptă doar cifre, spații și `+` și ridică `ValidationError` altfel (indiciu: `all(c.isdigit() or c in " +" for c in telefon)`, lecția 17). Un telefon gol trebuie acceptat.
3. Schimbă mesajul de mulțumire ca să includă și adresa de e-mail din `cleaned_data`.
4. Trimite formularul de mai multe ori, cu date greșite și corecte, și urmărește în terminalul serverului cererile `POST` (302) și `GET` (200) care urmează una după alta.

## Pe scurt

- Un formular Django e o clasă derivată din `forms.Form`, cu câmpuri (`CharField`, `EmailField`...) și reguli (`max_length`, `min_length`, `required`).
- În view: la GET, formular gol; la POST, `Formular(request.POST)` și `is_valid()`; datele curate sunt în `cleaned_data`.
- După un POST reușit, răspunde cu `redirect(...)` (POST-redirect-GET); la erori, reafișează același formular, legat.
- `{% csrf_token %}` e obligatoriu în orice `<form method="post">`; fără el, Django răspunde `403`.
- Regulile proprii se scriu în `clean_<camp>()`, care ridică `ValidationError`; `messages` duce un mesaj pe pagina de după redirecționare.

<!-- proiect: _blog/54 -->
<!-- proiect-final: _blog/55 -->
<!-- pregatire: python manage.py migrate -v 0 && python manage.py loaddata /lectii/_blog/date/53.json -v 0 -->
