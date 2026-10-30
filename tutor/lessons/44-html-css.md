## Ce este

O pagină web are două limbaje, cu roluri diferite:
- **HTML** („HyperText Markup Language”) descrie **structura și conținutul**: acesta e un titlu, acesta e un paragraf, aceasta e o listă, acesta e un link;
- **CSS** („Cascading Style Sheets”) descrie **aspectul**: culori, fonturi, spații, lățimi.

Cea mai mică pagină completă:

```html
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <title>Blogul Anei</title>
</head>
<body>
  <h1>Blogul Anei</h1>
  <p>Notițe despre Python, Django și Cluj.</p>
</body>
</html>
```

Un marcaj între `<` și `>`, ca `<h1>` sau `</h1>`, se numește **tag**. Browserul primește acest text de la server (corpul răspunsului HTTP din lecția 43), îl citește și desenează pagina.

## De ce contează

Django produce pagini HTML. Template-urile din lecția 48 sunt fișiere HTML cu „locuri libere” completate din Python, fișierele CSS devin „fișiere statice” la lecția 49, iar formularele din lecția 55 sunt formulare HTML ca cele de aici. Nu trebuie să fii designer, dar trebuie să poți scrie o pagină corectă, să înțelegi una scrisă de altcineva și să știi ce fac un formular și un selector CSS.

În lecția asta scrii de mână paginile blogului Anei. Din lecția 45 le vei transforma, pas cu pas, într-o aplicație Django.

## Cum funcționează

### Structura unei pagini

```html
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Blogul Anei</title>
  <link rel="stylesheet" href="stil.css">
</head>
<body>
  <!-- conținutul vizibil -->
</body>
</html>
```

- `<!doctype html>` spune că e o pagină HTML modernă;
- `<html lang="ro">` cuprinde tot; `lang` ajută cititoarele de ecran și traducerea automată;
- `<head>` conține informații **despre** pagină, care nu se afișează: codificarea (`charset="utf-8"`, obligatoriu pentru diacritice), titlul din tab-ul browserului, legătura spre CSS, `viewport` (ca pagina să arate bine pe telefon);
- `<body>` conține tot ce se vede;
- `<!-- ... -->` e un comentariu HTML.

### Tag-uri, elemente și atribute

```html
<a href="/articol/2/" class="titlu">De ce am ales Django</a>
```

- `<a ...>` e tag-ul de deschidere, `</a>` cel de închidere, iar împreună cu textul dintre ele formează un **element**;
- `href="/articol/2/"` și `class="titlu"` sunt **atribute**: perechi `nume="valoare"` scrise în tag-ul de deschidere;
- elementele se pot pune unele în altele (**imbricare**), dar se închid în ordinea inversă: `<p><strong>text</strong></p>`, nu `<p><strong>text</p></strong>`.

Câteva elemente nu au conținut și nici tag de închidere: `<meta>`, `<link>`, `<img>`, `<input>`, `<br>`.

Indentarea din HTML nu contează pentru browser, dar o folosim ca să se vadă ce element e în care, la fel ca în Python.

### Tag-uri uzuale

| Tag | Rol |
|---|---|
| `<h1>` … `<h3>` | titluri, de la cel mai important la cel mai puțin important; un singur `<h1>` pe pagină |
| `<p>` | paragraf |
| `<a href="...">` | link |
| `<strong>`, `<em>` | text important (îngroșat), accentuat (cursiv) |
| `<ul>` / `<ol>` cu `<li>` | listă neordonată (cu buline) / ordonată (numerotată) |
| `<img src="..." alt="...">` | imagine; `alt` descrie imaginea pentru cine nu o poate vedea |
| `<header>`, `<nav>`, `<main>`, `<footer>` | antetul, meniul, conținutul principal și subsolul paginii |
| `<article>`, `<section>` | un conținut de sine stătător (un articol) / o secțiune a paginii |
| `<div>`, `<span>` | „cutii” fără sens anume, folosite pentru grupare și stil (bloc / în interiorul textului) |

