<!-- proiect: _blog/52 -->
<!-- proiect-final: _blog/53 -->
<!-- pregatire: python manage.py migrate -v 0 && python manage.py loaddata /lectii/_blog/date/50.json -v 0 -->
## Ce este

O **relație** leagă rândurile unui model de rândurile altui model. Blogul Anei are nevoie de trei:
- fiecare articol aparține unei **categorii** (Programare, Călătorii), iar o categorie are mai multe articole: relație „unu la mai mulți”, scrisă cu `ForeignKey`;
- un articol are mai multe **etichete** (python, django), iar o etichetă apare la mai multe articole: relație „mai mulți la mai mulți”, scrisă cu `ManyToManyField`;
- un articol are mai multe **comentarii**, iar fiecare comentariu aparține unui singur articol: tot `ForeignKey`, de data asta în modelul `Comentariu`.

```python
class Comentariu(models.Model):
    articol = models.ForeignKey(Articol, on_delete=models.CASCADE, related_name="comentarii")
    autor = models.CharField(max_length=80)
    text = models.TextField()
```

În baza de date, `ForeignKey` devine o coloană care păstrează `id`-ul rândului legat (`articol_id`). În Python, `comentariu.articol` îți dă direct obiectul `Articol`, iar `articol.comentarii.all()` îți dă comentariile lui.

## De ce contează

Datele reale sunt aproape mereu legate între ele: comenzile au clienți, produsele au categorii, elevii au note la materii. Ai putea pune numele categoriei ca text în fiecare articol, dar atunci „Programare” ar fi scris de zeci de ori, o greșeală de tastare ar crea o categorie nouă, iar redenumirea ar cere modificarea fiecărui articol. Cu o relație, categoria există o singură dată, iar articolele trimit la ea.

Relațiile sunt și locul unde o aplicație devine ușor lentă fără să-ți dai seama (problema „N+1”, mai jos). Django îți dă uneltele să eviți asta.

## Cum funcționează

### Modelele noi

Modelele complete, după lecția asta:

<!-- fisier: articole/models.py -->
```python
from datetime import date

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

Ce e nou:
- `Categorie` și `Eticheta` sunt modele mici, cu un nume `unique=True`: nu pot exista două categorii „Programare”. Ele sunt definite **înaintea** lui `Articol`, pentru că `Articol` le folosește;
- `categorie = models.ForeignKey(Categorie, ...)` — fiecare articol trimite la o categorie;
  - `on_delete=models.SET_NULL` spune ce se întâmplă cu articolele când categoria lor e ștearsă: rămân, dar fără categorie. De aceea câmpul are și `null=True` (în baza de date poate fi gol) și `blank=True` (în formulare poate rămâne necompletat);
  - `related_name="articole"` e numele drumului **invers**: `categorie.articole.all()` dă articolele unei categorii;
- `etichete = models.ManyToManyField(Eticheta, ...)` — legătura „mai mulți la mai mulți”. Pentru ea, Django creează automat un tabel separat, cu perechi `(articol_id, eticheta_id)`;
- `Comentariu.articol` are `on_delete=models.CASCADE`: dacă articolul e șters, se șterg și comentariile lui („în cascadă”). Alte variante: `PROTECT` (interzice ștergerea cât timp există comentarii) sau `SET_NULL`, ca la categorie;
- `data = models.DateTimeField(auto_now_add=True)` pune automat data și ora la crearea comentariului;
- `get_absolute_url()` întoarce adresa paginii articolului, construită cu `reverse` din numele URL-ului: `reverse` face în Python ce face `{% url %}` în template-uri (lecția 48). O vor folosi formularele de la lecția 56.

Al treilea fel de relație, „unu la unu”, se scrie cu `models.OneToOneField`: fiecare rând are cel mult un partener, de exemplu un utilizator și profilul lui. Funcționează ca un `ForeignKey` cu `unique=True`.

### Migrarea

<!-- ruleaza -->
```bash
python manage.py makemigrations
python manage.py migrate
```

```text
Migrations for 'articole':
  articole/migrations/0003_categorie_eticheta_articol_categorie_comentariu_and_more.py
    + Create model Categorie
    + Create model Eticheta
    + Add field categorie to articol
    + Create model Comentariu
    + Add field etichete to articol
