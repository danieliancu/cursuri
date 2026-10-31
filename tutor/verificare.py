"""Verificarea exercițiilor fixe din lecții, făcută de cod (fără AI).

Fiecare exercițiu are un fișier `tutor/exercitii/NN-slug.toml` cu teste (ce primește programul la input și
ce trebuie să apară în output), verificări de structură (ex. „folosește un for”), indicii în trepte și o
soluție de referință (folosită doar de `tools/verifica_exercitii.py`, ca testele să fie mereu corecte).

Verdictul e exact („trebuia să apară 108.00, rândul 5 din output”); AI-ul (modelul mic) doar îl formulează.

Formatul unui test:
    [[test]]
    nume = "coș de 120 lei cu codul student"   # apare în verdict
    stdin = "120\\nstudent\\n"                  # ce primește input(), câte un rând pe răspuns
    contine = ["12.00", "108.00"]               # textele care trebuie să apară în output
    regex = ['^=+$']                            # expresii regulate pe output (pe forma „pliată”, vezi mai jos)
    nu_contine = ["cod necunoscut"]
    iesire = '''...'''                          # output-ul exact (rând cu rând), dacă e fix
    min_randuri = 5                             # câte rânduri ne-goale trebuie să afișeze cel puțin
    rand_gol = true                             # trebuie să afișeze și un rând gol
    de_ce = "..."                               # ce verifică testul, spus elevului când pică
    indiciu = "..."                             # primul indiciu când pică testul ăsta (apoi cele generale)

`contine`, `nu_contine` și `regex` nu țin cont de literele mari/mici, de diacritice și de spațiile multiple
(„Parolă puternică” = „parola  puternica”), ca elevul să aibă libertate la formulare.
"""
import ast
import difflib
import functools
import io
import re
import tokenize
import unicodedata
from pathlib import Path
from typing import Callable

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

from . import erori, iesire

EXERCITII_DIR = Path(__file__).resolve().parent / "exercitii"
INCEPUT_DIR = EXERCITII_DIR / "inceput"  # doar exemple de început, pentru lecțiile fără exercițiu fix
_NAME_RE = re.compile(r"^(?P<n>\d{2})-(?P<slug>[a-z0-9-]+)\.toml$")
MAX_OUTPUT = 1500  # cât din output intră în verdict (și la AI)


# ---------------------------------------------------------------- încărcare

@functools.cache
def _all() -> dict[str, dict]:
    out = {}
    for p in sorted(EXERCITII_DIR.glob("*.toml")):
        m = _NAME_RE.match(p.name)
        if m:
            data = tomllib.loads(p.read_text(encoding="utf-8"))
            data["slug"], data["numar"], data["sursa"] = m["slug"], int(m["n"]), p.name
            out[m["slug"]] = data
    return out


def exercitiu(slug: str) -> dict | None:
    return _all().get(slug)


def toate() -> list[dict]:
    return list(_all().values())


def inceput(slug: str) -> str:
    """Exemplul de început al lecției: `inceput` din exercițiul fix, altfel `exercitii/inceput/NN-slug.py`
    (lecțiile fără teste au doar exemplul, iar fișierul capitolului îl verifică tutorele)."""
    ex = exercitiu(slug)
    if ex and ex.get("inceput"):
        return ex["inceput"]
    p = next(INCEPUT_DIR.glob(f"[0-9][0-9]-{slug}.py"), None)
    return p.read_text(encoding="utf-8") if p else ""


def exercitiu_numar(n: int) -> dict | None:
    """Exercițiul lecției cu numărul `n` (ca în `capitole/NN-slug/`)."""
    return next((ex for ex in _all().values() if ex["numar"] == n), None)


# ---------------------------------------------------------------- potrivirea output-ului

def pliaza(s: str) -> str:
    """Fără diacritice, cu litere mici, fără spații la final de rând și cu spațiile multiple comasate."""
    s = unicodedata.normalize("NFD", s.replace("\r\n", "\n"))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return "\n".join(re.sub(r"[ \t]+", " ", ln).rstrip() for ln in s.split("\n"))


