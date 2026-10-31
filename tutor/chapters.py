"""Un folder de cod pentru fiecare capitol (subiect din curriculum), cu copie în baza de date.

Folderul e `capitole/NN-slug/` în proiectul elevului (NN = numărul subiectului în curriculum), așa că
exercițiile de la „Primul program” nu se amestecă cu cele de la „Liste” sau „Modele Django”.
Fișierele de pe disc sunt cele care rulează; tabelul `TopicCode` ține o copie a fiecăruia.
"""
import keyword
import re
import sys
import textwrap

from . import workspace
from .models import Topic, TopicCode

ROOT = "capitole"
_PATH_RE = re.compile(rf"^{ROOT}/\d+-(?P<slug>[^/]+)/")
MAX_SYNC_BYTES = 200_000
# Exercițiul fix al lecției (tutor/exercitii/) se scrie în fișierul principal al capitolului și e verificat de
# cod până e rezolvat; după aceea (sau dacă elevul spune că lucrează la altceva) îl verifică tutorele.
# Un timp a avut fișierul lui, `exercitiu.py`: `_retire_exercise_file` îl mută în fișierul principal.
LEGACY_EXERCISE_FILE = "exercitiu.py"


def _numbered_topics() -> list[Topic]:
    return list(Topic.objects.select_related("module").order_by("module__order", "order"))


def folder_for(topic: Topic) -> str:
    n = next(i for i, t in enumerate(_numbered_topics(), 1) if t.pk == topic.pk)
    return f"{ROOT}/{n:02d}-{topic.slug}"


def main_name(topic: Topic) -> str:
    """Fișierul principal al capitolului, numit după lecție: `liste.py`, `f_strings.py`.

    Un nume de modul standard (`dataclasses.py`, `http.py`) ar „ascunde” modulul real și ar strica
    importurile chiar în lecția despre el; un cuvânt rezervat (`while.py`) nu poate fi importat.
    În cazurile astea adăugăm `_exercitii`.
    """
    base = topic.slug.replace("-", "_")
    if base in sys.stdlib_module_names or keyword.iskeyword(base) or base in ("django", "test", "tests"):
        base += "_exercitii"
    return f"{base}.py"


def topic_for_path(rel: str) -> Topic | None:
    m = _PATH_RE.match(rel.replace("\\", "/"))
    return Topic.objects.filter(slug=m["slug"]).first() if m else None


def has_folder(topic: Topic) -> bool:
    """Lecțiile Django n-au folder de capitol: construiesc pe rând un singur proiect, `blog` (manage.py în rădăcină)."""
    return not topic.module.slug.startswith("django-")


def ensure(user, project: str, topic: Topic) -> str | None:
    """Creează (sau reface din baza de date) folderul capitolului; întoarce fișierul principal (None la Django)."""
    if not has_folder(topic):
        return None
    folder = folder_for(topic)
    main = f"{folder}/{main_name(topic)}"
    root = workspace.project_dir(user, project)
    _rename_legacy_main(user, project, folder, main)
    if not (root / folder).exists():
        saved = TopicCode.objects.filter(user=user, project=project, topic=topic)
        if saved:
            for c in saved:
                workspace.write_file(user, project, c.path, c.content)
        else:
            workspace.write_file(user, project, main, _header(topic, folder) + _starter(topic))
            sync(user, project, main)
    _retire_exercise_file(user, project, folder, main)
    _refresh_header(user, project, topic, folder, main)
    _add_starter(user, project, topic, main)
    if not (root / main).exists():
        files = sorted(p for p in (root / folder).rglob("*.py"))
        if files:
            return workspace.rel_of(user, project, files[0])
    return main


HEADER_WIDTH = 76
_RULE = "# " + "=" * (HEADER_WIDTH - 2)
_PATH_INTRO_RE = re.compile(
    r"^În (?:fișierul (?:capitolului|exercițiului), )?`capitole/[^`]+`(?:\s*\([^)]*\))?,?\s*(?P<rest>.)", re.S)
_LIST_RE = re.compile(r"^(?P<indent>\s*)(?P<mark>\d+\.|[-*])\s+(?P<text>.*)$")


