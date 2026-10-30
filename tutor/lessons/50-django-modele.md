<!-- proiect: _blog/49 -->
<!-- proiect-final: _blog/50 -->
## Ce este

Un **model** este o clasă Python care descrie un fel de date pe care aplicația le păstrează în **baza de date**: articole, comentarii, utilizatori. Fiecare model devine un **tabel**, fiecare atribut al clasei devine o **coloană**, iar fiecare obiect al clasei devine un **rând** din tabel.

Până acum, articolele blogului stăteau într-o listă Python, `ARTICOLE`, în `articole/views.py` (lecția 47). Lista e scrisă în cod: ca să adaugi un articol, trebuie să modifici fișierul, iar orice schimbare făcută în ea cât rulează serverul se pierde la repornire. De la lecția asta, articolele vor sta într-o bază de date, descrise de modelul `Articol`:

<!-- fisier: articole/models.py -->
```python
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
```

Partea din Django care traduce între obiecte Python și tabele se numește **ORM** (de la „Object-Relational Mapping”, adică „corespondența dintre obiecte și tabele”). Cu ORM-ul nu scrii SQL, limbajul bazelor de date: lucrezi cu clase și obiecte, ca la lecția 32, iar Django scrie SQL-ul pentru tine.

## De ce contează

Aproape orice aplicație web păstrează date: un magazin are produse și comenzi, o rețea socială are utilizatori și postări, blogul Anei are articole și, curând, comentarii. Datele trebuie să rămână și după ce serverul se oprește, să poată fi căutate rapid și să poată fi modificate de mai mulți utilizatori deodată. Exact asta face o bază de date.

Modelul e centrul unei aplicații Django. Din el, Django construiește tabelul (lecția 51), interogările (lecția 52), panoul de administrare (lecția 54) și formularele (lecția 56). Îl scrii o singură dată, iar restul se sprijină pe el.

## Cum funcționează

### Modelul, rând cu rând

Modelele unei aplicații stau în `models.py`, pe care `startapp` l-a creat gol la lecția 45. Ce înseamnă fiecare parte din `Articol`:

- `class Articol(models.Model):` — modelul e o clasă **derivată** din `models.Model` (moștenire, lecția 34). De la `models.Model` primește tot ce știe să facă: salvarea, ștergerea, căutarea. Numele modelului e la singular, cu literă mare, ca orice clasă;
- `titlu = models.CharField(max_length=200)` — un **câmp** de tip text scurt, cu cel mult 200 de caractere. `max_length` e obligatoriu: fără el, verificarea Django dă eroare (doar pe PostgreSQL e opțional), iar o limită rezonabilă e oricum o regulă bună pentru titluri și nume;
- `continut = models.TextField()` — text de orice lungime, pentru corpul articolului;
- `data_publicarii = models.DateField(default=date.today)` — o dată calendaristică. Dacă nu o dai la creare, Django apelează `date.today()` și pune data zilei. Observă că scriem `date.today` **fără paranteze**: dăm funcția însăși (lecția 21), ca Django s-o apeleze la fiecare articol nou;
- `class Meta:` — o clasă în interiorul clasei, cu opțiuni pentru tot modelul: `ordering` (ordinea implicită: cele mai noi primele, de aceea `-` în față) și numele pe care le folosește Django în pagini, la singular și la plural;
- `__str__` — metoda specială din lecția 35. Spune cum se afișează un articol ca text, de exemplu în shell sau în panoul de admin.

Seamănă mult cu o dataclass (lecția 36): declari câmpurile la nivelul clasei, cu tipul lor, iar Django scrie în locul tău `__init__` și restul. Diferența e că un model știe să se salveze în baza de date.

Un câmp pe care nu l-am scris: `id`. Django adaugă automat fiecărui model un număr unic, crescător, numit **cheie primară** (în engleză „primary key”). Primul articol salvat primește `id` 1, al doilea 2 și așa mai departe. E exact numărul din adresa `/articol/2/`.

### Tipuri de câmpuri și opțiuni

Cele mai folosite câmpuri:

