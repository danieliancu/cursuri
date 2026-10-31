"""Explică în română, fără AI, erorile Python pe care le întâlnește aproape orice începător.

`explica(output)` citește traceback-ul din output-ul unui program (ultimul rând „Tip: mesaj”, rândul din
codul elevului, sugestia „Did you mean”) și caută prima regulă potrivită. Textele vin din secțiunile
„Greșeli frecvente” ale lecțiilor, iar fiecare explicație trimite la lecția de unde e luată.
Pentru erorile pe care nu le recunoaște întoarce None: atunci rămâne tutorele AI.
"""
import re
from dataclasses import dataclass

# „NameError: name 'x' is not defined” — tipul poate avea și modul (json.decoder.JSONDecodeError).
_LAST_RE = re.compile(r"^(?P<tip>[A-Za-z_][\w.]*(?:Error|Exception|Exit|Interrupt|Iteration|Warning)):\s?(?P<msg>.*)$")
_FRAME_RE = re.compile(r'^\s*File "(?P<file>[^"]+)", line (?P<line>\d+)')
_DID_YOU_MEAN_RE = re.compile(r"Did you mean: '(?P<sug>[^']+)'\?")
_FORGOT_IMPORT_RE = re.compile(r"Did you forget to import '(?P<mod>[^']+)'\?")
# cadre din Python însuși, nu din codul elevului
_LIBRARY_RE = re.compile(r"([\\/]lib[\\/]python3|[\\/]Lib[\\/]|<frozen |site-packages|[\\/]\.pytutor[\\/])")


@dataclass(frozen=True)
class Regula:
    tip: str                # numele excepției (sau o listă separată prin „|”)
    mesaj: str              # regex pe mesaj; grupurile cu nume intră în șabloane
    titlu: str
    explicatie: str         # Markdown scurt, cu {grupuri} din `mesaj`
    lectie: str = ""        # slug-ul lecției care explică greșeala
    sectiune: str = ""      # titlul subsecțiunii din „Greșeli frecvente”


