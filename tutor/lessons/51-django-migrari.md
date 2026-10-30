<!-- proiect: _blog/50 -->
<!-- proiect-final: _blog/51 -->
<!-- pregatire: python manage.py migrate -v 0 && python manage.py loaddata /lectii/_blog/date/50.json -v 0 -->
## Ce este

O **migrare** este un fișier Python care descrie o schimbare a structurii bazei de date: „creează tabelul articolelor”, „adaugă coloana `publicat`”, „șterge coloana `rezumat`”. Migrările stau în folderul `migrations/` al fiecărei aplicații și sunt numerotate în ordine: `0001_initial.py`, `0002_articol_publicat.py` și așa mai departe.

Ai folosit deja două comenzi la lecția 50:
- `python manage.py makemigrations` **scrie** migrări noi, comparând modelele cu migrările existente;
- `python manage.py migrate` **aplică** migrările care nu au fost încă aplicate pe baza de date.

În lecția asta, Ana vrea să poată ține un articol ca ciornă, nepublicat. Pentru asta, modelul `Articol` primește un câmp nou, `publicat`, iar tabelul existent, cu cele trei articole, trebuie modificat fără să se piardă nimic.

## De ce contează

Modelele se schimbă tot timpul cât construiești o aplicație: un câmp nou, unul redenumit, o lungime mărită. Baza de date are însă deja date reale, pe care nu le poți șterge și reface de fiecare dată. Migrările rezolvă problema: fiecare schimbare devine un pas mic, numerotat, care se poate aplica (și, de obicei, anula) la fel pe calculatorul tău, al colegilor și pe serverul de producție (lecția 61).

Fișierele de migrare fac parte din cod: le salvezi în git (lecția 42) împreună cu modelele. Așa, oricine primește proiectul rulează `migrate` și ajunge la aceeași structură a bazei de date.

## Cum funcționează

### Istoricul migrărilor: showmigrations

`showmigrations` arată toate migrările proiectului și care dintre ele sunt aplicate (`[X]`):

<!-- ruleaza -->
```bash
python manage.py showmigrations
```

```text
admin
 [X] 0001_initial
 [X] 0002_logentry_remove_auto_add
 [X] 0003_logentry_add_action_flag_choices
articole
 [X] 0001_initial
auth
 [X] 0001_initial
 [X] 0002_alter_permission_name_max_length
 [X] 0003_alter_user_email_max_length
 [X] 0004_alter_user_username_opts
 [X] 0005_alter_user_last_login_null
 [X] 0006_require_contenttypes_0002
 [X] 0007_alter_validators_add_error_messages
 [X] 0008_alter_user_username_max_length
 [X] 0009_alter_user_last_name_max_length
 [X] 0010_alter_group_name_max_length
 [X] 0011_update_proxy_permissions
 [X] 0012_alter_user_first_name_max_length
contenttypes
 [X] 0001_initial
 [X] 0002_remove_content_type_name
sessions
 [X] 0001_initial
```

Aplicația noastră, `articole`, are o singură migrare, cea de la lecția 50. Restul aparțin aplicațiilor incluse în Django. Cum știe Django ce s-a aplicat? Ține evidența într-un tabel special din baza de date, `django_migrations`, unde fiecare migrare aplicată are un rând.

### Pasul 1: schimbi modelul

Câmpul nou, cu valoarea implicită `True`, ca toate articolele existente să rămână publicate:

<!-- fisier: articole/models.py -->
```python
from datetime import date

from django.db import models


class Articol(models.Model):
    titlu = models.CharField(max_length=200)
    continut = models.TextField()
    data_publicarii = models.DateField(default=date.today)
    publicat = models.BooleanField(default=True)

    class Meta:
        ordering = ["-data_publicarii"]
        verbose_name = "articol"
        verbose_name_plural = "articole"

    def __str__(self):
        return self.titlu
```

Deocamdată s-a schimbat doar codul Python. Baza de date nu știe nimic de coloana `publicat`.

### Pasul 2: makemigrations

Înainte să scrie ceva, poți întreba Django dacă are de scris o migrare. `--dry-run` doar arată, fără să creeze fișierul:

<!-- ruleaza -->
```bash
python manage.py makemigrations --dry-run
```