def _contine(out: str, text: str) -> bool:
    """Textul apare în output; la text pe mai multe rânduri (ex. un desen), spațiile din față contează."""
    if "\n" in text.strip("\n"):
        want = "\n".join(ln.rstrip() for ln in text.strip("\n").split("\n"))
        have = "\n".join(ln.rstrip() for ln in out.replace("\r\n", "\n").split("\n"))
        return want in have
    return pliaza(text).strip() in pliaza(out)


# ---------------------------------------------------------------- structura codului (AST)

STRUCTURI = {
    "if": "o instrucțiune `if`",
    "elif": "o ramură `elif`",
    "else": "o ramură `else`",
    "for": "o buclă `for`",
    "while": "o buclă `while`",
    "while_true": "o buclă `while True`",
    "break": "`break`",
    "continue": "`continue`",
    "for_else": "un `else` la `for` (rulează doar dacă bucla n-a fost oprită cu `break`)",
    "input": "`input()`, ca programul să citească de la tastatură",
    "fstring": "un f-string (`f\"...\"`)",
    "format": "un f-string cu formatare (ex. `{valoare:.2f}` sau `{text:<15}`)",
    "comentariu": "cel puțin un comentariu (`# ...`)",
    "inmultire": "o înmulțire (`*`)",
    "impartire_intreaga": "împărțirea întreagă `//`",
    "modulo": "restul împărțirii `%`",
    "reatribuire": "o variabilă care primește o valoare nouă (reatribuire)",
    "def": "o funcție (`def`)",
    "return": "o funcție care întoarce un rezultat (`return`)",
    "lista": "o listă (`[...]`)",
    "dict": "un dicționar (`{cheie: valoare}`)",
    "set": "un set (`set(...)` sau `{a, b}`)",
    "for_despachetare": "un `for` cu despachetare (ex. `for nume, x, y in orase:`)",
    "for_imbricat": "două bucle `for` una în alta",
    "list_comprehension": "un list comprehension (`[... for ... in ...]`)",
    "dict_comprehension": "un dict comprehension (`{cheie: valoare for ... in ...}`)",
    "set_comprehension": "un set comprehension (`{... for ... in ...}`)",
    "lambda": "o funcție `lambda`",
    "argument_implicit": "un parametru cu valoare implicită (ex. `zecimale=2`)",
    "args": "un parametru `*args` (oricâte argumente poziționale)",
    "keyword_only": "parametri doar cu nume, după `*` (ex. `def f(a, *, prag=5)`)",
    "global": "`global`",
    "docstring": "un docstring la fiecare funcție (primul rând din corp, între `\"\"\"`)",
    "type_hints": "type hints la toți parametrii și la rezultat (`-> ...`), la fiecare funcție",
    "default_mutabil": "o valoare implicită mutabilă (`=[]` sau `={}`) la un parametru",
    "alias_tip": "un alias de tip (ex. `Catalog = dict[str, list[float]]`)",
}


def _calls(tree: ast.AST) -> set[str]:
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name):
                out.add(n.func.id)
            elif isinstance(n.func, ast.Attribute):
                out.add(n.func.attr)
    return out


