# 1. citeste_numar(mesaj): întreabă până primește un număr, cu minus și virgulă (exemplu: așa se scrie)
def citeste_numar(mesaj):
    while True:
        text = input(mesaj).strip().replace(",", ".")
        try:
            return float(text)
        except ValueError:
            print("  Nu e un număr valid, mai încearcă.")


# 2. citeste_optiune(mesaj, optiuni): întreabă până primește una dintre opțiunile din listă
#    scrii așa: def citeste_optiune(mesaj, optiuni):
#                   while True:
#                       raspuns = input(mesaj).strip().lower()


# 3. Meniul: 1 = °C → °F, 2 = km → mile (0.621371), 3 = kg → livre (2.20462), 0 = ieșire
#    scrii așa: while True:
#                   optiune = citeste_optiune("Opțiunea: ", ["1", "2", "3", "0"])


# 4. După fiecare rezultat: „Vrei și conversia inversă? (da/nu)”; la „da”, convertești invers
#    scrii așa: if citeste_optiune("Vrei și conversia inversă? (da/nu) ", ["da", "nu"]) == "da":


# 5. Un dicționar care numără conversiile pe tipuri, afișat la ieșire (fără isdigit() nicăieri)
#    scrii așa: conversii[optiune] = conversii.get(optiune, 0) + 1
