## Ce este

Un **class-based view** (CBV, „view bazat pe clasă”) este un view scris ca **clasă**, nu ca funcție. Django are o colecție de clase gata făcute, numite **view-uri generice**, pentru operațiile care apar în orice site:

| Clasă | Ce face | La noi |
|---|---|---|
| `TemplateView` | afișează un template | pagina „Despre” |
| `ListView` | o listă de obiecte | lista articolelor |
| `DetailView` | un singur obiect, după `id` | pagina articolului |
| `FormView` | un formular care nu salvează în baza de date | contactul |
| `CreateView` | formular care **creează** un obiect | articol nou |
| `UpdateView` | formular care **modifică** un obiect | editarea |
| `DeleteView` | confirmare și **ștergere** | ștergerea (nou) |

Le folosești prin **moștenire** (lecția 34): scrii o clasă derivată și setezi doar ce diferă (modelul, template-ul, formularul). Restul, adică tiparele scrise de mână în lecțiile 52–57, vine din clasa de bază.

```python
class ListaArticole(ListView):
    queryset = Articol.objects.filter(publicat=True)
    template_name = "articole/lista.html"
    context_object_name = "articole"
```

## De ce contează

Uită-te la view-urile din lecția 57: `articol_nou` și `articol_editeaza` repetă același tipar (GET → formular gol, POST → `is_valid()` → `save()` → redirecționare), iar `contact` îl repetă și el. View-urile generice au acest tipar scris o dată, testat și documentat. Tu scrii doar diferențele.

Mai mult, permisiunile devin piese refolosibile, numite **mixin-uri**: `LoginRequiredMixin` în loc de `@login_required`, plus propriul nostru mixin `DoarAutorul`, pus la editare și la ștergere. E moștenirea multiplă pe care am pomenit-o la lecția 34.

Vei întâlni CBV-uri în aproape orice proiect Django și în documentație, iar Django REST Framework (lecția 60) se bazează tot pe ele. Funcțiile rămân însă perfect valabile: unele view-uri sunt mai clare așa, și le păstrăm.

## Cum funcționează

Lucrezi în proiectul PyTutor `blog`, pornind de la starea de la finalul lecției 57. Adresele și template-urile rămân aceleași, deci vizitatorii nu observă nicio diferență, în afară de pagina nouă de ștergere.

### 1. View-urile rescrise: articole/views.py

<!-- fisier: articole/views.py -->
```python
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
```

Clasă cu clasă:

**`ListaArticole(ListView)`**: `queryset` e lista de afișat (lecția 52). `template_name` e template-ul, iar `context_object_name` e numele sub care lista ajunge în template, aici `articole`, cum îl folosea deja `lista.html`.

**`DetaliuArticol(DetailView)`** caută un singur obiect în `queryset`, după cheia primară din adresă. Implicit, DetailView o caută sub numele `pk`. Adresele noastre folosesc `nr` (lecția 47), așa că setăm `pk_url_kwarg = "nr"`. Dacă articolul nu există, răspunsul e `404`, ca la `get_object_or_404`. Pentru formularul de comentariu suprascriem `get_context_data`: chemăm metoda clasei de bază cu `super()` (lecția 34), care pune deja `articol` în context, și adăugăm `formular`.

**`ArticolNou(LoginRequiredMixin, CreateView)`**: `CreateView` face tot tiparul GET/POST/`is_valid()`/`save()`/redirect din lecția 56. Redirecționarea merge la `get_absolute_url()` al obiectului nou. `extra_context` adaugă valori fixe în context. Metoda `form_valid` e „cârligul” pentru date corecte: completăm autorul pe `form.instance` (obiectul încă nesalvat, lecția 56), apoi `super().form_valid(form)` salvează (inclusiv etichetele, deci nu mai e nevoie de `save_m2m()`) și redirecționează.

**`DoarAutorul(UserPassesTestMixin)`** e mixin-ul nostru. `UserPassesTestMixin` cheamă metoda `test_func()` înainte de view: dacă întoarce `False`, utilizatorul autentificat primește `403`. `self.get_object()` e articolul din adresă, aceeași metodă pe care o folosesc `UpdateView` și `DeleteView`.

