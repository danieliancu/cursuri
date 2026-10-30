<!-- proiect: _blog/58 -->
<!-- proiect-final: _blog/59 -->
<!-- pregatire: python manage.py migrate -v 0 && python manage.py loaddata /lectii/_blog/date/57.json -v 0 -->
## Ce este

**Testarea în Django** înseamnă exact ce ai făcut la lecția 41, aplicat pe un site: scrii cod care verifică automat că restul codului face ce trebuie. Django vine cu propriul sistem de testare, construit peste modulul **unittest**:

- testele stau în `articole/tests.py` (fișierul creat de `startapp` la lecția 45);
- fiecare grup de teste e o clasă derivată din **`django.test.TestCase`**, iar fiecare test e o metodă al cărei nume începe cu `test`;
- le rulezi cu `python manage.py test`.

Față de unittest-ul simplu, `TestCase` din Django îți mai dă două lucruri esențiale:

- o **bază de date de test**, separată de cea reală, golită după fiecare test;
- un **client de test** (`self.client`), un „browser” simulat care trimite cereri către view-urile tale și îți dă răspunsurile, fără server.

```python
from django.test import TestCase


class ListaTests(TestCase):
    def test_pagina_principala_merge(self):
        raspuns = self.client.get("/")
        self.assertEqual(raspuns.status_code, 200)
```

## De ce contează

Blogul Anei a crescut mult: modele, formulare, autentificare, iar la lecția 58 view-urile au fost rescrise complet, ca clase. De fiecare dată ai verificat de mână, în browser, că totul merge. Cu fiecare lecție, lista de lucruri de verificat crește: lista arată doar articolele publicate? O ciornă dă 404? Un comentariu gol e respins? Mihai poate edita articolele Anei?

Testele fac aceste verificări în câteva secunde, de fiecare dată când rulezi o comandă. Când schimbi ceva și strici din greșeală altă parte a site-ului, afli imediat, nu de la un cititor nemulțumit. De aceea, în proiectele reale, testele rulează automat înainte de fiecare publicare (lecția 61).

Tot ce scrii în lecția asta lucrează în proiectul PyTutor **`blog`**, cel în care construiești blogul din lecția 45.

## Cum funcționează

### Unde stau testele și cum le rulezi

La lecția 45, `startapp` a creat `articole/tests.py` cu un singur comentariu:

```python
from django.test import TestCase

# Create your tests here.
```

Poți rula testele chiar acum. Comanda găsește toate fișierele ale căror nume încep cu `test` din aplicațiile proiectului:

<!-- ruleaza -->
```bash
python manage.py test
```

```text
Found 0 test(s).
System check identified no issues (0 silenced).

----------------------------------------------------------------------
Ran 0 tests in 0.000s

NO TESTS RAN
```

„NO TESTS RAN”: deocamdată nu există niciun test.

### Primul test: modelul

Începem cu ce e mai simplu de testat: metodele modelului `Articol` (lecțiile 50 și 53).

<!-- fisier: articole/tests.py -->
```python
from datetime import date

from django.test import TestCase

from .models import Articol


class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.articol = Articol.objects.create(
            titlu="De ce am ales Django",
            continut="Django are toate acestea „din cutie”.",
            data_publicarii=date(2026, 10, 2),
        )

    def test_str_e_titlul(self):
        self.assertEqual(str(self.articol), "De ce am ales Django")

    def test_adresa_articolului(self):
        self.assertEqual(self.articol.get_absolute_url(), f"/articol/{self.articol.id}/")
```

<!-- ruleaza -->
```bash
python manage.py test
```

```text
Found 2 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..
----------------------------------------------------------------------
Ran 2 tests in 0.010s

OK
Destroying test database for alias 'default'...
```

Ce e nou față de lecția 41:

- **`setUpTestData`** e o metodă de clasă (`@classmethod`, lecția 33) care pregătește datele **o singură dată** pentru toate testele din clasă. Obiectele create acolo se păstrează ca atribute ale clasei (`cls.articol`) și le folosești în teste ca `self.articol`;
- fiecare punct din rândul `..` e un test reușit, ca la unittest;
- „Creating test database” și „Destroying test database”: Django creează o bază de date nouă, goală, doar pentru teste, și o șterge la final.

### Baza de date de test

Testele **nu ating** baza de date reală. Baza de test pornește goală, primește tabelele din migrări și conține doar ce creezi tu în teste. După fiecare test, Django anulează tot ce a scris testul, deci fiecare test pornește din aceeași stare.

