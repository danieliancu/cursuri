# 1. Decoratorul valideaza_titlu: titlul gol dă ValueError, altfel e curățat (exemplu: așa se scrie)
from functools import wraps


def valideaza_titlu(functie):
    @wraps(functie)
    def invelis(titlu, *args, **kwargs):
        if not isinstance(titlu, str) or not titlu.strip():
            raise ValueError("Titlul nu poate fi gol")
        return functie(titlu.strip(), *args, **kwargs)

    return invelis


# 2. Decoratorul cu argument limita_imprumuturi(maxim); dicționarul stă pe funcția împachetată
#    scrii așa: def limita_imprumuturi(maxim):
#                   def decorator(functie):
#                       @wraps(functie)
#                       def invelis(titlu, cititor):
#    și:        invelis.imprumuturi = {}
#               raise PermissionError(f"{cititor} a atins limita de {maxim} cărți")


# 3. Decoratorul memoreaza, testat pe o funcție care afișează „calculez...”
#    scrii așa: if args in invelis.cache:
#                   return invelis.cache[args]


# 4. imprumuta(titlu, cititor) cu primii doi decoratori: titlu gol, 3 împrumuturi pentru Ana,
#    al 4-lea refuzat (maxim=3), erorile prinse cu try / except
#    scrii așa: @valideaza_titlu
#               @limita_imprumuturi(maxim=3)
#               def imprumuta(titlu, cititor):


# 5. @wraps peste tot; verifici cu print(imprumuta.__name__)
#    scrii așa: print(imprumuta.__name__)
