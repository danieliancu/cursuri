import os
import subprocess
import sys
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

from . import ai, chapters, erori, iesire, runner, verificare, workspace
from .admin import TopicAdmin
from .management.commands import load_lessons
from .models import LESSON_MANUAL, STATUS_DOING, STATUS_DONE, STATUS_TODO, CodeAnnotation, Topic, TopicProgress

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
    """Folderul proiectelor elevilor e mutat într-un folder temporar, ca testele să nu atingă `workspaces/`.

    Codul rulează local, nu în Docker: altfel testele ar folosi containerul unui elev real (`pytutor-u<id>`).
    """

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        override = self.settings(WORKSPACE_ROOT=Path(tmp.name), PYTUTOR_SANDBOX="local")
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


TRACEBACK_NAME = """Traceback (most recent call last):
  File "/work/proiect/capitole/01-primul-program/primul_program.py", line 3, in <module>
    Print("x")
    ^^^^^
NameError: name 'Print' is not defined. Did you mean: 'print'?
"""


class ErrorExplainTests(TestCase):
    """Erorile frecvente sunt explicate în română, fără AI, cu trimitere la lecție."""

    def test_name_error_with_suggestion(self):
        e = erori.explica("salut\n" + TRACEBACK_NAME)
        self.assertEqual((e["tip"], e["rand"], e["sugestie"]), ("NameError", 3, "print"))
        self.assertIn("`print`", e["explicatie"])
        self.assertEqual((e["lectie"]["slug"], e["lectie"]["numar"]), ("variabile", 2))

    def test_common_messages(self):
        cases = {
            'TypeError: can only concatenate str (not "int") to str': "Text adunat cu un număr",
            "ValueError: invalid literal for int() with base 10: 'abc'": "Textul nu e număr",
            "ZeroDivisionError: division by zero": "Împărțire la zero",
            "IndexError: list index out of range": "Index în afara listei",
            "KeyError: 'nume'": "Cheie inexistentă",
            "ModuleNotFoundError: No module named 'numpyy'": "Modulul nu e găsit",
        }
        for last, title in cases.items():
            e = erori.explica(f'Traceback (most recent call last):\n  File "p.py", line 1, in <module>\n    x\n{last}\n')
            self.assertEqual(e["titlu"], title, last)

    def test_syntax_error_line(self):
        e = erori.explica("  File \"p.py\", line 2\n    if x == 1\n             ^\nSyntaxError: expected ':'\n")
        self.assertEqual((e["titlu"], e["rand"]), ("Lipsesc cele două puncte", 2))

    def test_library_frames_are_skipped(self):
        out = ('Traceback (most recent call last):\n  File "/w/p.py", line 4, in <module>\n    json.loads("x")\n'
               '  File "/usr/local/lib/python3.12/json/__init__.py", line 346, in loads\n    return x\n'
               "json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n")
        self.assertIsNone(erori.explica(out))  # necunoscută: rămâne la tutorele AI
        self.assertEqual(erori._parse(out)["rand"], 4)

    def test_no_error(self):
        self.assertIsNone(erori.explica("Salut, lume!\n"))


def local_run(source):
    """Rulează `source` local, cu ecoul lui input() din lecții (ca verificarea din aplicație)."""
    tmp = tempfile.TemporaryDirectory()
    d = Path(tmp.name)
    (d / "p.py").write_text(source, encoding="utf-8")
    (d / "sitecustomize.py").write_text(iesire.HOOK, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(d), "PYTHONIOENCODING": "utf-8"}

    def run(stdin):
        res = subprocess.run([sys.executable, "p.py"], cwd=d, input=stdin.encode(), capture_output=True,
                             timeout=10, env=env)
        return res.returncode, (res.stdout + res.stderr).decode("utf-8")

    return run, tmp


