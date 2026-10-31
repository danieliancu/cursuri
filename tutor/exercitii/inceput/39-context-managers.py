# 1. Clasa Cronometru, un context manager care salvează durata în self.durata (exemplu: așa se scrie)
import time


class Cronometru:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, tip, valoare, traceback):
        self.durata = time.perf_counter() - self.start
        return False


with Cronometru() as c:
    sum(range(100_000))
print(f"Durata: {c.durata:.3f} secunde")


# 2. fisier_sigur(cale) cu @contextmanager: scrie în cale + ".tmp", închide, apoi os.replace doar
#    dacă blocul n-a dat eroare; altfel închide, șterge .tmp și dă raise
#    scrii așa: @contextmanager
#               def fisier_sigur(cale):
#                   f = open(cale + ".tmp", "w", encoding="utf-8")
#                   try:
#                       yield f
#                   except Exception:


# 3. Două teste: trei titluri, apoi un titlu + ValueError; afișezi dacă există fișierul și .tmp
#    scrii așa: print(Path(cale).exists(), Path(cale + ".tmp").exists())


# 4. Același with cu Cronometru() și fisier_sigur(...), pentru 10 000 de rânduri
#    scrii așa: with Cronometru() as c, fisier_sigur("mare.txt") as f:


# 5. În 2–3 propoziții: ce pățește fișierul final dacă scrii direct în el și apare o eroare
#    scrii așa: # Dacă programul se oprește la jumătate, ...
