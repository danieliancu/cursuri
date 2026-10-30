import tempfile
from datetime import timedelta
from io import StringIO
from pathlib import Path
from unittest import mock

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.management import CommandError, call_command
from django.template import Context, Template
from django.test import RequestFactory, TestCase
from django.utils import timezone

from . import ai, chapters, workspace
from .admin import TopicAdmin
from .management.commands import load_lessons
from .models import LESSON_MANUAL, STATUS_DOING, STATUS_DONE, Topic, TopicProgress

VALID = "\n\n".join(f"## {s}\n\nText." for s in load_lessons.SECTIONS) + "\n"


class LoadLessonsTests(TestCase):
    """Curriculumul e pus în baza de test de migrarea 0006; `primul-program` e lecția 01."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        patcher = mock.patch.object(load_lessons, "LESSONS_DIR", self.dir)
        patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, name: str, text: str = VALID) -> None:
        (self.dir / name).write_text(text, encoding="utf-8")

    def load(self, *args) -> None:
        call_command("load_lessons", *args, stdout=StringIO(), stderr=StringIO())

    def test_loads_lesson_as_manual(self):
        self.write("01-primul-program.md")
        self.load()
        t = Topic.objects.get(slug="primul-program")
        self.assertEqual(t.lesson, VALID.strip())
        self.assertEqual(t.lesson_model, LESSON_MANUAL)
        self.assertIsNotNone(t.lesson_updated_at)

    def test_unchanged_lesson_keeps_date(self):
        self.write("01-primul-program.md")
        self.load()
        first = Topic.objects.get(slug="primul-program").lesson_updated_at
        self.load()
        self.assertEqual(Topic.objects.get(slug="primul-program").lesson_updated_at, first)

    def test_check_does_not_write(self):
        self.write("01-primul-program.md")
        self.load("--check")
        self.assertEqual(Topic.objects.get(slug="primul-program").lesson_model, "")

    def test_rejects_wrong_number(self):
        self.write("02-primul-program.md")
        with self.assertRaises(CommandError):
            self.load()

    def test_rejects_unknown_slug(self):
        self.write("01-nu-exista.md")
        with self.assertRaises(CommandError):
            self.load()

    def test_rejects_missing_section(self):
        self.write("01-primul-program.md", VALID.replace("## Pe scurt", "## Rezumat"))
        with self.assertRaises(CommandError):
            self.load()

    def test_leading_directives_are_allowed(self):
        self.write("01-primul-program.md", "<!-- proiect: _blog/44 -->\n<!-- pregatire: x -->\n" + VALID)
        self.load()
        self.assertEqual(Topic.objects.get(slug="primul-program").lesson_model, LESSON_MANUAL)

    def test_headings_inside_code_are_ignored(self):
        self.write("01-primul-program.md", VALID.replace("Text.", "```python\n## nu e titlu\n```", 1))
        self.load()
        self.assertEqual(Topic.objects.get(slug="primul-program").lesson_model, LESSON_MANUAL)

    def test_only(self):
        self.write("01-primul-program.md")
        self.write("02-variabile.md")
        self.load("--only", "variabile")
        self.assertEqual(Topic.objects.get(slug="primul-program").lesson_model, "")
        self.assertEqual(Topic.objects.get(slug="variabile").lesson_model, LESSON_MANUAL)


class ClearLessonActionTests(TestCase):
    def test_manual_lessons_are_kept(self):
        Topic.objects.filter(slug="primul-program").update(lesson="manuală", lesson_model=LESSON_MANUAL)
        Topic.objects.filter(slug="variabile").update(lesson="de la AI", lesson_model="gpt-4.1")
        admin = TopicAdmin(Topic, AdminSite())
        request = RequestFactory().post("/")
        request.user = User.objects.create_superuser("admin", "", "x")
        with mock.patch.object(admin, "message_user"):
            admin.clear_lesson(request, Topic.objects.filter(slug__in=["primul-program", "variabile"]))
        self.assertEqual(Topic.objects.get(slug="primul-program").lesson, "manuală")
        self.assertEqual(Topic.objects.get(slug="variabile").lesson, "")


class WorkspaceTestCase(TestCase):
    """Folderul proiectelor elevilor e mutat într-un folder temporar, ca testele să nu atingă `workspaces/`."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        override = self.settings(WORKSPACE_ROOT=Path(tmp.name))
        override.enable()
        self.addCleanup(override.disable)
        self.user = User.objects.create_user("elev", "", "x")
        workspace.create_project(self.user, "proiect")
        self.root = workspace.project_dir(self.user, "proiect")


class ChapterFolderTests(WorkspaceTestCase):
    def test_python_topic_gets_chapter_folder(self):
        main = chapters.ensure(self.user, "proiect", Topic.objects.get(slug="liste"))
        self.assertTrue(main.startswith("capitole/") and main.endswith("/liste.py"))
        self.assertTrue((self.root / main).is_file())

    def test_django_topic_has_no_chapter_folder(self):
        """Lecțiile Django se fac în proiectul Django al elevului, nu în `capitole/`."""
        self.assertIsNone(chapters.ensure(self.user, "proiect", Topic.objects.get(slug="django-proiect")))
        self.assertFalse((self.root / "capitole").exists())

    def test_starting_django_topic_sends_no_chapter_event(self):
        events = []
        result, is_error = ai._record_progress(
            self.user, "proiect", {"topic": "django-proiect", "status": STATUS_DOING, "comment": "Am început."}, events)
        self.assertFalse(is_error)
        self.assertNotIn("chapter", [e["type"] for e in events])
        self.assertIn("n-are încă un proiect Django", result)
        self.assertFalse((self.root / "capitole").exists())


class DjangoProjectsTests(WorkspaceTestCase):
    def test_project_with_manage_py_is_django_whatever_its_name(self):
        workspace.create_project(self.user, "site-ul-meu")
        workspace.write_file(self.user, "site-ul-meu", "manage.py", "")
        self.assertEqual(workspace.django_projects(self.user), ["site-ul-meu"])
        self.assertIn("`site-ul-meu`", ai._django_projects_note(self.user, "proiect"))
        self.assertIn("Proiectul curent", ai._django_projects_note(self.user, "site-ul-meu"))


class NextActiveTopicTests(WorkspaceTestCase):
    """După „învățat”, tutorele află la ce subiect trec sumarul și editorul (aceeași regulă ca în app.js)."""

    def learn(self, slug):
        result, _ = ai._record_progress(self.user, "proiect", {"topic": slug, "status": STATUS_DONE, "comment": "Bine."}, [])
        return result

    def test_first_unlearned_topic_when_nothing_in_progress(self):
        self.assertIn("`variabile`", self.learn("primul-program"))

    def test_latest_topic_in_progress_wins(self):
        now = timezone.now()
        for minutes, slug in ((10, "if-else"), (1, "liste")):
            TopicProgress.objects.create(user=self.user, topic=Topic.objects.get(slug=slug), status=STATUS_DOING)
            # update() ocolește auto_now: fără ore diferite, ordinea dintre cele două ar fi la întâmplare
            TopicProgress.objects.filter(topic__slug=slug).update(updated_at=now - timedelta(minutes=minutes))
        self.assertIn("`liste`", self.learn("primul-program"))

    def test_whole_curriculum_learned(self):
        for t in Topic.objects.exclude(slug="primul-program"):
            TopicProgress.objects.create(user=self.user, topic=t, status=STATUS_DONE)
        self.assertIn("terminat tot curriculumul", self.learn("primul-program"))


class IconTagTests(TestCase):
    def test_icon_refers_to_sprite_in_page(self):
        """`<use href="#nume">` local: merge și când fișierele statice vin de pe alt domeniu."""
        html = Template('{% load pytutor %}{% icon_sprite %}{% icon "play" "fill" %}').render(Context())
        self.assertIn('<symbol id="play"', html)
        self.assertIn('class="icon-sprite"', html)
        self.assertIn('<svg class="i fill" aria-hidden="true"><use href="#play"/></svg>', html)
