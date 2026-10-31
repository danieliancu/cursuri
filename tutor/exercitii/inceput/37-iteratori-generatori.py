# 1. Generatorul imprumuturi_restante(imprumuturi, zi_curenta) (exemplu: așa se scrie)
def imprumuturi_restante(imprumuturi, zi_curenta):
    for titlu, cititor, zi_returnare in imprumuturi:
        if zi_returnare < zi_curenta:
            yield titlu, cititor, zi_curenta - zi_returnare


# 2. Generatorul infinit zile_lucratoare(start), care sare peste zilele 6, 7, 13, 14 ...;
#    primele 10 zile lucrătoare de la ziua 1, cu islice
#    scrii așa: zi = start
#               while True:
#                   if zi % 7 not in (6, 0):
#                       yield zi
#    apoi:      print(list(islice(zile_lucratoare(1), 10)))


# 3. Scrii imprumuturi.txt (titlu;cititor;zi_returnare) și un generator care îl citește
#    rând cu rând; îl legi de imprumuturi_restante pentru ziua 15
#    scrii așa: titlu, cititor, zi = rand.strip().split(";")
#               yield titlu, cititor, int(zi)


# 4. Totalul penalităților (2 lei pe zi) cu sum() și o expresie generator
#    scrii așa: total = sum(2 * zile for _, _, zile in ...)


# 5. Prima restanță cu next(..., None), sau „Nicio restanță”
#    scrii așa: prima = next(imprumuturi_restante(...), None)
