"""Rulează codul dintr-o lecție (tutor/lessons/NN-slug.md) în containerul sandbox și compară output-ul.

Convențiile din Markdown:
- un bloc ```python urmat de un bloc ```text e un program complet: se rulează și output-ul trebuie să fie
  exact cel din blocul text (între ele pot fi doar rânduri goale sau un rând care se termină cu „:”);
- dacă blocul text conține un traceback, ultimul rând (tipul și mesajul erorii) trebuie să fie identic, iar
  celelalte rânduri trebuie să apară în aceeași ordine în output-ul real (rândurile cu ^^^ se pot omite);
- un bloc ```python fără bloc text după el e un fragment: se verifică doar sintaxa;
- comentarii HTML înaintea blocului (elevul nu le vede):
    <!-- stdin: Ana\\n25 -->   ce primește input(); textul tastat apare în output, ca în terminal
    <!-- fisier: salut.py -->  numele fișierului (implicit program.py); fișierele rămân pentru blocurile următoare
    <!-- nu-rula -->           blocul e sărit cu totul
    <!-- ruleaza -->           înaintea unui bloc ```bash urmat de ```text: comenzile rulează în același folder
                               (pytest, git...), iar output-ul se compară după ce duratele („in 0.03s”) și
                               hash-urile de commit sunt înlocuite peste tot cu valori fixe
    <!-- comanda: CMD -->      înaintea unui bloc ```text: CMD rulează ascuns, iar output-ul trebuie să fie textul
                               din bloc (ex. `python /h/vezi_pagina.py /articol/1/`: ce vede browserul)

Fișiere și proiecte (lecțiile Django):
- `<!-- fisier: cale -->` funcționează pe orice bloc fără output (python, html, css...): conținutul e scris la
  calea dată (cu subfoldere), relativ la folderul lecției;
- `<!-- proiect: _blog/49 -->` oriunde în lecție: folderul lecției pornește cu o copie a acelui proiect
  (relativ la tutor/lessons/);
- `<!-- pregatire: CMD -->` (oricâte): rulează ascuns, după copierea proiectului și înaintea blocurilor; trebuie
  să nu afișeze nimic. `tutor/lessons/` e montat la /lectii, deci datele de test se încarcă așa:
  `<!-- pregatire: python manage.py migrate -v 0 && python manage.py loaddata /lectii/_blog/date/50.json -v 0 -->`;
- `<!-- proiect-final: _blog/50 -->`: la final, fișierele din folderul lecției trebuie să fie identice cu cele
  din acel proiect (fără db.sqlite3, __pycache__ și fișierele generate), ca lecția să arate tot ce se schimbă.

Folosire: python tools/verifica_lectie.py tutor/lessons/04-stringuri.md [alte fișiere...]
"""
import filecmp
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tutor.iesire import HOOK, compare  # noqa: E402 — comune cu verificarea exercițiilor

IMAGE = "pytutor-sandbox:2"
TIMEOUT = 60
# Pentru git în blocurile ```bash: autorul commit-urilor din lecții.
GIT_ENV = {
    "GIT_AUTHOR_NAME": "Ana Popescu", "GIT_AUTHOR_EMAIL": "ana@exemplu.ro",
    "GIT_COMMITTER_NAME": "Ana Popescu", "GIT_COMMITTER_EMAIL": "ana@exemplu.ro",
}
_DURATION_RE = re.compile(r"\b\d+\.\d+s\b")
_HASH_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
LESSONS = Path(__file__).resolve().parents[1] / "tutor" / "lessons"
VEZI = Path(__file__).resolve().parent / "vezi_pagina.py"
_PROJECT_RE = re.compile(r"<!--\s*proiect:\s*(\S+)\s*-->")
_FINAL_RE = re.compile(r"<!--\s*proiect-final:\s*(\S+)\s*-->")
_SETUP_RE = re.compile(r"<!--\s*pregatire:\s*(.+?)\s*-->")
# generate la rulare, nu fac parte din proiectul pe care îl scrie elevul
IGNORE = shutil.ignore_patterns("__pycache__", "db.sqlite3", ".pytest_cache", ".mypy_cache",
                                ".ruff_cache", "staticfiles", "*.pyc")

_FENCE_RE = re.compile(r"^```(\w*)\s*$")
_DIRECTIVE_RE = re.compile(r"^<!--\s*([\w-]+)\s*:?\s*(.*?)\s*-->$")