Articolele Anei din baza reală sunt neatinse, oricâte teste ai rula:

<!-- ruleaza -->
```bash
python manage.py shell -v 0 -c "from articole.models import Articol; print(Articol.objects.count())"
```

```text
3
```

Consecința importantă: un test **nu vede** articolele tale reale. Tot ce îi trebuie își creează singur, în `setUpTestData` (sau în `setUp`, care rulează înaintea **fiecărui** test și e potrivit când un test modifică datele). Greșeala 2 de mai jos arată ce se întâmplă când uiți asta.

### Clientul de test: paginile

`self.client` trimite cereri ca un browser. Primești înapoi răspunsul view-ului: codul de status, conținutul HTML, redirecționările. Câteva metode de verificare, specifice Django:

| Metodă | Verifică |
|---|---|
| `assertContains(raspuns, text)` | statusul e 200 **și** textul apare în pagină |
| `assertNotContains(raspuns, text)` | textul **nu** apare în pagină |
| `assertRedirects(raspuns, adresa)` | răspunsul redirecționează (302) spre acea adresă, iar pagina de destinație răspunde cu 200 |
| `assertContains(raspuns, html, html=True)` | fragmentul apare, comparat ca HTML (spațiile și ordinea atributelor nu contează) |

Adresele nu se scriu de mână: `reverse("lista")` le construiește după numele din `urls.py` (lecția 47), la fel ca `{% url %}` în template-uri.

```python
from django.urls import reverse


class ListaTests(DateDeTest):
    def test_arata_doar_articolele_publicate(self):
        raspuns = self.client.get(reverse("lista"))
        self.assertEqual(raspuns.status_code, 200)
        self.assertContains(raspuns, "De ce am ales Django")
        self.assertNotContains(raspuns, "Ciornă")
```

`DateDeTest` e o clasă de bază cu datele comune (un articol publicat, o ciornă, doi utilizatori), din care moștenesc celelalte clase de teste (moștenirea, lecția 34). O vezi întreagă în exemplul complet.

### Utilizatori și formulare

Paginile protejate cu `LoginRequiredMixin` (lecția 58) se testează în două feluri: fără cont (trebuie să redirecționeze la login) și cu cont. **`self.client.force_login(utilizator)`** te autentifică direct, fără parolă și fără formularul de login:

```python
class EditareTests(DateDeTest):
    def test_alt_utilizator_primeste_403(self):
        self.client.force_login(self.mihai)
        raspuns = self.client.get(reverse("articol_editeaza", args=[self.articol.id]))
        self.assertEqual(raspuns.status_code, 403)
```

Formularele (lecțiile 55 și 56) se pot testa și fără cereri: creezi formularul cu date și verifici `is_valid()` și `errors`.

```python
formular = ArticolForm(data={"titlu": "TITLU", "continut": "Text.", "data_publicarii": "2026-10-29"})
print(formular.is_valid(), formular.errors["titlu"])
```

### Fixture-uri

Un **fixture** e un fișier (de obicei JSON) cu date gata făcute, pe care Django le poate încărca în baza de date. Îl obții din baza reală cu `dumpdata`:

<!-- ruleaza -->
```bash
python manage.py dumpdata articole.categorie --indent 2
```

```text
[
{
  "model": "articole.categorie",
  "pk": 1,
  "fields": {
    "nume": "Programare"
  }
},
{
  "model": "articole.categorie",
  "pk": 2,
  "fields": {
    "nume": "Călătorii"
  }
}
]
```

Salvat într-un fișier din `articole/fixtures/` (cu `-o articole/fixtures/categorii.json`; folderul `fixtures` trebuie să existe deja), îl poți încărca în teste cu atributul `fixtures`:

```python
class CategoriiTests(TestCase):
    fixtures = ["categorii.json"]

    def test_sunt_doua_categorii(self):
        self.assertEqual(Categorie.objects.count(), 2)
```

Fixture-urile sunt comode pentru multe date, dar greu de întreținut: la fiecare câmp nou din model trebuie actualizate, iar cine citește testul nu vede datele. În blog folosim `setUpTestData`, unde datele stau chiar lângă teste.

### Când un test pică

Să vedem un test care pică. Schimbăm intenționat rezultatul așteptat:

<!-- fisier: articole/tests.py -->
```python
from datetime import date

from django.test import TestCase

from .models import Articol


class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.articol = Articol.objects.create(
            titlu="De ce am ales Django",
            continut="Django are toate acestea „din cutie”.",
            data_publicarii=date(2026, 10, 2),
        )

    def test_str_e_titlul(self):
        self.assertEqual(str(self.articol), "De ce am ales Flask")

    def test_adresa_articolului(self):
        self.assertEqual(self.articol.get_absolute_url(), f"/articol/{self.articol.id}/")
```

<!-- ruleaza -->
```bash
python manage.py test
```

```text
Found 2 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.F
======================================================================
FAIL: test_str_e_titlul (articole.tests.ModelTests.test_str_e_titlul)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "articole/tests.py", line 18, in test_str_e_titlul
    self.assertEqual(str(self.articol), "De ce am ales Flask")
AssertionError: 'De ce am ales Django' != 'De ce am ales Flask'
- De ce am ales Django
?               ^^ ^^^
+ De ce am ales Flask
?               ^^ ^^


----------------------------------------------------------------------
Ran 2 tests in 0.010s

FAILED (failures=1)
Destroying test database for alias 'default'...
```

Raportul spune tot ce-ți trebuie: **ce** test a picat (`test_str_e_titlul` din clasa `ModelTests`), **unde** (rândul 18 din `articole/tests.py`) și **de ce** (valoarea primită, apoi cea așteptată; semnele `^` marchează literele diferite). `F` înseamnă un test picat; o eroare neașteptată (o excepție în test) apare ca `E`.

Repară testul, punând la loc titlul corect:

<!-- fisier: articole/tests.py -->
```python
from datetime import date

from django.test import TestCase

from .models import Articol


class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.articol = Articol.objects.create(
            titlu="De ce am ales Django",
            continut="Django are toate acestea „din cutie”.",
            data_publicarii=date(2026, 10, 2),
        )

    def test_str_e_titlul(self):
        self.assertEqual(str(self.articol), "De ce am ales Django")

    def test_adresa_articolului(self):
        self.assertEqual(self.articol.get_absolute_url(), f"/articol/{self.articol.id}/")
```

### Ce se întâmplă „pe dedesubt”: ce face `manage.py test`

Cu `-v 2` vezi pașii pe care Django îi face în plus față de unittest:

<!-- ruleaza -->
```bash
python manage.py test articole.tests.ModelTests -v 2
```

```text
Found 2 test(s).
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Operations to perform:
  Synchronize unmigrated apps: messages, staticfiles
  Apply all migrations: admin, articole, auth, contenttypes, sessions
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying articole.0001_initial... OK
  Applying articole.0002_articol_publicat... OK
  Applying articole.0003_categorie_eticheta_articol_categorie_comentariu_and_more... OK
  Applying articole.0004_articol_autor... OK
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
System check identified no issues (0 silenced).
test_adresa_articolului (articole.tests.ModelTests.test_adresa_articolului) ... ok
test_str_e_titlul (articole.tests.ModelTests.test_str_e_titlul) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.010s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
```

Cu `-v 2` vezi și numele fiecărui test, cu rezultatul lui. Pas cu pas, ce face Django:

1. Django creează baza de test. Cu SQLite, ea stă **în memorie** (`memorydb_default`), nu într-un fișier, deci e foarte rapidă;
2. aplică pe ea **toate migrările**, ca structura să fie identică cu baza reală;
3. pentru fiecare clasă, rulează `setUpTestData` într-o **tranzacție** (un grup de operații care poate fi anulat în bloc). Fiecare test rulează apoi în propria tranzacție, anulată la final, deci modificările unui test nu ajung la următorul;
4. la sfârșit, șterge baza de test.

În timpul testelor, `DEBUG` e oprit automat, iar adresa folosită de client e `testserver`, permisă automat în `ALLOWED_HOSTS`.

Dacă preferi pytest (lecția 41), pachetul `pytest-django` îl leagă de Django, iar testele scrise cu `TestCase` merg și acolo. În lecțiile noastre rămânem la `manage.py test`.

## Exemplu complet

Testele blogului: modelul, lista, pagina unui articol, comentariile, crearea și editarea articolelor, formularul. Înlocuiește tot conținutul fișierului `articole/tests.py` (inclusiv testul stricat de mai sus):

