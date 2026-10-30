<!-- proiect: _blog/53 -->
<!-- proiect-final: _blog/54 -->
<!-- pregatire: python manage.py migrate -v 0 && python manage.py loaddata /lectii/_blog/date/53.json -v 0 -->
## Ce este

**Panoul de administrare** (în engleză „admin”) este o aplicație web gata făcută, inclusă în Django, din care poți vedea, adăuga, modifica și șterge datele modelelor tale: articole, categorii, comentarii, utilizatori. Nu scrii nicio pagină: îi spui doar ce modele să arate și cum, într-un fișier mic, `admin.py`.

```python
from django.contrib import admin

from .models import Articol

admin.site.register(Articol)
```

Panoul e la adresa `/admin/`, legată în `blog_proiect/urls.py` încă de la `startproject` (lecția 45), și e deschis doar pentru utilizatorii marcați ca personal al site-ului.

## De ce contează

Ana nu vrea să deschidă shell-ul de fiecare dată când scrie un articol sau șterge un comentariu nepotrivit. Îi trebuie un loc comod, în browser, cu formulare, căutare și filtre. Să-l construiască de la zero ar însemna zeci de view-uri, template-uri și formulare. Django îl generează din modele, pe baza câmpurilor, a `Meta` și a lui `__str__`.

Panoul de admin e unul dintre motivele pentru care Django e atât de folosit: în multe proiecte, el e chiar interfața echipei pentru conținut, de la prima zi.

## Cum funcționează

### Contul de administrator: createsuperuser

Ca să intri în panou, ai nevoie de un utilizator cu drepturi depline, un **superuser**. Comanda obișnuită e `python manage.py createsuperuser`, care îți cere pe rând numele, e-mailul și parola. În terminalul PyTutor însă, comenzile nu rulează într-un terminal „adevărat” (un TTY), iar Django refuză să ceară parola acolo:

<!-- ruleaza -->
```bash
python manage.py createsuperuser --username ana --email ana@exemplu.ro
```

```text
Superuser creation skipped due to not running in a TTY. You can run `manage.py createsuperuser` in your project to create one manually.
```

Soluția e varianta fără întrebări, `--noinput`, cu parola dată printr-o **variabilă de mediu** (lecția 46), scrisă chiar în fața comenzii:

<!-- ruleaza -->
```bash
DJANGO_SUPERUSER_PASSWORD=parola-ana-2026 python manage.py createsuperuser --noinput --username ana --email ana@exemplu.ro
```

```text
Superuser created successfully.
```

`NUME=valoare comanda` setează variabila doar pentru acea comandă. Cu `--noinput`, Django nu mai întreabă nimic: numele și e-mailul le primește ca opțiuni, iar parola o citește din variabila de mediu `DJANGO_SUPERUSER_PASSWORD` (fără ea, contul ar fi creat fără o parolă cu care să te poți autentifica). Folosește o parolă a ta, nu pe cea din lecție. Parola scrisă așa rămâne în istoricul terminalului, deci metoda e bună doar pentru proiectul de învățare. Pe un calculator obișnuit, `createsuperuser` simplu, cu întrebări, funcționează normal.

### Intrarea în panou

Un vizitator neautentificat care deschide `/admin/` e trimis la pagina de autentificare:

<!-- comanda: python /h/vezi_pagina.py /admin/ -->
```text
302 Found
Location: /admin/login/?next=/admin/
```

<!-- comanda: python /h/vezi_pagina.py /admin/login/ -->
```text
200 OK
Skip to main content
Administrare Django
Toggle theme (current theme: auto) Toggle theme (current theme: light) Toggle theme (current theme: dark)
Nume utilizator:
[câmp: username]
Parolă:
[câmp: password]
[Autentificare]
```

Panoul e tradus în română, pentru că `LANGUAGE_CODE = "ro"` (lecția 46); câteva texte mai rar folosite, ca „Toggle theme”, au rămas în engleză. `?next=/admin/` ține minte unde voiai să ajungi, ca să fii trimis acolo după autentificare (detalii la lecția 57).

După ce Ana se autentifică, prima pagină arată așa (vezi textul paginii; în browser e aranjată în tabele, iar aici celulele unui rând de tabel sunt despărțite prin „ | ”):