**`ArticolEditeaza(LoginRequiredMixin, DoarAutorul, UpdateView)`** combină trei clase. Ordinea contează: Python caută metodele în ordinea MRO (lecția 34), iar la moștenirea multiplă ia clasele de bază **de la stânga la dreapta**, deci întâi se verifică autentificarea, apoi dacă e autorul, abia apoi rulează formularul. `UpdateView` e `CreateView` cu `instance=` (lecția 56): formularul pornește completat, iar `save()` face `UPDATE`.

**`ArticolSterge`** e nou: la GET afișează pagina de confirmare, la POST șterge articolul și redirecționează la `success_url`. `reverse_lazy("lista")` e `reverse` „amânat”: adresa se calculează abia la prima folosire, pentru că atributele clasei se evaluează la importul fișierului, când adresele încă nu sunt încărcate.

**`Despre(TemplateView)`** și **`Contact(FormView)`**: aceeași logică, mai scurt. `FormView` nu salvează nimic: în `form_valid` doar trimitem mesajul, iar clasa de bază redirecționează la `success_url`.

`adauga_comentariu` și `inregistrare` rămân **funcții**: sunt scurte și clare așa. Un proiect poate amesteca liniștit funcții și clase.

### 2. Adresele: .as_view()

<!-- fisier: articole/urls.py -->
```python
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
```

`path()` vrea o funcție. `.as_view()` transformă clasa în una: o funcție care, la fiecare cerere, creează un obiect nou al clasei și apelează metoda potrivită (`get()`, `post()`). Numele URL-urilor rămân aceleași, deci toate `{% url %}`-urile din template-uri merg mai departe.

### 3. Template-urile: form, nu formular

View-urile generice pun formularul în context sub numele **`form`**. Până acum, view-urile noastre îl numeau `formular`, deci cele două template-uri de formular se schimbă (o singură linie fiecare):

<!-- fisier: articole/templates/articole/formular_articol.html -->
```html
{% extends "articole/base.html" %}

{% block titlu %}{{ titlu }} · Blogul Anei{% endblock %}

{% block continut %}
  <h1>{{ titlu }}</h1>
  <form method="post" class="formular">
    {% csrf_token %}
    {{ form.as_div }}
    <button type="submit">Salvează</button>
  </form>
{% endblock %}
```

<!-- fisier: articole/templates/articole/contact.html -->
```html
{% extends "articole/base.html" %}

{% block titlu %}Contact · Blogul Anei{% endblock %}

{% block continut %}
  <h1>Contact</h1>
  <form method="post" class="formular">
    {% csrf_token %}
    {{ form.as_div }}
    <button type="submit">Trimite mesajul</button>
  </form>
{% endblock %}
```

Pagina articolului primește linkul de ștergere, lângă cel de editare:

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
      <p>
        <a href="{% url 'articol_editeaza' articol.id %}">Editează articolul</a> ·
        <a href="{% url 'articol_sterge' articol.id %}">Șterge articolul</a>
      </p>
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

Aici rămâne `formular`: e numele pe care l-am pus noi în `get_context_data` din `DetaliuArticol` și în funcția `adauga_comentariu`.

Și pagina de confirmare a ștergerii. `DeleteView` pune articolul în context ca `articol`, numele modelului cu literă mică:

<!-- fisier: articole/templates/articole/confirma_stergere.html -->
```html
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
```

### Încearcă: același site

Lista arată la fel ca înainte:

<!-- comanda: python /h/vezi_pagina.py / | sed -n '/^Primul\|^De ce\|^O plimbare/p' -->
```text
O plimbare prin Cluj
De ce am ales Django
Primul meu program în Python
```

Formularul de articol nou (cu `{{ form.as_div }}`) și protecția `LoginRequiredMixin`:

<!-- comanda: python /h/vezi_pagina.py --user ana /articol/nou/ | sed -n '/^Articol nou/,/^Conținut/p' -->
```text
Articol nou
Titlu:
[câmp: titlu]
Conținut:
```

<!-- comanda: python /h/vezi_pagina.py /articol/nou/ -->
```text
302 Found
Location: /conturi/login/?next=/articol/nou/
```

Contactul funcționează ca la lecția 55, cu POST-redirect-GET:

<!-- comanda: python /h/vezi_pagina.py POST /contact/ nume=Mihai email=mihai@exemplu.ro "mesaj=Salut, Ana! Super blogul." -->
```text
302 Found
Location: /contact/
```

### Încearcă: ștergerea

Ana deschide pagina de confirmare a articolului 3:

<!-- comanda: python /h/vezi_pagina.py --user ana /articol/3/sterge/ | sed -n '/^Ștergi/,/^Renunță/p' -->
```text
Ștergi articolul „O plimbare prin Cluj”?
Comentariile lui se șterg și ele. Operația nu se poate anula.
Da, șterge
Renunță
```

Mihai nu e autorul, deci `DoarAutorul` îl oprește:

<!-- comanda: python /h/vezi_pagina.py --user mihai /articol/3/sterge/ 2>&1 | tail -n 2 -->
```text
403 Forbidden
403 Forbidden
```

Ana confirmă (POST), articolul dispare, iar ea ajunge la listă:

<!-- comanda: python /h/vezi_pagina.py --user ana POST /articol/3/sterge/ -->
```text
302 Found
Location: /
```

<!-- comanda: python /h/vezi_pagina.py / | sed -n '/^Primul\|^De ce\|^O plimbare/p' -->
```text
De ce am ales Django
Primul meu program în Python
```

### Ce se întâmplă „pe dedesubt”: o cerere prin CreateView

Când Ana trimite formularul de articol nou, funcția făcută de `ArticolNou.as_view()` creează un obiect `ArticolNou` și apelează `dispatch()`, care alege metoda după tipul cererii. Lanțul, simplificat:

1. `LoginRequiredMixin.dispatch()`: dacă nu e autentificată, redirecționare la login și gata;
2. `post()` → `get_form()` construiește `ArticolForm(request.POST)` (`form_class`);
3. `form.is_valid()` → dacă da, `form_valid(form)` (al nostru: autorul și mesajul), apoi `super().form_valid()` face `form.save()` și redirecționează la `get_success_url()`, adică `get_absolute_url()` al articolului;
4. dacă nu, `form_invalid(form)` reafișează template-ul cu formularul legat.

Fiecare pas e o metodă pe care o poți suprascrie. Ordinea în care Python le caută în clasele părinte se numește **MRO** („method resolution order”, lecția 34) și se poate afișa:

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c '
from articole.views import ArticolEditeaza

for clasa in ArticolEditeaza.__mro__[:6]:
    print(clasa.__name__)
'
```

```text
ArticolEditeaza
LoginRequiredMixin
DoarAutorul
UserPassesTestMixin
AccessMixin
UpdateView
```

`dispatch()` e căutat întâi în `LoginRequiredMixin`, care după verificare cheamă `super().dispatch()`, adică următoarea clasă din listă care are `dispatch()`. `DoarAutorul` nu are, deci urmează `UserPassesTestMixin`, care cheamă `test_func()` (cea din `DoarAutorul`). `AccessMixin`, clasa de bază comună a celor două mixin-uri Django, apare o singură dată, după amândouă. Fiecare mixin își face partea și dă mai departe.

## Exemplu complet

| Fișier | Ce s-a schimbat |
|---|---|
| `articole/views.py` | rescris: 7 view-uri generice, mixin-ul `DoarAutorul`; două funcții rămân |
| `articole/urls.py` | `.as_view()`, + `articol/<nr>/sterge/` |
| `articole/templates/articole/formular_articol.html`, `contact.html` | `{{ form.as_div }}` în loc de `formular` |
| `articole/templates/articole/detaliu.html` | + linkul „Șterge articolul” |
| `articole/templates/articole/confirma_stergere.html` | nou: confirmarea ștergerii |

Comparația cu lecția 57: `articol_nou` avea 14 rânduri, iar `ArticolNou` are 10, fără niciun `if request.method`, `is_valid()` sau `redirect`. Tiparul e în `CreateView`, scris o dată.

<!-- ruleaza -->
```bash
python manage.py check
```

```text
System check identified no issues (0 silenced).
```

## Greșeli frecvente

### 1. Template-ul caută alt nume decât cel din context

Dacă `formular_articol.html` ar fi rămas cu `{{ formular.as_div }}`, pagina s-ar fi încărcat fără nicio eroare, dar **fără câmpuri**:

```text
Articol nou
Salvează
```

Un nume necunoscut în template e tratat ca șir gol (lecția 48), deci nimic nu te avertizează. View-urile generice folosesc nume fixe: `form` pentru formular, `object` și numele modelului cu literă mică (`articol`) pentru obiect, `object_list` și `<model>_list` (`articol_list`) pentru liste, dacă nu setezi `context_object_name`. Când o pagină apare goală, verifică întâi numele variabilelor.

### 2. Lipsește .as_view()

```python
path("", views.ListaArticole, name="lista"),
```

Django ar apela view-ul cu `request`, adică `ListaArticole(request)`: un constructor de clasă care nu primește cererea așa. Greșeala e atât de des întâlnită, încât verificarea de sistem o prinde de la început: `python manage.py check` (și `runserver`, care rulează aceeași verificare la pornire) raportează `(urls.E009) Your URL pattern '' [name='lista'] has an invalid view, pass ListaArticole.as_view() instead of ListaArticole.` Pentru CBV-uri, în `urls.py` scrii mereu `.as_view()`.

### 3. pk_url_kwarg uitat

Fără `pk_url_kwarg = "nr"`, `DetailView` caută în adresă un parametru numit `pk` sau `slug`. Adresa noastră are `<int:nr>`, deci view-ul nu găsește nimic și ridică `AttributeError: Generic detail view DetaliuArticol must be called with either an object pk or a slug in the URLconf.` Soluții: `pk_url_kwarg = "nr"` (ca aici) sau schimbi adresa în `<int:pk>`.

### 4. Mixin-ul pus după clasa view-ului

```python
class ArticolEditeaza(UpdateView, LoginRequiredMixin):  # greșit
    ...
