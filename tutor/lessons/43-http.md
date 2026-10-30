## Ce este

**HTTP** („HyperText Transfer Protocol”) este limba în care vorbesc browserele și serverele web. Un **client** (de obicei browserul) trimite o **cerere** (în engleză „request”), iar un **server** trimite înapoi un **răspuns** („response”). Așa se întâmplă la fiecare pagină pe care o deschizi.

Când scrii în browser adresa unui articol de pe blogul Anei, browserul trimite un text de felul acesta:

```text
GET /articol/2/ HTTP/1.1
Host: blogul-anei.ro
Accept: text/html
Accept-Language: ro-RO,ro
```

Iar serverul răspunde tot cu text:

```text
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 1834

<!doctype html>
<html lang="ro">
...
```

Primul rând al cererii spune **ce** vrea clientul (metoda `GET` și calea `/articol/2/`). Primul rând al răspunsului spune **cum** a mers (codul `200`, adică „OK”). Urmează câteva **headere** (rânduri `Nume: valoare` cu informații suplimentare), un rând gol și, la răspuns, **corpul**: pagina HTML propriu-zisă (lecția 44).

## De ce contează

Din modulul următor vei construi blogul Anei cu Django. Django e, în esență, un program care primește cereri HTTP și întoarce răspunsuri HTTP: fiecare **view** (lecția 47) e o funcție care primește o cerere și produce un răspuns. Formularele (lecția 55), autentificarea (lecția 57) și publicarea pe internet (lecția 61) se bazează toate pe ce vezi în lecția asta.

Când ceva nu merge într-o aplicație web („pagina dă 404”, „formularul nu se trimite”, „după login ajung pe altă pagină”), răspunsul e aproape mereu în cerere sau în răspunsul HTTP. Dacă știi să le citești, știi unde să cauți.

## Cum funcționează

### Client și server

- **Serverul** e un program care rulează tot timpul și așteaptă cereri, pe un anumit **port** (un număr care identifică programul pe calculatorul respectiv; pentru web, de obicei 80 sau 443).
- **Clientul** se conectează la server, trimite o cerere, primește răspunsul și conexiunea se poate închide.
- Fiecare cerere e **independentă**: serverul nu ține minte singur cererile anterioare. Cum „știe” totuși un site că ești autentificat vei vedea la lecția 57 (cookie-uri și sesiuni).

Clientul nu trebuie să fie un browser. Poate fi și un program Python, cum vei vedea mai jos.

### Anatomia unui URL

Un **URL** e adresa completă a unei resurse. Modulul `urllib.parse` din biblioteca standard îl desface în bucăți:

```python
from urllib.parse import parse_qs, urlsplit

adresa = "https://blogul-anei.ro:443/articol/2/?sursa=newsletter&pagina=1#comentarii"
parti = urlsplit(adresa)
print("schema:   ", parti.scheme)
print("gazda:    ", parti.hostname)
print("port:     ", parti.port)
print("cale:     ", parti.path)
print("parametri:", parti.query)
print("fragment: ", parti.fragment)
print(parse_qs(parti.query))
```

```text
schema:    https
gazda:     blogul-anei.ro
port:      443
cale:      /articol/2/
parametri: sursa=newsletter&pagina=1
fragment:  comentarii
{'sursa': ['newsletter'], 'pagina': ['1']}
```

| Parte | Exemplu | Ce înseamnă |
|---|---|---|
| schema | `https` | protocolul; `https` e HTTP criptat |
| gazda | `blogul-anei.ro` | serverul la care te conectezi |
| port | `443` | lipsește de obicei: implicit 80 pentru `http`, 443 pentru `https` |
| cale | `/articol/2/` | **ce** resursă vrei de pe server; în Django, după cale se alege view-ul (lecția 47) |
| parametri („query string”) | `sursa=newsletter&pagina=1` | perechi `nume=valoare` despărțite prin `&`, după `?` |
| fragment | `comentarii` | după `#`; **nu** ajunge la server, browserul îl folosește ca să sară la o parte a paginii |

`parse_qs()` întoarce liste pentru că același nume poate apărea de mai multe ori (`?eticheta=python&eticheta=django`).

Un URL poate conține doar anumite caractere. Spațiile, diacriticele și semnele cu rol special (`&`, `?`, `#`) se **codifică** cu `%` și cod hexazecimal. Nu le scrii de mână: `urlencode()` și `quote()` o fac pentru tine.