<!-- comanda: python /h/vezi_pagina.py --user ana /admin/ -->
```text
200 OK
Skip to main content
Administrare Django
Bun venit, ana. Vizualizare site / Schimbă parola /
Deconectează-te
Toggle theme (current theme: auto) Toggle theme (current theme: light) Toggle theme (current theme: dark)
Administrare site
Autentificare și autorizare
Model name | Add link | Change or view list link
Grupuri | Adaugă | Schimbare
Utilizatori | Adaugă | Schimbare
Acțiuni recente
Acțiunile mele
Niciuna
```

Rândul „Model name | Add link | Change or view list link” e capul tabelului, ascuns în browser (îl citesc doar programele care citesc ecranul cu voce tare pentru nevăzători). Deocamdată apar doar utilizatorii și grupurile, din aplicația `auth` a Django. Articolele lipsesc: panoul arată doar modelele pe care i le dai explicit.

### Înregistrarea modelelor

Cea mai simplă formă: câte un `register` pentru fiecare model, în `articole/admin.py`:

<!-- fisier: articole/admin.py -->
```python
from django.contrib import admin

from .models import Articol, Categorie, Comentariu, Eticheta

admin.site.register(Articol)
admin.site.register(Comentariu)
admin.site.register(Categorie)
admin.site.register(Eticheta)
```

Django citește automat fișierul `admin.py` al fiecărei aplicații din `INSTALLED_APPS`. Prima pagină a panoului are acum o secțiune nouă:

<!-- comanda: python /h/vezi_pagina.py --user ana /admin/ -->
```text
200 OK
Skip to main content
Administrare Django
Bun venit, ana. Vizualizare site / Schimbă parola /
Deconectează-te
Toggle theme (current theme: auto) Toggle theme (current theme: light) Toggle theme (current theme: dark)
Administrare site
Articole
Model name | Add link | Change or view list link
Articole | Adaugă | Schimbare
Categorii | Adaugă | Schimbare
Comentarii | Adaugă | Schimbare
Etichete | Adaugă | Schimbare
Autentificare și autorizare
Model name | Add link | Change or view list link
Grupuri | Adaugă | Schimbare
Utilizatori | Adaugă | Schimbare
Acțiuni recente
Acțiunile mele
Niciuna
```

Titlul secțiunii vine de la aplicația `articole`, iar numele modelelor („Categorii”, „Etichete”) vin din `verbose_name_plural` din `Meta` (lecțiile 50 și 53). Lista comentariilor (aici și mai jos, doar partea principală a paginii):

<!-- comanda: python /h/vezi_pagina.py --user ana /admin/articole/comentariu/ | awk 'NR==1; /^Selectează/{p=1} p' -->
```text
200 OK
Selectează comentariu pentru schimbare
Adaugă comentariu
Acțiune:
[câmp: action] --------- Elimină comentarii selectate
Start
0 din 2 selectat
[câmp: ?]
Comentariu
[câmp: _selected_action] | Mihai despre „De ce am ales Django”
[câmp: _selected_action] | Mihai despre „O plimbare prin Cluj”
2 comentarii
```

Aici se vede promisiunea din lecția 35: fiecare rând din listă e textul întors de `__str__`. Pentru comentarii, `__str__` scris la lecția 53 („Mihai despre «De ce am ales Django»”) e exact ce vrei să vezi într-o listă. `[câmp: _selected_action]`, prima celulă a rândului, e căsuța de bifat, pentru acțiuni pe mai multe rânduri deodată (de exemplu ștergerea). Capul tabelului apare pe rânduri separate: `[câmp: ?]` e căsuța care le bifează pe toate (n-are nume în HTML), urmată de titlurile coloanelor; fiecare titlu e închis în HTML în blocuri proprii, de aceea nu e lipit cu „ | ”.

### Personalizarea cu ModelAdmin

Pentru articole, o singură coloană nu ajunge. O clasă derivată din `admin.ModelAdmin` spune panoului cum să arate un model. Varianta finală a fișierului:

<!-- fisier: articole/admin.py -->
```python
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
```

- `@admin.register(Articol)` e un decorator (lecția 38): face același lucru ca `admin.site.register(Articol, ArticolAdmin)`, dar stă chiar deasupra clasei;
- `list_display` — coloanele din lista de articole;
- `list_filter` — filtrele din dreapta listei (publicat da/nu, categoria);
- `search_fields` — câmpurile în care caută caseta de căutare;
- `inlines` — modele legate, editate pe aceeași pagină: comentariile apar sub articol. `TabularInline` le așază într-un tabel, iar `extra = 0` înseamnă „fără rânduri goale în plus pentru comentarii noi”.

