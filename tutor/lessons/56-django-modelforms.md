## Ce este

Un **ModelForm** este un formular Django construit **automat dintr-un model**. În loc să enumeri câmpurile de mână, ca la `ContactForm` (lecția 55), îi spui doar „formularul pentru modelul `Comentariu`, cu câmpurile `autor` și `text`”. Django ia din model tipurile câmpurilor, lungimile maxime și regulile, iar formularul știe să **salveze** singur obiectul în baza de date, cu `save()`.

```python
class ComentariuForm(forms.ModelForm):
    class Meta:
        model = Comentariu
        fields = ["autor", "text"]
```

În lecția asta, blogul Anei primește două lucruri: **comentariile se salvează** (promisiunea din lecția 44), iar articolele se pot **scrie și edita** din site, nu doar din panoul de admin.

## De ce contează

Majoritatea formularelor dintr-o aplicație reală creează sau modifică înregistrări din baza de date: un comentariu, un articol, un profil, o comandă. Câmpurile acestor formulare sunt aproape aceleași cu câmpurile modelului. Cu `forms.Form` le-ai scrie de două ori (o dată în model, o dată în formular), iar dacă schimbi modelul, trebuie să-ți amintești să schimbi și formularul.

`ModelForm` le ține într-un singur loc: modelul. Formularul preia regulile, iar `save()` face și `INSERT`, și `UPDATE`, fără să mai scrii tu `Comentariu.objects.create(...)` (lecția 52).

## Cum funcționează

Lucrezi în proiectul PyTutor `blog`, pornind de la starea de la finalul lecției 55.

### 1. Formularele: articole/forms.py

<!-- fisier: articole/forms.py -->
```python
from django import forms

from .models import Articol, Comentariu


class ContactForm(forms.Form):
    nume = forms.CharField(max_length=80)
    email = forms.EmailField()
    mesaj = forms.CharField(widget=forms.Textarea, min_length=10)


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
```

Clasa interioară `Meta` (ai văzut-o la modele, lecția 50) spune:
- `model`: din ce model se construiește formularul;
- `fields`: **ce câmpuri** apar, în ordinea dată. `Comentariu` mai are `articol` și `data`, dar pe acestea nu le completează vizitatorul: articolul îl știm din adresă, iar data se pune singură (`auto_now_add`);
- `labels` și `widgets` (opționale): etichete mai prietenoase și un `<textarea>` mai mic.

Fiecare câmp de model devine câmpul de formular potrivit: `CharField(max_length=200)` dă un câmp text cu aceeași limită, `ForeignKey` (categoria) dă o listă de alegere, `ManyToManyField` (etichetele) o listă cu selecție multiplă, `BooleanField` o căsuță de bifat.

`clean_titlu` e o validare proprie, ca în exercițiul lecției 55: ridică `ValidationError` dacă titlul e scris numai cu majuscule și **întoarce** valoarea curată (aici, fără spații la margini).

### 2. View-urile: articole/views.py

<!-- fisier: articole/views.py -->
```python
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
```

Ce e nou, pe rând:

**`detaliu`** trimite în template și un formular de comentariu gol.

**`adauga_comentariu`** primește doar POST-ul formularului de pe pagina articolului:
- `@require_POST` e un **decorator** (lecția 38) din Django: dacă cererea nu e POST, răspunde singur `405 Method Not Allowed`, fără să mai intre în funcție;
- `formular.save(commit=False)` construiește obiectul `Comentariu` din datele formularului, dar **nu-l salvează încă**. Îi lipsește articolul, care nu vine din formular, ci din adresă (`nr`). Îl completăm, apoi `comentariu.save()` face `INSERT`-ul;
- după salvare, POST-redirect-GET (lecția 55) înapoi la articol, direct la secțiunea `#comentarii` (ancora din lecția 44);
- dacă formularul are erori, se reafișează pagina articolului cu formularul legat, deci cu erorile lângă câmpuri.

**`articol_nou`**: același tipar ca la contact, doar că la date corecte `formular.save()` creează articolul și îl întoarce. `redirect(articol)` primește un obiect, nu un nume de URL, și folosește metoda lui `get_absolute_url()` (scrisă la lecția 53) ca să afle adresa.

