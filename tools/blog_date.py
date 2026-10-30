"""Generează tutor/lessons/_blog/date/{50,53,57}.json: datele de test ale blogului, pe forma modelelor."""
import json
import subprocess
from pathlib import Path

DATE = Path(r"C:\_work\pyth\tutor\lessons\_blog\date")
DATE.mkdir(parents=True, exist_ok=True)

ARTICOLE = [
    (1, "Primul meu program în Python", "2026-09-14", 1, [1],
     'Totul a început cu un simplu print("Salut, lume!"). '
     "Nu credeam că două cuvinte pe ecran pot să bucure atât de mult.\n\n"
     "Azi știu că a fost primul pas dintr-un drum lung: variabile, bucle, funcții și clase."),
    (2, "De ce am ales Django", "2026-10-02", 1, [1, 2],
     "După primele luni cu Python, voiam să fac un site adevărat: cu pagini, "
     "cu bază de date și cu un loc unde să mă autentific.\n\n"
     "Django are toate acestea „din cutie”, iar documentația lui e excelentă."),
    (3, "O plimbare prin Cluj", "2026-10-20", 2, [3],
     "Duminică am urcat pe dealul Cetățuia, de unde se vede tot Clujul. "
     "Pe drum am trecut prin Piața Unirii și pe lângă Teatrul Național.\n\n"
     "Data viitoare vreau să ajung și în Grădina Botanică."),
]
CATEGORII = [(1, "Programare"), (2, "Călătorii")]
ETICHETE = [(1, "python"), (2, "django"), (3, "cluj")]
COMENTARII = [
    (1, 2, "Mihai", "Foarte bun articol!", "2026-10-03T09:30:00Z"),
    (2, 3, "Mihai", "Și eu iubesc Clujul! Grădina Botanică merită.", "2026-10-21T17:15:00Z"),
]
PAROLE = {"ana": "parola-ana-2026", "mihai": "parola-mihai-2026"}


def hashes() -> dict[str, str]:
    code = (
        "import django; from django.conf import settings; settings.configure(); django.setup(); "
        "from django.contrib.auth.hashers import make_password; "
        f"[print(make_password(p)) for p in {list(PAROLE.values())!r}]"
    )
    out = subprocess.run(["docker", "run", "--rm", "pytutor-sandbox:2", "python", "-c", code],
                         capture_output=True, text=True, check=True).stdout.split()
    return dict(zip(PAROLE, out))


def fixture(forma: int, parole: dict[str, str]) -> list[dict]:
    obiecte = []
    if forma >= 57:
        obiecte += [
            {"model": "auth.user", "pk": 1, "fields": {
                "username": "ana", "first_name": "Ana", "last_name": "Popescu", "email": "ana@exemplu.ro",
                "password": parole["ana"], "is_staff": True, "is_superuser": True, "is_active": True,
                "date_joined": "2026-09-01T08:00:00Z"}},
            {"model": "auth.user", "pk": 2, "fields": {
                "username": "mihai", "first_name": "Mihai", "last_name": "Ionescu", "email": "mihai@exemplu.ro",
                "password": parole["mihai"], "is_staff": False, "is_superuser": False, "is_active": True,
                "date_joined": "2026-09-20T08:00:00Z"}},
        ]
    if forma >= 53:
        obiecte += [{"model": "articole.categorie", "pk": pk, "fields": {"nume": n}} for pk, n in CATEGORII]
        obiecte += [{"model": "articole.eticheta", "pk": pk, "fields": {"nume": n}} for pk, n in ETICHETE]
    for pk, titlu, data, categorie, etichete, continut in ARTICOLE:
        campuri = {"titlu": titlu, "continut": continut, "data_publicarii": data}
        if forma >= 53:
            campuri |= {"publicat": True, "categorie": categorie, "etichete": etichete}
        if forma >= 57:
            campuri["autor"] = 1
        obiecte.append({"model": "articole.articol", "pk": pk, "fields": campuri})
    if forma >= 53:
        obiecte += [
            {"model": "articole.comentariu", "pk": pk,
             "fields": {"articol": a, "autor": autor, "text": text, "data": data}}
            for pk, a, autor, text, data in COMENTARII
        ]
    return obiecte


parole = hashes()
for forma in (50, 53, 57):
    (DATE / f"{forma}.json").write_text(
        json.dumps(fixture(forma, parole), ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"date/{forma}.json")
