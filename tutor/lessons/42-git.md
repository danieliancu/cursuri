## Ce este

**Git** este un sistem de **control al versiunilor**: ține minte istoria unui proiect, adică fiecare stare salvată a fișierelor, cine a făcut-o, când și de ce. Poți vedea oricând ce s-a schimbat, te poți întoarce la o versiune veche și poți lucra la mai multe lucruri în paralel fără să le amesteci.

Câțiva termeni de bază:
- **repository** (prescurtat „repo”): folderul proiectului urmărit de git, împreună cu istoria lui;
- **commit**: o „fotografie” salvată a proiectului, cu un mesaj care spune ce s-a schimbat;
- **branch** (ramură): o linie separată de commit-uri, ca să lucrezi la ceva nou fără să atingi versiunea principală.

Git se folosește din terminal, cu comanda `git`. În terminalul din PyTutor e deja instalat.

## De ce contează

Fără git, „versiunile” arată așa: `jurnal.py`, `jurnal_vechi.py`, `jurnal_final.py`, `jurnal_final2.py`. Nu mai știi care e cea bună și ce s-a schimbat între ele. Cu git, ai un singur fișier și o istorie clară.

Git e și baza colaborării: aproape orice echipă de programatori își ține codul într-un repository, de obicei publicat pe un site ca **GitHub** sau **GitLab**. Și publicarea unei aplicații Django pe un server (lecția 61) pornește aproape mereu de la un repository git.

## Cum funcționează

### Configurarea, o singură dată

Fiecare commit înregistrează autorul. Înainte de primul commit, îi spui lui git cine ești:

```bash
git config --global user.name "Ana Popescu"
git config --global user.email "ana@exemplu.ro"
```

`--global` înseamnă „pentru toate proiectele mele”. Configurarea se păstrează până când mediul tău din PyTutor e refăcut (lecția 30); dacă git îți spune la un commit „Author identity unknown”, rulează din nou cele două comenzi.

### Un repository nou

Proiectul Anei, jurnalul de cheltuieli, are deocamdată un singur fișier:

<!-- fisier: jurnal.py -->
```python
def adauga(jurnal, descriere, suma):
    jurnal.append({"descriere": descriere, "suma": suma})


def total(jurnal):
    return sum(c["suma"] for c in jurnal)
```

În folderul proiectului, `git init` creează repository-ul:

<!-- ruleaza -->
```bash
git init -q
git config core.fileMode false
git status
```

```text
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	jurnal.py

nothing added to commit but untracked files present (use "git add" to track)
```

Ce se întâmplă:
- `git init` creează un folder ascuns, `.git`, în care git ține toată istoria. Fără `-q` („quiet”), ar fi afișat și o confirmare: `Initialized empty Git repository in .../.git/`;
- `git config core.fileMode false` e o setare necesară în PyTutor: proiectele tale sunt păstrate pe Windows, unde toate fișierele par „executabile”, iar fără ea git le-ar salva ca executabile și ar raporta schimbări care nu există. Setarea se face o dată pentru fiecare repository, imediat după `git init`, pentru că `git init` o scrie singur cu valoarea greșită;
- `git status` e comanda pe care o vei rula cel mai des: spune pe ce ramură ești (`main`) și ce fișiere sunt noi sau modificate. Aici, `jurnal.py` e **untracked**: git îl vede, dar încă nu-l urmărește.

### add și commit: cele două etape

Un commit se face în doi pași:
1. `git add` pune modificările în **zona de pregătire** (în engleză „staging area”), adică alegi ce intră în următorul commit;
2. `git commit` salvează tot ce e în zona de pregătire, cu un mesaj.

<!-- ruleaza -->
```bash
git add jurnal.py
git status
```

```text
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   jurnal.py

```

<!-- ruleaza -->
```bash
git commit -m "Adaugă funcțiile de bază ale jurnalului"
```

```text
[main (root-commit) 4f1c2a9] Adaugă funcțiile de bază ale jurnalului
 1 file changed, 6 insertions(+)
 create mode 100644 jurnal.py
```

