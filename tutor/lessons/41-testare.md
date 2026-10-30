## Ce este

Un **test automat** este cod care verifică alt cod: apelează o funcție cu niște valori și verifică dacă rezultatul e cel așteptat. În loc să rulezi programul și să te uiți „de mână” la ce afișează, rulezi testele, iar ele îți spun imediat ce merge și ce nu.

Cel mai simplu test e o instrucțiune `assert`:

```python
def media(note):
    return sum(note) / len(note)


assert media([9, 10, 8]) == 9
assert media([5]) == 5
print("Toate verificările au trecut.")
```

```text
Toate verificările au trecut.
```

`assert conditie` nu face nimic dacă condiția e adevărată și oprește programul cu `AssertionError` dacă e falsă. Pe această idee sunt construite uneltele de testare: modulul **unittest** din biblioteca standard și pachetul **pytest**, pe care îl vei folosi cel mai des. În terminalul din PyTutor, pytest e deja instalat.

## De ce contează

Fiecare modificare poate strica ceva ce mergea înainte. Când ai cinci funcții, le mai verifici de mână. Când ai cincizeci, nu mai poți. Testele verifică tot, în câteva secunde, de fiecare dată, la fel de atent.

Mai aduc două lucruri:
- **curaj să schimbi codul**: poți rescrie o funcție ca să fie mai clară, iar testele îți spun dacă face în continuare același lucru;
- **documentație care nu se învechește**: un test arată exact cum se folosește o funcție și ce întoarce în cazurile limită.

Orice proiect serios are teste, iar Django are propriul sistem de testare, construit peste unittest (lecția 59).

## Cum funcționează

### assert și mesajul lui

`assert` poate primi și un mesaj, afișat când verificarea eșuează:

<!-- fisier: test_assert.py -->
```python
def media(note):
    return sum(note) / len(note)


assert media([9, 10]) == 9, f"media([9, 10]) a dat {media([9, 10])}"
```

```text
Traceback (most recent call last):
  File "test_assert.py", line 5, in <module>
    assert media([9, 10]) == 9, f"media([9, 10]) a dat {media([9, 10])}"
           ^^^^^^^^^^^^^^^^^^^
AssertionError: media([9, 10]) a dat 9.5
```

Problema unui `assert` simplu: se oprește la prima greșeală și nu-ți spune nimic despre restul. Uneltele de testare rulează toate testele, chiar dacă unele eșuează, și la final îți dau un raport.

### Structura unui test

Un test bun are trei pași (în engleză „Arrange, Act, Assert”):
1. **pregătești** datele;
2. **apelezi** funcția testată;
3. **verifici** rezultatul.

Fiecare test verifică **un singur** comportament și are un nume care spune care: `test_media_unei_singure_note`, `test_media_listei_goale_da_eroare`.

### pytest

Codul de testat stă într-un modul, de exemplu `note.py`:

<!-- fisier: note.py -->
```python
def media(note: list[float]) -> float:
    """Media aritmetică; ridică ValueError pentru o listă goală."""
    if not note:
        raise ValueError("lista de note e goală")
    return sum(note) / len(note)


def calificativ(nota: float) -> str:
    if nota >= 9:
        return "Foarte bine"
    if nota >= 7:
        return "Bine"
    if nota >= 5:
        return "Suficient"
    return "Insuficient"
```

Testele stau într-un fișier separat, al cărui nume începe cu `test_`. Fiecare test e o funcție al cărei nume începe tot cu `test_`, iar verificările se fac cu `assert` obișnuit:

<!-- fisier: test_note.py -->
```python
import pytest

from note import calificativ, media


def test_media_mai_multor_note():
    assert media([9, 10, 8]) == 9


def test_media_unei_singure_note():
    assert media([7]) == 7


def test_media_listei_goale_da_eroare():
    with pytest.raises(ValueError):
        media([])


def test_calificativ_la_limite():
    assert calificativ(9) == "Foarte bine"
    assert calificativ(8.99) == "Bine"
    assert calificativ(5) == "Suficient"
    assert calificativ(4.99) == "Insuficient"
```

`pytest.raises(ValueError)` verifică faptul că blocul de sub el **ridică** eroarea cerută; testul eșuează dacă eroarea nu apare. E un context manager, ca `with open(...)` (lecția 39).

Testele se rulează din terminal. `-q` („quiet”) face raportul scurt:

<!-- ruleaza -->
```bash
python -m pytest -q test_note.py
```

```text
....                                                                     [100%]
4 passed in 0.01s
```

Fiecare punct e un test trecut. Fără numele fișierului, pytest caută singur toate fișierele `test_*.py` din folderul curent și din subfoldere.

### Când un test eșuează

Să presupunem că cineva „simplifică” funcția `calificativ` și schimbă `>=` în `>`:

<!-- fisier: note.py -->
```python
def media(note: list[float]) -> float:
    """Media aritmetică; ridică ValueError pentru o listă goală."""
    if not note:
        raise ValueError("lista de note e goală")
    return sum(note) / len(note)


def calificativ(nota: float) -> str:
    if nota > 9:
        return "Foarte bine"
    if nota > 7:
        return "Bine"
    if nota > 5:
        return "Suficient"
    return "Insuficient"
```

<!-- ruleaza -->
```bash
python -m pytest -q test_note.py
```

```text
...F                                                                     [100%]
=================================== FAILURES ===================================
__________________________ test_calificativ_la_limite __________________________

    def test_calificativ_la_limite():
>       assert calificativ(9) == "Foarte bine"
E       AssertionError: assert 'Bine' == 'Foarte bine'
E         
E         - Foarte bine
E         + Bine

test_note.py:20: AssertionError
=========================== short test summary info ============================
FAILED test_note.py::test_calificativ_la_limite - AssertionError: assert 'Bin...
1 failed, 3 passed in 0.03s
```

Raportul spune exact:
- **ce test** a eșuat: `test_calificativ_la_limite`;
- **ce rând**: cel marcat cu `>`, adică rândul 20 din `test_note.py`;
- **ce valori** au fost comparate: funcția a întors `'Bine'`, testul aștepta `'Foarte bine'`.

Rezumatul de la final („short test summary info”) are câte un rând pe test eșuat, tăiat la lățimea terminalului (de aici `...`); detaliile complete sunt mai sus.

Testul a prins o greșeală pe care ai fi putut-o rata ușor: nota 9 exact. Așa se testează **cazurile limită**: valorile de la granița dintre două situații (9 și 8.99, 5 și 4.99), lista goală, zero, numere negative, textul gol.

### unittest

Modulul **unittest** face parte din biblioteca standard, deci funcționează fără nicio instalare. Testele sunt metode ale unei clase derivate din `unittest.TestCase` (clasele și moștenirea, lecțiile 32 și 34), iar verificările se fac cu metode precum `assertEqual` și `assertRaises`:

<!-- fisier: test_note_unittest.py -->
```python
import unittest

from note import media


class TestMedia(unittest.TestCase):
    def test_media_mai_multor_note(self):
        self.assertEqual(media([9, 10, 8]), 9)

    def test_media_listei_goale_da_eroare(self):
        with self.assertRaises(ValueError):
            media([])
```

<!-- ruleaza -->
```bash
python -m unittest -v test_note_unittest
```

```text
test_media_listei_goale_da_eroare (test_note_unittest.TestMedia.test_media_listei_goale_da_eroare) ... ok
test_media_mai_multor_note (test_note_unittest.TestMedia.test_media_mai_multor_note) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

La comanda `unittest`, modulul se scrie fără `.py`. pytest știe să ruleze și teste scrise cu unittest, așa că le poți combina. Django folosește stilul unittest, deci îl vei revedea la lecția 59.

### Testarea unui program care are și main()

La lecția 29 ai învățat tiparul `if __name__ == "__main__": main()`. Acum vezi de ce contează: testele **importă** modulul, iar codul de sub `if` nu se execută la import. Funcțiile se pot testa, iar partea interactivă (`input()`, meniuri) nu pornește în timpul testelor.

<!-- fisier: conversii.py -->
```python
def celsius_in_fahrenheit(grade: float) -> float:
    return grade * 9 / 5 + 32


def main() -> None:
    grade = float(input("Grade Celsius: "))
    print(f"{celsius_in_fahrenheit(grade):.1f} °F")


if __name__ == "__main__":
    main()
```

<!-- fisier: test_conversii.py -->
```python
from conversii import celsius_in_fahrenheit


def test_punctul_de_inghet():
    assert celsius_in_fahrenheit(0) == 32


def test_punctul_de_fierbere():
    assert celsius_in_fahrenheit(100) == 212


def test_temperatura_negativa():
    assert celsius_in_fahrenheit(-40) == -40
```

<!-- ruleaza -->
```bash
python -m pytest -q test_conversii.py
```

```text
...                                                                      [100%]
3 passed in 0.01s
```

Regula practică: pune logica în funcții care **primesc** valori și **întorc** rezultate, iar citirea și afișarea în `main()`. Funcțiile de felul ăsta se testează ușor.

### Ce se întâmplă „pe dedesubt”: cum găsește pytest testele

pytest nu primește o listă de teste. Le **descoperă** după nume:
- caută fișierele `test_*.py` (sau `*_test.py`) din folderul dat și din subfoldere;
- în ele, caută funcțiile `test_*` și clasele `Test*` cu metode `test_*`;
- importă fiecare fișier și apelează fiecare test separat, prinzând orice excepție.

Un test e considerat eșuat dacă ridică o excepție (un `assert` fals ridică `AssertionError`) și trecut dacă se termină normal. De aceea un `assert` obișnuit ajunge. Ca să afișeze valorile comparate („`'Bine' == 'Foarte bine'`”), pytest **rescrie** instrucțiunile `assert` din fișierele de test în momentul în care le importă, adăugând cod care ține minte fiecare parte a comparației.

## Exemplu complet

Testele pentru funcțiile jurnalului de cheltuieli (lecțiile 27–31). Modulul:

<!-- fisier: jurnal.py -->
```python
CATEGORII = ("mâncare", "transport", "chirie", "distracție", "altele")


def cheltuiala(descriere: str, suma: float, categorie: str) -> dict:
    """Creează o cheltuială validată."""
    descriere = descriere.strip()
    if not descriere:
        raise ValueError("descrierea e goală")
    if suma <= 0:
        raise ValueError(f"suma trebuie să fie pozitivă, nu {suma}")
    if categorie not in CATEGORII:
        raise ValueError(f"categorie necunoscută: {categorie!r}")
    return {"descriere": descriere, "suma": round(suma, 2), "categorie": categorie}


def total_pe_categorii(jurnal: list[dict]) -> dict[str, float]:
    """Suma pe fiecare categorie care apare în jurnal."""
    totaluri: dict[str, float] = {}
    for c in jurnal:
        totaluri[c["categorie"]] = totaluri.get(c["categorie"], 0) + c["suma"]
    return totaluri
```

Testele, cu câte un test pentru fiecare comportament și pentru cazurile limită:

<!-- fisier: test_jurnal.py -->
```python
import pytest

from jurnal import cheltuiala, total_pe_categorii


def test_cheltuiala_valida_e_curatata_si_rotunjita():
    c = cheltuiala("  pizza ", 45.999, "mâncare")
    assert c == {"descriere": "pizza", "suma": 46.0, "categorie": "mâncare"}


def test_descrierea_goala_e_respinsa():
    with pytest.raises(ValueError):
        cheltuiala("   ", 10, "mâncare")


def test_suma_zero_sau_negativa_e_respinsa():
    with pytest.raises(ValueError):
        cheltuiala("bilet", 0, "transport")
    with pytest.raises(ValueError):
        cheltuiala("bilet", -5, "transport")


def test_categoria_necunoscuta_e_respinsa():
    with pytest.raises(ValueError, match="necunoscută"):
        cheltuiala("carte", 50, "cărți")


def test_totaluri_pe_categorii():
    jurnal = [
        cheltuiala("pizza", 45, "mâncare"),
        cheltuiala("bilet", 4.5, "transport"),
        cheltuiala("piață", 120.5, "mâncare"),
    ]
    assert total_pe_categorii(jurnal) == {"mâncare": 165.5, "transport": 4.5}


def test_totaluri_pentru_jurnal_gol():
    assert total_pe_categorii([]) == {}
```

<!-- ruleaza -->
```bash
python -m pytest -q test_jurnal.py
```

```text
......                                                                   [100%]
6 passed in 0.01s
```

Observă:
- numele testelor se citesc ca propoziții și spun ce se verifică;
- `match="necunoscută"` verifică și textul mesajului de eroare, nu doar tipul;
- jurnalul gol e un caz limită separat: o funcție care merge pe date „normale” poate cădea pe date goale.

## Greșeli frecvente

### 1. Test care nu începe cu test_

<!-- fisier: test_uitat.py -->
```python
from note import media


def verifica_media():
    assert media([9, 10]) == 100
```

<!-- ruleaza -->
```bash
python -m pytest -q test_uitat.py
```

```text

no tests ran in 0.00s
```

Testul e greșit (aștepta 100), dar nimeni n-a aflat, pentru că pytest nu l-a recunoscut ca test: numele funcției nu începe cu `test_`. Mesajul „no tests ran” e semnalul. Același lucru se întâmplă dacă fișierul nu se numește `test_*.py`.

### 2. Comparația care nu are assert

<!-- fisier: test_fara_assert.py -->
```python
from note import media


def test_media():
    media([9, 10]) == 100
```

<!-- ruleaza -->
```bash
python -m pytest -q test_fara_assert.py
```

```text
.                                                                        [100%]
1 passed in 0.01s
```

Testul „trece”, deși comparația e falsă: fără `assert`, rezultatul comparației se calculează și se aruncă. Un test trece dacă nu ridică nicio excepție. Verifică mereu că testul tău chiar poate eșua: strică intenționat funcția și uită-te dacă testul apare ca eșuat (`F`).

### 3. Modul fără if __name__ == "__main__"

Dacă modulul testat apelează `main()` direct, importul lui din test pornește programul, care cere `input()`:

<!-- fisier: conversii_fara_garda.py -->
```python
def celsius_in_fahrenheit(grade: float) -> float:
    return grade * 9 / 5 + 32


grade = float(input("Grade Celsius: "))
print(celsius_in_fahrenheit(grade))
```

<!-- fisier: test_fara_garda.py -->
```python
from conversii_fara_garda import celsius_in_fahrenheit


def test_inghet():
    assert celsius_in_fahrenheit(0) == 32
```

<!-- ruleaza -->
```bash
python -m pytest -q test_fara_garda.py 2>&1 | tail -n 3
```

```text
ERROR test_fara_garda.py - OSError: pytest: reading from stdin while output i...
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.10s
```

(`| tail -n 3` păstrează doar ultimele 3 rânduri ale raportului, care e lung.) Mesajul complet, tăiat aici, e „OSError: pytest: reading from stdin while output is captured!”: pytest nu-i dă codului acces la tastatură. Nici n-a ajuns să ruleze testul: a dat eroare la **colectare**, adică la importul fișierului. Soluția e garda din secțiunea despre `main()`.

### 4. float comparat cu ==

<!-- fisier: test_suma.py -->
```python
def test_suma_preturilor():
    assert 0.1 + 0.2 == 0.3
```

<!-- ruleaza -->
```bash
python -m pytest -q test_suma.py 2>&1 | tail -n 2
```

```text
FAILED test_suma.py::test_suma_preturilor - assert (0.1 + 0.2) == 0.3
1 failed in 0.02s
```

`0.1 + 0.2` e `0.30000000000000004`: calculul e corect, doar reprezentarea `float` nu e exactă (lecțiile 3 și 7). pytest are pentru asta `pytest.approx`, care compară cu o toleranță mică:

<!-- fisier: test_suma.py -->
```python
import pytest


def test_suma_preturilor():
    assert 0.1 + 0.2 == pytest.approx(0.3)
```

<!-- ruleaza -->
```bash
python -m pytest -q test_suma.py
```

```text
.                                                                        [100%]
1 passed in 0.01s
```

### 5. Funcții care afișează în loc să întoarcă

<!-- fisier: raport.py -->
```python
def total(preturi):
    print(sum(preturi))
```

<!-- fisier: test_raport.py -->
```python
from raport import total


def test_total():
    assert total([4.5, 8.5]) == 13
```

<!-- ruleaza -->
```bash
python -m pytest -q test_raport.py 2>&1 | tail -n 2
```

```text
FAILED test_raport.py::test_total - assert None == 13
1 failed in 0.02s
```

Funcția a afișat `13.0`, dar a întors `None` (lecția 18), iar testul nu are ce compara. Funcțiile pe care vrei să le testezi întorc rezultatul cu `return`; afișarea se face în altă parte, de exemplu în `main()`.

## Exercițiu

În `capitole/41-testare/testare.py`, scrie două funcții, apoi testele lor în fișierul `capitole/41-testare/test_testare.py`:

1. `nota_finala(note: list[float], bonus: float = 0) -> float`: media notelor plus bonusul, rotunjită la 2 zecimale, dar cel mult 10; ridică `ValueError` pentru o listă goală sau pentru o notă în afara intervalului 1–10;
2. `clasament(catalog: dict[str, list[float]]) -> list[str]`: numele elevilor sortate descrescător după media notelor; la medii egale, alfabetic;
3. scrie cel puțin 8 teste pytest, inclusiv pentru cazurile limită: bonus care trece de 10, listă goală, notă 0, notă 10.5, catalog gol, doi elevi cu aceeași medie;
4. rulează-le cu `python -m pytest -q capitole/41-testare`;
5. strică intenționat o funcție (de exemplu, uită rotunjirea) și verifică dacă măcar un test eșuează; apoi repar-o.

Funcțiile nu citesc și nu afișează nimic. Dacă vrei să le folosești și interactiv, adaugă un `main()` sub garda `if __name__ == "__main__":`.

## Pe scurt

- Un test automat apelează codul și verifică rezultatul; `assert conditie` ridică `AssertionError` dacă e falsă.
- **pytest**: fișiere `test_*.py`, funcții `test_*`, `assert` obișnuit; se rulează cu `python -m pytest -q`.
- `pytest.raises(Eroare)` verifică o excepție, iar `pytest.approx` compară valori `float`.
- **unittest** e în biblioteca standard: clase `TestCase`, `assertEqual`, `assertRaises`; Django folosește acest stil (lecția 59).
- Un test bun verifică un singur comportament, are un nume clar și acoperă cazurile limită.
- Codul testabil întoarce rezultate și ține citirea/afișarea în `main()`, sub `if __name__ == "__main__":`.
