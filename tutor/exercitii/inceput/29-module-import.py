# 1. Funcțiile pentru agenda_fisier.py; mută-le în acel fișier după ce le-ai înțeles (exemplu: așa se scrie)
import json


def incarca(cale):
    if not cale.exists():
        return {}
    with open(cale, encoding="utf-8") as fisier:
        return json.load(fisier)


def salveaza(agenda, cale):
    with open(cale, "w", encoding="utf-8") as fisier:
        json.dump(agenda, fisier, indent=2, ensure_ascii=False)


# 2. agenda_cautare.py: cauta(agenda, text) fără să conteze literele mari, pe_orase(agenda)
#    scrii așa: return {nume: date for nume, date in agenda.items() if text.lower() in nume.lower()}


# 3. Aici, în module_import.py: un „import modul”, un „from modul import ...”, meniul în main()
#    scrii așa: import agenda_fisier
#               from agenda_cautare import cauta, pe_orase


# 4. În agenda_cautare.py, un test rapid sub if __name__ == "__main__": (nu apare când îl imporți)
#    scrii așa: if __name__ == "__main__":
#                   print(cauta({"Ana Popescu": {"oras": "Cluj"}}, "ana"))


# 5. Calea JSON lângă cod, oricare ar fi folderul curent
#    scrii așa: CALE = Path(__file__).parent / "agenda.json"
