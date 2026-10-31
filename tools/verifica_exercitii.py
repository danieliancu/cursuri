"""Verifică exercițiile fixe (tutor/exercitii/NN-slug.toml): testele trebuie să fie corecte.

Pentru fiecare exercițiu:
- soluția de referință (`solutie`) trece toate verificările;
- fișierul gol de la începutul capitolului NU trece;
- exemplul de început (`inceput`, pus sub enunț în fișierul capitolului) e Python valid și NU trece singur;
- fiecare verificare de structură și fiecare indiciu există (3 indicii, în trepte).

Programele rulează local (cu interpretorul curent), cu ecoul lui input() din lecții.
Folosire: python tools/verifica_exercitii.py [01 08 ...]
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tutor import iesire, verificare  # noqa: E402

GOL = "# Capitolul NN: ...\n# Scrie aici exercițiile pentru acest capitol.\n\n"


def runner(workdir: Path, name: str, source: str):
    (workdir / name).write_text(source, encoding="utf-8")
    hook = workdir / "_hook"
    hook.mkdir(exist_ok=True)
    (hook / "sitecustomize.py").write_text(iesire.HOOK, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(hook), "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

    def run(stdin: str):
        try:
            res = subprocess.run([sys.executable, name], cwd=workdir, input=stdin.encode(), capture_output=True,
                                 env=env, timeout=10)
        except subprocess.TimeoutExpired:
            return None, ""
        return res.returncode, (res.stdout + res.stderr).decode("utf-8", "replace")

    return run


def check(ex: dict) -> list[str]:
    problems = []
    name = ex.get("fisier", "program.py")
    if len(ex.get("indicii", [])) != 3:
        problems.append("trebuie exact 3 indicii")
    if not ex.get("test"):
        problems.append("niciun test")
    for what in ex.get("structura", []) + ex.get("interzis", []):
        try:
            verificare._has(verificare.ast.parse("x = 1"), "x = 1", what)
        except ValueError as e:
            problems.append(str(e))
    with tempfile.TemporaryDirectory(prefix="exercitiu-") as tmp:
        sol = ex.get("solutie", "")
        v = verificare.verifica_cod(sol, ex, runner(Path(tmp), name, sol), name)
        if v["rezultat"] != "corect":
            problems.append(f"soluția de referință nu trece: {verificare.mesaj_simplu(v)}\n--- output:\n{v.get('obtinut', '')}")
        elif v["observatii"]:
            problems.append(f"soluția are observații pyflakes: {v['observatii']}")
        v = verificare.verifica_cod(GOL, ex, runner(Path(tmp), name, GOL), name)
        if v["rezultat"] == "corect":
            problems.append("un fișier gol trece verificarea")
        start = ex.get("inceput", "")
        if not start.strip():
            problems.append("lipsește exemplul de început (`inceput`)")
        else:
            try:
                compile(start, name, "exec")
            except SyntaxError as e:
                problems.append(f"exemplul de început nu e Python valid: {e.msg} (rândul {e.lineno})")
            grave = [o for o in verificare.observatii(start, name) if o["grav"]]
            if grave:
                problems.append(f"exemplul de început folosește nume nedefinite: {grave[0]['text']}")
            v = verificare.verifica_cod(start, ex, runner(Path(tmp), name, start), name)
            if v["rezultat"] == "corect":
                problems.append("exemplul de început trece singur verificarea (dă soluția)")
    return problems


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    only = set(sys.argv[1:])
    errors = 0
    for ex in verificare.toate():
        if only and f"{ex['numar']:02d}" not in only and ex["slug"] not in only:
            continue
        problems = check(ex)
        errors += len(problems)
        print(f"{ex['sursa']}: {len(ex['test'])} teste — " + ("OK" if not problems else f"{len(problems)} probleme"))
        for p in problems:
            print(f"  ✗ {p}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