Codul `4f1c2a9` e începutul **hash-ului** commit-ului, un identificator unic calculat din conținut. La tine va fi altul, pentru că depinde și de autor și de moment. Mesajul unui commit spune **ce face** schimbarea, la prezent: „Adaugă...”, „Repară...”, „Mută...”.

De ce doi pași? Ca să poți face commit-uri mici și clare. Dacă ai modificat trei fișiere pentru două lucruri diferite, faci două commit-uri, fiecare cu fișierele lui.

### Ce s-a schimbat: git diff

Ana adaugă o categorie la fiecare cheltuială:

<!-- fisier: jurnal.py -->
```python
def adauga(jurnal, descriere, suma, categorie="altele"):
    jurnal.append({"descriere": descriere, "suma": suma, "categorie": categorie})


def total(jurnal):
    return sum(c["suma"] for c in jurnal)
```

<!-- ruleaza -->
```bash
git diff
```

```text
diff --git a/jurnal.py b/jurnal.py
index 1a2b3c4..5d6e7f8 100644
--- a/jurnal.py
+++ b/jurnal.py
@@ -1,5 +1,5 @@
-def adauga(jurnal, descriere, suma):
-    jurnal.append({"descriere": descriere, "suma": suma})
+def adauga(jurnal, descriere, suma, categorie="altele"):
+    jurnal.append({"descriere": descriere, "suma": suma, "categorie": categorie})
 
 
 def total(jurnal):
```

Rândurile cu `-` au fost șterse, cele cu `+` adăugate, iar celelalte sunt context. Rulează `git diff` înainte de fiecare commit: e cel mai simplu mod de a vedea ce urmează să salvezi.

<!-- ruleaza -->
```bash
git add jurnal.py
git commit -q -m "Adaugă categoria la cheltuieli"
git log --oneline
```

```text
8b3e1d0 Adaugă categoria la cheltuieli
4f1c2a9 Adaugă funcțiile de bază ale jurnalului
```

`git log --oneline` arată istoria, câte un commit pe rând, cel mai nou sus. Fără `--oneline` vezi și autorul și data fiecărui commit.

### .gitignore: ce nu intră în repository

Unele fișiere nu au ce căuta în istorie: folderul `__pycache__` (lecția 29), creat automat de Python, mediul virtual `.venv/` (lecția 30), fișiere cu parole. Când Python importă `jurnal.py`, apare imediat `__pycache__`:

<!-- ruleaza -->
```bash
python -c "import jurnal"
git status --short
```

```text
?? __pycache__/
```

`git status --short` e forma scurtă: `??` înseamnă „neurmărit”. Fișierul `.gitignore` din rădăcina proiectului listează ce trebuie ignorat, câte un tipar pe rând. Îl poți crea în editor sau din terminal (`>` creează fișierul, `>>` adaugă la final):

<!-- ruleaza -->
```bash
echo "__pycache__/" > .gitignore
echo ".venv/" >> .gitignore
echo ".env" >> .gitignore
cat .gitignore
git status --short
```

```text
__pycache__/
.venv/
.env
?? .gitignore
```

`__pycache__/` a dispărut din listă. `.gitignore` însuși **se** pune în repository, ca toți cei care lucrează la proiect să ignore aceleași lucruri:

<!-- ruleaza -->
```bash
git add .gitignore
git commit -q -m "Ignoră __pycache__, .venv și .env"
git status
```

```text
On branch main
nothing to commit, working tree clean
```

„Working tree clean” înseamnă că nu există nicio modificare nesalvată.

### Anularea modificărilor: git restore

Dacă ai stricat un fișier și vrei înapoi versiunea din ultimul commit:

<!-- ruleaza -->
```bash
echo "cod stricat" >> jurnal.py
git status --short
git restore jurnal.py
git status --short
tail -n 2 jurnal.py
```

```text
 M jurnal.py
def total(jurnal):
    return sum(c["suma"] for c in jurnal)
```

