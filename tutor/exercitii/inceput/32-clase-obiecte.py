# 1. Clasa Membru: nume, varsta, oras (implicit "Cluj"), carti = [] și limita = 3 (exemplu: așa se scrie)
class Membru:
    def __init__(self, nume, varsta, oras="Cluj"):
        self.nume = nume
        self.varsta = varsta
        self.oras = oras
        self.carti = []
        self.limita = 3

    # 2. poate_imprumuta(): True dacă are mai puțin de limita cărți
    #    scrii așa: def poate_imprumuta(self):
    #                   return len(self.carti) < self.limita

    # 3. imprumuta(titlu): adaugă și întoarce True, altfel afișează un mesaj și întoarce False
    #    scrii așa: if self.poate_imprumuta():

    # 4. returneaza(titlu): scoate titlul sau afișează un mesaj dacă nu are cartea
    #    scrii așa: if titlu in self.carti:

    # 5. fisa(): „Ana Popescu (25 de ani, Cluj) - 2/3 cărți: Ion, Maitreyi”
    #    scrii așa: return f"{self.nume} ({self.varsta} de ani, {self.oras}) - ..."


# 6. Ana și Mihai, împrumuturi și returnări (unul peste limită, o carte pe care n-o are), apoi fișele
#    scrii așa: ana = Membru("Ana Popescu", 25)
#               print(ana.fisa())