```text
Migrations for 'articole':
  articole/migrations/0002_articol_publicat.py
    + Add field publicat to articol
```

Apoi o scrii de-adevăratelea:

<!-- ruleaza -->
```bash
python manage.py makemigrations
```

```text
Migrations for 'articole':
  articole/migrations/0002_articol_publicat.py
    + Add field publicat to articol
```

Fișierul nou (fără primul rând, cu data generării):

<!-- ruleaza -->
```bash
tail -n +3 articole/migrations/0002_articol_publicat.py
```

```text
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articole", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="articol",
            name="publicat",
            field=models.BooleanField(default=True),
        ),
    ]
```

Două părți:
- `dependencies` spune că migrarea vine **după** `0001_initial` din aplicația `articole`. Așa se formează un lanț, iar Django aplică migrările în ordinea corectă;
- `operations` e lista schimbărilor: aici, una singură, `AddField` („adaugă câmpul”).

Numele `0002_articol_publicat` l-a ales Django din ce conține migrarea. Poți da tu un nume, cu `makemigrations --name`, dar numele automate sunt de obicei bune.

### Pasul 3: migrate

<!-- ruleaza -->
```bash
python manage.py migrate
```

```text
Operations to perform:
  Apply all migrations: admin, articole, auth, contenttypes, sessions
Running migrations:
  Applying articole.0002_articol_publicat... OK
```

Django a aplicat doar migrarea care lipsea. Articolele existente au primit `publicat = True`, valoarea implicită:

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'for a in Articol.objects.all():' '    print(a.id, a.publicat, a)' ''; } | PYTHONPATH=/h python manage.py shell -->
```text
7 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol
>>> for a in Articol.objects.all():
...     print(a.id, a.publicat, a)
... 
3 True O plimbare prin Cluj
2 True De ce am ales Django
1 True Primul meu program în Python
>>> 
now exiting InteractiveConsole...
```

### Înapoi în timp: migrate la o migrare anterioară

Dacă dai `migrate` numele aplicației și al unei migrări, Django aduce baza de date exact în acel punct. Migrările de după sunt **anulate** (în engleză „unapplied”):

<!-- ruleaza -->
```bash
python manage.py migrate articole 0001
python manage.py showmigrations articole
```

```text
Operations to perform:
  Target specific migration: 0001_initial, from articole
Running migrations:
  Rendering model states... DONE
  Unapplying articole.0002_articol_publicat... OK
articole
 [X] 0001_initial
 [ ] 0002_articol_publicat
```

Coloana `publicat` a dispărut din tabel, dar fișierul migrării a rămas. Un `migrate` simplu o aplică din nou:

<!-- ruleaza -->
```bash
python manage.py migrate articole
python manage.py showmigrations articole
```

```text
Operations to perform:
  Apply all migrations: articole
Running migrations:
  Applying articole.0002_articol_publicat... OK
articole
 [X] 0001_initial
 [X] 0002_articol_publicat
```

Atenție: anularea lui `AddField` șterge coloana, cu tot cu valorile din ea. Pe date reale, gândește-te de două ori înainte să mergi înapoi.

### Ce se întâmplă „pe dedesubt”: SQL-ul unei migrări

`sqlmigrate` arată SQL-ul pe care l-ar trimite o migrare, fără să-l execute:

<!-- ruleaza -->
```bash
python manage.py sqlmigrate articole 0002
```

```text
BEGIN;
--
-- Add field publicat to articol
--
CREATE TABLE "new__articole_articol" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "publicat" bool NOT NULL, "titlu" varchar(200) NOT NULL, "continut" text NOT NULL, "data_publicarii" date NOT NULL);
INSERT INTO "new__articole_articol" ("id", "titlu", "continut", "data_publicarii", "publicat") SELECT "id", "titlu", "continut", "data_publicarii", 1 FROM "articole_articol";
DROP TABLE "articole_articol";
ALTER TABLE "new__articole_articol" RENAME TO "articole_articol";
COMMIT;
```

