# 1. Excepția de bază și cele două derivate din ea (exemplu: așa se scrie)
class EroareCatalog(Exception):
    pass


class ElevInexistent(EroareCatalog):
    pass


class NotaInvalida(EroareCatalog):
    pass


# 2. adauga_nota(catalog, elev, nota): ElevInexistent, NotaInvalida (text care nu e număr sau în afara 1–10)
#    scrii așa: if elev not in catalog:
#                   raise ElevInexistent(f"Elevul {elev!r} nu e în catalog")


# 3. medie(catalog, elev): ElevInexistent pentru elev necunoscut, ValueError dacă nu are note
#    scrii așa: raise ValueError(f"{elev} nu are încă note")


# 4. Bucla de comenzi („nota Ana 9”, „medie Ana”, rând gol = gata), cu un singur except EroareCatalog
#    scrii așa: except EroareCatalog as eroare:
#                   print(f"{type(eroare).__name__}: {eroare}")


# 5. Testează fiecare ramură de eroare: elev inexistent, notă „abc”, notă 11, elev fără note, comandă greșită
#    scrii așa: # nota Dan 9   -> ElevInexistent
