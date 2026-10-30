## Ce este

**Fișierele statice** sunt fișierele pe care site-ul le trimite browserului exact așa cum sunt, fără să le genereze: foi de stil CSS, imagini, fonturi, scripturi JavaScript. Sunt „statice” prin opoziție cu paginile HTML, pe care Django le construiește la fiecare cerere din template-uri și date.

În Django, fișierele statice ale unei aplicații stau în folderul ei `static/`, iar în template-uri le legi cu tag-ul `{% static %}`:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'articole/stil.css' %}">
```

`{% static 'articole/stil.css' %}` devine adresa fișierului, `/static/articole/stil.css`.

## De ce contează

La lecția 48, blogul a primit structura din lecția 44 (antet, meniu, articole, subsol), dar arată ca o pagină fără stil: font implicit, linkuri albastre subliniate, nicio culoare. Foaia de stil `stil.css` din lecția 44 le face să arate ca un blog. Rămâne doar să o pui unde o găsește Django și să o legi din macheta de bază.

Pe lângă CSS, aici vor sta mai târziu imaginile și scripturile site-ului. Felul în care Django le organizează contează mai ales la publicare (lecția 61), când toate fișierele statice ale tuturor aplicațiilor sunt adunate într-un singur folder, de unde sunt servite eficient.

## Cum funcționează

### Unde stau fișierele statice

Aplicația `django.contrib.staticfiles`, activă implicit în `INSTALLED_APPS` (lecția 45), caută fișiere în folderul `static/` al fiecărei aplicații. Ca la template-uri (lecția 48), le punem într-un subfolder cu numele aplicației:

```text
articole/
├── static/
│   └── articole/
│       └── stil.css
└── templates/
    └── articole/
        └── ...
```

Motivul e același: toate aplicațiile își pun fișierele statice în același „spațiu”, iar fără subfolder, un `stil.css` din altă aplicație l-ar putea ascunde pe al tău. Calea unui fișier static se scrie de la `static/`: `articole/stil.css`.

### `{% load static %}` și `{% static %}`

`{% static %}` nu face parte din tag-urile de bază ale template-urilor. Îl încarci cu `{% load static %}`, scris în **fiecare** template care îl folosește, de obicei pe primul rând. E ca un `import` (lecția 29), dar pentru template-uri.

```html
{% load static %}
...
<link rel="stylesheet" href="{% static 'articole/stil.css' %}">
```

`{% static %}` lipește `STATIC_URL` din setări (`"static/"`, lecția 46) în fața căii. De ce nu scrii direct `/static/articole/stil.css`? La publicare, fișierele statice pot ajunge la altă adresă, de exemplu pe alt server. Schimbi atunci `STATIC_URL`, iar toate linkurile se actualizează singure, la fel ca `{% url %}` pentru pagini.

Template-urile care fac `{% extends "articole/base.html" %}` primesc automat `<link>`-ul din macheta de bază, deci CSS-ul se leagă într-un singur loc, pentru tot site-ul.

### `findstatic`: unde e un fișier?

Comanda `findstatic` caută un fișier static exact cum l-ar căuta Django:

<!-- ruleaza -->
```bash
python manage.py findstatic articole/stil.css -v 2
```

```text
No matching file found for 'articole/stil.css'.

Looking in the following locations:
  /opt/venv/lib/python3.12/site-packages/django/contrib/admin/static
