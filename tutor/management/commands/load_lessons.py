import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from tutor.models import LESSON_MANUAL, Topic

LESSONS_DIR = Path(__file__).resolve().parents[2] / "lessons"
SECTIONS = [
    "Ce este",
    "De ce contează",
    "Cum funcționează",
    "Exemplu complet",
    "Greșeli frecvente",
    "Exercițiu",
    "Pe scurt",
]
_NAME_RE = re.compile(r"^(?P<n>\d{2})-(?P<slug>[a-z0-9-]+)\.md$")
_FENCE_RE = re.compile(r"^(```|~~~)")
_LEADING_COMMENTS_RE = re.compile(r"\A(\s*<!--.*?-->)+\s*", re.S)


def headings(text: str) -> list[str]:
    """Titlurile de nivel 2 din Markdown, fără cele din blocurile de cod."""
    out, in_code = [], False
    for line in text.splitlines():
        if _FENCE_RE.match(line):
            in_code = not in_code
        elif not in_code and line.startswith("## "):
            out.append(line[3:].strip())
    return out


def check(path: Path, numbers: dict[str, int]) -> list[str]:
    """Problemele unui fișier de lecție (listă goală = e în regulă)."""
    m = _NAME_RE.match(path.name)
    if not m:
        return ["numele trebuie să fie NN-slug.md"]
    slug, n = m["slug"], int(m["n"])
    if slug not in numbers:
        return [f"nu există subiectul „{slug}” în curriculum"]
    errors = []
    if numbers[slug] != n:
        errors.append(f"„{slug}” e lecția {numbers[slug]:02d} în curriculum, nu {n:02d}")
    text = path.read_text(encoding="utf-8")
    # comentariile HTML de la început (directivele pentru tools/verifica_lectie.py) nu se văd la elev
    if not _LEADING_COMMENTS_RE.sub("", text).startswith("## Ce este"):
        errors.append("trebuie să înceapă direct cu „## Ce este”")
    found = headings(text)
    if found != SECTIONS:
        errors.append(f"secțiunile sunt {found}, trebuie {SECTIONS}")
    return errors


class Command(BaseCommand):
    help = "Încarcă lecțiile din tutor/lessons/NN-slug.md în baza de date (AI-ul nu le mai suprascrie)."

    def add_arguments(self, parser):
        parser.add_argument("--check", action="store_true", help="doar verifică fișierele, nu scrie nimic")
        parser.add_argument("--only", help="o singură lecție: numărul (ex. 04) sau slug-ul")

    def handle(self, *args, **options):
        check_only, only = options["check"], options["only"]
        topics = list(Topic.objects.select_related("module").order_by("module__order", "order"))
        numbers = {t.slug: i for i, t in enumerate(topics, 1)}
        by_slug = {t.slug: t for t in topics}

        files = sorted(p for p in LESSONS_DIR.glob("*.md") if not p.name.startswith("_")) if LESSONS_DIR.is_dir() else []
        if only:
            if only.isdigit():
                files = [p for p in files if p.name.startswith(f"{int(only):02d}-")]
            else:
                files = [p for p in files if p.name[3:] == f"{only}.md"]
            if not files:
                raise CommandError(f"Nu găsesc lecția „{only}” în {LESSONS_DIR}.")

        loaded = unchanged = 0
        failed = []
        with_file = set()
        for path in files:
            errors = check(path, numbers)
            if errors:
                failed.append(path.name)
                for e in errors:
                    self.stderr.write(f"{path.name}: {e}")
                continue
            topic = by_slug[_NAME_RE.match(path.name)["slug"]]
            with_file.add(topic.slug)
            text = path.read_text(encoding="utf-8").strip()
            if topic.lesson == text and topic.lesson_model == LESSON_MANUAL:
                unchanged += 1
                continue
            loaded += 1
            if not check_only:
                topic.lesson, topic.lesson_model, topic.lesson_updated_at = text, LESSON_MANUAL, timezone.now()
                topic.save(update_fields=["lesson", "lesson_model", "lesson_updated_at"])

        if not only:
            for t in topics:
                if t.lesson_model == LESSON_MANUAL and t.slug not in with_file:
                    self.stderr.write(f"Atenție: „{t.slug}” e lecție manuală, dar nu mai are fișier (rămâne cum e).")

        verb = "de încărcat" if check_only else "încărcate"
        summary = f"{loaded} {verb}, {unchanged} neschimbate, {len(failed)} cu erori."
        if not only:
            summary += f" {len(topics) - len(with_file)} subiecte fără fișier."
        if failed:
            raise CommandError(summary)
        self.stdout.write(self.style.SUCCESS(summary))
