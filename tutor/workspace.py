"""Operații pe fișierele proiectelor elevilor.

Fiecare utilizator are folderul lui: WORKSPACE_ROOT/u<id>/<proiect>/.
"""
import re
import shutil
from pathlib import Path

from django.conf import settings

PROJECT_NAME_RE = re.compile(r"^[A-Za-z0-9_\-]{1,50}$")
HIDDEN = {"__pycache__", ".git", ".venv", "venv", "node_modules", ".mypy_cache", ".pytest_cache"}
MAX_FILE_BYTES = 1_000_000


class WorkspaceError(Exception):
    pass


def user_root(user) -> Path:
    d = settings.WORKSPACE_ROOT / f"u{user.pk}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def project_dir(user, project: str) -> Path:
    if not PROJECT_NAME_RE.match(project or ""):
        raise WorkspaceError("Nume de proiect invalid (doar litere, cifre, _ și -).")
    d = user_root(user) / project
    if not d.is_dir():
        raise WorkspaceError(f"Proiectul „{project}” nu există.")
    return d


def safe_path(user, project: str, rel: str) -> Path:
    """Rezolvă o cale relativă și refuză orice iese din folderul proiectului."""
    base = project_dir(user, project).resolve()
    rel = (rel or "").replace("\\", "/").lstrip("/")
    target = (base / rel).resolve()
    if target != base and not target.is_relative_to(base):
        raise WorkspaceError("Calea iese din proiect.")
    return target


def rel_of(user, project: str, p: Path) -> str:
    return p.resolve().relative_to(project_dir(user, project).resolve()).as_posix()


def list_projects(user) -> list[str]:
    return sorted(p.name for p in user_root(user).iterdir() if p.is_dir() and PROJECT_NAME_RE.match(p.name))


def django_projects(user) -> list[str]:
    """Proiectele elevului care sunt deja proiecte Django (`manage.py` în rădăcină), oricum s-ar numi."""
    return [p for p in list_projects(user) if (user_root(user) / p / "manage.py").is_file()]


STARTER_MAIN = '''# Bine ai venit! Acesta este primul tău fișier Python.
# Rulează-l din terminalul de jos cu:  python main.py

print("Salut, lume!")
'''


def create_project(user, name: str) -> None:
    if not PROJECT_NAME_RE.match(name or ""):
        raise WorkspaceError("Nume de proiect invalid (doar litere, cifre, _ și -).")
    d = user_root(user) / name
    if d.exists():
        raise WorkspaceError("Există deja un proiect cu acest nume.")
    d.mkdir(parents=True)
    (d / "main.py").write_text(STARTER_MAIN, encoding="utf-8")


def tree(user, project: str) -> list[dict]:
    base = project_dir(user, project)

    def walk(d: Path) -> list[dict]:
        items = []
        try:
            entries = sorted(d.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except OSError:
            return items
        for p in entries:
            if p.name in HIDDEN:
                continue
            node = {"name": p.name, "path": p.relative_to(base).as_posix()}
            if p.is_dir():
                node["type"] = "dir"
                node["children"] = walk(p)
            else:
                node["type"] = "file"
            items.append(node)
        return items

    return walk(base)


def flat_listing(user, project: str) -> str:
    """Listare text a proiectului, pentru AI."""
    lines = []

    def walk(nodes, depth):
        for n in nodes:
            lines.append("  " * depth + n["name"] + ("/" if n["type"] == "dir" else ""))
            if n["type"] == "dir":
                walk(n["children"], depth + 1)

    walk(tree(user, project), 0)
    return "\n".join(lines) or "(proiect gol)"


def read_file(user, project: str, rel: str) -> dict:
    p = safe_path(user, project, rel)
    if not p.is_file():
        raise WorkspaceError(f"Fișierul „{rel}” nu există.")
    if p.stat().st_size > MAX_FILE_BYTES:
        return {"path": rel_of(user, project, p), "binary": True, "content": "", "reason": "prea mare"}
    data = p.read_bytes()
    try:
        return {"path": rel_of(user, project, p), "binary": False, "content": data.decode("utf-8")}
    except UnicodeDecodeError:
        return {"path": rel_of(user, project, p), "binary": True, "content": "", "reason": "fișier binar"}


def write_file(user, project: str, rel: str, content: str) -> str:
    p = safe_path(user, project, rel)
    if p == project_dir(user, project).resolve() or p.is_dir():
        raise WorkspaceError("Calea indică un folder.")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8", newline="")
    return rel_of(user, project, p)


def create(user, project: str, rel: str, kind: str) -> str:
    p = safe_path(user, project, rel)
    if p.exists():
        raise WorkspaceError("Există deja.")
    if kind == "dir":
        p.mkdir(parents=True)
    else:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("", encoding="utf-8")
    return rel_of(user, project, p)


def rename(user, project: str, src: str, dst: str) -> str:
    a, b = safe_path(user, project, src), safe_path(user, project, dst)
    if not a.exists():
        raise WorkspaceError("Sursa nu există.")
    if b.exists():
        raise WorkspaceError("Destinația există deja.")
    b.parent.mkdir(parents=True, exist_ok=True)
    a.rename(b)
    return rel_of(user, project, b)


def delete(user, project: str, rel: str) -> None:
    p = safe_path(user, project, rel)
    if p == project_dir(user, project).resolve():
        raise WorkspaceError("Nu pot șterge rădăcina proiectului de aici.")
    if p.is_dir():
        shutil.rmtree(p)
    elif p.exists():
        p.unlink()
    else:
        raise WorkspaceError("Nu există.")