```

Python caută metodele de la stânga la dreapta, deci `UpdateView.dispatch()` vine primul, iar verificarea de login nu mai apucă să ruleze. Mixin-urile se scriu **întotdeauna înaintea** clasei view-ului: `LoginRequiredMixin, DoarAutorul, UpdateView`.

### 5. queryset sau get_queryset()?

`queryset = Articol.objects.filter(...)` e evaluat (leneș, lecția 52) la fiecare cerere, deci e corect pentru filtre fixe. Dacă filtrul depinde de cerere, de exemplu „doar articolele utilizatorului curent”, un atribut de clasă nu poate folosi `self.request`, pentru că el nu există la importul fișierului. Atunci suprascrii metoda:

```python
class ArticoleleMele(LoginRequiredMixin, ListView):
    template_name = "articole/lista.html"
    context_object_name = "articole"

    def get_queryset(self):
        return Articol.objects.filter(autor=self.request.user)
```

## Exercițiu

Lucrezi în proiectul PyTutor `blog`. La lecția 59 se adaugă doar teste, deci ce scrii aici rămâne.

1. Scrie view-ul `ArticoleleMele` de mai sus (cu `get_queryset`) la adresa `/conturi/articolele-mele/` și pune un link spre el în meniu, doar pentru utilizatorii autentificați.
2. Adaugă în `ListaArticole` atributul `paginate_by = 2` și verifică `/?page=2`. În `lista.html` folosește `page_obj.has_next` și `page_obj.next_page_number` pentru un link „Mai vechi”.
3. Scrie un view `ArticolePeCategorie(ListView)` la `/categorie/<int:nr>/`, care afișează doar articolele categoriei (`get_queryset` cu `self.kwargs["nr"]`) și refolosește `lista.html`.
4. Pune pe `ArticolSterge` un mesaj de confirmare: suprascrie `form_valid` ca în `ArticolNou`.

## Pe scurt

- Un class-based view e o clasă derivată dintr-un view generic (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`, `FormView`, `TemplateView`); setezi doar ce diferă.
- În `urls.py`, clasa devine view prin `.as_view()`.
- Atribute uzuale: `model`/`queryset`, `template_name`, `context_object_name`, `form_class`, `success_url` (cu `reverse_lazy`), `pk_url_kwarg`.
- Metode de suprascris: `get_context_data`, `form_valid`, `get_queryset`, `test_func`; în ele chemi `super()`.
- Mixin-urile (`LoginRequiredMixin`, `UserPassesTestMixin`, `DoarAutorul`) se pun înaintea clasei view-ului: MRO-ul le rulează de la stânga la dreapta.
- View-urile generice pun formularul în context ca `form`; un nume greșit în template dă o pagină goală, fără eroare.

<!-- proiect: _blog/57 -->
<!-- proiect-final: _blog/58 -->
<!-- pregatire: python manage.py migrate -v 0 && python manage.py loaddata /lectii/_blog/date/57.json -v 0 -->