Operations to perform:
  Apply all migrations: admin, articole, auth, contenttypes, sessions
Running migrations:
  Applying articole.0003_categorie_eticheta_articol_categorie_comentariu_and_more... OK
```

Numele lung l-a ales Django din operațiile migrării. Articolele existente au acum `categorie` goală (`None`) și nicio etichetă.

### Legarea obiectelor, în shell

Ana creează categoriile și etichetele și le leagă de articole:

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol, Categorie, Eticheta' 'programare = Categorie.objects.create(nume="Programare")' 'calatorii = Categorie.objects.create(nume="Călătorii")' 'python = Eticheta.objects.create(nume="python")' 'django = Eticheta.objects.create(nume="django")' 'cluj = Eticheta.objects.create(nume="cluj")' 'Articol.objects.filter(id__in=[1, 2]).update(categorie=programare)' 'clujul = Articol.objects.get(id=3)' 'clujul.categorie = calatorii' 'clujul.save()' 'clujul.etichete.add(cluj)' 'Articol.objects.get(id=1).etichete.add(python)' 'Articol.objects.get(id=2).etichete.set([python, django])' 'clujul.categorie' 'clujul.categorie.nume' 'clujul.categorie_id' 'programare.articole.all()' 'Articol.objects.get(id=2).etichete.all()' 'python.articole.count()'; } | PYTHONPATH=/h python manage.py shell -->
```text
10 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol, Categorie, Eticheta
>>> programare = Categorie.objects.create(nume="Programare")
>>> calatorii = Categorie.objects.create(nume="Călătorii")
>>> python = Eticheta.objects.create(nume="python")
>>> django = Eticheta.objects.create(nume="django")
>>> cluj = Eticheta.objects.create(nume="cluj")
>>> Articol.objects.filter(id__in=[1, 2]).update(categorie=programare)
2
>>> clujul = Articol.objects.get(id=3)
>>> clujul.categorie = calatorii
>>> clujul.save()
>>> clujul.etichete.add(cluj)
>>> Articol.objects.get(id=1).etichete.add(python)
>>> Articol.objects.get(id=2).etichete.set([python, django])
>>> clujul.categorie
<Categorie: Călătorii>
>>> clujul.categorie.nume
'Călătorii'
>>> clujul.categorie_id
2
>>> programare.articole.all()
<QuerySet [<Articol: De ce am ales Django>, <Articol: Primul meu program în Python>]>
>>> Articol.objects.get(id=2).etichete.all()
<QuerySet [<Eticheta: django>, <Eticheta: python>]>
>>> python.articole.count()
2
>>>
now exiting InteractiveConsole...
```

- un `ForeignKey` se setează ca orice atribut, cu un **obiect**: `clujul.categorie = calatorii`, apoi `save()`; sau, pentru mai multe rânduri, cu `update(categorie=programare)`;
- `clujul.categorie_id` e coloana din baza de date: doar `id`-ul categoriei;
- un `ManyToManyField` nu se setează cu `=`, ci prin managerul lui: `add(...)` adaugă etichete, `set([...])` le înlocuiește pe toate, `remove(...)` scoate una, `clear()` le scoate pe toate. Schimbările se salvează imediat, fără `save()`;
- `programare.articole.all()` folosește `related_name`: drumul invers, de la categorie la articolele ei.

Apoi, Mihai lasă două comentarii:

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol, Comentariu' 'django_articol = Articol.objects.get(id=2)' 'django_articol.comentarii.create(autor="Mihai", text="Foarte bun articol!")' 'Comentariu.objects.create(articol=Articol.objects.get(id=3), autor="Mihai", text="Și eu iubesc Clujul! Grădina Botanică merită.")' 'django_articol.comentarii.count()' 'Comentariu.objects.filter(autor="Mihai").count()'; } | PYTHONPATH=/h python manage.py shell -->
```text
10 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol, Comentariu
>>> django_articol = Articol.objects.get(id=2)
>>> django_articol.comentarii.create(autor="Mihai", text="Foarte bun articol!")
<Comentariu: Mihai despre „De ce am ales Django”>
>>> Comentariu.objects.create(articol=Articol.objects.get(id=3), autor="Mihai", text="Și eu iubesc Clujul! Grădina Botanică merită.")
<Comentariu: Mihai despre „O plimbare prin Cluj”>
>>> django_articol.comentarii.count()
1
>>> Comentariu.objects.filter(autor="Mihai").count()
2
>>>
now exiting InteractiveConsole...
```

Cele două variante fac același lucru: `articol.comentarii.create(...)` completează singur câmpul `articol`, iar `Comentariu.objects.create(articol=..., ...)` îl primește explicit.

### Interogări peste relații

În `filter`, `__` trece și dintr-un model în altul: `categorie__nume` înseamnă „câmpul `nume` al categoriei”.

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol, Categorie' 'Articol.objects.filter(categorie__nume="Programare")' 'Articol.objects.filter(etichete__nume="django")' 'Articol.objects.filter(comentarii__autor="Mihai")' 'Categorie.objects.filter(articole__titlu__icontains="cluj")'; } | PYTHONPATH=/h python manage.py shell -->
```text
10 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol, Categorie
>>> Articol.objects.filter(categorie__nume="Programare")
<QuerySet [<Articol: De ce am ales Django>, <Articol: Primul meu program în Python>]>
>>> Articol.objects.filter(etichete__nume="django")
<QuerySet [<Articol: De ce am ales Django>]>
>>> Articol.objects.filter(comentarii__autor="Mihai")
<QuerySet [<Articol: O plimbare prin Cluj>, <Articol: De ce am ales Django>]>
>>> Categorie.objects.filter(articole__titlu__icontains="cluj")
<QuerySet [<Categorie: Călătorii>]>
>>>
now exiting InteractiveConsole...
```

Django scrie pentru tine **join**-urile, adică interogările SQL care combină mai multe tabele.

### Pagina articolului: etichete și comentarii

View-ul `detaliu` nu se schimbă: articolul își aduce singur etichetele și comentariile. Template-ul le afișează:

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
  </section>
{% endblock %}
```