Tag-urile cu sens (`<article>`, `<nav>`, `<h2>`) sunt preferate față de `<div>`-uri peste tot: browserele, motoarele de căutare și cititoarele de ecran înțeleg mai bine pagina.

### Linkuri și căi

- `href="https://www.python.org/"`: adresă completă, spre alt site;
- `href="/articol/2/"`: începe cu `/`, deci e o cale de la rădăcina site-ului curent;
- `href="articol.html"`: fără `/` la început, deci e **relativă** la pagina curentă: fișierul `articol.html` din același folder.

Paginile din lecția asta folosesc căi relative (`articol.html`, `stil.css`), ca să meargă direct din folderul capitolului. În Django vei folosi căi construite de framework (lecțiile 47 și 49).

### Formulare

Un formular adună date de la utilizator și le trimite serverului ca cerere HTTP (lecția 43):

```html
<form action="/articol/2/comentariu/" method="post" class="formular-comentariu">
  <label for="autor">Numele tău</label>
  <input type="text" id="autor" name="autor" required>

  <label for="text">Comentariu</label>
  <textarea id="text" name="text" rows="4" required></textarea>

  <button type="submit">Trimite comentariul</button>
</form>
```

- `action` e adresa la care se trimit datele, iar `method` e `get` sau `post`;
- **`name`** e numele sub care pleacă valoarea fiecărui câmp: fără el, câmpul nu se trimite deloc;
- `<label for="autor">` e legat de câmpul cu `id="autor"`: un clic pe etichetă pune cursorul în câmp, iar cititoarele de ecran știu ce înseamnă câmpul;
- `type` alege felul câmpului: `text`, `email`, `password`, `number`, `checkbox`;
- `required` cere browserului să nu trimită formularul cu câmpul gol. E doar un ajutor pentru utilizator: serverul trebuie să verifice oricum datele, pentru că oricine poate trimite o cerere HTTP fără browser (ai făcut-o singur la lecția 43).

În Django, formularele POST au în plus un câmp ascuns de securitate, `{% csrf_token %}` (lecția 55).

### Legarea CSS

CSS-ul stă de obicei într-un fișier separat, legat din `<head>`:

```html
<link rel="stylesheet" href="stil.css">
```

Așa, același fișier dă aspectul tuturor paginilor site-ului. Se poate scrie CSS și direct în pagină, într-un element `<style>`, sau chiar pe un element, cu atributul `style="..."`, dar ambele se folosesc doar pentru cazuri mici: amestecă aspectul cu structura și se repetă de la o pagină la alta.

### Reguli și selectori

O regulă CSS are un **selector** (ce elemente) și o listă de **proprietăți** (cum arată):

```css
h1 {
  color: #2f6fde;
  font-size: 32px;
}
```

| Selector | Alege | Exemplu |
|---|---|---|
| `p` | toate elementele de acel tip | toate paragrafele |
| `.meta` | elementele cu `class="meta"` | `<p class="meta">` |
| `#autor` | elementul cu `id="autor"` (unic în pagină) | `<input id="autor">` |
| `article p` | paragrafele aflate **în interiorul** unui `<article>` | |
| `h1, h2` | și `h1`, și `h2` | |
| `a:hover` | linkurile peste care e mouse-ul | |

Un element poate avea mai multe clase, despărțite prin spațiu: `class="articol recomandat"`. Clasele sunt modul obișnuit de a da stil; `id`-urile se folosesc mai ales pentru legături (`<label for>`, linkuri `#comentarii`).

Proprietăți pe care le vei folosi des:

| Proprietate | Exemplu | Ce face |
|---|---|---|
| `color` | `color: #333;` | culoarea textului |
| `background-color` | `background-color: #f6f7f9;` | culoarea fundalului |
| `font-family` | `font-family: system-ui, sans-serif;` | fontul (primul disponibil din listă) |
| `font-size`, `line-height` | `font-size: 18px; line-height: 1.6;` | mărimea textului, distanța dintre rânduri |
| `margin`, `padding` | `margin: 16px 0;` | spațiul din afara / din interiorul chenarului |
| `border` | `border: 1px solid #ddd;` | chenarul |
| `max-width` | `max-width: 720px;` | lățimea maximă |
| `text-align` | `text-align: center;` | alinierea textului |

Culorile se scriu de obicei în hexazecimal, `#rrggbb` (roșu, verde, albastru), sau cu nume: `white`, `black`, `red`.

### HTML generat din Python

Paginile unui blog nu se scriu de mână, câte una pentru fiecare articol: se **generează** din date. Iată ideea, cu ce știi deja:

<!-- fisier: genereaza.py -->
```python
from html import escape
from pathlib import Path

articole = [
    {"nr": 1, "titlu": "Primul meu program în Python", "data": "14.09.2026", "categorie": "Programare"},
    {"nr": 2, "titlu": "De ce am ales Django", "data": "02.10.2026", "categorie": "Programare"},
    {"nr": 3, "titlu": "O plimbare prin Cluj", "data": "20.10.2026", "categorie": "Călătorii"},
]

elemente = []
for articol in articole:
    elemente.append(
        f'    <li><a href="/articol/{articol["nr"]}/">{escape(articol["titlu"])}</a> '
        f'<span class="meta">{articol["data"]} · {escape(articol["categorie"])}</span></li>'
    )

pagina = (
    '<!doctype html>\n<html lang="ro">\n<head>\n  <meta charset="utf-8">\n'
    "  <title>Blogul Anei</title>\n</head>\n<body>\n  <h1>Blogul Anei</h1>\n  <ul>\n"
    + "\n".join(elemente)
    + "\n  </ul>\n</body>\n</html>\n"
)
Path("index.html").write_text(pagina, encoding="utf-8")
print(pagina)
```

```text
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <title>Blogul Anei</title>
</head>
<body>
  <h1>Blogul Anei</h1>
  <ul>
    <li><a href="/articol/1/">Primul meu program în Python</a> <span class="meta">14.09.2026 · Programare</span></li>
    <li><a href="/articol/2/">De ce am ales Django</a> <span class="meta">02.10.2026 · Programare</span></li>
    <li><a href="/articol/3/">O plimbare prin Cluj</a> <span class="meta">20.10.2026 · Călătorii</span></li>
  </ul>
</body>
</html>
```

Funcționează, dar se citește greu: HTML-ul e risipit prin stringuri Python. **Template-urile** Django (lecția 48) rezolvă exact asta: scrii HTML normal, cu locuri marcate (`{{ articol.titlu }}`), iar Django le completează. `escape()` transformă caracterele cu rol special în HTML (`<`, `>`, `&`, ghilimele) în forme inofensive; vezi greșeala 5 de mai jos pentru motiv.

### Cum vezi o pagină în PyTutor

Browserul poate deschide fișierele HTML ale capitolului printr-un server web mic din biblioteca standard. În terminal, din rădăcina proiectului:

```bash
python -m http.server 8000 --bind 0.0.0.0 --directory capitole/44-html-css
```

Serverul pornește pe portul 8000 al mediului tău. Adresa la care îl deschizi în browser apare în bara terminalului („server: localhost:...”). În terminal vei vedea câte un rând pentru fiecare cerere (`"GET /stil.css HTTP/1.1" 200 -`), adică exact cererile HTTP din lecția 43. Îl oprești cu **Oprește** sau Ctrl+C.

După ce modifici un fișier, reîncarcă pagina în browser (F5). Dacă stilul nu se schimbă, browserul a păstrat versiunea veche a CSS-ului: reîncarcă forțat, cu Ctrl+F5.

### Ce se întâmplă „pe dedesubt”: modelul cutiei și cascada