```python
from urllib.parse import quote, urlencode

print(urlencode({"q": "Ana Popescu", "oras": "Iași"}))
print(quote("/căutare/cluj napoca/"))
```

```text
q=Ana+Popescu&oras=Ia%C8%99i
/c%C4%83utare/cluj%20napoca/
```

### Metodele GET și POST

Primul cuvânt din cerere e **metoda**. Două sunt folosite aproape tot timpul:

- **GET** cere o resursă: „dă-mi pagina asta”. Datele, dacă există, merg în URL, ca parametri. O cerere GET **nu ar trebui să modifice** nimic pe server: o poți repeta, o poți salva ca link, browserul o poate trimite din nou fără grijă.
- **POST** trimite date care **schimbă** ceva: un comentariu nou, o comandă, o autentificare. Datele merg în **corpul** cererii, nu în URL.

Regula practică: dacă după cerere ceva e altfel decât înainte (s-a salvat, s-a șters, s-a trimis), folosește POST.

### Răspunsul: coduri de status

Codul de status e un număr din trei cifre. Prima cifră spune categoria:

| Cod | Text | Când apare |
|---|---|---|
| `200` | OK | totul a mers, corpul conține ce ai cerut |
| `301` | Moved Permanently | resursa s-a mutat definitiv la altă adresă (headerul `Location`) |
| `302` | Found | „du-te acum la altă adresă”, de exemplu după trimiterea unui formular |
| `404` | Not Found | nu există nimic la calea cerută |
| `500` | Internal Server Error | programul de pe server a dat o eroare (în Django: o excepție în codul tău) |

Pe scurt: `2xx` succes, `3xx` redirecționare, `4xx` greșeala clientului (a cerut ceva ce nu există sau nu are voie), `5xx` greșeala serverului. Mai des întâlnite sunt și `403` (Forbidden, „nu ai voie”) și `400` (Bad Request, „cerere greșită”).

### Headere

Headerele sunt perechi `Nume: valoare`, câte una pe rând, după primul rând al cererii sau al răspunsului. Câteva pe care le vei întâlni des:

- `Host` (în cerere): numele site-ului cerut; pe același server pot sta mai multe site-uri;
- `Content-Type` (în răspuns sau în cererea POST): ce fel de date sunt în corp: `text/html; charset=utf-8`, `application/json`, `text/css`, `image/png`;
- `Content-Length`: câți **octeți** are corpul;
- `Location` (în răspunsurile `3xx`): adresa la care trebuie să meargă clientul;
- `Cookie` și `Set-Cookie`: mici bucăți de text pe care browserul le păstrează și le retrimite (lecția 57).

### Un server adevărat, în Python

Biblioteca standard are un server HTTP simplu, în modulul `http.server`. Ca să nu repetăm în fiecare exemplu codul care îl pornește, îl punem într-un modul mic (lecția 29), `server_mic.py`:

<!-- fisier: server_mic.py -->
```python
"""Pornește un server HTTP mic, în fundal, pe 127.0.0.1:8765 (pentru exemplele din lecție)."""
import threading
from http.server import HTTPServer

ADRESA = "http://127.0.0.1:8765"


def porneste_server(clasa_cereri):
    """Pornește serverul și îl întoarce; îl oprești cu server.shutdown()."""
    server = HTTPServer(("127.0.0.1", 8765), clasa_cereri)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
```

`127.0.0.1` înseamnă „calculatorul acesta” (îi mai spune și `localhost`). `threading` pornește serverul **în paralel** cu restul programului, într-un fir de execuție separat. Firele de execuție nu fac parte din curs; aici le folosim doar ca să avem clientul și serverul în același program. În Django nu vei avea nevoie de ele: serverul pornește singur, cu `runserver` (lecția 45).

Serverul primește cererile și le dă unei clase scrise de tine, derivată din `BaseHTTPRequestHandler` (moștenire, lecția 34). Pentru fiecare cerere GET, se apelează metoda `do_GET()`:

```python
from http.server import BaseHTTPRequestHandler
from urllib.request import urlopen

from server_mic import ADRESA, porneste_server


class Salut(BaseHTTPRequestHandler):
    def do_GET(self):
        corp = f"Salut! Ai cerut calea {self.path}".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(corp)))
        self.end_headers()
        self.wfile.write(corp)

    def log_message(self, *args):
        pass  # fără jurnalul obișnuit, cu data și ora fiecărei cereri


server = porneste_server(Salut)
with urlopen(ADRESA + "/articol/2/?sursa=newsletter") as raspuns:
    print(raspuns.status, raspuns.reason)
    print(raspuns.headers["Content-Type"])
    print(raspuns.read().decode("utf-8"))
server.shutdown()
```

```text
200 OK
text/plain; charset=utf-8
Salut! Ai cerut calea /articol/2/?sursa=newsletter
```

Partea de server, pas cu pas:
1. `self.path` e calea cerută, cu tot cu parametri;
2. `send_response(200)` scrie primul rând al răspunsului; `send_header()` adaugă câte un header; `end_headers()` pune rândul gol care desparte headerele de corp;
3. `self.wfile.write()` trimite corpul. Rețeaua transportă **octeți**, nu text, așa că textul e transformat întâi cu `.encode("utf-8")` (ca la fișiere, lecția 27). Pe partea cealaltă, `.decode("utf-8")` face transformarea inversă. Un șir de octeți are tipul `bytes`; când îl scrii direct în cod, are un `b` în față: `b"text"`.

Partea de client: `urlopen()` din `urllib.request` trimite cererea și întoarce răspunsul, pe care îl folosești cu `with` (lecția 39). Aceeași cerere o poate face și browserul; diferența e că browserul desenează HTML-ul, în loc să-l afișeze ca text.

### Când răspunsul nu e 200

Pentru coduri `4xx` și `5xx`, `urlopen()` ridică o excepție `HTTPError` (lecția 24), care conține codul și corpul răspunsului:

```python
from http.server import BaseHTTPRequestHandler
from urllib.error import HTTPError
from urllib.request import urlopen

from server_mic import ADRESA, porneste_server


class Pagini(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Prima pagina")
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass


server = porneste_server(Pagini)
for cale in ["/", "/nu-exista/"]:
    try:
        with urlopen(ADRESA + cale) as raspuns:
            print(cale, "->", raspuns.status, raspuns.read().decode("utf-8"))
    except HTTPError as eroare:
        print(cale, "->", eroare.code, eroare.reason)
server.shutdown()
```

```text
/ -> 200 Prima pagina
/nu-exista/ -> 404 Not Found
```

`send_error(404)` trimite un răspuns complet de eroare, cu o mică pagină HTML în corp. În `b"Prima pagina"` am evitat diacriticele: în `b"..."` poți scrie direct doar caractere ASCII; pentru restul folosești `"...".encode("utf-8")`.

### Formularele HTML sunt cereri HTTP

Un formular dintr-o pagină (lecția 44) nu face nimic magic: când apeși butonul, browserul construiește o cerere HTTP din câmpurile lui. Atributul `name` al fiecărui câmp devine numele parametrului.

Un formular de căutare, cu `method="get"`:

```html
<form action="/cauta/" method="get">
  <input type="text" name="q">
  <button type="submit">Caută</button>
</form>
```

Dacă scrii „python django” și apeși „Caută”, browserul merge la `/cauta/?q=python+django`: datele ajung în URL. Rezultatul căutării poate fi salvat ca link sau trimis unui prieten.

Formularul de comentariu de pe blogul Anei, cu `method="post"`:

```html
<form action="/articol/2/comentariu/" method="post">
  <input type="text" name="autor">
  <textarea name="text"></textarea>
  <button type="submit">Trimite</button>
</form>
```

Aici datele merg în corpul cererii, codificate exact ca parametrii unui URL. Le poți construi tu, cu `urlencode()`:

```python
from urllib.parse import urlencode

corp = urlencode({"autor": "Mihai", "text": "Foarte bun articol!"})
print(corp)
print(len(corp.encode("utf-8")), "octeți")
```

```text
autor=Mihai&text=Foarte+bun+articol%21
38 octeți
```

Cererea trimisă de browser arată așa:

```text
POST /articol/2/comentariu/ HTTP/1.1
Host: blogul-anei.ro
Content-Type: application/x-www-form-urlencoded
Content-Length: 38

autor=Mihai&text=Foarte+bun+articol%21
```

După ce salvează comentariul, serverul răspunde de obicei cu `302` și `Location: /articol/2/`, adică „du-te înapoi la articol”. Browserul face singur o nouă cerere GET la acea adresă. Tiparul se numește **POST-redirect-GET** și împiedică retrimiterea comentariului dacă utilizatorul reîncarcă pagina. Îl vei folosi în Django la lecția 55.

