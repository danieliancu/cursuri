# 1. Atributele de clasă și __init__; numar_membri crește la final, după validare (exemplu: așa se scrie)
class Membru:
    limita = 3
    numar_membri = 0

    def __init__(self, nume, email):
        self.nume = nume
        self.email = email
        self.carti = []
        Membru.numar_membri += 1

    # 2. Property email cu setter: salvează cu litere mici, ValueError dacă nu are exact un @
    #    scrii așa: @property
    #               def email(self):
    #                   return self._email
    #
    #               @email.setter
    #               def email(self, valoare):

    # 3. @classmethod din_dict(cls, date): un membru dintr-un dicționar {"nume": ..., "email": ...}
    #    scrii așa: return cls(date["nume"], date["email"])

    # 4. Property poate_imprumuta: mai puțin de limita cărți
    #    scrii așa: return len(self.carti) < self.limita

    # 5. @staticmethod email_valid(email), folosit de setter
    #    scrii așa: return email.count("@") == 1


# 6. Trei membri dintr-o listă de dicționare (unul cu email greșit, prins cu try / except),
#    Membru.numar_membri și două obiecte cu liste de cărți independente
#    scrii așa: try:
#                   membru = Membru.din_dict(date)
#               except ValueError as eroare:
