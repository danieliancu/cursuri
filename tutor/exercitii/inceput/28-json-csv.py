# 1. Agenda de pornire, salvată în agenda.json doar dacă fișierul nu există (exemplu: așa se scrie)
import json
from pathlib import Path

CALE_JSON = Path("agenda.json")
agenda = {
    "Ana Popescu": {"telefon": "0722111222", "oras": "Cluj", "etichete": ["familie"]},
    "Mihai Ionescu": {"telefon": "0733444555", "oras": "Iași", "etichete": ["serviciu", "sport"]},
    "Elena Radu": {"telefon": "0744666777", "oras": "Cluj", "etichete": []},
}
if not CALE_JSON.exists():
    with open(CALE_JSON, "w", encoding="utf-8") as fisier:
        json.dump(agenda, fisier, indent=2, ensure_ascii=False)


# 2. Încarcă agenda din agenda.json, cere un contact nou (etichete separate prin virgulă), salvează înapoi
#    scrii așa: with open(CALE_JSON, encoding="utf-8") as fisier:
#                   agenda = json.load(fisier)


# 3. Exportă în agenda.csv cu csv.DictWriter: coloanele nume, telefon, oras, etichete, separatorul ;
#    scrii așa: coloane = ["nume", "telefon", "oras", "etichete"]
#               scriitor = csv.DictWriter(fisier, fieldnames=coloane, delimiter=";")
#               "etichete": ", ".join(date["etichete"])


# 4. Citește înapoi agenda.csv cu csv.DictReader și numără contactele pe orașe
#    scrii așa: for rand in csv.DictReader(fisier, delimiter=";"):


# 5. Compară numele din CSV cu cele din JSON, ca seturi, și afișează rezultatul
#    scrii așa: if nume_csv == set(agenda):