class ExerciseCheckTests(TestCase):
    """Verdictul exercițiilor fixe îl dă codul: teste, structură, sintaxă."""

    def check(self, slug, source):
        run, tmp = local_run(source)
        self.addCleanup(tmp.cleanup)
        return verificare.verifica_cod(source, verificare.exercitiu(slug), run, "p.py")

    def test_reference_solutions_pass(self):
        for ex in verificare.toate():
            with self.subTest(ex["slug"]):
                self.assertEqual(self.check(ex["slug"], ex["solutie"])["rezultat"], "corect")

    def test_wrong_total_reports_expected_value(self):
        sol = verificare.exercitiu("if-else")["solutie"].replace("cos - reducere + transport", "cos + transport")
        v = self.check("if-else", sol)
        self.assertEqual((v["rezultat"], v["test"], v["asteptat"]), ("greșit", "coș de 120 lei cu codul student", "108.00"))
        self.assertEqual(v["intrare"], ["120", "student"])

    def test_missing_structure(self):
        v = self.check("for-range", 'print("fără bucle")\n')
        self.assertEqual((v["etapa"], v["lipseste"]), ("structura", "for"))

    def test_forbidden_break(self):
        sol = verificare.exercitiu("while")["solutie"] + "\nwhile True:\n    break\n"
        self.assertEqual(self.check("while", sol)["interzis"], "break")

    def test_syntax_error_is_explained(self):
        v = self.check("primul-program", '# fișa\nprint("a" * 3\n')
        self.assertEqual(v["etapa"], "sintaxa")
        self.assertEqual(v["eroare"]["titlu"], "Paranteză neînchisă")

    def test_crash_is_explained(self):
        sol = verificare.exercitiu("input-conversii")["solutie"].replace("int(input(", "(input(")
        v = self.check("input-conversii", sol)
        self.assertEqual(v["motiv"], "eroare")
        self.assertEqual(v["eroare"]["tip"], "TypeError")

    def test_repeated_number_must_not_count(self):
        """Ca în jocul din lecție, un număr repetat consumă o încercare: exact ce cere exercițiul să repari."""
        sol = verificare.exercitiu("break-continue")["solutie"].replace(
            '        print(f"Ai mai încercat {numar}. Încercarea nu se pune.")\n',
            '        print(f"Ai mai încercat {numar}. Încercarea nu se pune.")\n        incercari += 1\n')
        v = self.check("break-continue", sol)
        self.assertEqual((v["rezultat"], v["asteptat"]), ("greșit", "ghicit din 3"))

    def test_folded_matching(self):
        self.assertTrue(verificare._contine("PAROLA  puternica: true", "Parolă puternică: True"))
        self.assertFalse(verificare._contine("  *\n ***", "   *\n  ***"))


class ExerciseEndpointTests(WorkspaceTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        call_command("load_lessons", "--only", "08", stdout=StringIO(), stderr=StringIO())  # antetul vine din lecție
        self.path = chapters.ensure(self.user, "proiect", Topic.objects.get(slug="if-else"))
        self.ex = verificare.exercitiu("if-else")

    def post(self, url, **body):
        return self.client.post(f"/api/projects/proiect/{url}", body, content_type="application/json").json()

    @mock.patch.object(ai, "formuleaza", side_effect=lambda user, project, verdict, fallback: fallback)
    def test_wrong_then_right(self, _):
        workspace.write_file(self.user, "proiect", self.path, self.ex["solutie"].replace("- reducere", ""))
        r = self.post("exercitiu/verifica", path=self.path)
        self.assertTrue(r["exercitiu"])
        self.assertEqual((r["verdict"]["rezultat"], r["indiciu"]["treapta"]), ("greșit", 1))
        self.assertIn("108.00", r["mesaj"])
        # detaliile stau într-un balon pe rând: testul, ce trebuia și indiciul, care urcă la fiecare încercare
        note = CodeAnnotation.objects.get(user=self.user, project="proiect", path=self.path).notes[0]
        self.assertIn("108.00", note["text"])
        self.assertIn("Indiciu 1/3", note["text"])
        self.assertEqual(self.post("exercitiu/verifica", path=self.path)["indiciu"]["treapta"], 2)
        self.assertEqual(self.post("exercitiu/verifica", path=self.path)["indiciu"]["treapta"], 3)

        workspace.write_file(self.user, "proiect", self.path, self.ex["solutie"])
        r = self.post("exercitiu/verifica", path=self.path)
        self.assertEqual(r["verdict"]["rezultat"], "corect")
        self.assertEqual(TopicProgress.objects.get(user=self.user, topic__slug="if-else").status, STATUS_DONE)
        self.assertIn("progress", [e["type"] for e in r["events"]])
        self.assertFalse(CodeAnnotation.objects.filter(user=self.user, project="proiect", path=self.path).exists())
        # verificarea rămâne în conversație, ca tutorele mare să știe ce s-a întâmplat
        self.assertEqual(ai.ui_messages(self.user, "proiect")[-1]["text"], r["mesaj"])

    def test_file_without_exercise(self):
        self.assertFalse(self.post("exercitiu/verifica", path="main.py")["exercitiu"])

    def test_exercise_is_in_the_chapter_file(self):
        """Un singur fișier: exercițiul fix se scrie în fișierul capitolului, cu enunțul scurt în antet."""
        self.assertTrue(self.path.endswith("/if_else.py"))
        self.assertIn("Valoarea coșului", (self.root / self.path).read_text(encoding="utf-8"))
        self.assertFalse((self.root / self.path).with_name("exercitiu.py").exists())

    @mock.patch.object(ai, "formuleaza", side_effect=lambda user, project, verdict, fallback: fallback)
    def test_chapter_file_has_a_started_example(self, _):
        """Sub enunț: primul pas scris ca model, apoi „scrii așa: …”. Exemplul singur nu rezolvă exercițiul."""
        text = (self.root / self.path).read_text(encoding="utf-8")
        self.assertIn("(exemplu: așa se scrie)", text)
        self.assertIn('text = input("Valoarea coșului: ")', text)
        self.assertIn("#    scrii așa:", text)
        self.assertEqual(self.post("exercitiu/verifica", path=self.path)["verdict"]["rezultat"], "greșit")
        # un fișier în care elevul a scris deja cod nu primește exemplul
        workspace.write_file(self.user, "proiect", self.path, "# antet\nprint('al meu')\n")
        chapters.ensure(self.user, "proiect", Topic.objects.get(slug="if-else"))
        self.assertNotIn("exemplu: așa", (self.root / self.path).read_text(encoding="utf-8"))

    @mock.patch.object(ai, "formuleaza", side_effect=lambda user, project, verdict, fallback: fallback)
    def test_safety_net_hands_the_file_to_the_tutor(self, _):
        """„Nu lucrez la exercițiul lecției”: fișierul nu mai e verificat cu teste, până la „Exercițiu nou”."""
        workspace.write_file(self.user, "proiect", self.path, 'varsta = int(input("Câți ani ai? "))\nprint("E ok")\n')
        self.post("exercitiu/verifica", path=self.path)
        note = CodeAnnotation.objects.get(user=self.user, project="proiect", path=self.path).notes[0]
        self.assertIn("#nu-e-exercitiul", note["text"])
        self.assertTrue(self.post("exercitiu/sari", path=self.path)["ok"])
        self.assertFalse(CodeAnnotation.objects.filter(user=self.user, project="proiect", path=self.path).exists())
        self.assertFalse(self.post("exercitiu/verifica", path=self.path)["exercitiu"])
        self.post("pas", tip="exercitiu", path=self.path)
        self.assertTrue(self.post("exercitiu/verifica", path=self.path)["exercitiu"])

    @mock.patch.object(ai, "formuleaza", side_effect=lambda user, project, verdict, fallback: fallback)
    def test_solved_exercise_frees_the_file(self, _):
        workspace.write_file(self.user, "proiect", self.path, self.ex["solutie"])
        self.assertEqual(self.post("exercitiu/verifica", path=self.path)["verdict"]["rezultat"], "corect")
        self.assertFalse(self.post("exercitiu/verifica", path=self.path)["exercitiu"])

    def test_lesson_with_a_started_example_has_no_statement_header(self):
        """La lecțiile cu exemplu de început, fișierul începe direct cu pașii (enunțul e în lecție)."""
        self.assertTrue((self.root / self.path).read_text(encoding="utf-8").startswith("# 1. "))
        old = "# Capitolul 08: Decizii\n# Scrie aici exercițiile pentru acest capitol.\n\nprint('codul meu')\n"
        workspace.write_file(self.user, "proiect", self.path, old)
        chapters.ensure(self.user, "proiect", Topic.objects.get(slug="if-else"))
        self.assertEqual((self.root / self.path).read_text(encoding="utf-8"), "print('codul meu')\n")

    def test_other_lessons_start_with_the_lesson_statement(self):
        """Fără exemplu de început: enunțul din lecție e în antet; cel vechi se înlocuiește fără să atingă codul."""
        call_command("load_lessons", "--only", "12", stdout=StringIO(), stderr=StringIO())
        topic = Topic.objects.get(slug="liste")
        path = chapters.ensure(self.user, "proiect", topic)
        text = (self.root / path).read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# ===="))
        self.assertNotIn("capitole/12-liste", text.split("\n")[5])  # „În `capitole/...`, scrie” → „Scrie”
        workspace.write_file(self.user, "proiect", path, "# Capitolul 12: Liste\n# Scrie aici exercițiile pentru acest capitol.\n\nprint('codul meu')\n")
        chapters.ensure(self.user, "proiect", topic)
        new = (self.root / path).read_text(encoding="utf-8")
        self.assertTrue(new.startswith("# ====") and new.rstrip().endswith("print('codul meu')"))
        chapters.ensure(self.user, "proiect", topic)
        self.assertEqual((self.root / path).read_text(encoding="utf-8"), new)  # a doua oară nu schimbă nimic

    def test_legacy_exercise_file_moves_into_the_chapter_file(self):
        topic = Topic.objects.get(slug="while")
        main = chapters.ensure(self.user, "proiect", topic)
        legacy = main.rsplit("/", 1)[0] + "/exercitiu.py"
        workspace.write_file(self.user, "proiect", main, "# Capitolul 09: Bucla while\n")  # ca înainte: doar antetul
        workspace.write_file(self.user, "proiect", legacy, "# antet\nprint('pușculița')\n")
        chapters.ensure(self.user, "proiect", topic)
        self.assertFalse((self.root / legacy).exists())
        self.assertIn("pușculița", (self.root / main).read_text(encoding="utf-8"))

    @mock.patch.object(ai, "formuleaza", side_effect=lambda user, project, verdict, fallback: fallback)
    def test_hints_restart_for_a_different_program(self, _):
        workspace.write_file(self.user, "proiect", self.path, self.ex["solutie"].replace("- reducere", ""))
        self.post("exercitiu/verifica", path=self.path)
        self.assertEqual(self.post("exercitiu/verifica", path=self.path)["indiciu"]["treapta"], 2)
        workspace.write_file(self.user, "proiect", self.path, 'x = input("Câți ani ai? ")\nprint("E ok")\n')
        self.assertEqual(self.post("exercitiu/verifica", path=self.path)["indiciu"]["treapta"], 1)


class CurrentLessonTests(WorkspaceTestCase):
    """Lecția curentă e ultima deschisă de elev; „în lucru” înseamnă că chiar lucrează la ea."""

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def open(self, slug):
        return self.client.post("/api/projects/proiect/chapter", {"topic": slug}, content_type="application/json").json()

    def current(self):
        return self.client.get("/api/progress?project=proiect").json()["current"]

    def test_looking_at_a_lesson_does_not_start_it(self):
        self.assertEqual(self.open("pep8-stil")["status"], STATUS_TODO)
        self.assertFalse(TopicProgress.objects.filter(user=self.user, topic__slug="pep8-stil").exists())
        self.assertEqual(self.current(), "pep8-stil")

    def test_learned_lesson_can_be_the_current_one(self):
        TopicProgress.objects.create(user=self.user, topic=Topic.objects.get(slug="liste"), status=STATUS_DOING)
        TopicProgress.objects.create(user=self.user, topic=Topic.objects.get(slug="primul-program"), status=STATUS_DONE)
        self.open("primul-program")
        self.assertEqual(self.current(), "primul-program")  # nu mai sare la ultima lecție „în lucru”

    def test_running_chapter_code_marks_it_in_progress(self):
        with mock.patch.object(runner, "run"):
            self.client.post("/api/projects/proiect/term/run", {"command": "python capitole/12-liste/liste.py"},
                             content_type="application/json")
        self.assertEqual(TopicProgress.objects.get(user=self.user, topic__slug="liste").status, STATUS_DOING)


class LocalStepTests(WorkspaceTestCase):
    """„Următorul pas” și „Exercițiu nou” răspund din curriculum, fără AI, când se poate."""

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def step(self, **body):
        return self.client.post("/api/projects/proiect/pas", body, content_type="application/json").json()

    def test_next_step_is_the_pending_exercise(self):
        r = self.step(tip="urmator")
        self.assertFalse(r["ai"])
        self.assertEqual(r["path"], "capitole/01-primul-program/primul_program.py")
        self.assertIn("lecția 1", r["mesaj"])
        self.assertTrue((self.root / r["path"]).is_file())
        self.assertEqual(TopicProgress.objects.get(user=self.user, topic__slug="primul-program").status, STATUS_DOING)
        self.assertEqual(ai.ui_messages(self.user, "proiect")[-1]["text"], r["mesaj"])

    def test_next_step_after_learned_topic(self):
        TopicProgress.objects.create(user=self.user, topic=Topic.objects.get(slug="primul-program"), status=STATUS_DONE)
        self.assertEqual(self.step(tip="urmator")["path"], "capitole/02-variabile/variabile.py")

    def test_new_exercise_uses_the_fixed_one_of_the_open_file(self):
        r = self.step(tip="exercitiu", path="capitole/09-while/while_exercitii.py")
        self.assertEqual(r["path"], "capitole/09-while/while_exercitii.py")

    def test_new_exercise_goes_to_ai_when_there_is_no_fixed_one(self):
        self.assertTrue(self.step(tip="exercitiu", path="capitole/12-liste/liste.py")["ai"])
        TopicProgress.objects.create(user=self.user, topic=Topic.objects.get(slug="while"), status=STATUS_DONE)
        self.assertTrue(self.step(tip="exercitiu", path="capitole/09-while/while_exercitii.py")["ai"])


class CheckModeTests(WorkspaceTestCase):
    """„Rulează și verifică” fără exercițiu fix: modelul mic, context redus, doar uneltele de baloane și progres."""

    def test_check_gets_only_the_current_turn(self):
        calls = []

        def fake_rounds(user, project, conv, since=None):
            calls.append((since, ai._check_history(conv, since)))
            yield {"type": "text", "text": "Bine!"}

        workspace.write_file(self.user, "proiect", "main.py", 'print("x")\n')
        with mock.patch.object(ai, "_anthropic_rounds", fake_rounds), mock.patch.object(ai, "_openai_rounds", fake_rounds), \
                mock.patch.object(ai, "_progress_check", return_value=iter(())):
            list(ai.chat_stream(self.user, "proiect", "Am rulat codul.", {"open_file": "main.py"}, mode="check"))
        since, msgs = calls[0]
        self.assertIsNotNone(since)
        self.assertEqual(len(msgs), 1)
        context = msgs[0].content[0]["text"]
        self.assertIn("main.py", context)
        self.assertNotIn("## Curriculum", context)
        self.assertEqual({t["name"] for t in ai.CHECK_TOOLS}, {"annotate_code", "record_progress"})

    def test_terminal_output_explains_known_error(self):
        sess = runner.get(self.user, "proiect")
        sess.command, sess.command_start, sess.returncode, sess.busy = "python main.py", 0, 1, False
        sess.text, sess.base = TRACEBACK_NAME, 0
        self.assertEqual(runner.output(self.user, "proiect")["eroare"]["titlu"], "Nume scris greșit")