R = Regula
REGULI = [
    # ---------------------------------------------------------------- sintaxă
    R("SyntaxError", r"expected ':'", "Lipsesc cele două puncte",
      "Rândurile care deschid un bloc (`if`, `elif`, `else`, `for`, `while`, `def`) se termină cu `:`. "
      "Adaugă `:` la finalul rândului {rand}.", "if-else", "1. Lipsesc cele două puncte"),
    R("SyntaxError", r"unterminated string literal", "Ghilimele neînchise",
      "„Unterminated string literal” înseamnă „text neterminat”: ai deschis ghilimelele, dar nu le-ai închis. "
      "Textul trebuie să înceapă și să se termine cu același fel de ghilimele.",
      "primul-program", "1. Ghilimele neînchise"),
    R("SyntaxError", r"unterminated triple-quoted string", "Ghilimele triple neînchise",
      "Un text început cu `\"\"\"` sau `'''` trebuie închis cu aceleași trei ghilimele.",
      "primul-program", "1. Ghilimele neînchise"),
    R("SyntaxError", r"invalid character '(?P<c>[“”„‘’])'", "Ghilimele „românești”",
      "Python acceptă doar ghilimelele drepte `\"` și `'`. Caracterul `{c}` vine de obicei din Word sau dintr-un chat: "
      "șterge-l și scrie ghilimelele de la tastatură.",
      "primul-program", "2. Ghilimele „românești” copiate din Word sau din chat"),
    R("SyntaxError", r"'(?P<p>[(\[{])' was never closed", "Paranteză neînchisă",
      "Ai deschis `{p}` pe rândul {rand}, dar nu l-ai închis. Numără parantezele: fiecare deschisă are nevoie de "
      "perechea ei. Uneori Python arată greșeala abia pe rândul de sub ea.",
      "traceback", "SyntaxError nu are cadre"),
    R("SyntaxError", r"unmatched '(?P<p>[)\]}])'", "Paranteză în plus",
      "Pe rândul {rand} e un `{p}` care nu închide nimic. Șterge-l sau adaugă paranteza de deschidere care lipsește.",
      "traceback", "SyntaxError nu are cadre"),
    R("SyntaxError", r"f-string: expecting '}'", "Acoladă neînchisă în f-string",
      "Într-un f-string, fiecare `{{` are nevoie de perechea ei `}}`. Verifică acoladele de pe rândul {rand}.",
      "f-strings", ""),
    R("SyntaxError", r"Missing parentheses in call to 'print'", "print fără paranteze",
      "În Python 3, `print` e o funcție: ce afișezi stă între paranteze, `print(\"Salut\")`.",
      "primul-program", "5. print fără paranteze"),
    R("SyntaxError", r"Maybe you meant '==' or ':=' instead of '='", "= în loc de ==",
      "`=` dă o valoare unei variabile; pentru a compara două valori se folosește `==`. "
      "Pe rândul {rand} scrie `==`.", "if-else", "3. = în loc de == în condiție"),
    R("SyntaxError", r"Perhaps you forgot a comma", "Lipsește o virgulă",
      "Între valorile dintr-o listă de argumente sau elemente trebuie virgulă. Pe rândul {rand} lipsește una.",
      "primul-program", ""),
    R("SyntaxError", r"cannot assign to (?P<ce>True|False|None)", "Nume rezervat",
      "`{ce}` e un cuvânt rezervat al limbajului, nu poate primi o valoare. Alege alt nume pentru variabilă.",
      "variabile", "4. Un cuvânt rezervat ca nume"),
    R("SyntaxError", r"invalid decimal literal", "Nume care începe cu cifră",
      "Numele de variabile nu pot începe cu o cifră și nu pot conține spații. Exemplu corect: `nota1`, nu `1nota`.",
      "variabile", "3. Nume care încep cu cifră sau conțin spații"),
    R("SyntaxError", r"'return' outside function", "return în afara unei funcții",
      "`return` are sens doar în interiorul unei funcții (`def`). Verifică indentarea rândului {rand}.",
      "functii-definire", ""),
    R("SyntaxError", r"'(?P<cuv>break|continue)' outside loop|'(?P<cuv2>break|continue)' not properly in loop",
      "break / continue în afara buclei",
      "`break` și `continue` pot sta doar în interiorul unei bucle `for` sau `while`. "
      "Verifică indentarea rândului {rand}.", "break-continue", ""),
    R("IndentationError", r"unexpected indent", "Spații în plus la începutul rândului",
      "„Unexpected indent” înseamnă „indentare neașteptată”: rândul {rand} începe cu spații, deși nu e într-un bloc. "
      "Șterge spațiile din fața lui.", "primul-program", "4. Spații în fața rândului"),
    R("IndentationError", r"expected an indented block after '(?P<instr>\w+)' statement on line (?P<linie>\d+)",
      "Blocul nu e indentat",
      "După `{instr}` de pe rândul {linie} trebuia să urmeze un bloc indentat: rândurile din el încep cu 4 spații.",
      "if-else", "2. Blocul nu e indentat"),
    R("IndentationError", r"expected an indented block", "Blocul nu e indentat",
      "După un rând terminat cu `:` urmează un bloc indentat: rândurile din el încep cu 4 spații.",
      "if-else", "2. Blocul nu e indentat"),
    R("IndentationError", r"unindent does not match any outer indentation level", "Indentare inconsecventă",
      "Rândul {rand} are alt număr de spații decât blocurile de deasupra. Folosește peste tot câte 4 spații pe nivel.",
      "if-else", "5. Indentare inconsecventă"),
    R("TabError", r"", "Tab-uri amestecate cu spații",
      "Blocul folosește și tab-uri, și spații. Python le vrea pe aceleași: folosește doar spații (4 pe nivel).",
      "if-else", "5. Indentare inconsecventă"),
    R("SyntaxError", r"^invalid syntax$", "Sintaxă greșită",
      "Python nu înțelege rândul {rand}. Uită-te după `:` lipsă, ghilimele sau paranteze neînchise, `=` în loc de `==`. "
      "Dacă rândul pare corect, greșeala e adesea pe rândul de deasupra.",
      "traceback", "SyntaxError nu are cadre"),

    # ---------------------------------------------------------------- nume
    R("NameError", r"name '(?P<nume>[^']+)' is not defined. Did you mean: '(?P<sug>[^']+)'\?",
      "Nume scris greșit",
      "Python nu cunoaște numele `{nume}` și sugerează `{sug}`. Dacă acolo voiai `{sug}`, corectează scrierea "
      "(literele mari și mici contează). Dacă nu, `{nume}` e o variabilă care n-a primit încă o valoare mai sus.",
      "variabile", "2. O greșeală de tastare în nume"),
    R("NameError", r"name '(?P<nume>[^']+)' is not defined. Did you forget to import '(?P<mod>[^']+)'",
      "Lipsește importul",
      "Folosești modulul `{mod}` fără să-l fi importat. Adaugă `import {mod}` la începutul fișierului.",
      "module-import", ""),
    R("NameError", r"name '(?P<nume>[^']+)' is not defined", "Nume necunoscut",
      "Python nu cunoaște numele `{nume}` pe rândul {rand}. Fie variabila primește o valoare abia mai jos (o variabilă "
      "există doar după rândul în care o creezi), fie numele e scris altfel decât la creare. "
      "Dacă `{nume}` trebuia să fie un text, pune-l între ghilimele.",
      "variabile", "1. Folosirea unei variabile înainte să existe"),
    R("UnboundLocalError", r"local variable '(?P<nume>[^']+)'|local variable '(?P<nume2>[^']+)'|"
      r"cannot access local variable '(?P<nume3>[^']+)'", "Variabilă locală fără valoare",
      "O atribuire oriunde într-o funcție face numele local în toată funcția. Funcția încearcă să citească variabila "
      "înainte să-i dea o valoare. Trimite valoarea ca argument și întoarce rezultatul cu `return`.",
      "scope", "1. UnboundLocalError la modificarea unei variabile globale"),

    # ---------------------------------------------------------------- tipuri
    R("TypeError", r'can only concatenate str \(not "(?P<t>\w+)"\) to str', "Text adunat cu un număr",
      "`+` poate doar să „lipească” un text de alt text, nu un text de un `{t}`. Transformă valoarea cu `str(...)` "
      "sau, mai simplu, folosește un f-string: `f\"Ai {{varsta}} ani\"`.",
      "numere", "5. Adunarea unui număr cu un text"),
    R("TypeError", r"unsupported operand type\(s\) for (?P<op>\S+): '(?P<a>\w+)' and '(?P<b>\w+)'",
      "Operație între tipuri diferite",
      "Operația `{op}` nu merge între un `{a}` și un `{b}`. Dacă una din valori vine din `input()`, e text: "
      "transform-o cu `int(...)` sau `float(...)` înainte de calcul.",
      "input-conversii", "1. Calcule cu rezultatul lui input(), fără conversie"),
    R("TypeError", r"can't multiply sequence by non-int of type '(?P<t>\w+)'", "Înmulțire cu un text",
      "Un text se poate înmulți doar cu un număr întreg (`\"ab\" * 3`). Aici al doilea termen e `{t}`: "
      "probabil vine din `input()` și trebuie transformat cu `int(...)`.",
      "input-conversii", "1. Calcule cu rezultatul lui input(), fără conversie"),
    R("TypeError", r"'(?P<op>[<>]=?)' not supported between instances of '(?P<a>\w+)' and '(?P<b>\w+)'",
      "Comparație între tipuri diferite",
      "Nu poți compara cu `{op}` un `{a}` cu un `{b}`. Cel mai des, unul e text venit din `input()`: "
      "transformă-l cu `int(...)` înainte de comparație.", "input-conversii", ""),
    R("TypeError", r"'(?P<t>\w+)' object is not iterable", "Nu se poate parcurge",
      "`for` merge peste o colecție (listă, text, `range(...)`), nu peste un `{t}`. "
      "Pentru a repeta de N ori, scrie `for i in range(N):`.", "for-range", ""),
    R("TypeError", r"unhashable type: '(?P<t>\w+)'", "Cheie care nu poate fi folosită",
      "Cheile unui dicționar (și elementele unui set) trebuie să fie imutabile. Un `{t}` se poate schimba, deci nu "
      "poate fi cheie: folosește un tuplu sau un text.", "dictionare", "3. Listă folosită drept cheie"),
    R("TypeError", r"(?P<f>[\w.]+)\(\) missing (?P<n>\d+) required positional argument",
      "Lipsesc argumente",
      "Funcția `{f}` cere mai multe valori decât i-ai dat. Python îți spune exact ce lipsește în mesaj; "
      "pune-le între parantezele apelului.", "functii-definire", "4. Număr greșit de argumente"),
    R("TypeError", r"(?P<f>[\w.]+)\(\) takes (?P<n>\d+) positional arguments? but (?P<m>\d+) (?:were|was) given",
      "Prea multe argumente",
      "Funcția `{f}` primește {n} argument(e), dar i-ai dat {m}. Verifică apelul de pe rândul {rand}.",
      "functii-definire", "4. Număr greșit de argumente"),
    R("TypeError", r"'(?P<t>\w+)' object is not callable", "Apel pe ceva care nu e funcție",
      "Ai pus paranteze `(...)` după o valoare de tip `{t}`, ca și cum ar fi o funcție. Poate ai dat unei variabile "
      "numele unei funcții (`list`, `str`, `input`...) și ai acoperit-o, sau voiai paranteze drepte `[...]`.",
      "scope", "3. Un nume built-in acoperit de o variabilă"),
    R("TypeError", r"'NoneType' object is not subscriptable", "None în loc de valoare",
      "Valoarea de pe rândul {rand} e `None`: de obicei o funcție care nu are `return`, sau rezultatul lui "
      "`.sort()` / `.append()`, care modifică lista pe loc și întorc `None`.",
      "liste", "2. Atribuirea rezultatului lui append() sau sort()"),
    R("TypeError", r"'(?P<t>\w+)' object is not subscriptable", "Index pe ceva care nu e colecție",
      "`[...]` merge pe liste, texte, tupluri și dicționare, nu pe un `{t}`.", "liste", ""),
    R("TypeError", r"object of type '(?P<t>\w+)' has no len\(\)", "len() pe un număr",
      "`len()` numără elementele unei colecții sau caracterele unui text; un `{t}` nu are lungime. "
      "Pentru cifrele unui număr: `len(str(numar))`.", "stringuri", ""),
    R("TypeError", r"'(?P<t>\w+)' object does not support item assignment", "Valoare care nu se poate modifica",
      "Un `{t}` nu poate fi modificat pe loc. Construiește o valoare nouă (de exemplu un text nou) în loc să schimbi "
      "un element.", "stringuri", "2. Încercarea de a schimba un caracter"),

    # ---------------------------------------------------------------- valori
    R("ValueError", r"invalid literal for int\(\) with base 10: ''", "Răspuns gol",
      "`int()` a primit un text gol: s-a apăsat Enter fără să se scrie nimic. Scrie un număr când programul îl cere.",
      "input-conversii", "4. Răspuns gol"),
    R("ValueError", r"invalid literal for int\(\) with base 10: '(?P<v>-?\d+[.,]\d+)'", "Număr cu zecimale în int()",
      "`int()` acceptă doar numere întregi scrise ca text; `{v}` are zecimale. Folosește `float(...)` sau scrie un "
      "număr întreg.", "input-conversii", "2. int() pe un număr cu zecimale"),
    R("ValueError", r"invalid literal for int\(\) with base 10: '(?P<v>.*)'", "Textul nu e număr",
      "`int()` a primit textul `{v}`, care nu arată ca un număr. Un text care nu arată exact ca un număr dă "
      "`ValueError`.", "input-conversii", "Conversia în număr: int() și float()"),
    R("ValueError", r"could not convert string to float: '(?P<v>.*)'", "Textul nu e număr",
      "`float()` a primit `{v}`, care nu e un număr. Atenție: zecimalele se scriu cu punct (`3.5`), nu cu virgulă.",
      "input-conversii", "3. Virgula zecimală românească"),
    R("ValueError", r"too many values to unpack \(expected (?P<n>\d+)", "Prea multe valori la despachetare",
      "În stânga lui `=` sunt {n} variabile, dar în dreapta sunt mai multe valori. Numărul trebuie să fie egal.",
      "tupluri", "4. Număr greșit de variabile la despachetare"),
    R("ValueError", r"not enough values to unpack \(expected (?P<n>\d+), got (?P<m>\d+)\)",
      "Prea puține valori la despachetare",
      "În stânga lui `=` sunt {n} variabile, dar în dreapta doar {m} valori. Numărul trebuie să fie egal.",
      "tupluri", "4. Număr greșit de variabile la despachetare"),
    R("ValueError", r"list\.remove\(x\): x not in list", "Valoarea nu e în listă",
      "`remove()` caută valoarea în listă și dă eroare dacă nu o găsește. Verifică întâi cu `if valoare in lista:`.",
      "liste", "3. remove() pe o valoare care nu există"),
    R("ValueError", r"(?P<v>.+) is not in list", "Valoarea nu e în listă",
      "`index()` n-a găsit {v} în listă. Verifică întâi cu `in`.", "liste", ""),

    # ---------------------------------------------------------------- colecții
    R("IndexError", r"string index out of range", "Index prea mare (text)",
      "Ai cerut o poziție care nu există în text. Ultimul index e mereu `len(text) - 1`, iar numărătoarea începe de la 0.",
      "stringuri", "3. Index prea mare"),
    R("IndexError", r"(list|tuple) index out of range", "Index în afara listei",
      "Ai cerut o poziție care nu există. O listă cu 3 elemente are indicii 0, 1 și 2; ultimul element e `lista[-1]`.",
      "liste", "1. Index în afara listei"),
    R("KeyError", r"(?P<cheie>.+)", "Cheie inexistentă",
      "Dicționarul nu are cheia {cheie}. Verifică scrierea (literele mari contează) sau folosește `in` ori "
      "`.get()` când cheia poate lipsi.", "dictionare", "1. Cheie inexistentă"),
    R("AttributeError", r"'NoneType' object has no attribute '(?P<a>[^']+)'", "None în loc de valoare",
      "Valoarea pe care chemi `.{a}` e `None`: de obicei rezultatul unei funcții fără `return` sau al unei metode "
      "care modifică pe loc (`.sort()`, `.append()`).",
      "liste", "2. Atribuirea rezultatului lui append() sau sort()"),
    R("AttributeError", r"'(?P<t>\w+)' object has no attribute '(?P<a>[^']+)'. Did you mean: '(?P<sug>[^']+)'\?",
      "Metodă scrisă greșit",
      "Un `{t}` nu are `.{a}`. Probabil ai vrut să scrii `.{sug}`.", "traceback",
      "3. Ignorarea sugestiilor „Did you mean”"),
    R("AttributeError", r"module '(?P<m>[^']+)' has no attribute '(?P<a>[^']+)'. Did you mean: '(?P<sug>[^']+)'\?",
      "Funcție scrisă greșit",
      "Modulul `{m}` nu are `{a}`. Probabil ai vrut să scrii `{m}.{sug}`.", "traceback",
      "3. Ignorarea sugestiilor „Did you mean”"),
    R("AttributeError", r"'tuple' object has no attribute '(?P<a>[^']+)'", "Metodă de listă pe un tuplu",
      "Tuplurile nu se pot modifica, deci nu au `.{a}`. Dacă trebuie să adaugi sau să ștergi, folosește o listă.",
      "tupluri", "2. Metode de listă pe un tuplu"),
    R("AttributeError", r"'(?P<t>\w+)' object has no attribute '(?P<a>[^']+)'", "Metodă inexistentă",
      "Un `{t}` nu are metoda sau atributul `.{a}`. Verifică numele și tipul valorii (de exemplu, listele au "
      "`.append()`, nu `.push()`).", "tupluri", ""),
    R("AttributeError", r"module '(?P<m>[^']+)' has no attribute '(?P<a>[^']+)'", "Funcție inexistentă în modul",
      "Modulul `{m}` nu are `{a}`. Verifică numele, sau dacă ți-ai numit propriul fișier `{m}.py` "
      "(atunci Python îl importă pe al tău).", "module-import", ""),

    # ---------------------------------------------------------------- aritmetică, module, fișiere, altele
    R("ZeroDivisionError", r"", "Împărțire la zero",
      "Pe rândul {rand} se împarte la zero. Când împărțitorul vine dintr-un calcul sau de la utilizator, "
      "verifică întâi dacă e zero (`if impartitor != 0:`).", "numere", "1. Împărțirea la zero"),
    R("ModuleNotFoundError", r"No module named '(?P<m>[^']+)'", "Modulul nu e găsit",
      "Python nu găsește modulul `{m}`. Cauze, în ordinea frecvenței: numele e scris greșit; modulul e în alt folder; "
      "e un pachet care nu e instalat (`pip install ...`).", "module-import", "1. Modulul nu e găsit"),
    R("ImportError", r"cannot import name '(?P<n>[^']+)' from '(?P<m>[^']+)'", "Nume inexistent în modul",
      "Modulul `{m}` a fost găsit, dar nu conține `{n}`. Verifică numele.",
      "module-import", "2. Un nume care nu există în modul"),
    R("FileNotFoundError", r"No such file or directory: '(?P<f>[^']+)'", "Fișierul nu există",
      "Nu găsesc fișierul `{f}`. Cele mai dese cauze sunt numele scris greșit și folderul curent diferit de cel în "
      "care e fișierul.", "fisiere", "1. Fișierul nu există"),
    R("EOFError", r"", "Programul așteaptă input",
      "`input()` aștepta un răspuns, dar nu a mai primit nimic. Rulează programul și scrie răspunsul în terminal, "
      "apoi apasă Enter.", "input-conversii", ""),
    R("RecursionError", r"", "Funcția se cheamă la nesfârșit",
      "O funcție se apelează pe ea însăși fără să se oprească. Orice funcție recursivă are nevoie de un caz în care "
      "nu se mai apelează (cazul de bază).", "functii-definire", ""),
]