Lista articolelor arată acum coloanele și filtrele:

<!-- comanda: python /h/vezi_pagina.py --user ana /admin/articole/articol/ | awk 'NR==1; /^Selectează/{p=1} p' -->
```text
200 OK
Selectează articol pentru schimbare
Adaugă articol
[câmp: q] [Caută]
Acțiune:
[câmp: action] --------- Elimină articole selectate
Start
0 din 3 selectat
[câmp: ?]
Titlu
Categorie
Data publicarii
Publicat
[câmp: _selected_action] | O plimbare prin Cluj | Călătorii | 20 Octombrie 2026
[câmp: _selected_action] | De ce am ales Django | Programare | 2 Octombrie 2026
[câmp: _selected_action] | Primul meu program în Python | Programare | 14 Septembrie 2026
3 articole
Filtru
Show counts
După publicat
Toate
Da
Nu
După categorie
Toate
Călătorii
Programare
-
```

Coloana „Publicat” e afișată în browser ca o bifă verde, o imagine, de aceea nu apare în textul de mai sus. Lunile au majusculă („20 Octombrie 2026”) pentru că panoul nu folosește `|lower`, ca template-urile blogului (lecția 48). Titlurile coloanelor vin din numele câmpurilor („Data publicarii”); le poți schimba cu `verbose_name="data publicării"` în model (urmat de `makemigrations` și `migrate`). Căutarea după „Django”:

<!-- comanda: python /h/vezi_pagina.py --user ana /admin/articole/articol/?q=Django | awk 'NR==1; /^Selectează/{p=1} p' -->
```text
200 OK
Selectează articol pentru schimbare
Adaugă articol
[câmp: q] [Caută] 1 rezultat (3 în total)
Acțiune:
[câmp: action] --------- Elimină articole selectate
Start
0 din 1 selectat
[câmp: ?]
Titlu
Categorie
Data publicarii
Publicat
[câmp: _selected_action] | De ce am ales Django | Programare | 2 Octombrie 2026
1 articol
Filtru
Show counts
După publicat
Toate
Da
Nu
După categorie
Toate
Călătorii
Programare
-
```

Caseta de căutare trimite `?q=Django` în adresă (o cerere GET, lecția 43), iar Django caută textul în `titlu` și în `continut`, cu `icontains` (lecția 52).

### Ce se întâmplă „pe dedesubt”: formularele generate din model

Pagina de editare a unui articol e un formular construit automat din câmpurile modelului:

<!-- comanda: python /h/vezi_pagina.py --user ana /admin/articole/articol/2/change/ | awk 'NR==1; /^Schimbă articol/{p=1} p' -->
```text
200 OK
Schimbă articol
De ce am ales Django
Istoric
Vizualizează pe site
Titlu:
[câmp: titlu]
Continut:
[câmp: continut] După primele luni cu Python, voiam să fac un site adevărat: cu pagini, cu bază de date și cu un loc unde să mă autentific. Django are toate acestea „din cutie”, iar documentația lui e excelentă.
Data publicarii:
[câmp: data_publicarii]
[câmp: publicat]
Publicat
Categorie:
[câmp: categorie] --------- Călătorii Programare
Etichete:
[câmp: etichete] cluj django python
Hold down “Control”, or “Command” on a Mac, to select more than one.
Comentarii
Autor | Text | Elimină?
Mihai despre „De ce am ales Django”
[câmp: comentarii-0-autor]
[câmp: comentarii-0-text] Foarte bun articol!
[câmp: comentarii-0-DELETE]
[câmp: comentarii-__prefix__-autor]
[câmp: comentarii-__prefix__-text]
[Salvează] [Salvați și mai adăugați] [Salvați și continuați editarea] Șterge
```

Fiecare câmp de model a devenit câmpul potrivit de formular:
- `CharField` → o casetă de text, `TextField` → o zonă de text mare, `DateField` → o casetă pentru dată;
- `BooleanField` → o căsuță de bifat;
- `ForeignKey` → o listă derulantă cu toate categoriile (`---------` înseamnă „fără categorie”, posibil datorită lui `blank=True`);
- `ManyToManyField` → o listă din care alegi mai multe etichete;
- comentariile, prin `ComentariuInline`, cu câte un rând pentru fiecare. Rândul cu `__prefix__` nu e un rând gol vizibil: e un model ascuns, din care butonul „Adaugă încă un Comentariu” creează în browser rânduri noi.

