# 1. descrie_url(adresa): schema, gazda, portul (sau cel implicit), calea și parametrii
#    (exemplu: așa se scrie)
from urllib.parse import parse_qs, urlsplit


def descrie_url(adresa):
    parti = urlsplit(adresa)
    port = parti.port or {"http": 80, "https": 443}.get(parti.scheme)
    print("Schema:", parti.scheme)
    print("Gazda:", parti.hostname)
    print("Port:", port)
    print("Calea:", parti.path)
    for nume, valori in parse_qs(parti.query).items():
        print(f"  {nume} = {valori[0]}")


descrie_url("https://exemplu.ro/cauta?oras=Ia%C8%99i")


# 2. În Blog (din exemplul complet, cu server_mic.py copiat alături): calea GET /despre/
#    scrii așa: if cale == "/despre/":
#                   ...   # textul despre Ana, 25 de ani, din Cluj


# 2b. Parametrul ?cauta= pe GET /, fără să conteze literele mari și mici
#    scrii așa: cautat = parse_qs(parti.query).get("cauta", [""])[0].lower()
#               if cautat in articol["titlu"].lower():


# 2c. Comentariu cu autor gol sau lipsă: răspuns 400 cu un mesaj, fără salvare
#    scrii așa: if not campuri.get("autor", [""])[0].strip():


# 3. Testezi fiecare cale nouă cu cere(), inclusiv un 400 și un 404
#    scrii așa: print(cere("GET", "/despre/"))