def _has(tree: ast.AST, source: str, what: str) -> bool:
    nodes = list(ast.walk(tree))
    if what.startswith("apel:"):
        return what[5:] in _calls(tree)
    if what == "if":
        return any(isinstance(n, ast.If) for n in nodes)
    if what == "elif":
        return any(isinstance(n, ast.If) and len(n.orelse) == 1 and isinstance(n.orelse[0], ast.If) for n in nodes)
    if what == "else":
        return any(isinstance(n, ast.If) and n.orelse and not (len(n.orelse) == 1 and isinstance(n.orelse[0], ast.If))
                   for n in nodes)
    if what == "for":
        return any(isinstance(n, ast.For) for n in nodes)
    if what == "while":
        return any(isinstance(n, ast.While) for n in nodes)
    if what == "while_true":
        return any(isinstance(n, ast.While) and isinstance(n.test, ast.Constant) and n.test.value is True for n in nodes)
    if what == "break":
        return any(isinstance(n, ast.Break) for n in nodes)
    if what == "continue":
        return any(isinstance(n, ast.Continue) for n in nodes)
    if what == "for_else":
        return any(isinstance(n, ast.For) and n.orelse for n in nodes)
    if what == "input":
        return "input" in _calls(tree)
    if what == "fstring":
        return any(isinstance(n, ast.JoinedStr) for n in nodes)
    if what == "format":
        return any(isinstance(n, ast.FormattedValue) and n.format_spec is not None for n in nodes)
    if what == "comentariu":
        try:
            return any(t.type == tokenize.COMMENT for t in tokenize.generate_tokens(io.StringIO(source).readline))
        except (tokenize.TokenError, SyntaxError):
            return "#" in source
    if what == "inmultire":
        return any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult) for n in nodes)
    if what == "impartire_intreaga":
        return any(isinstance(n, (ast.BinOp, ast.AugAssign)) and isinstance(n.op, ast.FloorDiv) for n in nodes)
    if what == "modulo":
        return any(isinstance(n, (ast.BinOp, ast.AugAssign)) and isinstance(n.op, ast.Mod) for n in nodes)
    if what == "reatribuire":
        seen: dict[str, int] = {}
        for n in nodes:
            targets = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(n, ast.AugAssign) else []
            for t in targets:
                if isinstance(t, ast.Name):
                    seen[t.id] = seen.get(t.id, 0) + 1
        return any(v >= 2 for v in seen.values())
    if what == "def":
        return any(isinstance(n, ast.FunctionDef) for n in nodes)
    funcs = [n for n in nodes if isinstance(n, ast.FunctionDef)]
    if what == "return":
        return any(isinstance(n, ast.Return) and n.value is not None for n in nodes)
    if what == "lista":
        return any(isinstance(n, (ast.List, ast.ListComp)) for n in nodes) or "list" in _calls(tree)
    if what == "dict":
        return any(isinstance(n, (ast.Dict, ast.DictComp)) for n in nodes) or "dict" in _calls(tree)
    if what == "set":
        return any(isinstance(n, (ast.Set, ast.SetComp)) for n in nodes) or "set" in _calls(tree)
    if what == "for_despachetare":
        return any(isinstance(n, (ast.For, ast.comprehension)) and isinstance(n.target, ast.Tuple) for n in nodes)
    if what == "for_imbricat":
        return any(isinstance(n, ast.For) and any(isinstance(m, ast.For) for m in ast.walk(n) if m is not n)
                   for n in nodes)
    if what == "list_comprehension":
        return any(isinstance(n, ast.ListComp) for n in nodes)
    if what == "dict_comprehension":
        return any(isinstance(n, ast.DictComp) for n in nodes)
    if what == "set_comprehension":
        return any(isinstance(n, ast.SetComp) for n in nodes)
    if what == "lambda":
        return any(isinstance(n, ast.Lambda) for n in nodes)
    if what == "argument_implicit":
        return any(f.args.defaults or any(d is not None for d in f.args.kw_defaults) for f in funcs)
    if what == "args":
        return any(f.args.vararg for f in funcs)
    if what == "keyword_only":
        return any(f.args.kwonlyargs for f in funcs)
    if what == "global":
        return any(isinstance(n, ast.Global) for n in nodes)
    if what == "docstring":
        return bool(funcs) and all(ast.get_docstring(f) for f in funcs)
    if what == "type_hints":
        def annotated(f):
            a = f.args
            params = a.posonlyargs + a.args + a.kwonlyargs + [p for p in (a.vararg, a.kwarg) if p]
            return f.returns is not None and all(p.annotation is not None for p in params)
        return bool(funcs) and all(annotated(f) for f in funcs)
    if what == "default_mutabil":
        mutable = (ast.List, ast.Dict, ast.Set)
        return any(isinstance(d, mutable) for f in funcs for d in f.args.defaults + f.args.kw_defaults)
    if what == "alias_tip":
        return any(isinstance(n, (ast.Assign, ast.AnnAssign)) and isinstance(n.value, ast.Subscript)
                   and isinstance(n.value.value, ast.Name) and n.value.value.id in ("dict", "list", "tuple", "set")
                   for n in getattr(tree, "body", []))
    raise ValueError(f"verificare de structură necunoscută: {what}")