<!-- fisier: articole/tests.py -->
```python
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import ArticolForm
from .models import Articol, Categorie, Comentariu


class DateDeTest(TestCase):
    """Datele comune: create o singură dată pentru toată clasa, refăcute pentru fiecare test."""

    @classmethod
    def setUpTestData(cls):
        cls.ana = User.objects.create_user("ana", password="parola-ana-2026")
        cls.mihai = User.objects.create_user("mihai", password="parola-mihai-2026")
        programare = Categorie.objects.create(nume="Programare")
        cls.articol = Articol.objects.create(
            titlu="De ce am ales Django",
            continut="Django are toate acestea „din cutie”.",
            data_publicarii=date(2026, 10, 2),
            categorie=programare,
            autor=cls.ana,
        )
        cls.ciorna = Articol.objects.create(
            titlu="Ciornă", continut="Încă lucrez la el.", publicat=False
        )


class ModelTests(DateDeTest):
    def test_str_e_titlul(self):
        self.assertEqual(str(self.articol), "De ce am ales Django")

    def test_adresa_articolului(self):
        self.assertEqual(self.articol.get_absolute_url(), f"/articol/{self.articol.id}/")


class ListaTests(DateDeTest):
    def test_arata_doar_articolele_publicate(self):
        raspuns = self.client.get(reverse("lista"))
        self.assertEqual(raspuns.status_code, 200)
        self.assertContains(raspuns, "De ce am ales Django")
        self.assertNotContains(raspuns, "Ciornă")


class DetaliuTests(DateDeTest):
    def test_articol_existent(self):
        raspuns = self.client.get(self.articol.get_absolute_url())
        self.assertContains(raspuns, "<h1>De ce am ales Django</h1>", html=True)

    def test_articol_inexistent_da_404(self):
        raspuns = self.client.get("/articol/999/")
        self.assertEqual(raspuns.status_code, 404)

    def test_ciorna_nu_se_vede(self):
        raspuns = self.client.get(self.ciorna.get_absolute_url())
        self.assertEqual(raspuns.status_code, 404)


class ComentariuTests(DateDeTest):
    def test_comentariu_valid_e_salvat_si_redirectionat(self):
        adresa = reverse("comentariu", args=[self.articol.id])
        raspuns = self.client.post(adresa, {"autor": "Mihai", "text": "Foarte bun articol!"})
        self.assertRedirects(raspuns, self.articol.get_absolute_url() + "#comentarii")
        self.assertEqual(Comentariu.objects.get().text, "Foarte bun articol!")

    def test_comentariu_fara_text_nu_e_salvat(self):
        adresa = reverse("comentariu", args=[self.articol.id])
        raspuns = self.client.post(adresa, {"autor": "Mihai", "text": ""})
        self.assertEqual(raspuns.status_code, 200)
        self.assertFalse(Comentariu.objects.exists())


class ArticolNouTests(DateDeTest):
    def test_cere_autentificare(self):
        raspuns = self.client.get(reverse("articol_nou"))
        self.assertRedirects(raspuns, "/conturi/login/?next=/articol/nou/")

    def test_autorul_e_utilizatorul_logat(self):
        self.client.force_login(self.ana)
        date_formular = {
            "titlu": "Un articol nou",
            "continut": "Text.",
            "data_publicarii": "2026-10-29",
            "publicat": "on",
        }
        self.client.post(reverse("articol_nou"), date_formular)
        self.assertEqual(Articol.objects.get(titlu="Un articol nou").autor, self.ana)


class EditareTests(DateDeTest):
    def test_alt_utilizator_primeste_403(self):
        self.client.force_login(self.mihai)
        raspuns = self.client.get(reverse("articol_editeaza", args=[self.articol.id]))
        self.assertEqual(raspuns.status_code, 403)

    def test_autorul_poate_edita(self):
        self.client.force_login(self.ana)
        raspuns = self.client.get(reverse("articol_editeaza", args=[self.articol.id]))
        self.assertEqual(raspuns.status_code, 200)


class ArticolFormTests(TestCase):
    def test_titlu_numai_cu_majuscule_e_respins(self):
        date_formular = {"titlu": "TITLU", "continut": "Text.", "data_publicarii": "2026-10-29"}
        formular = ArticolForm(data=date_formular)
        self.assertFalse(formular.is_valid())
        self.assertEqual(formular.errors["titlu"], ["Nu scrie titlul numai cu majuscule."])
```

<!-- ruleaza -->
```bash
python manage.py test
```

```text
Found 13 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.............
----------------------------------------------------------------------
Ran 13 tests in 1.000s

OK
Destroying test database for alias 'default'...
```

Observă:

- **`DateDeTest`** nu are niciun test; există doar ca celelalte clase să moștenească datele. Fiecare clasă derivată primește propriul `setUpTestData`, rulat o dată pentru ea;
- **ciorna** (`publicat=False`) există ca să putem verifica ce **nu** trebuie să apară: nici în listă, nici la adresa ei;
- **comentariul gol** verifică ambele jumătăți: pagina se reafișează (200, nu redirect) **și** nimic n-a fost salvat;
- **`ArticolNouTests`** verifică și protecția (fără cont → login), și comportamentul (autorul e cel logat);
- `html=True` compară HTML, nu text brut, deci `<h1>De ce am ales Django</h1>` se potrivește oricum ar fi scris în template.

Cu 13 teste, o schimbare care strică lista, comentariile sau permisiunile e prinsă în câteva secunde.

## Greșeli frecvente

Pentru greșelile de mai jos folosim un fișier de încercare, `articole/tests_incercare.py`, ca să nu stricăm testele bune. La final îl ștergem.

### 1. Metoda nu începe cu test

<!-- fisier: articole/tests_incercare.py -->
```python
from django.test import TestCase


class IncercareTests(TestCase):
    def verifica_titlul(self):
        self.assertEqual(1, 2)
```

<!-- ruleaza -->
```bash
python manage.py test articole.tests_incercare
```

```text
Found 0 test(s).
System check identified no issues (0 silenced).

----------------------------------------------------------------------
Ran 0 tests in 0.000s

NO TESTS RAN
```

Testul, deși greșit (`1 != 2`), nu pică, pentru că nici nu rulează: Django caută doar metodele ale căror nume încep cu `test`, exact ca unittest și pytest (lecția 41). „NO TESTS RAN” sau un număr de teste mai mic decât te așteptai e semnalul. Corect: `def test_titlul(self):`.

### 2. Testul se bazează pe datele din baza reală

<!-- fisier: articole/tests_incercare.py -->
```python
from django.test import TestCase

from .models import Articol


class IncercareTests(TestCase):
    def test_primul_articol_exista(self):
        raspuns = self.client.get("/articol/1/")
        self.assertEqual(raspuns.status_code, 200)

    def test_numar_articole(self):
        self.assertEqual(Articol.objects.count(), 3)
```

<!-- ruleaza -->
```bash
python manage.py test articole.tests_incercare
```

```text
Found 2 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
FF
======================================================================
FAIL: test_numar_articole (articole.tests_incercare.IncercareTests.test_numar_articole)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "articole/tests_incercare.py", line 12, in test_numar_articole
    self.assertEqual(Articol.objects.count(), 3)
AssertionError: 0 != 3

======================================================================
FAIL: test_primul_articol_exista (articole.tests_incercare.IncercareTests.test_primul_articol_exista)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "articole/tests_incercare.py", line 9, in test_primul_articol_exista
    self.assertEqual(raspuns.status_code, 200)
AssertionError: 404 != 200

----------------------------------------------------------------------
Ran 2 tests in 0.010s

FAILED (failures=2)
Destroying test database for alias 'default'...
```

În baza reală sunt 3 articole, dar testele rulează pe baza de test, care e goală: 0 articole, iar `/articol/1/` dă 404. Creează datele în test (`setUpTestData`) și folosește obiectele create, nu numere fixe ca `1` (`self.articol.get_absolute_url()`, ca în exemplul complet).

### 3. Text comparat cu bytes

<!-- fisier: articole/tests_incercare.py -->
```python
from django.test import TestCase


class IncercareTests(TestCase):
    def test_titlul_blogului(self):
        raspuns = self.client.get("/")
        self.assertIn("Blogul Anei", raspuns.content)
```

<!-- ruleaza -->
```bash
python manage.py test articole.tests_incercare
```

```text
Found 1 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
E
======================================================================
ERROR: test_titlul_blogului (articole.tests_incercare.IncercareTests.test_titlul_blogului)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "articole/tests_incercare.py", line 7, in test_titlul_blogului
    self.assertIn("Blogul Anei", raspuns.content)
TypeError: a bytes-like object is required, not 'str'

----------------------------------------------------------------------
Ran 1 test in 0.010s

FAILED (errors=1)
Destroying test database for alias 'default'...
```

(Am scurtat tracebackul: între ultimele două rânduri apare și un cadru din interiorul lui unittest.) `raspuns.content` conține **octeții** trimiși browserului (`bytes`), nu un `str`. Folosește `self.assertContains(raspuns, "Blogul Anei")`, care se ocupă singur de conversie și verifică și statusul.

### 4. Un fixture care nu există

<!-- fisier: articole/tests_incercare.py -->
```python
from django.test import TestCase


class IncercareTests(TestCase):
    fixtures = ["blog.json"]

    def test_categorii(self):
        pass
```

