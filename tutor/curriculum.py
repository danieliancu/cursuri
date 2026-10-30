"""Curriculumul PyTutor: de la primul program Python până la o aplicație Django publicată.

Structura (module și subiecte) e fixă. Lecțiile sunt în `tutor/lessons/NN-slug.md` (`python manage.py load_lessons`);
AI-ul scrie la prima deschidere doar lecțiile care nu au încă fișier.
Slug-urile sunt identificatori stabili — tutorele îi folosește când salvează progresul.
Pentru actualizare după modificări: `python manage.py sync_curriculum`.
"""

# (slug, titlu, descriere, [(slug, titlu, ce acoperă), ...])
CURRICULUM = [
    ("bazele", "Bazele Python", "Primii pași: cum rulează un program, valori și variabile.", [
        ("primul-program", "Primul program", "Ce e Python și interpretorul, rularea unui fișier .py din terminal, print(), comentarii, indentarea ca sintaxă."),
        ("variabile", "Variabile și atribuire", "Ce e o variabilă (nume care referă un obiect), atribuire, reatribuire, reguli și convenții de nume (snake_case), type()."),
        ("numere", "Numere și operatori", "int și float, operatori aritmetici (+ - * / // % **), precedență, round(), erori de rotunjire cu float."),
        ("stringuri", "Șiruri de caractere", "str: ghilimele, indexare și slicing, len(), metode uzuale (upper, lower, strip, split, join, replace), imutabilitate."),
        ("f-strings", "Formatarea textului", "f-strings, formatare numerică ({x:.2f}), caractere speciale (\\n, \\t), șiruri pe mai multe rânduri."),
        ("input-conversii", "input() și conversii de tip", "Citirea de la tastatură cu input(), mereu str; conversii int(), float(), str(); ValueError la conversie greșită."),
        ("bool-comparatii", "Boolean și comparații", "True/False, operatori de comparație, and/or/not, truthiness (valori considerate false), comparații înlănțuite."),
    ]),
    ("control", "Controlul fluxului", "Decizii și repetiții.", [
        ("if-else", "Decizii: if / elif / else", "Sintaxa if/elif/else, blocuri prin indentare, condiții compuse, if imbricat, expresia condițională (x if c else y)."),
        ("while", "Bucla while", "while cu condiție, contoare, bucle infinite și cum le eviți, validarea input-ului într-o buclă."),
        ("for-range", "Bucla for și range()", "Iterarea peste secvențe, range(start, stop, pas), acumulatori (sumă, numărare), bucle imbricate."),
        ("break-continue", "break, continue și else la bucle", "Ieșirea din buclă, sărirea unui pas, clauza else a buclelor, pass."),
    ]),
    ("colectii", "Colecții de date", "Liste, dicționare și prietenii lor.", [
        ("liste", "Liste", "Creare, indexare, slicing, append/insert/remove/pop, sortare (sort vs sorted), in, len, liste imbricate, mutabilitate și aliasing."),
        ("tupluri", "Tupluri și despachetare", "Tupluri, imutabilitate, despachetare (a, b = ...), swap, returnarea mai multor valori."),
        ("dictionare", "Dicționare", "Perechi cheie-valoare, acces, get(), adăugare/ștergere, iterare cu items(), dicționare imbricate, când folosești un dict."),
        ("seturi", "Seturi", "Elemente unice, operații de mulțimi (uniune, intersecție, diferență), eliminarea duplicatelor."),
        ("comprehensions", "Comprehensions", "List, dict și set comprehensions, cu condiții; când sunt mai clare decât o buclă și când nu."),
        ("iterare-avansata", "Iterare avansată", "enumerate(), zip(), reversed(), sum/min/max/any/all, sortare cu key."),
    ]),
    ("functii", "Funcții", "Cod reutilizabil și bine organizat.", [
        ("functii-definire", "Definirea funcțiilor", "def, parametri vs argumente, return vs print, None implicit, de ce împărțim codul în funcții."),
        ("argumente", "Argumente avansate", "Valori implicite (și capcana listei mutabile), argumente keyword, *args, **kwargs."),
        ("scope", "Domeniul variabilelor", "Variabile locale vs globale, regula LEGB, de ce evităm global."),
        ("lambda-functii-valori", "Funcții ca valori și lambda", "Funcțiile ca obiecte, transmiterea lor ca argument, lambda, sorted/map/filter cu key."),
        ("docstrings-type-hints", "Docstrings și type hints", "Documentarea funcțiilor, adnotări de tip (int, str, list[int], Optional), de ce ajută."),
    ]),
    ("erori", "Erori și depanare", "Cum citești erorile și cum le tratezi.", [
        ("traceback", "Citirea unui traceback", "Structura unui traceback, tipuri comune de erori (SyntaxError, NameError, TypeError, IndexError, KeyError, ValueError), cum găsești linia vinovată."),
        ("try-except", "try / except / else / finally", "Prinderea excepțiilor specifice, else și finally, de ce nu folosim except gol."),
        ("raise-exceptii", "Ridicarea excepțiilor", "raise, excepții proprii (clase derivate din Exception), când e bine să arunci o eroare."),
        ("depanare", "Tehnici de depanare", "print debugging, breakpoint() și pdb, izolarea problemei, citirea atentă a mesajelor."),
    ]),
    ("fisiere-module", "Fișiere, module și pachete", "Lucrul cu date externe și organizarea codului.", [
        ("fisiere", "Citirea și scrierea fișierelor", "open(), moduri (r, w, a), with, citire linie cu linie, encoding utf-8, pathlib.Path."),
        ("json-csv", "JSON și CSV", "Modulele json și csv: citire, scriere, conversie între date Python și fișiere."),
        ("module-import", "Module și import", "import, from ... import, module proprii, if __name__ == \"__main__\"."),
        ("pip-venv", "pip și medii virtuale", "Instalarea pachetelor cu pip, venv, requirements.txt, de ce izolăm dependențele."),
        ("biblioteca-standard", "Biblioteca standard", "datetime, random, math, os/pathlib, collections (Counter, defaultdict)."),
    ]),
    ("oop", "Programare orientată pe obiecte", "Clase, obiecte și modelarea problemelor.", [
        ("clase-obiecte", "Clase și obiecte", "class, __init__, self, instanțe, atribute de instanță, metode."),
        ("atribute-metode", "Atribute și metode", "Atribute de clasă vs de instanță, metode care modifică starea, @classmethod, @staticmethod, @property."),
        ("mostenire", "Moștenire", "Clase derivate, super(), suprascrierea metodelor, isinstance, compoziție vs moștenire."),
        ("metode-speciale", "Metode speciale", "__str__, __repr__, __eq__, __len__, __lt__ și cum fac obiectele să se comporte natural."),
        ("dataclasses", "Dataclasses", "@dataclass, câmpuri, valori implicite, frozen, când le folosești."),
    ]),
    ("intermediar", "Python intermediar", "Unelte pe care le vei vedea peste tot, inclusiv în Django.", [
        ("iteratori-generatori", "Iteratori și generatori", "Protocolul de iterare, yield, expresii generator, evaluare leneșă."),
        ("decoratori", "Decoratori", "Funcții care împachetează funcții, sintaxa @, functools.wraps, exemple (login_required în Django)."),
        ("context-managers", "Context managers", "with, __enter__/__exit__, contextlib.contextmanager."),
    ]),
    ("calitate", "Cod de calitate", "Cod lizibil, testat și versionat.", [
        ("pep8-stil", "Stil și PEP 8", "Convenții de nume, formatare, lungimea liniilor, cod lizibil, unelte (black, ruff)."),
        ("testare", "Testare automată", "De ce testăm, assert, unittest și pytest, structura unui test, testarea cazurilor limită."),
        ("git", "Git, pe scurt", "Ce e controlul versiunilor, init, add, commit, status, log, .gitignore, branch-uri de bază."),
    ]),
    ("web", "Cum funcționează web-ul", "Fundamentele de care ai nevoie înainte de Django.", [
        ("http", "HTTP: cerere și răspuns", "Client și server, URL, metode GET/POST, coduri de status, headere, formulare HTML."),
        ("html-css", "HTML și CSS de bază", "Structura unei pagini, tag-uri uzuale, formulare, legarea CSS, selectori simpli."),
    ]),
    ("django-baza", "Django: fundamentele", "Primul proiect Django, de la URL la pagină.", [
        ("django-proiect", "Proiect și aplicații", "django-admin startproject, manage.py, startapp, structura folderelor, INSTALLED_APPS, runserver."),
        ("django-settings", "settings.py", "Setările importante (DEBUG, ALLOWED_HOSTS, DATABASES, TEMPLATES, STATIC), variabile de mediu, SECRET_KEY."),
        ("django-urls-views", "URL-uri și view-uri", "urls.py, path(), parametri în URL, view-uri ca funcții, HttpResponse, render()."),
        ("django-templates", "Template-uri", "Limbajul de template: {{ }}, {% %}, if/for, moștenire (extends, block), include, filtre."),
        ("django-static", "Fișiere statice", "CSS/JS/imagini în Django, {% static %}, STATIC_URL, organizarea fișierelor."),
    ]),
    ("django-date", "Django: date și modele", "Baza de date prin ORM.", [
        ("django-modele", "Modele", "models.Model, tipuri de câmpuri, opțiuni (null, blank, default), __str__, Meta."),
        ("django-migrari", "Migrări", "makemigrations, migrate, ce e o migrare, istoric, cum repari probleme comune."),
        ("django-orm", "Interogări cu ORM", "objects.all/filter/get/exclude, lookups (__contains, __gte), order_by, create, update, delete, QuerySet leneș."),
        ("django-relatii", "Relații între modele", "ForeignKey, ManyToManyField, OneToOneField, related_name, select_related/prefetch_related."),
        ("django-admin", "Panoul de admin", "createsuperuser, admin.site.register, ModelAdmin (list_display, search_fields, list_filter)."),
    ]),
    ("django-interactiv", "Django: aplicații interactive", "Formulare, utilizatori și view-uri pe clase.", [
        ("django-forms", "Formulare", "forms.Form, validare, cleaned_data, afișarea în template, CSRF, POST-redirect-GET."),
        ("django-modelforms", "ModelForm", "Formulare generate din modele, salvare, editare, validare personalizată."),
        ("django-auth", "Autentificare", "Login, logout, înregistrare, @login_required, request.user, permisiuni de bază."),
        ("django-cbv", "Class-based views", "View, TemplateView, ListView, DetailView, CreateView/UpdateView/DeleteView, mixin-uri."),
    ]),
    ("django-avansat", "Django: mai departe", "Calitate și publicare.", [
        ("django-teste", "Testarea în Django", "TestCase, clientul de test, testarea modelelor și view-urilor, fixture-uri."),
        ("django-api", "API-uri cu Django REST Framework", "Ce e un API REST, JSON, serializere, APIView/ViewSet, routere."),
        ("django-deploy", "Publicarea aplicației", "DEBUG=False, setări de producție, collectstatic, gunicorn, baza de date în producție, variabile de mediu."),
    ]),
]


def sync(Module, Topic) -> None:
    """Creează/actualizează modulele și subiectele (fără să atingă lecțiile deja scrise)."""
    for m_order, (m_slug, m_title, m_desc, topics) in enumerate(CURRICULUM, 1):
        module, _ = Module.objects.update_or_create(
            slug=m_slug, defaults={"title": m_title, "description": m_desc, "order": m_order}
        )
        for t_order, (t_slug, t_title, t_summary) in enumerate(topics, 1):
            Topic.objects.update_or_create(
                slug=t_slug,
                defaults={"module": module, "title": t_title, "summary": t_summary, "order": t_order},
            )