def descrie_structura(what: str) -> str:
    if what.startswith("apel:"):
        return f"`{what[5:]}()`"
    return STRUCTURI.get(what, what)


# ---------------------------------------------------------------- pyflakes (avertismente de stil)

def observatii(source: str, fisier: str = "program.py") -> list[dict]:
    """Avertismentele utile unui începător: nume nedefinit, import sau variabilă nefolosită."""
    try:
        from pyflakes import checker, messages
    except ImportError:
        return []
    try:
        tree = ast.parse(source, fisier)
    except SyntaxError:
        return []
    out = []
    for m in checker.Checker(tree, filename=fisier).messages:
        name = m.message_args[0] if m.message_args else ""
        if isinstance(m, messages.UndefinedName):
            text = f"Numele `{name}` nu e definit nicăieri în fișier."
        elif isinstance(m, messages.UnusedImport):
            text = f"Importul `{name}` nu e folosit."
        elif isinstance(m, messages.UnusedVariable):
            text = f"Variabila `{name}` primește o valoare, dar nu e folosită."
        elif isinstance(m, messages.RedefinedWhileUnused):
            text = f"`{name}` e definit din nou înainte să fie folosit."
        else:
            continue
        out.append({"rand": m.lineno, "text": text, "grav": isinstance(m, messages.UndefinedName)})
    return out


# ---------------------------------------------------------------- verificarea

Runner = Callable[[str], tuple["int | None", str]]


def fara_cod(source: str) -> bool:
    """Fișierul are doar comentarii, texte între ghilimele (docstring-uri) sau `pass`: nimic de verificat.
    O greșeală de sintaxă înseamnă că elevul a scris ceva, deci nu e „fără cod”."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    return all(
        isinstance(s, ast.Pass) or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)
                                    and isinstance(s.value.value, str))
        for s in tree.body
    )


def verifica_cod(source: str, ex: dict, run: Runner, fisier: str = "program.py") -> dict:
    """Verdictul pentru codul `source` al exercițiului `ex`. `run(stdin)` rulează programul și întoarce
    (cod de ieșire sau None la timeout, output) — în aplicație e containerul elevului, la validare un subprocess."""
    v: dict = {"rezultat": "greșit", "exercitiu": ex.get("titlu", ""), "teste": [], "observatii": []}

    # 1. sintaxa: fără ea nu rulează nimic
    try:
        tree = ast.parse(source, fisier)
    except SyntaxError as e:
        text = (f'  File "{fisier}", line {e.lineno}\n    {(e.text or "").rstrip()}\n'
                f"{type(e).__name__}: {e.msg}\n")
        v.update(etapa="sintaxa", rand=e.lineno, detaliu="Programul are o greșeală de sintaxă și nu poate porni.",
                 eroare=erori.explica(text))
        return v
    if fara_cod(source):
        v.update(etapa="gol", detaliu="Fișierul nu conține încă niciun cod.")
        return v

    # 2. pyflakes
    obs = observatii(source, fisier)
    v["observatii"] = [o for o in obs if not o["grav"]]
    grave = [o for o in obs if o["grav"]]

    # 3. structura cerută de exercițiu
    for what in ex.get("structura", []):
        if not _has(tree, source, what):
            v.update(etapa="structura", detaliu=f"Exercițiul cere {descrie_structura(what)}, dar nu o găsesc în cod.",
                     lipseste=what)
            return v
    for what in ex.get("interzis", []):
        if _has(tree, source, what):
            v.update(etapa="structura", detaliu=f"Exercițiul cere să rezolvi fără {descrie_structura(what)}.",
                     interzis=what)
            return v

    # 4. testele
    for t in ex.get("test", []):
        stdin = t.get("stdin", "")
        rc, out = run(stdin)
        out = out.replace("\r\n", "\n")
        problema = _problema(t, rc, out)
        v["teste"].append({"nume": t.get("nume", ""), "ok": problema is None})
        if problema:
            v.update(etapa="test", test=t.get("nume", ""), intrare=_arata_intrare(stdin),
                     obtinut=_scurt(out), **problema)
            if t.get("de_ce"):
                v["de_ce"] = t["de_ce"]
            if t.get("indiciu"):
                v["indiciu_test"] = t["indiciu"]
            return v

    if grave:  # n-a crăpat la teste, dar un nume nedefinit tot e o greșeală (pe o ramură netestată)
        v.update(etapa="observatii", rand=grave[0]["rand"], detaliu=grave[0]["text"])
        return v
    v.update(rezultat="corect", etapa="ok", detaliu="Toate verificările au trecut.")
    return v


def _problema(t: dict, rc: "int | None", out: str) -> dict | None:
    if rc is None:
        return {"detaliu": "Programul nu s-a terminat în timp: probabil așteaptă mai multe răspunsuri decât "
                           "primește sau are o buclă care nu se oprește.", "motiv": "timeout"}
    if rc != 0 or "Traceback (most recent call last)" in out:
        e = erori.explica(out)
        return {"detaliu": "Programul s-a oprit cu o eroare.", "motiv": "eroare", "eroare": e,
                "rand": e["rand"] if e else None}
    if "iesire" in t and not iesire.compare(t["iesire"], out):
        diff = iesire.first_difference(t["iesire"], out)
        if diff:
            rand, exp, act = diff
            return {"detaliu": f"Output-ul diferă la rândul {rand}.", "motiv": "iesire",
                    "rand_iesire": rand, "asteptat": exp, "obtinut_rand": act}
    for text in t.get("contine", []):
        if not _contine(out, text):
            return {"detaliu": f"În output trebuia să apară „{text}”, dar nu apare.", "motiv": "lipseste",
                    "asteptat": text}
    for pattern in t.get("regex", []):
        if not re.search(pattern, pliaza(out), re.M):
            return {"detaliu": t.get("regex_de_ce", "Output-ul nu are forma cerută."), "motiv": "forma",
                    "asteptat": t.get("regex_text", pattern)}
    for text in t.get("nu_contine", []):
        if _contine(out, text):
            return {"detaliu": f"În output NU trebuia să apară „{text}”.", "motiv": "in_plus", "nedorit": text}
    lines = [ln for ln in out.split("\n") if ln.strip()]
    if len(lines) < t.get("min_randuri", 0):
        return {"detaliu": f"Programul trebuia să afișeze cel puțin {t['min_randuri']} rânduri; a afișat {len(lines)}.",
                "motiv": "prea_putin"}
    if t.get("rand_gol") and not re.search(r"\S[^\n]*\n[ \t]*\n[ \t]*\S", out):
        return {"detaliu": "Trebuia să afișezi și un rând gol (de exemplu cu `print()`).", "motiv": "rand_gol"}
    return None


def _arata_intrare(stdin: str) -> list[str]:
    return stdin.removesuffix("\n").split("\n") if stdin else []


def _scurt(out: str) -> str:
    out = out.strip("\n")
    return out if len(out) <= MAX_OUTPUT else "…\n" + out[-MAX_OUTPUT:]


# ---------------------------------------------------------------- pentru AI

def pentru_ai(v: dict, hint: dict | None) -> dict:
    """Verdictul pe scurt (câteva sute de tokeni), pentru formularea făcută de modelul mic."""
    out = {k: v[k] for k in ("rezultat", "exercitiu", "detaliu", "test", "intrare", "asteptat", "de_ce") if v.get(k)}
    if v.get("motiv") == "iesire":
        out["obtinut_pe_rand"] = v.get("obtinut_rand")
    elif v.get("obtinut"):
        out["obtinut"] = v["obtinut"][-600:]
    e = v.get("eroare")
    if e:
        out["eroare"] = {"tip": e["tip"], "rand": e["rand"], "explicatie": e["explicatie"]}
    if v.get("observatii"):
        out["observatie_stil"] = v["observatii"][0]["text"]
    if hint:
        out["indiciu"] = hint["text"]
    return out


def alt_program(vechi: str, nou: str) -> bool:
    """Codul s-a schimbat radical față de verificarea anterioară (nu e doar o corectură)."""
    if not vechi:
        return False
    cod = lambda s: [ln.strip() for ln in s.split("\n") if ln.strip() and not ln.lstrip().startswith("#")]  # noqa: E731
    return difflib.SequenceMatcher(None, cod(vechi), cod(nou)).ratio() < 0.4


# ---------------------------------------------------------------- balonul din cod

def balon(v: dict, source: str, hint: dict | None) -> dict | None:
    """Tot ce s-a găsit la verificare, ca balon pe rândul cel mai potrivit din cod (None dacă e corect)."""
    if v["rezultat"] == "corect":
        return None
    e = v.get("eroare")
    line = v.get("rand") or (e or {}).get("rand") or _rand_probabil(v, source)
    parts = []
    if e:
        title = e["titlu"]
        parts.append(e["explicatie"])
    else:
        title = "Ce nu merge încă"
    if v.get("test"):
        intrare = ", ".join(f"`{x}`" for x in v.get("intrare", [])) or "niciunul"
        parts.insert(0, f"**Testul „{v['test']}”** (răspunsuri la input: {intrare})")
    if not e:
        parts.append(v.get("detaliu", ""))
    if v.get("motiv") == "iesire":
        parts.append(f"Trebuia `{v['asteptat']}`, a ieșit `{v['obtinut_rand']}`.")
    if v.get("de_ce"):
        parts.append(v["de_ce"])
    if v.get("obtinut") and not e:
        tail = "\n".join(v["obtinut"].split("\n")[-8:])
        parts.append(f"Finalul output-ului tău:\n```\n{tail}\n```")
    if hint:
        parts.append(f"**Indiciu {hint['treapta']}/{hint['din']}:** {hint['text']}")
    # plasa de siguranță: fișierul capitolului e și locul încercărilor elevului (app.js tratează linkul)
    parts.append(f"[{SKIP_LINK_TEXT}](#{SKIP_LINK})")
    return {"line": line, "title": title[:80], "text": "\n\n".join(p for p in parts if p)}


SKIP_LINK = "nu-e-exercitiul"
SKIP_LINK_TEXT = "Nu lucrez la exercițiul lecției, ci la altceva"


def _rand_probabil(v: dict, source: str) -> int:
    """Fără un rând indicat de eroare: ultimul `print` (acolo se vede rezultatul greșit), altfel primul rând de cod."""
    lines = source.split("\n")
    if v.get("etapa") == "test":
        for i in range(len(lines) - 1, -1, -1):
            if "print(" in lines[i]:
                return i + 1
    return next((i + 1 for i, ln in enumerate(lines) if ln.strip() and not ln.lstrip().startswith("#")), 1)


# ---------------------------------------------------------------- mesajul fără AI

def mesaj_simplu(v: dict, indiciu: str | None = None) -> str:
    """Verdictul spus în română de un șablon: rezerva când modelul mic nu e disponibil."""
    if v["rezultat"] == "corect":
        msg = "Bravo! Programul trece toate verificările exercițiului."
        if v.get("observatii"):
            msg += " O observație de stil: " + v["observatii"][0]["text"]
        return msg + " Poți trece la lecția următoare."
    parts = [v.get("detaliu", "")]
    if v.get("test"):
        intrare = ", ".join(f"`{x}`" for x in v.get("intrare", [])) or "nimic"
        parts.insert(0, f"Testul „{v['test']}” (răspunsuri la input: {intrare}):")
    if v.get("motiv") == "iesire":
        parts.append(f"Trebuia `{v['asteptat']}`, a ieșit `{v['obtinut_rand']}`.")
    e = v.get("eroare")
    if e:
        parts.append(f"**{e['titlu']}**" + (f" (rândul {e['rand']})" if e.get("rand") else "") + f": {e['explicatie']}")
    if v.get("de_ce"):
        parts.append(v["de_ce"])
    if indiciu:
        parts.append(f"Indiciu: {indiciu}")
    parts.append("Corectează și apasă din nou **Rulează și verifică**.")
    return " ".join(p for p in parts if p)
