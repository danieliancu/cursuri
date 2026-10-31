# 1. Autor(nume, an_nastere), cu frozen=True (exemplu: așa se scrie)
from dataclasses import dataclass


@dataclass(frozen=True)
class Autor:
    nume: str
    an_nastere: int


# 2. Carte(titlu, autor, an, pagini, genuri), cu genuri pornind de la field(default_factory=list);
#    __post_init__ ridică ValueError pentru an înainte de nașterea autorului sau pagini <= 0
#    scrii așa: genuri: list[str] = field(default_factory=list)
#               def __post_init__(self):
#                   if self.pagini <= 0:
#                       raise ValueError("Numărul de pagini trebuie să fie pozitiv")


# 3. Property-ul varsta_autorului_la_publicare
#    scrii așa: @property
#               def varsta_autorului_la_publicare(self):


# 4. Cel puțin 5 cărți de la 2–3 autori: sortate după an, apoi dicționarul Autor -> titluri
#    scrii așa: for carte in sorted(carti, key=lambda c: c.an):
#               pe_autori.setdefault(carte.autor, []).append(carte.titlu)


# 5. O carte publicată înainte de nașterea autorului, cu eroarea prinsă
#    scrii așa: try:
#               except ValueError as e:


# 6. Încerci să schimbi numele unui autor; explici eroarea într-un comentariu
#    scrii așa: except FrozenInstanceError as e:
