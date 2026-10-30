# Plan: lecțiile scrise în proiect (nu generate de AI la cerere)

**Stare:** gata — toate cele 61 de lecții sunt scrise, verificate automat, recenzate și încărcate în aplicație (2026-10-30).
**Cum pornești:** îi spui lui Claude Code: „Scrie lecțiile pentru modulul 1, după `docs/PLAN-LECTII.md`.” Continui cu modulul următor în aceeași formă.

## Decizia

Cele 61 de lecții din curriculum se scriu aici, în proiect, ca fișiere Markdown verificate, nu de `gpt-4.1` la prima deschidere.
Generarea cu AI rămâne doar ca **rezervă**, pentru o lecție care încă nu are fișier.

## De ce

| | Scrise aici | Generate de AI în aplicație |
|---|---|---|
| Calitate | lecții complete, cu stil unitar; fiecare trimite la cele dinainte | ~1.500 de tokeni, fiecare scrisă separat |
| Codul din exemple | **rulat și verificat** înainte de salvare | neverificat, poate conține greșeli |
| Control | le citești și le corectezi înainte să le vadă elevii; sunt în proiect | apar direct la elev |
| Primul elev care o deschide | o vede imediat | așteaptă ~20 s cât se scrie |
| Cost OpenAI | £0 | ~£0,01 pe lecție, ~£0,65 pentru toate, o singură dată |
| Cost real | timp și consum din abonamentul Claude Code | — |

Banii contează puțin. Motivele sunt calitatea și exemplele verificate.

## Unde stau lecțiile

- **Fișierele:** câte unul pe lecție, în `tutor/lessons/NN-slug.md`, de exemplu `tutor/lessons/04-stringuri.md`.
  - `NN` e numărul lecției în curriculum, la fel ca la folderele de cod `capitole/NN-slug/`.
- **Încărcarea în baza de date:** o comandă nouă, `python manage.py load_lessons`, copiază fișierele în `Topic.lesson`.
  - Pune `lesson_model = "manual"`.
  - Rulează și la deploy, după `migrate`.
- **Regula de prioritate:**
  - O lecție cu `lesson_model = "manual"` nu e niciodată suprascrisă de AI.
  - Acțiunea din admin „Șterge lecția” nu se aplică lecțiilor manuale; pentru ele se editează fișierul.
- **Lecțiile generate deja:** cele 9 lecții scrise de AI (vezi tabelul) se înlocuiesc pe măsură ce le scriem aici.

## Structura unei lecții

Aceleași secțiuni ca acum, ca pagina de progres să rămână la fel. Fiecare lecție începe direct cu `## Ce este`.

1. `## Ce este`: definiția pe înțelesul unui începător.
2. `## De ce contează`: la ce folosește într-un program real.
3. `## Cum funcționează`: explicația principală, cu exemple mici comentate și ce se întâmplă „pe dedesubt” unde ajută.
4. `## Exemplu complet`: un program scurt și realist, **cu output-ul lui real**.
5. `## Greșeli frecvente`: 3–5 greșeli, fiecare cu codul greșit, **eroarea reală** și varianta corectă.
6. `## Exercițiu`: o sarcină pentru fișierul capitolului (`capitole/NN-slug/<slug>.py`), fără soluție.
7. `## Pe scurt`: 3–6 puncte de reținut.

## Reguli de scriere

- **Limba:** româna, cu diacritice. Termenii tehnici rămân în engleză și se explică în română (ex. „list comprehension”, „view”).
- **Nivelul:** explicat de la zero, dar nu infantil. O lecție se bazează doar pe lecțiile **dinaintea** ei; dacă e nevoie de ceva de mai târziu, se spune explicit („vom vedea la lecția 18”).
- **Codul:**
  - conform PEP 8;
  - blocuri cu limbaj (```python, ```bash, ```html);
  - nume de variabile în română, la fel ca exercițiile tutorelui (ex. `nume`, `varsta`, `oras`).
- **Continuitatea:** exemplele din același modul pot folosi aceleași personaje sau date (ex. o listă de cumpărături), ca elevul să recunoască contextul.
- **Lungimea:** cât e nevoie pentru subiect. Orientativ 600–1.500 de cuvinte; lecțiile Django pot fi mai lungi.
- **Django (lecțiile 45–61):** lecțiile construiesc pe rând **același proiect**, un blog simplu, ca fiecare lecție să adauge ceva la ce există.

## Verificarea, obligatorie înainte de salvare

- Fiecare bloc ```python care e program complet **se rulează** cu Python 3.12, în containerul `pytutor-sandbox`. Output-ul din lecție trebuie să fie cel real.
- La „Greșeli frecvente”, eroarea arătată e cea pe care o dă **efectiv** Python: tipul erorii și mesajul.
- Exemplele Django se verifică într-un proiect temporar: `startproject`, `migrate`, `runserver` sau `manage.py test`, după caz.
- Lecțiile se citesc o dată cap-coadă pe modul, pentru continuitate și ca să nu existe trimiteri la lucruri nepredate.

## Cum lucrăm, pe module

1. Claude scrie lecțiile unui modul în `tutor/lessons/` și verifică tot codul.
2. Rulează `load_lessons` și verifică pagina `/progres/` în browser.
3. Tu le citești și ceri modificări unde e cazul.
4. Se bifează în tabelul de mai jos și se trece la modulul următor.

La primul modul se face și partea tehnică: comanda `load_lessons`, regula „manual nu se suprascrie” și acțiunea din admin.

## Lecțiile

Stare: ⬜ de scris · 🤖 generată de AI (de înlocuit) · 📝 scrisă aici, verificată, așteaptă recitirea · ✅ recitită și aprobată (01–44: recitite de Claude la cererea ta, 2026-10-29 — două recenzii independente, o trecere de claritate, verificare a afișării; 45–61: recenzii independente pe module, verificare automată și a afișării, 2026-10-29/30)

### 1. Bazele Python
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 01 | Primul program | `primul-program` | ✅ |
| 02 | Variabile și atribuire | `variabile` | ✅ |
| 03 | Numere și operatori | `numere` | ✅ |
| 04 | Șiruri de caractere | `stringuri` | ✅ |
| 05 | Formatarea textului | `f-strings` | ✅ |
| 06 | input() și conversii de tip | `input-conversii` | ✅ |
| 07 | Boolean și comparații | `bool-comparatii` | ✅ |

### 2. Controlul fluxului
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 08 | Decizii: if / elif / else | `if-else` | ✅ |
| 09 | Bucla while | `while` | ✅ |
| 10 | Bucla for și range() | `for-range` | ✅ |
| 11 | break, continue și else la bucle | `break-continue` | ✅ |

### 3. Colecții de date
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 12 | Liste | `liste` | ✅ |
| 13 | Tupluri și despachetare | `tupluri` | ✅ |
| 14 | Dicționare | `dictionare` | ✅ |
| 15 | Seturi | `seturi` | ✅ |
| 16 | Comprehensions | `comprehensions` | ✅ |
| 17 | Iterare avansată | `iterare-avansata` | ✅ |

### 4. Funcții
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 18 | Definirea funcțiilor | `functii-definire` | ✅ |
| 19 | Argumente avansate | `argumente` | ✅ |
| 20 | Domeniul variabilelor | `scope` | ✅ |
| 21 | Funcții ca valori și lambda | `lambda-functii-valori` | ✅ |
| 22 | Docstrings și type hints | `docstrings-type-hints` | ✅ |

### 5. Erori și depanare
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 23 | Citirea unui traceback | `traceback` | ✅ |
| 24 | try / except / else / finally | `try-except` | ✅ |
| 25 | Ridicarea excepțiilor | `raise-exceptii` | ✅ |
| 26 | Tehnici de depanare | `depanare` | ✅ |

### 6. Fișiere, module și pachete
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 27 | Citirea și scrierea fișierelor | `fisiere` | ✅ |
| 28 | JSON și CSV | `json-csv` | ✅ |
| 29 | Module și import | `module-import` | ✅ |
| 30 | pip și medii virtuale | `pip-venv` | ✅ |
| 31 | Biblioteca standard | `biblioteca-standard` | ✅ |

### 7. Programare orientată pe obiecte
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 32 | Clase și obiecte | `clase-obiecte` | ✅ |
| 33 | Atribute și metode | `atribute-metode` | ✅ |
| 34 | Moștenire | `mostenire` | ✅ |
| 35 | Metode speciale | `metode-speciale` | ✅ |
| 36 | Dataclasses | `dataclasses` | ✅ |

### 8. Python intermediar
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 37 | Iteratori și generatori | `iteratori-generatori` | ✅ |
| 38 | Decoratori | `decoratori` | ✅ |
| 39 | Context managers | `context-managers` | ✅ |

### 9. Cod de calitate
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 40 | Stil și PEP 8 | `pep8-stil` | ✅ |
| 41 | Testare automată | `testare` | ✅ |
| 42 | Git, pe scurt | `git` | ✅ |

### 10. Cum funcționează web-ul
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 43 | HTTP: cerere și răspuns | `http` | ✅ |
| 44 | HTML și CSS de bază | `html-css` | ✅ |

### 11. Django: fundamentele
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 45 | Proiect și aplicații | `django-proiect` | ✅ |
| 46 | settings.py | `django-settings` | ✅ |
| 47 | URL-uri și view-uri | `django-urls-views` | ✅ |
| 48 | Template-uri | `django-templates` | ✅ |
| 49 | Fișiere statice | `django-static` | ✅ |

### 12. Django: date și modele
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 50 | Modele | `django-modele` | ✅ |
| 51 | Migrări | `django-migrari` | ✅ |
| 52 | Interogări cu ORM | `django-orm` | ✅ |
| 53 | Relații între modele | `django-relatii` | ✅ |
| 54 | Panoul de admin | `django-admin` | ✅ |

### 13. Django: aplicații interactive
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 55 | Formulare | `django-forms` | ✅ |
| 56 | ModelForm | `django-modelforms` | ✅ |
| 57 | Autentificare | `django-auth` | ✅ |
| 58 | Class-based views | `django-cbv` | ✅ |

### 14. Django: mai departe
| # | Lecție | Slug | Stare |
|---|---|---|---|
| 59 | Testarea în Django | `django-teste` | ✅ |
| 60 | API-uri cu Django REST Framework | `django-api` | ✅ |
| 61 | Publicarea aplicației | `django-deploy` | ✅ |