### Ce se întâmplă „pe dedesubt”: HTTP e doar text pe o conexiune

`urlopen()` și browserul ascund detaliile, dar dedesubt e foarte simplu: clientul deschide o conexiune la server (un **socket**), scrie textul cererii și citește textul răspunsului. Poți face asta de mână, cu modulul `socket`:

```python
import socket
from http.server import BaseHTTPRequestHandler

from server_mic import porneste_server


class Salut(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Bună de la server!".encode("utf-8"))

    def log_message(self, *args):
        pass


server = porneste_server(Salut)
cerere = b"GET /articol/2/ HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n"
with socket.create_connection(("127.0.0.1", 8765)) as conexiune:
    conexiune.sendall(cerere)
    raspuns = b""
    while bucata := conexiune.recv(1024):
        raspuns += bucata
server.shutdown()

antet, corp = raspuns.decode("utf-8").split("\r\n\r\n", 1)
randuri = antet.split("\r\n")
print("Primul rând:", randuri[0])
print("Headere:", [rand.split(":")[0] for rand in randuri[1:]])
print("Corp:", corp)
```

```text
Primul rând: HTTP/1.0 200 OK
Headere: ['Server', 'Date', 'Content-Type']
Corp: Bună de la server!
```

Câteva observații:
- rândurile din HTTP se termină cu `\r\n` (două caractere: „întoarcere la început de rând” și rând nou), iar headerele se termină cu un rând gol, adică `\r\n\r\n`;
- serverul din biblioteca standard răspunde cu versiunea mai veche `HTTP/1.0`, chiar dacă cererea a fost `HTTP/1.1`; pentru exemplele noastre nu contează;
- `send_response()` a adăugat singur headerele `Server` și `Date` (le-am afișat doar numele, pentru că valorile se schimbă la fiecare rulare);
- `while bucata := conexiune.recv(1024):` citește până când serverul închide conexiunea. Operatorul `:=` atribuie și întoarce valoarea în același timp; e o scriere scurtă pe care o vei întâlni în codul altora, dar n-o vei folosi des.

HTTPS adaugă peste această conexiune un strat de criptare, ca nimeni de pe drum să nu poată citi sau modifica textul. Conținutul cererilor rămâne același.

## Exemplu complet

O versiune foarte mică a blogului Anei, fără Django: articolele stau într-un dicționar, iar serverul răspunde la trei feluri de cereri:
- `GET /`: lista articolelor;
- `GET /articol/<nr>/`: un articol, cu comentariile lui (sau `404`);
- `POST /articol/<nr>/comentariu/`: adaugă un comentariu, apoi redirecționează (`302`) înapoi la articol.

<!-- fisier: blog_mic.py -->
```python
from http.server import BaseHTTPRequestHandler
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode
from urllib.request import urlopen

from server_mic import ADRESA, porneste_server

articole = {
    1: {"titlu": "Primul meu program în Python", "comentarii": []},
    2: {"titlu": "De ce am ales Django", "comentarii": []},
}


class Blog(BaseHTTPRequestHandler):
    def raspunde(self, cod, text):
        corp = text.encode("utf-8")
        self.send_response(cod)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(corp)))
        self.end_headers()
        self.wfile.write(corp)

    def numar_articol(self):
        """/articol/2/... -> 2; pentru orice altă cale, None."""
        bucati = self.path.strip("/").split("/")
        if len(bucati) >= 2 and bucati[0] == "articol" and bucati[1].isdigit():
            return int(bucati[1])
        return None

    def do_GET(self):
        if self.path == "/":
            linii = [f"{nr}. {articol['titlu']}" for nr, articol in articole.items()]
            self.raspunde(200, "\n".join(linii))
            return
        nr = self.numar_articol()
        if nr not in articole:
            self.raspunde(404, "Articolul nu există.")
            return
        articol = articole[nr]
        linii = [articol["titlu"], f"Comentarii: {len(articol['comentarii'])}"]
        linii += [f"- {c['autor']}: {c['text']}" for c in articol["comentarii"]]
        self.raspunde(200, "\n".join(linii))

    def do_POST(self):
        nr = self.numar_articol()
        if nr not in articole or not self.path.endswith("/comentariu/"):
            self.raspunde(404, "Nu există.")
            return
        lungime = int(self.headers["Content-Length"])
        date = parse_qs(self.rfile.read(lungime).decode("utf-8"))
        articole[nr]["comentarii"].append({"autor": date["autor"][0], "text": date["text"][0]})
        self.send_response(302)
        self.send_header("Location", f"/articol/{nr}/")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *args):
        pass


def cere(cale, date=None):
    """Trimite GET (sau POST, dacă primește date) și afișează ce s-a întâmplat."""
    corp = urlencode(date).encode("utf-8") if date else None
    metoda = "POST" if date else "GET"
    try:
        with urlopen(ADRESA + cale, data=corp) as raspuns:
            final = raspuns.url.replace(ADRESA, "")
            print(f"{metoda} {cale} -> {raspuns.status} (pagina finală: {final})")
            print(raspuns.read().decode("utf-8"))
    except HTTPError as eroare:
        print(f"{metoda} {cale} -> {eroare.code}")
        print(eroare.read().decode("utf-8"))
    print()


server = porneste_server(Blog)
cere("/")
cere("/articol/2/")
cere("/articol/2/comentariu/", {"autor": "Mihai", "text": "Foarte bun articol!"})
cere("/articol/7/")
server.shutdown()
```

```text
GET / -> 200 (pagina finală: /)
1. Primul meu program în Python
2. De ce am ales Django

GET /articol/2/ -> 200 (pagina finală: /articol/2/)
De ce am ales Django
Comentarii: 0

POST /articol/2/comentariu/ -> 200 (pagina finală: /articol/2/)
De ce am ales Django
Comentarii: 1
- Mihai: Foarte bun articol!

GET /articol/7/ -> 404
Articolul nu există.
```

Observă:
- cererea POST a primit de la server `302`, dar clientul a urmat singur redirecționarea, cu o cerere GET, așa că noi vedem `200` și pagina finală `/articol/2/`. Exact asta face și browserul;
- `self.rfile.read(lungime)` citește corpul cererii; câți octeți să citească aflăm din headerul `Content-Length`;
- tot ce face aici codul de mână (desfacerea căii în bucăți, alegerea funcției după cale și metodă, codificarea răspunsului) va face Django pentru tine: căile le vei descrie în `urls.py`, iar răspunsurile le vei scrie în view-uri (lecția 47).

## Greșeli frecvente

### 1. URL fără schemă

<!-- fisier: client.py -->
```python
from urllib.request import urlopen

urlopen("127.0.0.1:8765/articol/2/")
```

```text
Traceback (most recent call last):
  File "client.py", line 3, in <module>
    urlopen("127.0.0.1:8765/articol/2/")
urllib.error.URLError: <urlopen error unknown url type: 127.0.0.1>
```

(Am scurtat tracebackul: între rânduri apar mai multe cadre din interiorul modulului `urllib`.) Fără `http://`, Python a citit `127.0.0.1` ca și cum ar fi schema (tot ce e înainte de primul `:`) și nu cunoaște o asemenea schemă. Browserul completează singur `http://` sau `https://`, dar un program nu. Scrie mereu adresa completă: `urlopen("http://127.0.0.1:8765/articol/2/")`.

### 2. Spații și diacritice puse direct în URL

<!-- fisier: client.py -->
```python
from urllib.request import urlopen

urlopen("http://127.0.0.1:8765/cauta/?q=Ana Popescu")
```

```text
Traceback (most recent call last):
  File "client.py", line 3, in <module>
    urlopen("http://127.0.0.1:8765/cauta/?q=Ana Popescu")
http.client.InvalidURL: URL can't contain control characters. '/cauta/?q=Ana Popescu' (found at least ' ')
```

(Am scurtat tracebackul: între rânduri apar mai multe cadre din interiorul modulelor `urllib` și `http`.) Un URL nu poate conține spații, iar diacriticele scrise direct dau și ele eroare (alta, de codificare). Construiește parametrii cu `urlencode()`, care îi codifică pe toți:

```python
from urllib.parse import urlencode

print("http://127.0.0.1:8765/cauta/?" + urlencode({"q": "Ana Popescu"}))
```

```text
http://127.0.0.1:8765/cauta/?q=Ana+Popescu
```

### 3. Un 404 neprins

<!-- fisier: client.py -->
```python
from http.server import BaseHTTPRequestHandler
from urllib.request import urlopen

from server_mic import ADRESA, porneste_server


class Gol(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_error(404)

    def log_message(self, *args):
        pass


server = porneste_server(Gol)
urlopen(ADRESA + "/articol/7/")
```