` M` înseamnă „modificat”. După `git restore`, fișierul a revenit la versiunea salvată, iar `git status --short` nu mai afișează nimic. Atenție: modificările anulate așa nu se mai pot recupera.

### Ramuri: git switch și git merge

O ramură îți permite să lucrezi la ceva nou fără să atingi `main`, versiunea care trebuie să meargă mereu. `git switch -c nume` creează o ramură nouă și trece pe ea:

<!-- ruleaza -->
```bash
git switch -c raport
git branch
```

```text
Switched to a new branch 'raport'
  main
* raport
```

`git branch` listează ramurile; steluța arată ramura curentă. Commit-urile făcute acum ajung doar pe `raport`. Vei vedea tot fluxul în exemplul complet.

### Ce se întâmplă „pe dedesubt”: commit-urile sunt fotografii legate între ele

Fiecare commit păstrează o fotografie completă a fișierelor urmărite (git nu copiază de fiecare dată fișierele neschimbate, ci refolosește ce are deja), plus mesajul, autorul, data și o legătură spre commit-ul **părinte**, cel dinaintea lui. Hash-ul e calculat din toate acestea, deci orice schimbare, oricât de mică, dă alt hash. De aceea istoria nu poate fi modificată pe ascuns.

O ramură e doar o **etichetă** care arată spre un commit, la fel cum o variabilă e o etichetă pe un obiect (lecția 2). Când faci un commit pe o ramură, eticheta se mută pe commit-ul nou. Ramura `main` și ramura `raport` sunt două etichete; crearea unei ramuri nu copiază nimic, de aceea e instantanee.

Totul stă în folderul `.git`. Dacă îl ștergi, pierzi istoria; fișierele proiectului rămân.

## Exemplu complet

Pe ramura `raport`, Ana adaugă o funcție care afișează totalul pe categorii:

<!-- fisier: jurnal.py -->
```python
def adauga(jurnal, descriere, suma, categorie="altele"):
    jurnal.append({"descriere": descriere, "suma": suma, "categorie": categorie})


def total(jurnal):
    return sum(c["suma"] for c in jurnal)


def raport(jurnal):
    totaluri = {}
    for c in jurnal:
        totaluri[c["categorie"]] = totaluri.get(c["categorie"], 0) + c["suma"]
    return totaluri
```

<!-- ruleaza -->
```bash
git commit -am "Adaugă raportul pe categorii"
git switch main
tail -n 2 jurnal.py
```

```text
[raport 2c7d9e1] Adaugă raportul pe categorii
 1 file changed, 7 insertions(+)
Switched to branch 'main'
def total(jurnal):
    return sum(c["suma"] for c in jurnal)
```

`git commit -a` adaugă automat toate fișierele **deja urmărite** care au fost modificate, așa că nu mai e nevoie de `git add`. (Fișierele noi tot trebuie adăugate cu `git add`.) Pe `main`, `jurnal.py` nu are încă funcția `raport`: lucrul de pe ramură nu a atins versiunea principală.

Când funcția e gata și testată, o aduci pe `main` cu `git merge`:

<!-- ruleaza -->
```bash
git merge raport
git log --oneline
git branch -d raport
```

```text
Updating 5e4d3c2..2c7d9e1
Fast-forward
 jurnal.py | 7 +++++++
 1 file changed, 7 insertions(+)
2c7d9e1 Adaugă raportul pe categorii
5e4d3c2 Ignoră __pycache__, .venv și .env
8b3e1d0 Adaugă categoria la cheltuieli
4f1c2a9 Adaugă funcțiile de bază ale jurnalului
Deleted branch raport (was 2c7d9e1).
```

„Fast-forward” înseamnă că `main` nu avusese commit-uri noi între timp, așa că git a mutat pur și simplu eticheta `main` pe ultimul commit al ramurii. `git branch -d` șterge eticheta ramurii terminate; commit-urile rămân în istorie.

### Publicarea pe GitHub (pe scurt)

Un repository local poate fi legat de unul **la distanță** (în engleză „remote”), de exemplu pe GitHub, ca să ai o copie de siguranță și să lucrezi cu alții. După ce creezi un repository gol pe site, comenzile arată așa:

```bash
git remote add origin https://github.com/ana-popescu/jurnal.git
git push -u origin main
```

- `git remote add origin URL` dă numele `origin` adresei repository-ului de pe GitHub;
- `git push` trimite commit-urile tale acolo; `-u` ține minte legătura, așa că data viitoare ajunge `git push`;
- `git pull` aduce commit-urile făcute de alții, iar `git clone URL` copiază un repository întreg pe calculatorul tău.

Terminalul din PyTutor nu are acces la internet, așa că aceste comenzi le vei folosi pe propriul calculator sau pe un server.

## Greșeli frecvente

### 1. Commit fără add

<!-- ruleaza -->
```bash
echo "# TODO: export CSV" >> jurnal.py
git commit -m "Notează exportul CSV"
```

```text
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   jurnal.py

no changes added to commit (use "git add" and/or "git commit -a")
```

Modificarea există, dar nu e în zona de pregătire, deci commit-ul nu are ce salva. Git îți spune chiar soluțiile: `git add jurnal.py` urmat de `git commit`, sau direct `git commit -a`:

<!-- ruleaza -->
```bash
git commit -q -am "Notează exportul CSV"
git log --oneline -n 1
```

```text
9a8b7c6 Notează exportul CSV
```

(`-n 1` afișează doar ultimul commit.)

### 2. Comenzi git în afara repository-ului

<!-- ruleaza -->
```bash
cd ..
git status
```

```text
fatal: not a git repository (or any of the parent directories): .git
```

Git caută folderul `.git` în folderul curent și în cele de deasupra. Aici `cd ..` a ieșit din proiect, iar deasupra nu e niciun repository. În PyTutor, fiecare comandă pornește din rădăcina proiectului curent, așa că eroarea apare de obicei altfel: într-un proiect nou, în care n-ai rulat încă `git init` (fiecare proiect are repository-ul lui).

### 3. Conflict la merge

Un conflict apare când două ramuri modifică **aceleași rânduri** în feluri diferite. Pe ramura `lei`, Ana rotunjește totalul:

<!-- ruleaza -->
```bash
git switch -q -c lei
sed -i 's/return sum(c\["suma"\] for c in jurnal)/return round(sum(c["suma"] for c in jurnal), 2)/' jurnal.py
git commit -q -am "Rotunjește totalul la bani"
git switch -q main
sed -i 's/return sum(c\["suma"\] for c in jurnal)/return sum(c["suma"] for c in jurnal if c["suma"] > 0)/' jurnal.py
git commit -q -am "Ignoră sumele negative în total"
git merge lei
```

```text
Auto-merging jurnal.py
CONFLICT (content): Merge conflict in jurnal.py
Automatic merge failed; fix conflicts and then commit the result.
```

(`sed -i` modifică un rând dintr-un fișier direct din terminal; aici înlocuiește editarea pe care ai face-o în editor.) Git nu poate ghici care variantă e bună, așa că le pune pe amândouă în fișier, între marcaje. `sed -n '5,11p'` afișează rândurile 5–11:

<!-- ruleaza -->
```bash
sed -n '5,11p' jurnal.py
```

```text
def total(jurnal):
<<<<<<< HEAD
    return sum(c["suma"] for c in jurnal if c["suma"] > 0)
=======
    return round(sum(c["suma"] for c in jurnal), 2)
>>>>>>> lei
```

Între `<<<<<<< HEAD` și `=======` e varianta de pe ramura curentă (`main`), între `=======` și `>>>>>>> lei` cea de pe `lei`. Deschizi fișierul în editor, păstrezi ce trebuie (aici, ambele idei: rotunjirea și ignorarea sumelor negative) și ștergi marcajele. După rezolvare, `jurnal.py` arată așa (comentariul `TODO` de la final vine de la greșeala 1):

