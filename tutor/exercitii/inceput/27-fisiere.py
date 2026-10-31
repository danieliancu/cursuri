# 1. Calea fișierului lecturi.txt, lângă script (exemplu: așa se scrie)
from pathlib import Path

CALE = Path(__file__).parent / "lecturi.txt"
print(f"Jurnalul se salvează în: {CALE}")


# 2. Meniul: 1 = adaugă (modul "a"), 2 = tabel aliniat, 3 = statistici, 0 = ieșire
#    scrii așa: with open(CALE, "a", encoding="utf-8") as fisier:
#                   fisier.write(f"{titlu};{autor};{pagini}\n")


# 3. Dacă fișierul nu există, opțiunile 2 și 3 afișează „Jurnalul e gol”
#    scrii așa: if not CALE.exists():
#                   print("Jurnalul e gol")


# 4. Statistici: număr de cărți, total pagini, cartea cea mai lungă, cărți pe autor (dicționar)
#    scrii așa: pe_autori[autor] = pe_autori.get(autor, 0) + 1


# 5. La citire, ignori rândurile goale sau cu alt număr de câmpuri, cu mesaj și numărul rândului
#    scrii așa: for numar, linie in enumerate(fisier, start=1):
#                   campuri = linie.strip().split(";")
#                   if len(campuri) != 3:
