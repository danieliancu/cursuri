# 1. Clasa de bază Material(titlu, an), cu zile = 14, descriere() și taxa() (exemplu: așa se scrie)
class Material:
    zile = 14

    def __init__(self, titlu, an):
        self.titlu = titlu
        self.an = an

    def descriere(self):
        return f"{self.titlu} ({self.an})"

    def taxa(self, zile_intarziere):
        return zile_intarziere * 0.5


# 2. Carte(Material) adaugă autor și extinde descriere()
#    scrii așa: class Carte(Material):
#                   def __init__(self, titlu, an, autor):
#                       super().__init__(titlu, an)
#    apoi:      return super().descriere() + f", de {self.autor}"


# 3. Revista(Material): zile = 7, iar taxa() e 1 leu pe zi
#    scrii așa: class Revista(Material):
#                   zile = 7


# 4. Audiobook(Carte) adaugă durata_minute; descriere() arată durata în ore și minute
#    scrii așa: ore, minute = divmod(self.durata_minute, 60)


# 5. Excepțiile: EroareBiblioteca(Exception) și MaterialInexistent, derivată din ea
#    scrii așa: class EroareBiblioteca(Exception):
#                   pass


# 6. Lista cu câte un obiect din fiecare clasă: descriere, zile, taxa(3), fără isinstance
#    scrii așa: for material in materiale:
#                   print(material.descriere(), material.zile, material.taxa(3))


# 7. cauta(materiale, titlu) ridică MaterialInexistent; o prinzi cu except EroareBiblioteca
#    scrii așa: raise MaterialInexistent(f"Nu există „{titlu}”")
