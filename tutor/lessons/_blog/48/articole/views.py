from datetime import date

from django.http import Http404
from django.shortcuts import render

# Datele vin deocamdată dintr-o listă Python; la lecția 52 le vom citi din baza de date.
ARTICOLE = [
    {
        "id": 3,
        "titlu": "O plimbare prin Cluj",
        "data_publicarii": date(2026, 10, 20),
        "categorie": "Călătorii",
        "continut": (
            "Duminică am urcat pe dealul Cetățuia, de unde se vede tot Clujul. "
            "Pe drum am trecut prin Piața Unirii și pe lângă Teatrul Național.\n\n"
            "Data viitoare vreau să ajung și în Grădina Botanică."
        ),
    },
    {
        "id": 2,
        "titlu": "De ce am ales Django",
        "data_publicarii": date(2026, 10, 2),
        "categorie": "Programare",
        "continut": (
            "După primele luni cu Python, voiam să fac un site adevărat: cu pagini, "
            "cu bază de date și cu un loc unde să mă autentific.\n\n"
            "Django are toate acestea „din cutie”, iar documentația lui e excelentă."
        ),
    },
    {
        "id": 1,
        "titlu": "Primul meu program în Python",
        "data_publicarii": date(2026, 9, 14),
        "categorie": "Programare",
        "continut": (
            'Totul a început cu un simplu print("Salut, lume!"). '
            "Nu credeam că două cuvinte pe ecran pot să bucure atât de mult.\n\n"
            "Azi știu că a fost primul pas dintr-un drum lung: "
            "variabile, bucle, funcții și clase."
        ),
    },
]


def gaseste(nr):
    """Articolul cu id-ul `nr` sau pagina 404, dacă nu există."""
    for articol in ARTICOLE:
        if articol["id"] == nr:
            return articol
    raise Http404("Articolul nu există.")


def lista(request):
    return render(request, "articole/lista.html", {"articole": ARTICOLE})


def detaliu(request, nr):
    return render(request, "articole/detaliu.html", {"articol": gaseste(nr)})


def despre(request):
    return render(request, "articole/despre.html")