def _plain(text: str) -> str:
    """Markdown-ul din lecție ca text simplu pentru un comentariu: fără `cod`, **bold** și linkuri."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.replace("`", "")


def _comment_lines(markdown: str) -> list[str]:
    """Secțiunea „Exercițiu” a lecției, ca rânduri de comentariu: paragrafe împărțite la lățime, liste cu
    numerele aliniate, blocurile de cod păstrate exact (indentate)."""
    out: list[str] = []
    in_code = False
    for raw in markdown.split("\n"):
        line = raw.rstrip()
        if line.startswith("```"):
            in_code = not in_code
            if not in_code:
                out.append("#")
            continue
        if in_code:
            out.append(f"#     {line}".rstrip())
            continue
        if not line.strip():
            if out and out[-1] != "#":
                out.append("#")
            continue
        m = _LIST_RE.match(line)
        if m:
            # în Markdown, sub-punctele sunt indentate cât textul punctului-părinte: păstrăm alinierea
            mark = m["mark"] if m["mark"].endswith(".") else "-"
            first = "#   " + " " * len(m["indent"]) + f"{mark} "
            rest = "#   " + " " * len(m["indent"]) + " " * (len(mark) + 1)
            out += textwrap.wrap(_plain(m["text"]), HEADER_WIDTH, initial_indent=first, subsequent_indent=rest)
        else:
            out += textwrap.wrap(_plain(line.strip()), HEADER_WIDTH, initial_indent="# ", subsequent_indent="# ")
    while out and out[-1] == "#":
        out.pop()
    return out


def _header(topic: Topic, folder: str) -> str:
    """Antetul fișierului capitolului: enunțul exercițiului din lecție, ușor de urmărit în editor.

    Lecțiile cu exemplu de început n-au antet: pașii din exemplu spun ce e de făcut, iar enunțul e în lecție."""
    from . import ai, verificare

    n = folder.split("/")[1].split("-")[0]
    ex = verificare.exercitiu(topic.slug)
    if ex and ex.get("inceput"):
        return ""
    section = ai._exercise_section(topic.lesson)
    body = section.split("\n", 1)[1].strip() if section else ""
    if not body:
        return f"# Capitolul {n}: {topic.title}\n# Scrie aici exercițiile pentru acest capitol.\n\n"
    # „În `capitole/03-numere/numere.py`, scrie un calculator...” → „Scrie un calculator...”: suntem chiar în fișier
    body = _PATH_INTRO_RE.sub(lambda m: m["rest"].upper(), body, count=1)
    title = f"Exercițiul: {ex['titlu']}" if ex else "Exercițiul lecției"
    lines = [_RULE, f"# Capitolul {n}: {topic.title}", f"# {title}", _RULE, "#"]
    lines += _comment_lines(body)
    lines += ["#", _RULE]
    if ex:
        lines += textwrap.wrap(
            "Când e gata, apasă „Rulează și verifică”: testele lecției îl verifică pe loc. După ce îl rezolvi, "
            "fișierul e liber pentru alte exerciții.", HEADER_WIDTH, initial_indent="# ", subsequent_indent="# ")
    else:
        lines += textwrap.wrap("Când e gata, apasă „Rulează și verifică”: tutorele îți verifică programul.",
                               HEADER_WIDTH, initial_indent="# ", subsequent_indent="# ")
    lines.append(_RULE)
    return "\n".join(lines) + "\n\n"


# Antetele scrise de aplicație (cele vechi, de 2-3 rânduri, și cel cu enunțul, între 4 rânduri de „=”): le
# refacem din lecție când s-a schimbat ceva, fără să atingem codul elevului de sub ele.
_OLD_HEADER_RE = re.compile(
    r"\A(?:# Capitolul \d+: .*\n)(?:# (?:Scrie aici exercițiile pentru acest capitol\.|Exercițiul lecției: .*|"
    r"„Rulează și verifică” îl verifică automat\..*)\n)*\n?"
)
_HEADER_RE = re.compile(r"\A# ={20,}\n# Capitolul \d+: .*\n(?:(?:#.*)?\n)*?(?:# ={20,}\n(?:(?:#.*)?\n)*?){3}\n?")


def _refresh_header(user, project: str, topic: Topic, folder: str, main: str) -> None:
    path = workspace.project_dir(user, project) / main
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    m = _HEADER_RE.match(text) or _OLD_HEADER_RE.match(text)
    if not m:
        return
    new = _header(topic, folder)
    if m.group(0) == new:
        return
    workspace.write_file(user, project, main, new + text[m.end():].lstrip("\n"))
    sync(user, project, main)


def _starter(topic: Topic) -> str:
    """Exemplul de început de sub enunț (tutor/exercitii/: `inceput`, sau tutor/exercitii/inceput/ la lecțiile
    fără teste): primul pas scris ca model, apoi câte un comentariu „scrii așa: …” la fiecare pas. Elevul vede
    cum se scrie și continuă după model."""
    from . import verificare

    return verificare.inceput(topic.slug).lstrip("\n")


def _add_starter(user, project: str, topic: Topic, main: str) -> None:
    """Fișierele create înainte de exemplele de început: îl adăugăm doar dacă elevul n-a scris încă niciun cod."""
    starter = _starter(topic)
    path = workspace.project_dir(user, project) / main
    if not starter or not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if _code_lines(text):
        return
    workspace.write_file(user, project, main, (text.rstrip("\n") + "\n\n" if text.strip() else "") + starter)
    sync(user, project, main)


def exercise_path(topic: Topic) -> str | None:
    """Fișierul principal al capitolului, dacă lecția are exercițiu fix (acolo se scrie exercițiul)."""
    from . import verificare

    if not has_folder(topic) or not verificare.exercitiu(topic.slug):
        return None
    return f"{folder_for(topic)}/{main_name(topic)}"


def _code_lines(text: str) -> list[str]:
    return [ln for ln in text.split("\n") if ln.strip() and not ln.lstrip().startswith("#")]


def _retire_exercise_file(user, project: str, folder: str, main: str) -> None:
    """Fostul `exercitiu.py`: gol → șters; cu cod, iar fișierul principal fără cod → mutat în el.
    Dacă amândouă au cod, rămâne ca fișier obișnuit al capitolului."""
    old = f"{folder}/{LEGACY_EXERCISE_FILE}"
    root = workspace.project_dir(user, project)
    if not (root / old).is_file():
        return
    content = (root / old).read_text(encoding="utf-8")
    main_text = (root / main).read_text(encoding="utf-8") if (root / main).is_file() else ""
    if _code_lines(content) and _code_lines(main_text):
        return
    if _code_lines(content):
        workspace.write_file(user, project, main, content)
        sync(user, project, main)
    workspace.delete(user, project, old)
    forget(user, project, old)


def _rename_legacy_main(user, project: str, folder: str, main: str) -> None:
    """Capitolele create înainte aveau `main.py`; îl redenumim după lecție (pe disc și în baza de date)."""
    old = f"{folder}/main.py"
    root = workspace.project_dir(user, project)
    if (root / old).is_file() and not (root / main).exists():
        workspace.rename(user, project, old, main)
        TopicCode.objects.filter(user=user, project=project, path=old).update(path=main)
    elif not (root / folder).exists() and not TopicCode.objects.filter(user=user, project=project, path=main).exists():
        # folderul se va reface din baza de date: refacem direct cu numele nou
        TopicCode.objects.filter(user=user, project=project, path=old).update(path=main)


def sync(user, project: str, rel: str) -> None:
    """Salvează în baza de date copia unui fișier dintr-un folder de capitol (sau a unui folder întreg)."""
    rel = rel.replace("\\", "/").strip("/")
    p = workspace.safe_path(user, project, rel)
    files = [p] if p.is_file() else sorted(f for f in p.rglob("*") if f.is_file()) if p.is_dir() else []
    for f in files:
        frel = workspace.rel_of(user, project, f)
        topic = topic_for_path(frel)
        if not topic or f.stat().st_size > MAX_SYNC_BYTES or "__pycache__" in frel:
            continue
        try:
            content = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        TopicCode.objects.update_or_create(
            user=user, project=project, path=frel, defaults={"topic": topic, "content": content}
        )


def forget(user, project: str, rel: str) -> None:
    """Fișierul sau folderul a fost șters / mutat: scoatem și copiile din baza de date."""
    rel = rel.replace("\\", "/").strip("/")
    TopicCode.objects.filter(user=user, project=project, path=rel).delete()
    TopicCode.objects.filter(user=user, project=project, path__startswith=rel + "/").delete()


def paths_by_topic(user, project: str) -> dict[int, str]:
    """topic_id -> fișierul principal al capitolului, pentru capitolele care au cod în proiect."""
    mains = {t.pk: main_name(t) for t in Topic.objects.all()}
    out: dict[int, str] = {}
    for topic_id, path in TopicCode.objects.filter(user=user, project=project).values_list("topic_id", "path"):
        if topic_id not in out or path.endswith("/" + mains.get(topic_id, "")):
            out[topic_id] = path
    return out