Surprinzător de mult pentru o coloană! SQLite știe să facă doar puține schimbări într-un tabel existent, așa că Django face „ocolul” sigur:
1. creează un tabel nou, `new__articole_articol`, cu structura dorită;
2. copiază toate rândurile din cel vechi, punând `1` (adică `True`) în coloana nouă;
3. șterge tabelul vechi și îl redenumește pe cel nou.

`BEGIN` și `COMMIT` înseamnă că toți pașii formează o **tranzacție**: ori reușesc toți, ori, la o eroare, nu se aplică niciunul. Pe alte baze de date (PostgreSQL, în producție) aceeași migrare devine un simplu `ALTER TABLE ... ADD COLUMN`. Tu scrii aceeași migrare Python; Django alege SQL-ul potrivit.

## Exemplu complet

Întregul drum al unei schimbări de model, cu verificările pe care le face un programator atent. Modelul are deja câmpul `publicat`, iar migrarea e aplicată:

<!-- ruleaza -->
```bash
python manage.py makemigrations --check
python manage.py showmigrations articole
python manage.py migrate
```

```text
No changes detected
articole
 [X] 0001_initial
 [X] 0002_articol_publicat
Operations to perform:
  Apply all migrations: admin, articole, auth, contenttypes, sessions
Running migrations:
  No migrations to apply.
```

- `makemigrations --check` răspunde „No changes detected”: modelele și migrările spun același lucru. Dacă ar lipsi o migrare, comanda ar afișa ce lipsește și ar ieși cu cod de eroare, fără să scrie fișierul. De aceea e folosită des în verificările automate, rulate alături de teste (lecția 41), și înainte de publicare;
- `showmigrations` confirmă că ambele migrări sunt aplicate;
- `migrate` nu mai are nimic de făcut.

Și noul câmp, folosit: Ana ascunde temporar un articol, apoi îl publică din nou.

<!-- comanda: { sleep 8; printf '%s\n' 'from articole.models import Articol' 'a = Articol.objects.get(id=3)' 'a.publicat = False' 'a.save()' 'Articol.objects.get(id=3).publicat' 'a.publicat = True' 'a.save()'; } | PYTHONPATH=/h python manage.py shell -->
```text
7 objects imported automatically (use -v 2 for details).

Python 3.12.16 (main, Oct 28 2026, 02:01:20) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from articole.models import Articol
>>> a = Articol.objects.get(id=3)
>>> a.publicat = False
>>> a.save()
>>> Articol.objects.get(id=3).publicat
False
>>> a.publicat = True
>>> a.save()
>>> 
now exiting InteractiveConsole...
```

Pentru a modifica un rând: îl citești, schimbi atributul și apelezi `save()`. Al doilea `get` citește din nou din baza de date și confirmă că schimbarea a fost salvată. La lecția 52, pagina blogului va afișa doar articolele cu `publicat=True`.

## Greșeli frecvente

### 1. Ai schimbat modelul, dar ai uitat makemigrations

Pornim de la modelul fără `publicat`, adăugăm câmpul și rulăm direct `migrate`:

<!-- comanda: rm -rf /tmp/p && cp -r . /tmp/p && cd /tmp/p && python manage.py migrate articole 0001 -v 0 && rm articole/migrations/0002_articol_publicat.py && python manage.py migrate -->
```text
Operations to perform:
  Apply all migrations: admin, articole, auth, contenttypes, sessions
Running migrations:
  No migrations to apply.
  Your models in app(s): 'articole' have changes that are not yet reflected in a migration, and so won't be applied.
  Run 'manage.py makemigrations' to make new migrations, and then re-run 'manage.py migrate' to apply them.
```

`migrate` aplică doar migrări existente; nu se uită direct la modele. Mesajul îți spune exact ce ai de făcut: `makemigrations`, apoi din nou `migrate`.

### 2. Ai făcut migrarea, dar ai uitat migrate

Fișierul `0002_articol_publicat.py` există, dar n-a fost aplicat. Codul crede că există coloana `publicat`; baza de date, nu:

<!-- comanda: rm -rf /tmp/p && cp -r . /tmp/p && cd /tmp/p && python manage.py migrate articole 0001 -v 0 && python manage.py shell -v 0 -c "from articole.models import Articol; print(Articol.objects.first())" -->
```text
Traceback (most recent call last):
django.db.utils.OperationalError: no such column: articole_articol.publicat
```

(Tracebackul e scurtat.) „No such column” e semnul clasic al unei migrări neaplicate. Și `runserver` te avertizează la pornire, cu un mesaj de forma „You have 1 unapplied migration(s)”; nu-l ignora. Soluția: `python manage.py migrate`.

### 3. Ștergerea sau editarea „de mână” a migrărilor aplicate

O migrare aplicată e trecută în tabelul `django_migrations`. Dacă îi ștergi fișierul sau îi schimbi conținutul, codul și baza de date nu mai spun aceeași poveste, iar următoarele `makemigrations` și `migrate` vor face lucruri ciudate. Regula: **nu modifica și nu șterge migrări care au fost deja aplicate** (mai ales dacă le-au primit și alții, prin git). Dacă ai greșit ceva într-un model, schimbi modelul și faci o **migrare nouă**, care corectează.

Singura excepție rezonabilă: o migrare pe care tocmai ai creat-o, încă neaplicată și netrimisă nimănui. Pe aceea o poți șterge și o poți genera din nou.

### 4. Redenumirea unui câmp

Dacă redenumești `continut` în `text`, Django vede două schimbări: un câmp a dispărut și unul nou a apărut. La `makemigrations`, te întreabă în terminal dacă e o redenumire: `Was articol.continut renamed to articol.text (a TextField)? [y/N]`. Răspunde `y`: migrarea va fi `RenameField`, iar datele rămân. Dacă răspunzi `n`, migrarea ar șterge coloana veche, cu tot conținutul articolelor, și ar crea una goală. Citește mereu întrebările și rezumatul pe care le afișează `makemigrations`.

### 5. Două migrări cu același număr

Lucrezi cu un coleg pe ramuri diferite (lecția 42): fiecare adaugă alt câmp și face `0003_...`. După `merge`, aplicația are două migrări care depind amândouă de `0002`, iar `migrate` refuză să continue, cu mesajul „Conflicting migrations detected”. Rezolvarea e `python manage.py makemigrations --merge`, care creează o migrare ce le leagă pe amândouă. Mai simplu: înainte să faci o migrare nouă, adu-ți întâi ultimele schimbări ale colegilor.

## Exercițiu

Lucrezi în proiectul PyTutor `blog`.

1. Rulează `python manage.py showmigrations articole` și notează ce migrări ai.
2. Dacă n-ai făcut-o deja cât ai citit lecția, adaugă în `Articol` câmpul `publicat = models.BooleanField(default=True)`, exact ca în lecție, și rulează `makemigrations --dry-run`, apoi `makemigrations`. Deschide în editor fișierul migrării noi (`0002_articol_publicat.py`). Ce operație conține?
3. Rulează `python manage.py sqlmigrate articole 0002` și explică, cu cuvintele tale, cei patru pași ai SQL-ului.
4. Aplică migrarea, apoi, în `python manage.py shell`, ascunde articolul „O plimbare prin Cluj” (`publicat = False`) și verifică printr-un al doilea `get` că s-a salvat.
5. Anulează migrarea (`migrate articole 0001`), verifică cu `showmigrations`, apoi aplic-o din nou. Ce valoare are acum `publicat` la articolul pe care l-ai ascuns la pasul 4? De ce?

La final, `makemigrations --check` trebuie să răspundă „No changes detected”: lecția 52 pornește de la modelul cu `publicat`.

## Pe scurt

- O migrare e un fișier Python numerotat care descrie o schimbare a structurii bazei de date; migrările unei aplicații formează un lanț prin `dependencies`.
- `makemigrations` scrie migrări din schimbările modelelor; `migrate` le aplică; `showmigrations` arată ce e aplicat (`[X]`).
- `migrate aplicatie 0001` anulează migrările de după `0001`; atenție, anularea poate șterge date.
- `sqlmigrate` arată SQL-ul unei migrări; `makemigrations --check` verifică dacă lipsește vreo migrare.
- „No such column” sau „unapplied migration(s)” înseamnă că ai uitat `migrate`; „changes that are not yet reflected in a migration” înseamnă că ai uitat `makemigrations`.
- Nu edita și nu șterge migrări deja aplicate: corectezi printr-o migrare nouă.