Browserul desenează **fiecare element ca o cutie**, cu patru straturi, din interior spre exterior:

```text
+---------------- margin ----------------+
|  +------------- border -------------+  |
|  |  +---------- padding ----------+ |  |
|  |  |          conținut          | |  |
|  |  +----------------------------+ |  |
|  +----------------------------------+  |
+----------------------------------------+
```

`padding` e spațiul dintre conținut și chenar (are culoarea fundalului elementului), iar `margin` e spațiul dintre chenar și elementele vecine (e transparent). Majoritatea problemelor de „de ce e textul ăsta lipit de margine?” se rezolvă cu una dintre ele.

„Cascading” din numele CSS-ului înseamnă că mai multe reguli se pot aplica aceluiași element, iar browserul le combină după câteva reguli:
- regulile mai **specifice** câștigă: `#autor` bate `.camp`, care bate `input`;
- la specificitate egală, câștigă regula scrisă **mai jos** în fișier;
- unele proprietăți (culoarea, fontul) se **moștenesc** de la elementul părinte: dacă `body` are `color: #333`, toate paragrafele primesc această culoare, cu excepția celor pentru care o regulă proprie spune altceva.

## Exemplu complet

Paginile blogului Anei: lista articolelor (`index.html`), un articol cu comentarii și formularul de comentariu (`articol.html`) și stilul comun (`stil.css`). Le vei regăsi, aproape neschimbate, în template-urile Django din lecțiile 48–49.

`index.html`:

```html
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Blogul Anei</title>
  <link rel="stylesheet" href="stil.css">
</head>
<body>
  <header class="antet">
    <a href="index.html" class="sigla">Blogul Anei</a>
    <nav>
      <a href="index.html">Articole</a>
      <a href="despre.html">Despre</a>
    </nav>
  </header>

  <main>
    <h1>Articole</h1>

    <article class="articol">
      <h2><a href="articol.html">De ce am ales Django</a></h2>
      <p class="meta">2 octombrie 2026 · <span class="categorie">Programare</span></p>
      <p>După primele luni cu Python, voiam să fac un site adevărat...</p>
    </article>

    <article class="articol">
      <h2><a href="articol.html">Primul meu program în Python</a></h2>
      <p class="meta">14 septembrie 2026 · <span class="categorie">Programare</span></p>
      <p>Totul a început cu un simplu <code>print("Salut, lume!")</code>.</p>
    </article>
  </main>

  <footer class="subsol">
    <p>Ana Popescu, Cluj · 2026</p>
  </footer>
</body>
</html>
```

`articol.html`:

```html
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>De ce am ales Django · Blogul Anei</title>
  <link rel="stylesheet" href="stil.css">
</head>
<body>
  <header class="antet">
    <a href="index.html" class="sigla">Blogul Anei</a>
    <nav>
      <a href="index.html">Articole</a>
      <a href="despre.html">Despre</a>
    </nav>
  </header>

  <main>
    <article class="articol">
      <h1>De ce am ales Django</h1>
      <p class="meta">2 octombrie 2026 · <span class="categorie">Programare</span></p>
      <p>După primele luni cu Python, voiam să fac un site adevărat: cu pagini,
        cu bază de date și cu un loc unde să mă autentific.</p>
      <p>Django are toate acestea „din cutie”, iar documentația lui e excelentă.</p>
    </article>

    <section class="comentarii" id="comentarii">
      <h2>Comentarii (1)</h2>
      <div class="comentariu">
        <p class="meta"><strong>Mihai</strong> · 3 octombrie 2026</p>
        <p>Foarte bun articol!</p>
      </div>

      <form action="/articol/2/comentariu/" method="post" class="formular-comentariu">
        <h3>Lasă un comentariu</h3>
        <label for="autor">Numele tău</label>
        <input type="text" id="autor" name="autor" required>

        <label for="text">Comentariu</label>
        <textarea id="text" name="text" rows="4" required></textarea>

        <button type="submit">Trimite comentariul</button>
      </form>
    </section>
  </main>

  <footer class="subsol">
    <p>Ana Popescu, Cluj · 2026</p>
  </footer>
</body>
</html>
```

