"""Un folder de cod pentru fiecare capitol (subiect din curriculum), cu copie în baza de date.

Folderul e `capitole/NN-slug/` în proiectul elevului (NN = numărul subiectului în curriculum), așa că
exercițiile de la „Primul program” nu se amestecă cu cele de la „Liste” sau „Modele Django”.
Fișierele de pe disc sunt cele care rulează; tabelul `TopicCode` ține o copie a fiecăruia.
"""
import keyword
import re
import sys

from . import workspace
from .models import Topic, TopicCode

ROOT = "capitole"
_PATH_RE = re.compile(rf"^{ROOT}/\d+-(?P<slug>[^/]+)/")
MAX_SYNC_BYTES = 200_000


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
            header = (
                f"# Capitolul {folder.split('/')[1].split('-')[0]}: {topic.title}\n"
                f"# Scrie aici exercițiile pentru acest capitol.\n\n"
            )
            workspace.write_file(user, project, main, header)
            sync(user, project, main)
    if not (root / main).exists():
        files = sorted(p for p in (root / folder).rglob("*.py"))
        if files:
            return workspace.rel_of(user, project, files[0])
    return main


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