def _parse(output: str) -> dict | None:
    lines = [ln.rstrip() for ln in output.replace("\r\n", "\n").split("\n")]
    last = None
    for i in range(len(lines) - 1, -1, -1):
        m = _LAST_RE.match(lines[i])
        if m:
            last = (i, m)
            break
    if not last:
        return None
    idx, m = last
    tip = m["tip"].rsplit(".", 1)[-1]
    rand, fisier, cod = None, None, ""
    for j in range(idx - 1, -1, -1):  # ultimul cadru din codul elevului
        f = _FRAME_RE.match(lines[j])
        if f and not _LIBRARY_RE.search(f["file"]):
            rand, fisier = int(f["line"]), f["file"]
            cod = lines[j + 1].strip() if j + 1 < idx else ""
            break
    return {"tip": tip, "mesaj": m["msg"].strip(), "rand": rand, "fisier": fisier, "cod": cod}


def explica(output: str) -> dict | None:
    """Explicația pentru ultima eroare din `output`, sau None dacă nu e o eroare cunoscută."""
    p = _parse(output or "")
    if not p:
        return None
    for r in REGULI:
        if p["tip"] not in r.tip.split("|"):
            continue
        m = re.search(r.mesaj, p["mesaj"])
        if not m:
            continue
        values = {k: v for k, v in m.groupdict().items() if v is not None}
        values["rand"] = p["rand"] or "indicat"
        text = r.explicatie.format_map(_Missing(values))
        sug = _DID_YOU_MEAN_RE.search(p["mesaj"])
        return {
            "tip": p["tip"],
            "mesaj": p["mesaj"],
            "titlu": r.titlu,
            "explicatie": text,
            "rand": p["rand"],
            "fisier": p["fisier"],
            "cod": p["cod"],
            "sugestie": sug["sug"] if sug else None,
            "lectie": _lectie(r.lectie, r.sectiune),
        }
    return None


class _Missing(dict):
    def __missing__(self, key):
        return "?"


def _lectie(slug: str, sectiune: str) -> dict | None:
    """Numărul și titlul lecției (din curriculum), pentru link."""
    if not slug:
        return None
    try:
        from .models import Topic  # import târziu: modulul se poate folosi și fără Django configurat

        topics = list(Topic.objects.order_by("module__order", "order").values_list("slug", "title"))
    except Exception:  # noqa: BLE001 — fără bază de date: doar slug-ul
        return {"slug": slug, "numar": None, "titlu": "", "sectiune": sectiune}
    for n, (s, title) in enumerate(topics, 1):
        if s == slug:
            return {"slug": slug, "numar": n, "titlu": title, "sectiune": sectiune}
    return None