`stil.css`:

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

.formular-comentariu label {
  display: block;
  margin-top: 12px;
  font-weight: bold;
}

.formular-comentariu input,
.formular-comentariu textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 8px;
  border: 1px solid #c9ccd1;
  border-radius: 6px;
  font: inherit;
}

.formular-comentariu button {
  margin-top: 12px;
  padding: 8px 16px;
  border: 0;
  border-radius: 6px;
  background-color: #2f6fde;
  color: white;
  cursor: pointer;
}

.subsol {
  text-align: center;
  color: #6b7280;
  font-size: 14px;
}
```

Câteva lucruri de observat:
- antetul și subsolul sunt **identice** în ambele pagini. Pe un site cu 50 de pagini, o schimbare în meniu ar trebui făcută de 50 de ori. Moștenirea template-urilor din Django (`{% extends %}`, lecția 48) scrie partea comună o singură dată;
- linkurile spre articol duc toate la același fișier, `articol.html`, pentru că paginile sunt scrise de mână. În Django vor fi `/articol/1/`, `/articol/2/`, generate automat;
- formularul trimite POST la `/articol/2/comentariu/`. Deschis cu `http.server`, trimiterea lui dă o eroare (`501`, „Unsupported method”), pentru că acel server știe doar să trimită fișiere. Datele vor fi primite și salvate abia în Django (lecțiile 55–56);
- `display: flex` pe antet așază sigla și meniul pe același rând, la capete opuse. E singura proprietate „de aranjare” din exemplu; restul sunt culori și spații;
- `box-sizing: border-box` face ca `width: 100%` să includă și `padding`-ul și chenarul, altfel câmpurile ar ieși puțin în afara articolului (vezi modelul cutiei).

## Greșeli frecvente

### 1. Lipsește `<meta charset="utf-8">`

Fără el, browserul poate ghici greșit codificarea și citește octeții UTF-8 ca pe un alt alfabet (de obicei Windows-1252). Iată exact ce vede atunci:

```python
text = "Bună ziua, Iași"
octeti = text.encode("utf-8")
print(octeti.decode("cp1252"))
```

```text
BunÄƒ ziua, IaÈ™i
```

Când vezi `Äƒ`, `È™` sau `Ã®` în locul diacriticelor, problema e aproape sigur codificarea. Pune `<meta charset="utf-8">` primul în `<head>` și salvează fișierul în UTF-8 (lecția 27).

### 2. Tag neînchis sau închis în ordine greșită

```html
<p>Am învățat <strong>Python</p>
<p>Al doilea paragraf apare și el îngroșat.</p>
```

Browserul nu dă erori: încearcă să „repare” singur HTML-ul greșit și ghicește ce ai vrut. Rezultatul e imprevizibil; aici, textul îngroșat se poate întinde și peste paragraful următor. Închide fiecare element, în ordinea inversă deschiderii:

```html
<p>Am învățat <strong>Python</strong></p>
<p>Al doilea paragraf e normal.</p>
```

Un editor cu indentare corectă și validatorul de la W3C (validator.w3.org) prind astfel de greșeli.

### 3. Câmp de formular fără `name`

```html
<form action="/cauta/" method="get">
  <input type="text" id="q">
  <button type="submit">Caută</button>