```text
Traceback (most recent call last):
  File "client.py", line 16, in <module>
    urlopen(ADRESA + "/articol/7/")
urllib.error.HTTPError: HTTP Error 404: Not Found
```

(Și aici am scurtat cadrele din `urllib`.) Pentru `urlopen()`, un cod `4xx` sau `5xx` e o excepție, nu un răspuns obișnuit. Dacă pagina poate lipsi, prinde `HTTPError`, ca în exemplul complet.

### 4. Date sensibile într-o cerere GET

```python
from urllib.parse import parse_qs, urlsplit

adresa = "http://blogul-anei.ro/autentificare/?utilizator=ana&parola=Secret2026"
print(parse_qs(urlsplit(adresa).query))
```

```text
{'utilizator': ['ana'], 'parola': ['Secret2026']}
```

Nu e o eroare de Python, dar e o greșeală gravă: tot ce e în URL rămâne în istoricul browserului, în jurnalele serverului și poate ajunge la alte site-uri. Parolele și alte date sensibile se trimit **doar** cu POST, în corpul cererii, și **doar** prin HTTPS. Formularul de autentificare din Django (lecția 57) face exact asta.

### 5. Un link care modifică date

```html
<a href="/articol/2/sterge/">Șterge articolul</a>
```

Un link face o cerere GET. Browserele și alte programe pot încărca linkurile „din proprie inițiativă” (de exemplu, ca să pregătească pagina din timp), iar un robot de căutare care le urmărește pe toate ar șterge articole fără ca cineva să apese ceva. Orice acțiune care modifică date trebuie făcută cu un formular POST:

```html
<form action="/articol/2/sterge/" method="post">
  <button type="submit">Șterge articolul</button>
</form>
```

## Exercițiu

În `capitole/43-http/http_exercitii.py` (fișierul nu se poate numi `http.py`: ar „ascunde” modulul `http` din biblioteca standard, pe care chiar îl folosești, exact ca la lecția 36 cu `dataclasses`):

1. scrie o funcție `descrie_url(adresa)` care afișează schema, gazda, portul (sau portul implicit, dacă lipsește: 80 pentru `http`, 443 pentru `https`), calea și fiecare parametru pe câte un rând; încearcă-o pe trei adrese diferite, dintre care una cu diacritice codificate (`?oras=Ia%C8%99i`), și afișează valoarea decodificată (`parse_qs` o decodifică singur);
2. pornind de la exemplul complet (copiază și `server_mic.py` în același folder), adaugă blogului:
   - calea `GET /despre/`, care răspunde cu un text despre Ana (25 de ani, din Cluj);
   - parametrul `?cauta=` pe `GET /`, care afișează doar articolele al căror titlu conține textul căutat, fără să conteze literele mari și mici;
   - pentru un comentariu cu câmpul `autor` gol sau lipsă, răspuns `400` cu un mesaj, în loc de salvare;
3. testează fiecare cale nouă cu funcția `cere()`, inclusiv un caz care dă `400` și unul care dă `404`.

Bonus: deschide blogul din browser. Pentru asta, serverul trebuie să asculte pe `0.0.0.0:8000` (adresa pe care PyTutor o face vizibilă din browser) și să nu se oprească imediat. La finalul fișierului, în locul cererilor de test și al lui `porneste_server(...)`, scrie `HTTPServer(("0.0.0.0", 8000), Blog).serve_forever()` (cu `from http.server import HTTPServer` sus) și rulează fișierul. Adresa la care îl deschizi apare în bara terminalului („server: localhost:...”); îl oprești cu **Oprește** sau Ctrl+C.

## Pe scurt

- HTTP e un dialog de tip cerere–răspuns: clientul (browserul) cere, serverul răspunde; fiecare cerere e independentă.
- Un URL are schemă, gazdă, port, cale, parametri (`?a=1&b=2`) și fragment (`#...`, care nu ajunge la server); `urllib.parse` le desface și le codifică.
- GET cere o resursă și nu ar trebui să modifice nimic; POST trimite date care schimbă ceva, în corpul cererii.
- Codul de status spune cum a mers: `200` OK, `301`/`302` redirecționare (cu `Location`), `404` nu există, `500` eroare pe server.
- Headerele (`Content-Type`, `Content-Length`, `Location`, `Cookie`) descriu cererea și răspunsul; corpul conține datele.
- Un formular HTML e doar o cerere HTTP construită din câmpurile lui; după un POST reușit, serverul redirecționează (POST-redirect-GET).
