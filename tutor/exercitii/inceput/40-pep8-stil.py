# 1. Copiezi codul din enunț sub aceste rânduri și rulezi ruff în terminal (exemplu: așa arată comanda)
#    ruff check --select E,F,W,I,N --output-format concise capitole/40-pep8-stil/pep8_stil.py
#    Notezi aici, în comentarii, ce probleme raportează:
#    - ...


# 2. Repari: snake_case, is None, fără importuri nefolosite, o instrucțiune pe rând
#    scrii așa: def calculeaza_reducere(valoare, cod):
#                   if cod is None:
#                       return 0


# 3. Constante cu nume clare în loc de 0.1, 150, 20
#    scrii așa: REDUCERE_STUDENT = 0.1


# 4. Type hints și docstring pentru funcție
#    scrii așa: def calculeaza_reducere(valoare: float, cod: str | None) -> float:
#                   """Întoarce reducerea în lei pentru codul dat."""


# 5. black, apoi din nou ruff check, black --check și mypy, fără nicio problemă raportată
#    scrii așa (în terminal): black capitole/40-pep8-stil/pep8_stil.py


# 6. Rulezi programul: rezultatul trebuie să fie tot 20
#    scrii așa: rezultat = calculeaza_reducere(200, "vara2026")