<!-- ruleaza -->
```bash
python manage.py test articole.tests_incercare
```

```text
Found 1 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
E
======================================================================
ERROR: setUpClass (articole.tests_incercare.IncercareTests)
----------------------------------------------------------------------
Traceback (most recent call last):
django.core.management.base.CommandError: No fixture named 'blog' found.

----------------------------------------------------------------------
Ran 0 tests in 0.010s

FAILED (errors=1)
Destroying test database for alias 'default'...
```

(Și aici am scurtat tracebackul, care trece prin codul comenzii `loaddata`.) Django caută fixture-urile în folderul `fixtures/` al fiecărei aplicații, deci aici în `articole/fixtures/blog.json`. Eroarea apare în `setUpClass`, înaintea oricărui test, de aceea „Ran 0 tests”. Verifică numele fișierului și folderul.

### 5. Pagina protejată, testată fără cont

<!-- fisier: articole/tests_incercare.py -->
```python
from django.test import TestCase
from django.urls import reverse


class IncercareTests(TestCase):
    def test_formularul_articolului_nou(self):
        raspuns = self.client.get(reverse("articol_nou"))
        self.assertEqual(raspuns.status_code, 200)
```

<!-- ruleaza -->
```bash
python manage.py test articole.tests_incercare
```

```text
Found 1 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
F
======================================================================
FAIL: test_formularul_articolului_nou (articole.tests_incercare.IncercareTests.test_formularul_articolului_nou)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "articole/tests_incercare.py", line 8, in test_formularul_articolului_nou
    self.assertEqual(raspuns.status_code, 200)
AssertionError: 302 != 200

----------------------------------------------------------------------
Ran 1 test in 0.010s

FAILED (failures=1)
Destroying test database for alias 'default'...
```

`302` e redirecționarea spre login: clientul de test pornește **neautentificat**, ca un vizitator nou. Pentru pagina văzută de un utilizator, creează-l în `setUpTestData` și apelează `self.client.force_login(utilizator)` înainte de cerere.

După încercări, șterge fișierul și verifică faptul că testele bune trec în continuare:

<!-- ruleaza -->
```bash
rm articole/tests_incercare.py
python manage.py test
```

```text
Found 13 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.............
----------------------------------------------------------------------
Ran 13 tests in 1.000s

OK
Destroying test database for alias 'default'...
```

## Exercițiu

În proiectul PyTutor **`blog`**, adaugă în `articole/tests.py` (fișierul capitolului, `capitole/59-django-teste/django_teste.py`, poate rămâne pentru notițe):

1. o clasă `DespreTests` cu un test care verifică faptul că `/despre/` răspunde cu 200 și conține „Sunt Ana Popescu” (folosește `reverse("despre")` și `assertContains`; doar „Ana Popescu” ar apărea pe orice pagină, în subsol);
2. o clasă `ContactTests` cu două teste:
   - un formular valid (`nume` „Mihai”, un `email` corect, un `mesaj` de cel puțin 10 caractere) trimis cu `self.client.post(..., follow=True)` ajunge înapoi la `/contact/` și afișează mesajul „Mulțumim, Mihai!”;
   - un email invalid (`"mihai-la-exemplu"`) reafișează pagina (200) fără mesajul de mulțumire;
3. în `EditareTests`, un test care verifică faptul că Mihai primește 403 și la pagina de **ștergere** a articolului Anei (`articol_sterge`);
4. rulează `python manage.py test` până trec toate (17 teste: cele 13 din lecție și 4 noi). Apoi strică intenționat un test, citește raportul și repară-l.

## Pe scurt

- Testele Django stau în `articole/tests.py`, în clase derivate din `django.test.TestCase`, și rulează cu `python manage.py test`.
- Testele folosesc o bază de date separată, goală la început și anulată după fiecare test; datele le creezi în `setUpTestData` (o dată pe clasă) sau `setUp` (înaintea fiecărui test).
- `self.client` simulează un browser: `get`, `post`, `force_login`; verifici cu `assertContains`, `assertNotContains`, `assertRedirects` și `status_code`.
- `reverse("nume")` construiește adresele după numele din `urls.py`; formularele se pot testa direct, cu `is_valid()` și `errors`.
- Fixture-urile (`dumpdata`, `fixtures = [...]`) încarcă date gata făcute din `fixtures/`; pentru puține date, `setUpTestData` e mai clar.
- Un test care pică arată ce test, unde și de ce: `F` e o verificare falsă, `E` o excepție neașteptată.