```

Fișierul nu e găsit, iar `-v 2` arată unde a căutat: deocamdată doar în fișierele statice ale panoului de administrare, pentru că folderul `articole/static/` încă nu există. După ce creezi fișierul (în exemplul complet), comanda îl va găsi.

### Ce se întâmplă „pe dedesubt”

Cu `DEBUG` pornit, `runserver` servește singur fișierele statice. La o cerere spre `/static/articole/stil.css`, aplicația `staticfiles` caută `articole/stil.css` în folderele `static/` ale aplicațiilor și trimite fișierul cu tipul `text/css` (lecția 43). Browserul face o cerere separată pentru fiecare fișier static legat din pagină.

Cu `DEBUG` oprit, `runserver` nu le mai servește: pe un server real, fișierele statice sunt adunate cu `python manage.py collectstatic` și servite de o unealtă făcută pentru asta: un server web ca nginx sau, pentru site-uri mici, pachetul WhiteNoise (lecția 61).

Browserul păstrează fișierele statice în **cache**, adică le reține ca să nu le ceară la fiecare pagină. De aceea, după ce modifici CSS-ul, uneori nu vezi schimbarea până nu reîncarci pagina forțat: Ctrl+F5 (Cmd+Shift+R pe Mac).

## Exemplu complet

Foaia de stil din lecția 44, mutată în aplicație ca `articole/static/articole/stil.css`. O singură diferență față de lecția 44: clasa formularului de comentarii devine `.formular`, ca s-o folosească toate formularele site-ului (lecțiile 55–57), și acoperă și listele de opțiuni (`select`). Am adăugat și două clase, `.errorlist` și `.mesaj`, pentru erorile de validare și mesajele de confirmare de la lecția 55.

<!-- fisier: articole/static/articole/stil.css -->
```css
body {
  margin: 0;
  font-family: system-ui, sans-serif;
  line-height: 1.6;
  color: #222;
  background-color: #f6f7f9;
}

main {
  max-width: 720px;
  margin: 0 auto;
  padding: 0 16px 32px;
}

.antet {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #1f2937;
}

.antet a {
  color: white;
  text-decoration: none;
  margin-left: 16px;
}

.antet .sigla {
  margin-left: 0;
  font-weight: bold;
  font-size: 20px;
}

.articol {
  background-color: white;
  border: 1px solid #e3e5e8;
  border-radius: 8px;
  padding: 16px 20px;
  margin: 16px 0;
}

.articol h2 a {
  color: #2f6fde;
  text-decoration: none;
}

.articol h2 a:hover {
  text-decoration: underline;
}

.meta {
  color: #6b7280;
  font-size: 14px;
}

.categorie {
  background-color: #e8f0fe;
  color: #2f6fde;
  padding: 2px 8px;
  border-radius: 999px;
}

.comentariu {
  border-left: 3px solid #2f6fde;
  padding-left: 12px;
  margin: 12px 0;
}

/* Toate formularele site-ului: comentarii, contact, articole, autentificare. */
.formular label {
  display: block;
  margin-top: 12px;
  font-weight: bold;
}

.formular input,
.formular textarea,
.formular select {
  width: 100%;
  box-sizing: border-box;
  padding: 8px;
  border: 1px solid #c9ccd1;
  border-radius: 6px;
  font: inherit;
}

.formular button {
  margin-top: 12px;
  padding: 8px 16px;
  border: 0;
  border-radius: 6px;
  background-color: #2f6fde;
  color: white;
  cursor: pointer;
}

/* Erorile de validare (lecția 55) și mesajele de confirmare. */
.errorlist {
  color: #b42318;
  padding-left: 18px;
}

.mesaj {
  background-color: #e7f6ec;
  border: 1px solid #a6dcb6;
  border-radius: 6px;
  padding: 8px 12px;
  margin: 16px 0;
}

.subsol {
  text-align: center;
  color: #6b7280;
  font-size: 14px;
}
```

Macheta de bază, `articole/templates/articole/base.html`, cu două rânduri noi: `{% load static %}` la început și `<link>`-ul spre CSS în `<head>`:

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

Acum Django găsește fișierul:

<!-- ruleaza -->
```bash
python manage.py findstatic articole/stil.css
```

```text
Found 'articole/stil.css' here:
  articole/static/articole/stil.css
```

(La tine, calea apare completă, cu folderul proiectului `blog` în față.)

În HTML-ul paginii, `{% static %}` a devenit adresa fișierului:

<!-- comanda: python /h/vezi_pagina.py --html / | sed -n 1,10p -->
```text
200 OK
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Blogul Anei</title>
  <link rel="stylesheet" href="/static/articole/stil.css">
</head>
<body>
```

Pornește serverul și deschide blogul: antetul închis la culoare cu sigla „Blogul Anei”, articolele în casete albe cu colțuri rotunjite, categoriile ca etichete albastre, subsolul centrat. Toate paginile au același stil, pentru că toate moștenesc `base.html`.

## Greșeli frecvente

### 1. `{% load static %}` uitat

Fără primul rând din `base.html`:

<!-- comanda: cp -r . /tmp/p && cd /tmp/p && sed -i "/{% load static %}/d" articole/templates/articole/base.html && python /h/vezi_pagina.py / -->
```text
Traceback (most recent call last):
django.template.exceptions.TemplateSyntaxError: Invalid block tag on line 7: 'static'. Did you forget to register or load this tag?
```

Mesajul chiar te întreabă: „ai uitat să încarci acest tag?”. `{% load static %}` se scrie în **fiecare** template care folosește `{% static %}`. `{% extends %}` nu „transmite” tag-urile încărcate în macheta de bază.

### 2. Calea greșită în `{% static %}`

Ai scris `{% static 'stil.css' %}`, fără folderul aplicației. Pagina se încarcă fără nicio eroare, cu linkul `/static/stil.css`, dar fără stil: browserul cere fișierul și primește 404. `findstatic` arată imediat problema:

<!-- ruleaza -->
```bash
python manage.py findstatic stil.css
```

```text
No matching file found for 'stil.css'.
```

Calea din `{% static %}` e cea de la `static/`: `articole/stil.css`. Când pagina apare fără stil, primul lucru pe care îl verifici e cu `findstatic`.

### 3. Fișierul pus direct în `static/`

`articole/static/stil.css`, fără subfolderul `articole/`, funcționează cu `{% static 'stil.css' %}`. Problema apare când adaugi altă aplicație care are și ea un `static/stil.css`: Django îl folosește pe primul găsit, iar unul dintre ele e ignorat fără nicio eroare. Subfolderul cu numele aplicației evită asta.

### 4. Schimbarea din CSS „nu apare”

Ai modificat o culoare în `stil.css`, ai reîncărcat pagina și arată la fel. De cele mai multe ori, browserul folosește copia păstrată în cache. Reîncarcă forțat cu Ctrl+F5. Dacă nici așa nu apare, verifică cu `findstatic` că modifici chiar fișierul pe care îl folosește Django.

## Exercițiu

În proiectul PyTutor `blog`, creează `articole/static/articole/stil.css` și actualizează `base.html` ca în exemplul complet, apoi verifică stilul în browser. După aceea:

1. schimbă culoarea antetului (`.antet`, `background-color`) cu o culoare care îți place; reîncarcă forțat pagina dacă nu vezi schimbarea;
2. adaugă o imagine mică. O imagine SVG e un fișier text, deci o poți scrie direct în editor: creează `articole/static/articole/sigla.svg` cu rândul `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"><circle cx="12" cy="12" r="10" fill="#2f6fde"/></svg>`, apoi afișeaz-o în antet, lângă textul siglei, cu `<img src="{% static 'articole/sigla.svg' %}" alt="" width="24">`;
3. verifică ambele fișiere cu `python manage.py findstatic`;
4. pornește serverul cu `DJANGO_DEBUG=0` (lecția 46) și observă că pagina apare fără stil: fișierele statice nu mai sunt servite. Vei vedea la lecția 61 cum se rezolvă asta pe un server real.

Schimbările tale de culori și imaginea sunt doar pentru copia ta: lecțiile următoare nu modifică `stil.css`. `base.html` se schimbă însă la lecțiile 55–57; dacă vrei să păstrezi imaginea în antet, adaugă din nou rândul cu `<img>` în fișierul nou.

## Pe scurt

- Fișierele statice (CSS, imagini, JavaScript) stau în `articole/static/articole/`, cu un subfolder care poartă numele aplicației.
- În template: `{% load static %}` pe primul rând, apoi `{% static 'articole/stil.css' %}`, care devine `/static/articole/stil.css`.
- `{% load static %}` trebuie scris în fiecare template care folosește `{% static %}`; altfel apare `TemplateSyntaxError`.
- O cale greșită în `{% static %}` nu dă eroare în pagină, ci un 404 pentru fișier; `python manage.py findstatic cale` arată unde caută Django.
- `runserver` servește fișierele statice doar cu `DEBUG` pornit; la publicare se folosește `collectstatic` (lecția 61).
- Dacă o schimbare din CSS nu apare, reîncarcă forțat pagina (Ctrl+F5).

<!-- proiect: _blog/48 -->
<!-- proiect-final: _blog/49 -->