**`articol_editeaza`**: diferența e `instance=articol`. La GET, formularul pornește completat cu datele articolului. La POST, `save()` face `UPDATE` pe acel articol, în loc să creeze unul nou.

Deocamdată oricine poate scrie și edita articole. La lecția 57 vom cere autentificare.

### 3. Adresele: articole/urls.py

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
]
```

`articol/<int:nr>/comentariu/` e exact adresa din lecția 44 (`POST /articol/<nr>/comentariu/`).

### 4. Template-urile

Pagina articolului primește linkul de editare și formularul de comentariu, sub lista comentariilor:

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
    <p><a href="{% url 'articol_editeaza' articol.id %}">Editează articolul</a></p>
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

Aici `action` e necesar: formularul stă pe pagina articolului (`/articol/2/`), dar se trimite la altă adresă (`/articol/2/comentariu/`).

Un singur template servește și pentru articol nou, și pentru editare. Diferă doar titlul, pe care îl trimite view-ul:

<!-- fisier: articole/templates/articole/formular_articol.html -->
```html
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
```

În meniu apare linkul „Scrie un articol”:

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
      <a href="{% url 'articol_nou' %}">Scrie un articol</a>
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

### Încearcă: un comentariu nou

Ioana lasă un comentariu la articolul 2. Browserul trimite POST-ul, iar serverul răspunde cu redirecționarea:

<!-- comanda: python /h/vezi_pagina.py POST /articol/2/comentariu/ autor=Ioana "text=Și eu am ales Django pentru proiectul de licență!" -->
```text
302 Found
Location: /articol/2/#comentarii
```

Pagina articolului, după redirecționare (la tine, comentariul nou are data de azi):

<!-- comanda: python /h/vezi_pagina.py /articol/2/ | sed -n '/^Comentarii/,$p' | sed 's/^\(Ioana · \).*/\129 octombrie 2026/' -->
```text
Comentarii (2)
Mihai · 3 octombrie 2026
Foarte bun articol!
Ioana · 29 octombrie 2026
Și eu am ales Django pentru proiectul de licență!
Lasă un comentariu
Numele tău:
[câmp: autor]
Comentariu:
[câmp: text]
Trimite comentariul
Ana Popescu, Cluj · 2026
```

Un comentariu fără text nu se salvează. Pagina se reafișează cu eroarea, iar numele rămâne completat:

<!-- comanda: python /h/vezi_pagina.py POST /articol/3/comentariu/ autor=Radu text= | sed -n '/^Lasă un comentariu/,$p' -->
```text
Lasă un comentariu
Numele tău:
[câmp: autor]
Comentariu:
Acest câmp este obligatoriu.
[câmp: text]
Trimite comentariul
Ana Popescu, Cluj · 2026
```

Mesajul „Acest câmp este obligatoriu.” vine din model: `text = models.TextField()` nu are `blank=True`, deci câmpul e obligatoriu și în formular.

### Încearcă: un articol nou

Formularul generat din model:

<!-- comanda: python /h/vezi_pagina.py /articol/nou/ | sed -n '/^Articol nou/,$p' -->
```text
Articol nou
Titlu:
[câmp: titlu]
Conținut:
[câmp: continut]
Categorie:
[câmp: categorie] --------- Călătorii Programare
Etichete:
[câmp: etichete] cluj django python
Data publicării:
[câmp: data_publicarii]
Publicat:
[câmp: publicat]
Salvează
Ana Popescu, Cluj · 2026
```

Categoriile și etichetele vin din baza de date, ca opțiuni ale listelor (`---------` înseamnă „fără categorie”). Un titlu scris numai cu majuscule e oprit de `clean_titlu`:

<!-- comanda: python /h/vezi_pagina.py POST /articol/nou/ "titlu=ZIUA MEA LA MUNTE" "continut=Am urcat pe Vlădeasa." categorie=2 data_publicarii=2026-10-28 publicat=on | sed -n '/^Titlu/,/^Conținut/p' -->
```text
Titlu:
Nu scrie titlul numai cu majuscule.
[câmp: titlu]
Conținut:
```

Cu un titlu normal, articolul se salvează, iar `redirect(articol)` duce la pagina lui:

<!-- comanda: python /h/vezi_pagina.py POST /articol/nou/ "titlu=Ziua mea la munte" "continut=Am urcat pe Vlădeasa." categorie=2 data_publicarii=2026-10-28 publicat=on -->
```text
302 Found
Location: /articol/4/
```

Articolul are numărul 4, pentru că în baza de date erau deja trei.

### Ce se întâmplă „pe dedesubt”: ce face save()

Încă de la `is_valid()`, formularul pune valorile din `cleaned_data` pe obiectul din `formular.instance`. Fără `instance=...`, acesta e un obiect **nou**, încă nesalvat (`Articol()`); cu `instance=articol`, e articolul existent. Apoi `save()` face doi pași:
1. apelează `instance.save()`. Pentru un obiect nou, Django face `INSERT`; pentru unul care are deja `id`, face `UPDATE` (lecțiile 50–52);
2. salvează relațiile multi-la-multi (etichetele), care au nevoie ca obiectul să aibă deja `id`.

Cu `commit=False`, niciunul dintre pași nu se face: primești obiectul ca să-l completezi. Dacă formularul are câmpuri multi-la-multi, după `obiect.save()` trebuie apelat și `formular.save_m2m()`. `ComentariuForm` nu are, de aceea în `adauga_comentariu` nu apare.

Poți urmări pașii și în shell:

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c '
from articole.forms import ArticolForm
from articole.models import Articol

articol = Articol.objects.get(id=1)
formular = ArticolForm({"titlu": "Primul meu program", "continut": articol.continut,
                        "data_publicarii": "2026-09-14", "publicat": True}, instance=articol)
print(formular.is_valid(), formular.instance.id)
formular.save()
print(Articol.objects.get(id=1).titlu, Articol.objects.count())
'
```

