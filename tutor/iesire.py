"""Compararea output-ului unui program cu cel așteptat — comun verificării lecțiilor și a exercițiilor.

Nu depinde de Django, ca să poată fi importat și din `tools/verifica_lectie.py`.
"""

# input() afișează și textul „tastat”, ca output-ul să arate ca în terminal.
HOOK = '''import builtins, sys
def _input(prompt=""):
    print(prompt, end="", flush=True)
    line = sys.stdin.readline()
    if not line:
        raise EOFError("EOF when reading a line")
    line = line.rstrip("\\n")
    print(line, flush=True)
    return line
builtins.input = _input
'''


def compare(expected: str, actual: str) -> bool:
    """Output identic rând cu rând (fără spațiile de la final); la traceback, doar rândurile esențiale."""
    exp, act = expected.rstrip("\n").splitlines(), actual.rstrip("\n").splitlines()
    if not any(s.startswith("Traceback") for s in exp):
        return [s.rstrip() for s in exp] == [s.rstrip() for s in act]
    if not exp or not act or exp[-1].rstrip() != act[-1].rstrip():
        return False
    it = iter(s.rstrip() for s in act)
    return all(any(s.rstrip() == a for a in it) for s in exp)


def first_difference(expected: str, actual: str) -> tuple[int, str, str] | None:
    """Primul rând (numerotat de la 1) la care output-ul diferă: (rând, așteptat, obținut)."""
    exp, act = expected.rstrip("\n").splitlines(), actual.rstrip("\n").splitlines()
    for i in range(max(len(exp), len(act))):
        e = exp[i].rstrip() if i < len(exp) else None
        a = act[i].rstrip() if i < len(act) else None
        if e != a:
            return i + 1, e if e is not None else "(nimic)", a if a is not None else "(nimic)"
    return None
