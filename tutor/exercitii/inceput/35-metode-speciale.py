# 1. Membru(nume, numar_legitimatie) cu __str__ și __repr__ (exemplu: așa se scrie)
class Membru:
    def __init__(self, nume, numar_legitimatie):
        self.nume = nume
        self.numar_legitimatie = numar_legitimatie

    def __str__(self):
        return f"{self.nume} (legitimația {self.numar_legitimatie})"

    def __repr__(self):
        return f"Membru({self.nume!r}, {self.numar_legitimatie})"

    # 1b. __eq__ și __hash__ după legitimație, __lt__ după nume (fără să conteze literele mari)
    #    scrii așa: def __eq__(self, other):
    #                   return self.numar_legitimatie == other.numar_legitimatie
    #    apoi:      return hash(self.numar_legitimatie)
    #    și:        return self.nume.lower() < other.nume.lower()


# 2. ListaAsteptare(titlu): adauga(membru) fără dubluri, __len__, __contains__, __str__
#    scrii așa: class ListaAsteptare:
#                   def adauga(self, membru):
#                       if membru in self.membri:
#    și:        return f"„{self.titlu}”: {len(self)} în așteptare"


# 3. Patru membri (doi cu aceeași legitimație); arăți adăugarea refuzată, sorted(),
#    print() pe o listă de membri și if lista: pe o listă de așteptare goală
#    scrii așa: membri = [Membru("Ana Popescu", 1024), Membru("Ana P.", 1024), ...]
#               print(sorted(membri))