@dataclass
class Block:
    lang: str
    code: str
    line: int
    directives: dict = field(default_factory=dict)
    output: "Block | None" = None


def parse(text: str) -> list[Block]:
    lines = text.splitlines()
    blocks: list[Block] = []
    directives: dict = {}
    between: list[str] = []  # textul dintre blocul anterior și cel curent
    i = 0
    while i < len(lines):
        m = _FENCE_RE.match(lines[i])
        d = _DIRECTIVE_RE.match(lines[i].strip())
        if d:
            directives[d[1]] = d[2]
        elif m and m[1]:
            start, body = i + 1, []
            i += 1
            while i < len(lines) and lines[i].rstrip() != "```":
                body.append(lines[i])
                i += 1
            block = Block(m[1], "\n".join(body) + "\n", start, directives)
            prev = blocks[-1] if blocks else None
            gap = [s for s in between if s.strip()]
            if (block.lang == "text" and "comanda" not in block.directives
                    and prev and prev.lang in ("python", "bash") and prev.output is None
                    and (not gap or (len(gap) == 1 and gap[0].rstrip().endswith(":")))):
                prev.output = block
            else:
                blocks.append(block)
            directives, between = {}, []
        else:
            between.append(lines[i])
        i += 1
    return blocks


def write(workdir: Path, name: str, code: str) -> None:
    target = workdir / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(code, encoding="utf-8", newline="\n")


def hook_dir() -> Path:
    """Fișierele ajutătoare ale verificării, montate la /h — în afara folderului lecției, ca git să nu le vadă."""
    global _HOOK_DIR
    if _HOOK_DIR is None:
        _HOOK_DIR = Path(tempfile.mkdtemp(prefix="lectie-hook-"))
        (_HOOK_DIR / "sitecustomize.py").write_text(HOOK, encoding="utf-8")
        shutil.copy(VEZI, _HOOK_DIR / "vezi_pagina.py")
    return _HOOK_DIR


_HOOK_DIR: Path | None = None


def run(workdir: Path, name: str, code: str, stdin: str) -> str:
    write(workdir, name, code)
    args = [
        "docker", "run", "--rm", "-i", "--network", "none",
        "-v", f"{workdir}:/w", "-v", f"{hook_dir()}:/h:ro", "-w", "/w", "-e", "PYTHONPATH=/h",
        IMAGE, "sh", "-c", f"python {name} 2>&1",
    ]
    # bytes, nu text: pe Windows modul text ar transforma \n în \r\n
    res = subprocess.run(args, input=stdin.encode(), capture_output=True, timeout=TIMEOUT)
    if res.stderr.strip():
        raise RuntimeError(res.stderr.decode("utf-8", "replace").strip())
    return res.stdout.decode("utf-8").replace("\r\n", "\n").replace("/w/", "")


def run_shell(workdir: Path, code: str) -> str:
    env = [x for k, v in GIT_ENV.items() for x in ("-e", f"{k}={v}")]
    args = ["docker", "run", "--rm", "-i", "--network", "none", "-v", f"{workdir}:/w", "-v", f"{hook_dir()}:/h:ro",
            "-v", f"{LESSONS}:/lectii:ro", "-w", "/w", *env, IMAGE, "sh", "-c", f"{{\n{code}\n}} 2>&1"]
    res = subprocess.run(args, capture_output=True, timeout=TIMEOUT)
    if res.stderr.strip():
        raise RuntimeError(res.stderr.decode("utf-8", "replace").strip())
    return res.stdout.decode("utf-8").replace("\r\n", "\n").replace("/w/", "")


def normalize(text: str) -> str:
    return _HASH_RE.sub("<hash>", _DURATION_RE.sub("0.00s", text))