<!-- fisier: jurnal.py -->
```python
def adauga(jurnal, descriere, suma, categorie="altele"):
    jurnal.append({"descriere": descriere, "suma": suma, "categorie": categorie})


def total(jurnal):
    return round(sum(c["suma"] for c in jurnal if c["suma"] > 0), 2)


def raport(jurnal):
    totaluri = {}
    for c in jurnal:
        totaluri[c["categorie"]] = totaluri.get(c["categorie"], 0) + c["suma"]
    return totaluri
# TODO: export CSV
```

Apoi salvezi rezolvarea cu `git add` și `git commit`:

<!-- ruleaza -->
```bash
git add jurnal.py
git commit -q -m "Combină rotunjirea cu ignorarea sumelor negative"
git status
```

```text
On branch main
nothing to commit, working tree clean
```

Conflictele sunt normale când lucrează mai mulți oameni pe același cod. Le eviți în mare parte cu commit-uri mici și ramuri care nu trăiesc prea mult.

### 4. Un fișier adăugat în .gitignore după ce a fost salvat

`.gitignore` afectează doar fișierele **neurmărite**. Dacă un fișier e deja în istorie, git îl urmărește în continuare:

<!-- ruleaza -->
```bash
echo "parola=1234" > secrete.txt
git add secrete.txt
git commit -q -m "Adaugă notițe"
echo "secrete.txt" >> .gitignore
echo "parola=5678" > secrete.txt
git status --short
```

```text
 M .gitignore
 M secrete.txt
```

`secrete.txt` apare tot ca modificat. Trebuie scos din urmărire cu `git rm --cached`, care îl scoate din repository, dar îl lasă pe disc:

<!-- ruleaza -->
```bash
git rm --cached secrete.txt
git commit -q -am "Nu mai urmări secrete.txt"
git status --short
```

```text
rm 'secrete.txt'
```

Atenție: versiunea veche, cu `parola=1234`, **rămâne în istorie**. O parolă ajunsă într-un commit, mai ales pe GitHub, trebuie considerată compromisă și schimbată. De aceea `.gitignore` se scrie **la începutul** proiectului, iar secretele se țin în fișiere ca `.env` (lecția 46).

## Exercițiu

Lucrează în proiectul tău din PyTutor, în rădăcina lui (folderul în care pornește terminalul):

1. configurează `user.name` și `user.email`, apoi creează repository-ul cu `git init` și rulează imediat `git config core.fileMode false`;
2. creează `.gitignore` cu cel puțin `__pycache__/`, `.venv/`, `.env` și `.pytest_cache/`; verifică cu `git status --short` că nu mai apar;
3. fă un prim commit cu tot proiectul (`git add .` adaugă tot ce nu e ignorat);
4. în `capitole/42-git/git.py`, scrie o funcție `salut(nume)` care întoarce un text; fă commit;
5. creează ramura `majuscule`, modifică funcția astfel încât numele să fie scris cu `.title()`, fă commit, întoarce-te pe `main` și unește ramura cu `git merge`;
6. provoacă intenționat un conflict: pe două ramuri diferite, modifică același rând din `git.py` în două feluri, unește-le, rezolvă conflictul în editor și fă commit;
7. la final, `git log --oneline` trebuie să arate cel puțin 5 commit-uri, cu mesaje clare, la prezent.

## Pe scurt

- Git păstrează istoria proiectului în folderul `.git`; un commit e o fotografie salvată, cu mesaj, autor și un hash unic.
- Fluxul de bază: `git status` → `git add fisier` → `git commit -m "Mesaj clar"`; `git diff` arată ce s-a schimbat, `git log --oneline` arată istoria.
- `.gitignore` exclude fișierele care nu au ce căuta în istorie: `__pycache__/`, `.venv/`, `.env`; scrie-l la începutul proiectului.
- `git restore fisier` anulează modificările nesalvate; `git rm --cached` scoate un fișier din urmărire.
- Ramurile (`git switch -c`, `git merge`, `git branch -d`) separă lucrul nou de `main`; un conflict se rezolvă în editor, apoi `git add` și `git commit`.
- `git remote`, `git push`, `git pull` și `git clone` leagă repository-ul de GitHub sau de alt server.