| Câmp | Ce păstrează | Exemplu |
|---|---|---|
| `CharField(max_length=...)` | text scurt, cu lungime maximă | titlu, nume, oraș |
| `TextField()` | text lung | conținutul unui articol |
| `IntegerField()` | număr întreg | vârstă, stoc |
| `DecimalField(max_digits=..., decimal_places=...)` | număr zecimal exact | preț (lecția 3: banii nu se țin în `float`) |
| `BooleanField()` | `True` / `False` | publicat sau nu |
| `DateField()`, `DateTimeField()` | dată, dată cu oră | data publicării |
| `EmailField()` | text verificat ca e-mail | adresa unui abonat |

Câmpurile prin care un model trimite la alt model (de exemplu, comentariul la articolul lui) vin la lecția 53.

Opțiuni pe care le primește aproape orice câmp:
- `default=...` — valoarea folosită când nu dai una;
- `null=True` — în baza de date, câmpul poate rămâne gol (`NULL`, echivalentul lui `None`);
- `blank=True` — în formulare (lecțiile 54–56), câmpul poate fi lăsat necompletat;
- `unique=True` — două rânduri nu pot avea aceeași valoare.

`null` privește baza de date, iar `blank` privește formularele. La câmpurile de text, convenția Django e să nu folosești `null=True`: un text lipsă se păstrează ca `""`.

### De la clasă la tabel: makemigrations și migrate

Clasa singură nu creează nimic în baza de date. Mai sunt doi pași, pe care îi faci după fiecare schimbare a modelelor:

<!-- ruleaza -->
```bash
python manage.py makemigrations
```

```text
Migrations for 'articole':
  articole/migrations/0001_initial.py
    + Create model Articol
```

`makemigrations` compară modelele cu ce știe deja despre ele și scrie o **migrare**: un fișier Python care descrie schimbarea („creează modelul Articol”). Uită-te la el: e cod obișnuit, generat de Django.

<!-- ruleaza -->
```bash
tail -n +3 articole/migrations/0001_initial.py
```

```text
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Articol",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("titlu", models.CharField(max_length=200)),
                ("continut", models.TextField()),
                ("data_publicarii", models.DateField(default=datetime.date.today)),
            ],
            options={
                "verbose_name": "articol",
                "verbose_name_plural": "articole",
                "ordering": ["-data_publicarii"],
            },
        ),
    ]
```

(`tail -n +3` afișează fișierul de la al treilea rând: primul rând conține data și ora la care ai rulat comanda.) Se vede și câmpul `id`, adăugat automat.

Apoi `migrate` aplică migrarea: creează efectiv tabelul în baza de date.

<!-- ruleaza -->
```bash
python manage.py migrate
```

```text
Operations to perform:
  Apply all migrations: admin, articole, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying articole.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
```

Fiind primul `migrate` al proiectului, Django creează și tabelele aplicațiilor incluse de la început în `INSTALLED_APPS` (utilizatori, sesiuni, admin). Baza de date e fișierul `db.sqlite3` din rădăcina proiectului, setat în `DATABASES` (lecția 46). **SQLite** e o bază de date care stă într-un singur fișier, perfectă pentru început; la lecția 61 vei vedea ce se schimbă în producție. Despre migrări în detaliu, la lecția 51.

### Lucrul cu modelul în shell

Ca să încerci modelul fără să scrii view-uri, Django are un **shell**: consola interactivă Python (cea cu `>>>`), dar cu proiectul tău deja încărcat. Îl pornești în terminal cu `python manage.py shell`, apoi scrii rândurile după `>>>` unul câte unul, cu Enter după fiecare. Ieși cu `exit()` (în terminalul PyTutor merge și butonul **Oprește**).

În transcrierile din lecții, tu scrii doar ce apare după `>>>` și `...`; restul e răspunsul shell-ului. Ultimul rând, „now exiting InteractiveConsole...”, apare când ieși din shell.

Hai să mutăm cele trei articole din lista `ARTICOLE` în baza de date:

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'from articole.views import ARTICOLE' 'Articol.objects.count()' 'for a in ARTICOLE:' '    Articol.objects.create(id=a["id"], titlu=a["titlu"], continut=a["continut"], data_publicarii=a["data_publicarii"])' '' 'Articol.objects.count()' 'Articol.objects.all()'; } | PYTHONPATH=/h python manage.py shell -->
```text
7 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol
>>> from articole.views import ARTICOLE
>>> Articol.objects.count()
0
>>> for a in ARTICOLE:
...     Articol.objects.create(id=a["id"], titlu=a["titlu"], continut=a["continut"], data_publicarii=a["data_publicarii"])
... 
<Articol: O plimbare prin Cluj>
<Articol: De ce am ales Django>
<Articol: Primul meu program în Python>
>>> Articol.objects.count()
3
>>> Articol.objects.all()
<QuerySet [<Articol: O plimbare prin Cluj>, <Articol: De ce am ales Django>, <Articol: Primul meu program în Python>]>
>>> 
now exiting InteractiveConsole...
```