În template, metodele se apelează **fără paranteze**: `articol.comentarii.all`, `articol.comentarii.count`. Filtrul `join` lipește etichetele cu virgulă, ca `", ".join(...)` (lecția 4), folosind `__str__`-ul fiecăreia. `_meta.html` (lecția 48) afișa deja categoria cu `{% if articol.categorie %}`; acum, când articolul are o categorie, ea apare lângă dată.

### Ce se întâmplă „pe dedesubt”: problema N+1 și select_related

Pe pagina listei, fiecare articol își afișează categoria. Fără grijă, asta înseamnă o interogare pentru lista de articole, plus încă **una pentru fiecare articol**, ca să-i aducă categoria: pentru N articole, N+1 interogări. Poți număra interogările în shell (Django le ține minte cât timp `DEBUG` e activ):

<!-- comanda: { sleep 8; printf '%s\n' 'from django.db import connection, reset_queries' 'from articole.models import Articol' 'reset_queries()' 'for a in Articol.objects.all():' '    print(a, "-", a.categorie)' '' 'len(connection.queries)' 'reset_queries()' 'for a in Articol.objects.select_related("categorie"):' '    print(a, "-", a.categorie)' '' 'len(connection.queries)'; } | PYTHONPATH=/h python manage.py shell -->
```text
10 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from django.db import connection, reset_queries
>>> from articole.models import Articol
>>> reset_queries()
>>> for a in Articol.objects.all():
...     print(a, "-", a.categorie)
...
O plimbare prin Cluj - Călătorii
De ce am ales Django - Programare
Primul meu program în Python - Programare
>>> len(connection.queries)
4
>>> reset_queries()
>>> for a in Articol.objects.select_related("categorie"):
...     print(a, "-", a.categorie)
...
O plimbare prin Cluj - Călătorii
De ce am ales Django - Programare
Primul meu program în Python - Programare
>>> len(connection.queries)
1
>>>
now exiting InteractiveConsole...
```

`select_related("categorie")` aduce articolele **și** categoriile lor într-o singură interogare, cu un join. La 3 articole diferența e mică; la 100 de articole pe pagină, sunt 101 interogări față de una. De aceea, view-ul listei folosește acum `select_related`:

