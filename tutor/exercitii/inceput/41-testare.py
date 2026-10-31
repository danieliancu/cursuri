# 1. nota_finala(note, bonus=0): media + bonus, 2 zecimale, cel mult 10; ValueError la date greșite
#    (exemplu: așa se scrie)
def nota_finala(note: list[float], bonus: float = 0) -> float:
    if not note:
        raise ValueError("Lista de note e goală")
    for nota in note:
        if not 1 <= nota <= 10:
            raise ValueError(f"Nota {nota} nu e între 1 și 10")
    return min(round(sum(note) / len(note) + bonus, 2), 10)


# 2. clasament(catalog): numele sortate descrescător după medie; la medii egale, alfabetic
#    scrii așa: def clasament(catalog: dict[str, list[float]]) -> list[str]:
#                   return sorted(catalog, key=lambda nume: (-media_lui(nume), nume))


# 3. În test_testare.py: cel puțin 8 teste pytest, inclusiv cazurile limită
#    scrii așa: from testare import clasament, nota_finala
#               def test_bonus_nu_trece_de_10():
#                   assert nota_finala([9, 10], bonus=2) == 10
#               def test_lista_goala():
#                   with pytest.raises(ValueError):


# 4. Rulezi testele în terminal
#    scrii așa: python -m pytest -q capitole/41-testare


# 5. Strici intenționat o funcție (de exemplu, scoți round), verifici că pică un test, apoi o repari
#    scrii așa: return min(sum(note) / len(note) + bonus, 10)   # fără round, doar ca probă