Ce s-a întâmplat:
- primele rânduri le scrie shell-ul la pornire. „7 objects imported automatically” înseamnă că Django a importat deja automat modelele tuturor aplicațiilor (`Articol`, plus `User` și alte modele ale lui Django); noi am scris totuși importul, ca să fie clar de unde vine `Articol`;
- `Articol.objects` e **managerul** modelului: punctul de pornire pentru tot ce citești sau scrii în tabel. Îl vei folosi din plin la lecția 52;
- `create(...)` construiește obiectul și îl salvează imediat. Am dat explicit `id`-ul din listă, ca adresele `/articol/1/`, `/articol/2/` și `/articol/3/` să rămână aceleași;
- după `for`, rândul gol (`...` urmat de Enter) îi spune consolei că blocul s-a terminat;
- `<Articol: O plimbare prin Cluj>` e textul dat de `__str__`; fără el, ai vedea doar `Articol object (3)`.

Același lucru, pas cu pas: construiești obiectul ca pe orice obiect Python (lecția 32), apoi îl salvezi cu `save()`.

<!-- comanda: { sleep 8; printf '%s\n' 'from datetime import date' 'from articole.models import Articol' 'nou = Articol(titlu="Ciorna mea", continut="Încă scriu la el.")' 'nou.id' 'nou.save()' 'nou.id' 'nou.data_publicarii == date.today()' 'nou.delete()' 'Articol.objects.count()'; } | PYTHONPATH=/h python manage.py shell -->
```text
7 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from datetime import date
>>> from articole.models import Articol
>>> nou = Articol(titlu="Ciorna mea", continut="Încă scriu la el.")
>>> nou.id
>>> nou.save()
>>> nou.id
4
>>> nou.data_publicarii == date.today()
True
>>> nou.delete()
(1, {'articole.Articol': 1})
>>> Articol.objects.count()
3
>>> 
now exiting InteractiveConsole...
```

Înainte de `save()`, obiectul există doar în memorie, iar `id`-ul lui e `None` (consola nu afișează nimic pentru `None`). După `save()`, are rândul lui în tabel și un `id`. Data publicării a fost completată automat cu data de azi, datorită lui `default=date.today`. `delete()` șterge rândul și spune câte rânduri a șters.

View-urile citesc încă din lista `ARTICOLE`, deci paginile blogului arată la fel. Le vom muta pe baza de date la lecția 52.

### Ce se întâmplă „pe dedesubt”: SQL-ul generat

Bazele de date relaționale înțeleg **SQL**. Poți vedea ce SQL a scris Django pentru migrarea noastră:

<!-- ruleaza -->
```bash
python manage.py sqlmigrate articole 0001
```

```text
BEGIN;
--
-- Create model Articol
--
CREATE TABLE "articole_articol" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "titlu" varchar(200) NOT NULL, "continut" text NOT NULL, "data_publicarii" date NOT NULL);
COMMIT;
```

Tabelul se numește `articole_articol`: numele aplicației, `_` și numele modelului cu litere mici. `CharField(max_length=200)` a devenit `varchar(200)`, iar `NOT NULL` înseamnă că nicio coloană nu poate rămâne goală (n-am pus `null=True`). Valoarea implicită `date.today` nu apare în SQL: o pune Python, la crearea obiectului, nu baza de date.

La fel, când scrii `Articol.objects.count()`, Django trimite bazei de date `SELECT COUNT(*) FROM "articole_articol"`. Nu trebuie să știi SQL ca să folosești Django, dar e bine să știi că există.

## Exemplu complet

Modelul complet al lecției e cel de la început, în `articole/models.py`. Iată ce poți face cu el, într-o singură sesiune de shell: cauți după `id`, citești câmpurile și vezi ordinea dată de `Meta.ordering`.

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'a = Articol.objects.get(id=2)' 'a' 'a.titlu' 'a.data_publicarii' 'print(a.continut)' 'for articol in Articol.objects.all():' '    print(articol.id, articol.data_publicarii, articol)' '' 'Articol._meta.verbose_name_plural'; } | PYTHONPATH=/h python manage.py shell -->
```text
7 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol
>>> a = Articol.objects.get(id=2)
>>> a
<Articol: De ce am ales Django>
>>> a.titlu
'De ce am ales Django'
>>> a.data_publicarii
datetime.date(2026, 10, 2)
>>> print(a.continut)
După primele luni cu Python, voiam să fac un site adevărat: cu pagini, cu bază de date și cu un loc unde să mă autentific.

Django are toate acestea „din cutie”, iar documentația lui e excelentă.
>>> for articol in Articol.objects.all():
...     print(articol.id, articol.data_publicarii, articol)
... 
3 2026-10-20 O plimbare prin Cluj
2 2026-10-02 De ce am ales Django
1 2026-09-14 Primul meu program în Python
>>> Articol._meta.verbose_name_plural
'articole'
>>> 
now exiting InteractiveConsole...
```

Observă:
- `get(id=2)` aduce exact un articol, după cheia primară; despre `get` și surorile lui, la lecția 52;
- câmpurile sunt atribute obișnuite: `a.titlu` e un `str`, `a.data_publicarii` e un `date` (lecția 31);
- articolele vin de la cel mai nou la cel mai vechi, deși nu am cerut nicio ordine: așa spune `ordering = ["-data_publicarii"]`;
- `_meta` păstrează opțiunile din `class Meta`; îl folosește Django intern, de exemplu în panoul de admin (lecția 54).

## Greșeli frecvente

### 1. Folosirea modelului înainte de migrate

Ai scris modelul, dar ai uitat `makemigrations` și `migrate`. Tabelul nu există încă:

<!-- comanda: rm -rf /tmp/p && cp -r . /tmp/p && cd /tmp/p && rm -f db.sqlite3 && rm -f articole/migrations/0001_initial.py && python manage.py shell -v 0 -c "from articole.models import Articol; print(Articol.objects.count())" -->
```text
Traceback (most recent call last):
sqlite3.OperationalError: no such table: articole_articol

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
django.db.utils.OperationalError: no such table: articole_articol
```

(Am păstrat doar rândurile importante: în realitate, tracebackul are câteva zeci de rânduri din interiorul Django.) Sunt două erori legate: SQLite raportează problema, iar Django o „împachetează” în eroarea lui, cu același mesaj. „No such table” înseamnă exact ce spune: în baza de date nu există tabelul `articole_articol`. Rulează `python manage.py makemigrations`, apoi `python manage.py migrate`. Același mesaj îl vei vedea și în browser, pe pagina galbenă de eroare a Django, dacă un view folosește modelul.

### 2. Tipul câmpului scris greșit

<!-- nu-rula -->
```python
titlu = models.CharFiled(max_length=200)
```

<!-- comanda: rm -rf /tmp/p && cp -r . /tmp/p && cd /tmp/p && sed -i 's/models.CharField(max_length=200)/models.CharFiled(max_length=200)/' articole/models.py && python manage.py makemigrations -->
```text
Traceback (most recent call last):
  File "/tmp/p/articole/models.py", line 7, in Articol
    titlu = models.CharFiled(max_length=200)
            ^^^^^^^^^^^^^^^^
AttributeError: module 'django.db.models' has no attribute 'CharFiled'. Did you mean: 'CharField'?
```

(Am scurtat tracebackul; în proiectul tău calea începe cu `/work/blog/` în loc de `/tmp/p/`.) Orice comandă `manage.py` încarcă întâi modelele, deci o greșeală de scriere în `models.py` oprește tot, chiar și `runserver`. Citește ultimul rând (lecția 23): Python îți sugerează chiar numele corect.

### 3. date.today() cu paranteze

<!-- nu-rula -->
```python
data_publicarii = models.DateField(default=date.today())
```

<!-- comanda: rm -rf /tmp/p && cp -r . /tmp/p && cd /tmp/p && sed -i 's/default=date.today)/default=date.today())/' articole/models.py && python manage.py check -->
```text
System check identified some issues:

WARNINGS:
articole.Articol.data_publicarii: (fields.W161) Fixed default value provided.
	HINT: It seems you set a fixed date / time / datetime value as default for this field. This may not be what you want. If you want to have the current date as default, use `django.utils.timezone.now`

System check identified 1 issue (0 silenced).
```

Înainte de majoritatea comenzilor (`runserver`, `migrate`, `makemigrations`), Django face o **verificare a sistemului** (în engleză „system check”); `python manage.py check` o rulează singură. Aici a găsit o problemă: cu paranteze, `date.today()` se calculează **o singură dată**, când pornește programul, iar toate articolele ar primi aceeași dată. Fără paranteze, dai funcția, iar Django o apelează la fiecare articol nou. Django te avertizează („Fixed default value provided”), dar nu te oprește: e un avertisment (`WARNINGS`), nu o eroare.

### 4. Model fără __str__

<!-- comanda: rm -rf /tmp/p && cp -r . /tmp/p && cd /tmp/p && sed -i '/def __str__/,+1d' articole/models.py && python manage.py shell -v 0 -c "from articole.models import Articol; print(Articol.objects.all())" -->
```text
<QuerySet [<Articol: Articol object (3)>, <Articol: Articol object (2)>, <Articol: Articol object (1)>]>
```

Totul funcționează, dar articolele se văd doar ca „Articol object (3)”, în shell, în mesajele de eroare și în panoul de admin. Scrie mereu un `__str__` care întoarce ceva ce recunoaște un om (titlul, numele).

### 5. Câmp nou fără valoare pentru rândurile existente

Adaugi la `Articol` un câmp obligatoriu, de exemplu `autor = models.CharField(max_length=80)`, după ce tabelul are deja articole. Ce valoare să primească articolele vechi în coloana nouă?

<!-- comanda: rm -rf /tmp/p && cp -r . /tmp/p && cd /tmp/p && sed -i 's/    continut = models.TextField()/    continut = models.TextField()\n    autor = models.CharField(max_length=80)/' articole/models.py && python manage.py makemigrations --noinput -->
```text
Field 'autor' on model 'articol' not migrated: it is impossible to add a non-nullable field without specifying a default.
```

Aici am rulat comanda fără întrebări (`--noinput`), iar Django a refuzat să adauge câmpul. Rulată normal, în terminal, comanda îți oferă un meniu din care alegi o valoare pentru rândurile vechi. Rezolvarea curată e o valoare implicită (`default="Ana Popescu"`) sau un câmp care poate rămâne gol. Despre migrările care modifică un tabel existent, la lecția 51.

## Exercițiu

Lucrezi în proiectul PyTutor `blog`, cel început la lecția 45. Dacă n-ai făcut-o încă, scrie modelul `Articol` din lecție în `articole/models.py` și rulează `makemigrations` și `migrate`.

1. Pornește `python manage.py shell` și mută cele trei articole din `ARTICOLE` în baza de date, ca în lecție (păstrează `id`-urile), dacă n-ai făcut-o deja cât ai citit lecția; verifică la final cu `Articol.objects.count()`.
2. Creează un al patrulea articol, al tău, cu `Articol(...)` și `save()`, fără să dai data. Afișează-i `id`-ul și data publicării.
3. Afișează toate articolele cu un `for`, pe câte un rând: data, apoi titlul. Ce articol apare primul și de ce?
4. Încearcă `Articol.objects.get(id=99)` și citește eroarea (o vei înțelege la lecția 52).
5. Șterge articolul tău cu `delete()`, ca baza de date să rămână cu cele trei articole ale Anei. Nu modifica modelul: lecția 51 pornește exact de la el.

## Pe scurt

- Un model e o clasă derivată din `models.Model`; fiecare atribut de tip câmp devine o coloană, fiecare obiect un rând dintr-un tabel.
- Câmpuri uzuale: `CharField(max_length=...)`, `TextField`, `IntegerField`, `DecimalField`, `BooleanField`, `DateField`; opțiuni: `default`, `null`, `blank`, `unique`.
- `id`-ul (cheia primară) e adăugat automat; `class Meta` dă ordinea implicită și numele modelului, iar `__str__` felul în care se afișează.
- După orice schimbare a modelelor: `python manage.py makemigrations`, apoi `python manage.py migrate`.
- `python manage.py shell` deschide consola Python cu proiectul încărcat: `Articol.objects.create(...)`, `obiect.save()`, `obiect.delete()`, `Articol.objects.all()`.
- „No such table” înseamnă migrări neaplicate; `default=date.today` se scrie fără paranteze.