```text
True 1
Primul meu program 4
```

Titlul articolului 1 s-a schimbat, iar numărul de articole a rămas 4 (cele trei inițiale plus „Ziua mea la munte”, scris mai sus): `instance` a făcut din `save()` un `UPDATE`. (Fiindcă nu am trimis `categorie` și `etichete`, ele s-au golit: un formular de editare trimite mereu **toate** câmpurile, de aceea în browser ele vin precompletate.)

## Exemplu complet

| Fișier | Ce s-a schimbat |
|---|---|
| `articole/forms.py` | + `ComentariuForm` și `ArticolForm` (cu `clean_titlu`) |
| `articole/views.py` | + `adauga_comentariu` (`@require_POST`, `commit=False`), `articol_nou`, `articol_editeaza`; `detaliu` trimite un formular gol |
| `articole/urls.py` | + `articol/<nr>/comentariu/`, `articol/nou/`, `articol/<nr>/editeaza/` |
| `articole/templates/articole/detaliu.html` | + formularul de comentariu și linkul de editare |
| `articole/templates/articole/formular_articol.html` | nou: un template pentru articol nou și editare |
| `articole/templates/articole/base.html` | + linkul „Scrie un articol” |

Formularul de editare pornește completat cu datele articolului:

<!-- comanda: python /h/vezi_pagina.py /articol/2/editeaza/ | sed -n '/^Editează/,/^Categorie/p' -->
```text
Editează: De ce am ales Django
Titlu:
[câmp: titlu]
Conținut:
[câmp: continut] După primele luni cu Python, voiam să fac un site adevărat: cu pagini, cu bază de date și cu un loc unde să mă autentific. Django are toate acestea „din cutie”, iar documentația lui e excelentă.
Categorie:
```

(Valoarea titlului e în atributul `value` al câmpului, deci nu apare în textul de mai sus; conținutul e în `<textarea>`, deci se vede.)

<!-- ruleaza -->
```bash
python manage.py check
```

```text
System check identified no issues (0 silenced).
```

## Greșeli frecvente

### 1. ModelForm fără fields

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c '
from django import forms
from articole.models import Comentariu

class ComentariuForm(forms.ModelForm):
    class Meta:
        model = Comentariu
' 2>&1 | tail -n 1
```

```text
django.core.exceptions.ImproperlyConfigured: Creating a ModelForm without either the 'fields' attribute or the 'exclude' attribute is prohibited; form ComentariuForm needs updating.
```

Django te obligă să spui explicit ce câmpuri apar. Există și `fields = "__all__"`, dar e periculos: dacă adaugi mai târziu în model un câmp care nu trebuie atins de vizitatori (de exemplu autorul, la lecția 57), el apare automat în formular. Scrie lista câmpurilor.

### 2. save() fără câmpul care nu e în formular

Dacă în `adauga_comentariu` ai scrie direct `formular.save()`, comentariul n-ar avea articol:

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c '
from articole.forms import ComentariuForm

formular = ComentariuForm({"autor": "Radu", "text": "Bravo!"})
print(formular.is_valid())
formular.save()
' 2>&1 | tail -n 1
```

```text
django.db.utils.IntegrityError: NOT NULL constraint failed: articole_comentariu.articol_id
```

Baza de date refuză un comentariu fără articol (`articol_id` nu poate fi gol). Formularul a fost valid, pentru că `articol` nu face parte din el. Soluția e cea din lecție: `save(commit=False)`, completezi `articol`, apoi `save()`.

### 3. Editare fără instance=

```python
def articol_editeaza(request, nr):
    articol = get_object_or_404(Articol, id=nr)
    formular = ArticolForm(request.POST)  # lipsește instance=articol
    ...
```

Nu apare nicio eroare, dar `save()` creează un articol **nou** la fiecare editare, iar cel vechi rămâne neschimbat. Iar la GET, formularul pornește gol, nu cu datele articolului. Și la GET, și la POST e nevoie de `instance=articol`.

### 4. GET pe o adresă care acceptă doar POST

<!-- comanda: python /h/vezi_pagina.py /articol/2/comentariu/ -->
```text
Method Not Allowed (GET): /articol/2/comentariu/
405 Method Not Allowed
```

`@require_POST` respinge orice altă metodă cu `405`. Așa se întâmplă dacă pui un link `<a href="{% url 'comentariu' 2 %}">` în loc de un formular: un link face mereu GET.

### 5. clean_<camp> care nu întoarce valoarea

```python
def clean_titlu(self):
    titlu = self.cleaned_data["titlu"].strip()
    if titlu.isupper():
        raise forms.ValidationError("Nu scrie titlul numai cu majuscule.")
    # lipsește return titlu
```

O funcție fără `return` întoarce `None` (lecția 18), iar Django pune exact valoarea întoarsă în `cleaned_data["titlu"]`. Titlul devine `None`, iar validarea modelului îl respinge: lângă câmpul „Titlu” apare „Acest câmp nu poate fi nul.”, deși ai scris un titlu corect. O metodă `clean_<camp>` întoarce **mereu** valoarea curată.

## Exercițiu

Lucrezi în proiectul PyTutor `blog`. E o extindere a lecției: la lecția 57 vei înlocui `views.py`, `detaliu.html` și `base.html` cu versiunile din lecție, deci păstrează-ți adăugirile.

1. În `ComentariuForm`, adaugă `clean_text`, care respinge comentariile cu mai puțin de 3 cuvinte (`len(text.split())`), și `clean_autor`, care întoarce numele cu `title()` (lecția 4). Verifică în browser că „ana popescu” se salvează „Ana Popescu”.
2. În `formular_articol.html`, adaugă lângă butonul „Salvează” un link „Anulează”, care duce înapoi la lista articolelor.
3. În `ArticolForm`, adaugă `clean_continut`, care cere cel puțin 20 de caractere.
4. Scrie un articol nou din site, apoi editează-l și verifică în panoul de admin (lecția 54) că s-a modificat același articol, nu s-a creat altul.

## Pe scurt

- `forms.ModelForm` construiește formularul din model: în `Meta` dai `model` și lista `fields` (obligatorie), plus opțional `labels` și `widgets`.
- `formular.save()` creează obiectul (`INSERT`); cu `instance=obiect` îl modifică (`UPDATE`), iar la GET formularul pornește completat.
- `save(commit=False)` dă obiectul nesalvat, ca să completezi câmpurile care nu vin din formular (articolul unui comentariu), apoi `obiect.save()`.
- `redirect(obiect)` folosește `get_absolute_url()`; `@require_POST` respinge alte metode cu `405`.
- Validările proprii stau în `clean_<camp>()`, care ridică `ValidationError` sau **întoarce** valoarea curată.

<!-- proiect: _blog/55 -->
<!-- proiect-final: _blog/56 -->
<!-- pregatire: python manage.py migrate -v 0 && python manage.py loaddata /lectii/_blog/date/53.json -v 0 -->