</form>
```

Formularul se trimite, dar la `/cauta/?`, fără niciun parametru: câmpurile fără `name` nu pleacă spre server. `id` e pentru etichete și CSS, iar `name` e pentru server. Corect:

```html
<input type="text" id="q" name="q">
```

### 4. Calea greșită spre fișierul CSS

```html
<link rel="stylesheet" href="css/stil.css">
```

Dacă `stil.css` e în același folder cu pagina, nu în `css/`, pagina apare fără niciun stil și fără niciun mesaj de eroare pe pagină. Eroarea se vede în terminalul în care rulează `http.server`, într-un rând care începe cu adresa clientului și data și se termină așa:

```text
"GET /css/stil.css HTTP/1.1" 404 -
```

Când stilul „nu se aplică”, verifică întâi dacă fișierul CSS a fost găsit (`200`) sau nu (`404`). În browser, același lucru apare în instrumentele pentru dezvoltatori (F12, tab-ul „Network” sau „Rețea”).

### 5. Text de la utilizatori pus în HTML fără `escape()`

Un „comentariu” trimis de cineva rău intenționat:

```python
from html import escape

comentariu = '<script>alert("Ai fost păcălit!")</script>'
print(f"<p>{comentariu}</p>")
print(f"<p>{escape(comentariu)}</p>")
```

```text
<p><script>alert("Ai fost păcălit!")</script></p>
<p>&lt;script&gt;alert(&quot;Ai fost păcălit!&quot;)&lt;/script&gt;</p>
```

În prima variantă, browserul ar **executa** codul JavaScript din comentariu pe pagina oricui o deschide. Atacul se numește XSS („cross-site scripting”) și poate fura sesiuni de autentificare. În a doua, caracterele speciale au fost înlocuite cu entități HTML (`&lt;` înseamnă `<`), deci browserul afișează textul exact cum a fost scris, fără să-l execute. Template-urile Django fac această înlocuire automat (lecția 48), dar trebuie să știi de ce există.

## Exercițiu

În folderul `capitole/44-html-css/`:

1. creează `index.html`, `articol.html` și `stil.css` după exemplul complet, dar pentru blogul **tău** (alt nume, alte articole, alte culori); adaugă și o pagină `despre.html`, cu o imagine (`<img>` cu `alt`; poate fi o imagine de pe internet, dată cu adresa completă) și o listă numerotată;
2. în `stil.css`, folosește cel puțin: un selector de tag, unul de clasă, un selector de tip `article p` și un `:hover`; dă articolelor un chenar și spațiu interior (`padding`);
3. deschide paginile în browser cu `http.server` (comanda din lecție) și verifică în terminal că toate cererile au primit `200`, inclusiv cea pentru `stil.css`;
4. în fișierul capitolului, `capitole/44-html-css/html_css.py`, scrie o funcție `pagina_lista(articole)` care primește o listă de dicționare (`titlu`, `data`, `categorie`) și întoarce HTML-ul complet al paginii de listă, legat de `stil.css`, cu `escape()` pe toate textele; scrie rezultatul în `capitole/44-html-css/generat.html` (cu `encoding="utf-8"`) și deschide-l în browser;
5. adaugă intenționat un articol cu titlul `<b>Test</b> & alte „ghilimele”` și verifică în browser că titlul apare exact așa, ca text.

## Pe scurt

- HTML descrie structura (tag-uri, atribute, elemente imbricate), iar CSS descrie aspectul.
- O pagină are `<!doctype html>`, `<html lang="ro">`, `<head>` (cu `<meta charset="utf-8">`, `<title>`, `<link>` spre CSS) și `<body>`.
- Tag-uri de bază: `h1`–`h3`, `p`, `a`, `ul`/`ol`/`li`, `img`, plus tag-urile cu sens `header`, `nav`, `main`, `article`, `section`, `footer`.
- Un formular trimite câmpurile care au `name` la adresa din `action`, cu metoda din `method`; `<label for>` se leagă de `id`-ul câmpului.
- CSS: `selector { proprietate: valoare; }`; selectori de tag, `.clasa`, `#id`, descendenți; fiecare element e o cutie cu `padding`, `border` și `margin`.
- Textul venit de la utilizatori se pune în HTML doar după `escape()`; în Django, template-urile fac asta automat.