<!-- fisier: articole/views.py -->
```python
from django.shortcuts import get_object_or_404, render

from .models import Articol


def lista(request):
    articole = Articol.objects.filter(publicat=True).select_related("categorie")
    return render(request, "articole/lista.html", {"articole": articole})


def detaliu(request, nr):
    articol = get_object_or_404(Articol, id=nr, publicat=True)
    return render(request, "articole/detaliu.html", {"articol": articol})


def despre(request):
    return render(request, "articole/despre.html")
```

`select_related` merge pentru `ForeignKey` și `OneToOneField` (un singur obiect legat). Pentru relațiile care aduc **mai multe** obiecte (etichetele unui articol, comentariile lui) există `prefetch_related("etichete")`, care face o a doua interogare pentru toate articolele deodată, în loc de câte una pentru fiecare.

## Exemplu complet

Pagina articolului „De ce am ales Django”, cu categoria, etichetele și comentariul lui Mihai (la tine, data comentariului va fi ziua în care l-ai adăugat; aici e cea de pe blogul Anei):

<!-- comanda: python manage.py loaddata /lectii/_blog/date/53.json -v 0 && python /h/vezi_pagina.py /articol/2/ -->
```text
200 OK
Blogul Anei
Articole Despre
De ce am ales Django
2 octombrie 2026 · Programare
După primele luni cu Python, voiam să fac un site adevărat: cu pagini, cu bază de date și cu un loc unde să mă autentific.
Django are toate acestea „din cutie”, iar documentația lui e excelentă.
Etichete: django, python
Comentarii (1)
Mihai · 3 octombrie 2026
Foarte bun articol!
Ana Popescu, Cluj · 2026
```

Și lista, unde fiecare articol are acum categoria lângă dată:

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

## Greșeli frecvente

### 1. Numele drumului invers

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Categorie' 'programare = Categorie.objects.get(nume="Programare")' 'programare.articol_set.all()' 'programare.articole.count()'; } | PYTHONPATH=/h python manage.py shell -->
```text
>>> programare = Categorie.objects.get(nume="Programare")
>>> programare.articol_set.all()
Traceback (most recent call last):
  File "<console>", line 1, in <module>
AttributeError: 'Categorie' object has no attribute 'articol_set'. Did you mean: 'articole'?
>>> programare.articole.count()
2
>>>
now exiting InteractiveConsole...
```

(Aici și mai jos am păstrat doar rândurile de la comanda greșită încolo și am scurtat tracebackurile.) Fără `related_name`, Django ar fi numit drumul invers `articol_set` (numele modelului cu litere mici, plus `_set`). Pentru că am dat `related_name="articole"`, numele implicit nu mai există, iar Python îți sugerează chiar numele corect. Dacă nu-l știi, deschide `models.py`.

### 2. Atribuire directă la un ManyToManyField

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol, Eticheta' 'a = Articol.objects.get(id=1)' 'a.etichete = [Eticheta.objects.get(nume="python")]' 'a.etichete.set([Eticheta.objects.get(nume="python")])'; } | PYTHONPATH=/h python manage.py shell -->
```text
>>> a = Articol.objects.get(id=1)
>>> a.etichete = [Eticheta.objects.get(nume="python")]
Traceback (most recent call last):
  File "<console>", line 1, in <module>
TypeError: Direct assignment to the forward side of a many-to-many set is prohibited. Use etichete.set() instead.
>>> a.etichete.set([Eticheta.objects.get(nume="python")])
>>>
now exiting InteractiveConsole...
```

`etichete` nu e o listă, ci un manager: folosește `set()`, `add()`, `remove()` sau `clear()`.

### 3. Etichete pentru un articol încă nesalvat

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol, Eticheta' 'nou = Articol(titlu="Ciornă", continut="...")' 'nou.etichete.add(Eticheta.objects.get(nume="python"))'; } | PYTHONPATH=/h python manage.py shell -->
```text
>>> nou = Articol(titlu="Ciornă", continut="...")
>>> nou.etichete.add(Eticheta.objects.get(nume="python"))
Traceback (most recent call last):
  File "<console>", line 1, in <module>
ValueError: "<Articol: Ciornă>" needs to have a value for field "id" before this many-to-many relationship can be used.
>>>
now exiting InteractiveConsole...
```

