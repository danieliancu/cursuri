# 1. Data de terminare a lecției 61 și ziua săptămânii, în română (exemplu: așa se scrie)
from datetime import date, timedelta

ZILE = ["luni", "marți", "miercuri", "joi", "vineri", "sâmbătă", "duminică"]
START = date(2026, 10, 1)
final = START + timedelta(days=2 * (61 - 1))
print(f"Termini cursul pe {final.isoformat()}, într-o zi de {ZILE[final.weekday()]}")


# 2. Zilele rămase de la 29 octombrie și procentul din curs care ar trebui să fie gata
#    scrii așa: zile_trecute = (date(2026, 10, 29) - START).days
#               terminate = math.floor(zile_trecute / 2) + 1


# 3. Test-surpriză: 5 lecții diferite dintre cele terminate, cu random.seed(2026)
#    scrii așa: random.seed(2026)
#               print(random.sample(range(1, terminate + 1), 5))


# 4. Minutele pe săptămâni din lista ta de tupluri (data, lectie, minute), cu defaultdict și Counter
#    scrii așa: pe_saptamani[ziua.isocalendar().week] += minute
#               Counter(pe_saptamani).most_common(1)


# 5. Numele din variabila de mediu ELEV, folosit în titlul raportului
#    scrii așa: elev = os.environ.get("ELEV", "elev")