def project_diff(workdir: Path, expected: Path) -> list[str]:
    """Diferențele dintre fișierele lecției și proiectul așteptat (fără fișierele generate)."""
    with tempfile.TemporaryDirectory(prefix="lectie-final-") as tmp:
        got, expected = Path(tmp) / "p", shutil.copytree(expected, Path(tmp) / "e", ignore=IGNORE)
        shutil.copytree(workdir, got, ignore=IGNORE)
        files = lambda root: {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        have, want = files(got), files(expected)
        out = [f"lipsește din lecție: {f}" for f in sorted(want - have)]
        out += [f"în plus față de proiect: {f}" for f in sorted(have - want)]
        out += [f"diferit: {f}" for f in sorted(have & want) if not same_file(got / f, expected / f)]
        return out


# Generate de Django diferit la fiecare rulare: data din antetul migrărilor, cheia aleatoare din startproject.
_VOLATILE = [
    (re.compile(r"^# Generated by Django [\d.]+ on .*$", re.M), "# Generated by Django"),
    (re.compile(r"""^SECRET_KEY = ['"]django-insecure-.*['"]$""", re.M), "SECRET_KEY = 'django-insecure-...'"),
]


def same_file(a: Path, b: Path) -> bool:
    if filecmp.cmp(a, b, shallow=False):
        return True
    try:
        ta, tb = a.read_text(encoding="utf-8"), b.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    for pattern, repl in _VOLATILE:
        ta, tb = pattern.sub(repl, ta), pattern.sub(repl, tb)
    return ta == tb


def check_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    blocks = parse(text)
    errors = ran = compiled = 0
    with tempfile.TemporaryDirectory(prefix="lectie-") as tmp:
        workdir = Path(tmp)
        start = _PROJECT_RE.search(text)
        if start:
            shutil.copytree(LESSONS / start[1], workdir, dirs_exist_ok=True, ignore=IGNORE)
        for cmd in _SETUP_RE.findall(text):
            out = run_shell(workdir, cmd).strip()
            if out:  # pregătirea trebuie să fie tăcută (ex. migrate -v 0, loaddata -v 0)
                errors += 1
                print(f"✗ {path.name}: pregătirea „{cmd}” a afișat:\n{out}")
        for b in blocks:
            where = f"{path.name}:{b.line}"
            if b.lang == "text" and "comanda" in b.directives:
                try:
                    actual = run_shell(workdir, b.directives["comanda"])
                except (RuntimeError, subprocess.TimeoutExpired) as e:
                    errors += 1
                    print(f"✗ {where}: nu s-a putut rula: {e}")
                    continue
                ran += 1
                if not compare(normalize(b.code), normalize(actual)):
                    errors += 1
                    print(f"✗ {where}: output diferit\n--- în lecție:\n{b.code}--- real:\n{actual}")
                continue
            if b.lang == "bash" and "ruleaza" in b.directives and b.output is not None:
                try:
                    actual = run_shell(workdir, b.code)
                except (RuntimeError, subprocess.TimeoutExpired) as e:
                    errors += 1
                    print(f"✗ {where}: nu s-a putut rula: {e}")
                    continue
                ran += 1
                if not compare(normalize(b.output.code), normalize(actual)):
                    errors += 1
                    print(f"✗ {where}: output diferit\n--- în lecție:\n{b.output.code}--- real:\n{actual}")
                continue
            if "nu-rula" in b.directives:
                continue
            if b.lang != "python":
                if "fisier" in b.directives and b.output is None and b.lang not in ("text", "bash"):
                    write(workdir, b.directives["fisier"], b.code)
                continue
            name = b.directives.get("fisier", "program.py")
            if b.output is None:
                if "fisier" in b.directives:
                    write(workdir, name, b.code)
                try:
                    compile(b.code, name, "exec")
                    compiled += 1
                except SyntaxError as e:
                    errors += 1
                    print(f"✗ {where}: fragment cu SyntaxError ({e.msg}, rândul {e.lineno})")
                continue
            stdin = b.directives.get("stdin", "").replace("\\n", "\n")
            if stdin and not stdin.endswith("\n"):
                stdin += "\n"
            try:
                actual = run(workdir, name, b.code, stdin)
            except (RuntimeError, subprocess.TimeoutExpired) as e:
                errors += 1
                print(f"✗ {where}: nu s-a putut rula: {e}")
                continue
            ran += 1
            if not compare(b.output.code, actual):
                errors += 1
                print(f"✗ {where}: output diferit\n--- în lecție:\n{b.output.code}--- real:\n{actual}")
        final = _FINAL_RE.search(text)
        if final:
            for problem in project_diff(workdir, LESSONS / final[1]):
                errors += 1
                print(f"✗ {path.name}: proiectul final ({final[1]}): {problem}")
    status = "OK" if not errors else f"{errors} probleme"
    print(f"{path.name}: {ran} programe rulate, {compiled} fragmente compilate — {status}")
    return errors


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    return 1 if sum(check_file(Path(p)) for p in sys.argv[1:]) else 0


if __name__ == "__main__":
    sys.exit(main())