„Vizualizează pe site” apare pentru că modelul are `get_absolute_url()` (lecția 53). Același mecanism, formulare construite din modele, îl vei folosi în paginile tale la lecția 56, cu `ModelForm`. Și validarea e automată: un titlu gol sau prea lung e refuzat, cu un mesaj lângă câmp.

Accesul e controlat de două atribute ale utilizatorului: `is_staff` (poate intra în panou) și `is_superuser` (are toate drepturile). Un utilizator obișnuit, chiar autentificat, nu poate intra (vezi greșelile frecvente). Fiecare schimbare făcută din panou e înregistrată: pe prima pagină, la „Acțiuni recente”, îți vezi propriile schimbări, iar butonul „Istoric” al fiecărui obiect arată toate schimbările lui, cu autorul și data.

## Exemplu complet

Fișierul complet al lecției e `articole/admin.py`, în varianta cu `ArticolAdmin` de mai sus. Un drum obișnuit al Anei prin panou:
1. intră pe `/admin/` și se autentifică;
2. deschide „Articole”, caută „Cluj”, alege din dreapta filtrul „După publicat: Da”, apoi revine la „Toate”;
3. deschide articolul „De ce am ales Django”, corectează comentariul lui Mihai din tabelul de sub articol și apasă „Salvează”; apoi, la „Primul meu program în Python”, adaugă eticheta `django`;
4. intră la „Comentarii” și șterge un comentariu nepotrivit, din listă, cu acțiunea „Elimină comentarii selectate”.

Tot ce a modificat apare imediat pe blog, pentru că panoul și paginile publice citesc aceeași bază de date.

## Greșeli frecvente

### 1. Coloană inexistentă în list_display

`list_display = ["titlu", "autor", "publicat"]`, dar `Articol` nu are (încă) un câmp `autor`:

<!-- comanda: rm -rf /tmp/p && cp -r . /tmp/p && cd /tmp/p && sed -i 's/"titlu", "categorie", "data_publicarii", "publicat"/"titlu", "autor", "publicat"/' articole/admin.py && python manage.py check -->
```text
SystemCheckError: System check identified some issues:

ERRORS:
<class 'articole.admin.ArticolAdmin'>: (admin.E108) The value of 'list_display[1]' refers to 'autor', which is not a callable or attribute of 'ArticolAdmin', or an attribute, method, or field on 'articole.Articol'.

System check identified 1 issue (0 silenced).
```

Verificarea sistemului (lecția 50) controlează și `admin.py`: `list_display[1]` e al doilea element din listă (numărătoarea de la 0), iar mesajul spune exact ce nu găsește. Același fel de eroare apare pentru `list_filter` cu nume greșite. `search_fields` nu e verificat așa: un nume greșit trece de `check` și dă eroare abia la prima căutare (greșeala 3).

### 2. Același model înregistrat de două ori

Ai păstrat un `admin.site.register(Articol)` mai vechi la finalul fișierului, deși `ArticolAdmin` are deja `@admin.register(Articol)`:

<!-- comanda: rm -rf /tmp/p && cp -r . /tmp/p && cd /tmp/p && printf 'admin.site.register(Articol)\n' >> articole/admin.py && python manage.py check -->
```text
Traceback (most recent call last):
  File "/tmp/p/articole/admin.py", line 27, in <module>
    admin.site.register(Articol)
django.contrib.admin.exceptions.AlreadyRegistered: The model Articol is already registered with 'articole.ArticolAdmin'.
```

(Tracebackul e scurtat.) Un model se înregistrează o singură dată: fie cu `register`, fie cu decoratorul. Pentru că `admin.py` se încarcă la pornire, eroarea oprește orice comandă, inclusiv `runserver`.

### 3. Căutare într-un ForeignKey

`search_fields = ["titlu", "categorie"]` trece de verificare, dar pagina crapă la prima căutare:

<!-- comanda: rm -rf /tmp/p && cp -r . /tmp/p && cd /tmp/p && sed -i 's/search_fields = \["titlu", "continut"\]/search_fields = ["titlu", "categorie"]/' articole/admin.py && python /h/vezi_pagina.py --user ana /admin/articole/articol/?q=Cluj -->
```text
Internal Server Error: /admin/articole/articol/
Traceback (most recent call last):
django.core.exceptions.FieldError: Unsupported lookup 'icontains' for ForeignKey or join on the field not permitted.
```