Tabelul de legătură păstrează perechi de `id`-uri, iar un articol nesalvat nu are încă `id`. Salvează întâi articolul (`nou.save()` sau `create`), apoi adaugă etichetele.

### 4. Un id în loc de obiect la ForeignKey

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'a = Articol.objects.get(id=1)' 'a.categorie = 1' 'a.categorie_id = 1'; } | PYTHONPATH=/h python manage.py shell -->
```text
>>> a = Articol.objects.get(id=1)
>>> a.categorie = 1
Traceback (most recent call last):
  File "<console>", line 1, in <module>
ValueError: Cannot assign "1": "Articol.categorie" must be a "Categorie" instance.
>>> a.categorie_id = 1
>>>
now exiting InteractiveConsole...
```

`a.categorie` vrea un obiect `Categorie`. Dacă ai doar `id`-ul, scrie-l în coloana propriu-zisă, `a.categorie_id = 1`, apoi `save()`.

### 5. Duplicat într-un câmp unique

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Categorie' 'Categorie.objects.create(nume="Programare")' 'Categorie.objects.get_or_create(nume="Programare")'; } | PYTHONPATH=/h python manage.py shell -->
```text
>>> Categorie.objects.create(nume="Programare")
Traceback (most recent call last):
sqlite3.IntegrityError: UNIQUE constraint failed: articole_categorie.nume

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "<console>", line 1, in <module>
django.db.utils.IntegrityError: UNIQUE constraint failed: articole_categorie.nume
>>> Categorie.objects.get_or_create(nume="Programare")
(<Categorie: Programare>, False)
>>>
now exiting InteractiveConsole...
```

`unique=True` e o regulă a bazei de date: al doilea „Programare” e refuzat cu `IntegrityError`. Când nu știi dacă obiectul există deja, `get_or_create` îl caută și îl creează doar dacă lipsește; întoarce perechea `(obiect, creat)`, unde `creat` spune dacă a fost nevoie de creare.

## Exercițiu

Lucrezi în proiectul PyTutor `blog`. Actualizează `models.py`, `views.py` și `detaliu.html` ca în lecție, fă migrarea și creează în shell categoriile, etichetele și cele două comentarii ale lui Mihai, ca în lecție, dacă n-ai făcut-o deja cât ai citit-o (a doua oară, `create` ar da `IntegrityError`, vezi greșeala 5). Apoi:

1. adaugă eticheta `django` și la articolul 1, apoi scoate-o la loc (`add`, `remove`);
2. afișează, pentru fiecare categorie, numele și câte articole are (`categorie.articole.count()`);
3. găsește toate comentariile la articolele din categoria „Călătorii”, cu un singur `filter` (`articol__categorie__nume=...`);
4. numără interogările pentru o buclă care afișează fiecare articol cu etichetele lui, cu și fără `prefetch_related("etichete")`;
5. verifică în browser pagina `/articol/3/`: categoria, eticheta și comentariul lui Mihai.

Păstrează datele create: lecția 54 le va afișa în panoul de administrare.

## Pe scurt

- `ForeignKey` leagă „mai mulți la unul” (multe articole, o categorie); `ManyToManyField` leagă „mai mulți la mai mulți” (articole și etichete); `OneToOneField` leagă „unu la unu”.
- `on_delete` decide ce se întâmplă la ștergerea obiectului legat: `CASCADE`, `SET_NULL` (cu `null=True`), `PROTECT`.
- `related_name` dă numele drumului invers: `categorie.articole.all()`, `articol.comentarii.all()`.
- Un `ForeignKey` primește un obiect (sau `camp_id` primește un `id`); un `ManyToManyField` se schimbă cu `add`, `set`, `remove`, `clear`, după ce obiectul e salvat.
- `filter(categorie__nume="Programare")` caută peste relații.
- Problema N+1: `select_related` pentru `ForeignKey`, `prefetch_related` pentru relațiile cu mai multe obiecte.