(Tracebackul e scurtat.) Căutarea folosește `icontains` (lecția 52), care are sens pe text, nu pe o legătură către alt tabel. Caută în câmpul de text al categoriei, peste relație (lecția 53): `search_fields = ["titlu", "categorie__nume"]`.

### 4. Model fără __str__

Dacă `Categorie` n-ar avea `__str__`, lista categoriilor ar arăta așa:

<!-- comanda: rm -rf /tmp/p && cp -r . /tmp/p && cd /tmp/p && sed -i '/def __str__(self):/,+1d' articole/models.py && python /h/vezi_pagina.py --user ana /admin/articole/categorie/ | awk 'NR==1; /^Selectează/{p=1} p' -->
```text
200 OK
Selectează categorie pentru schimbare
Adaugă categorie
Acțiune:
[câmp: action] --------- Elimină categorii selectate
Start
0 din 2 selectat
[câmp: ?]
Categorie
[câmp: _selected_action] | Categorie object (2)
[câmp: _selected_action] | Categorie object (1)
2 categorii
```

Același „Categorie object (1)” ar apărea și în lista derulantă din pagina articolului. Scrie mereu `__str__` la modele: panoul de admin e primul loc unde se vede lipsa lui.

### 5. Un utilizator obișnuit încearcă să intre în panou

Mihai are cont pe site, dar nu face parte din personal (`is_staff` e `False`):

<!-- comanda: rm -rf /tmp/p && cp -r . /tmp/p && cd /tmp/p && python manage.py shell -v 0 -c "from django.contrib.auth.models import User; User.objects.create_user('mihai', password='parola-mihai-2026')" && python /h/vezi_pagina.py --follow --user mihai /admin/ -->
```text
200 OK
Skip to main content
Administrare Django
Sunteți autentificat ca mihai, dar nu sunteți autorizat să accesați această pagină. Doriți să vă autentificați cu un alt cont?
Nume utilizator:
[câmp: username]
Parolă:
[câmp: password]
[Autentificare]
```

Nu e o eroare a ta, ci regula panoului: doar personalul intră. Ca Mihai să poată modera comentarii, Ana îi bifează, din pagina lui de utilizator, căsuța care corespunde lui `is_staff` (accesul personalului la panou), iar din permisiuni îi dă doar drepturile de care are nevoie (de exemplu, să schimbe și să șteargă comentarii). Despre utilizatori și autentificare în paginile tale, la lecția 57.

## Exercițiu

Lucrezi în proiectul PyTutor `blog`. Creează-ți superuserul cu `--noinput` și scrie `articole/admin.py` ca în lecție. Pornește `python manage.py runserver 0.0.0.0:8000`, deschide adresa din bara terminalului și adaugă `/admin/` la final. Apoi:

1. adaugă din panou un articol nou, nepublicat, cu categoria „Programare” și eticheta `python`; verifică pe blog că nu apare în listă;
2. caută articolele care conțin „Cluj” și încearcă filtrele din dreapta;
3. deschide un articol și adaugă un comentariu din tabelul de sub el;
4. încearcă să salvezi un articol cu titlul gol și citește mesajul de eroare;
5. pentru comentarii, adaugă `list_filter = ["articol"]` în `ComentariuAdmin` și vezi filtrul nou. La final, scoate-l la loc și șterge articolul de test, ca proiectul să rămână ca în lecție: lecția 55 pornește de la `admin.py`-ul de aici.

## Pe scurt

- Panoul de admin e la `/admin/` și e generat din modele; intră doar utilizatorii cu `is_staff` (superuserii au toate drepturile).
- `createsuperuser` creează contul de administrator; în terminalul PyTutor, cu `--noinput` și `DJANGO_SUPERUSER_PASSWORD=...` în fața comenzii.
- `admin.site.register(Model)` face modelul vizibil; `@admin.register(Model)` pe o clasă `ModelAdmin` îl și personalizează.
- `list_display`, `list_filter`, `search_fields` și `inlines` (`TabularInline`) sunt opțiunile cele mai folosite.
- Panoul folosește `__str__`, `verbose_name` și `verbose_name_plural` din modele; câmpurile devin automat câmpuri de formular, cu validare.
- Nume greșite în `list_display` și `list_filter` sunt prinse de verificarea sistemului; cele din `search_fields` apar abia la căutare, iar căutarea într-un `ForeignKey` se face într-un câmp de text al modelului legat (`categorie__nume`).
