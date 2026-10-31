"""Teste în browser: interfața (app.js, md.js) rulată de un Chrome real, fără fereastră.

Aplicația pornește pe un server de test, cu proiectele elevului într-un folder temporar și terminalul în
modul local (fără Docker). Cer Playwright (requirements-dev.txt) și Chrome instalat; altfel sunt sărite.
Bibliotecile din pagină (CodeMirror, marked, DOMPurify) vin de pe cdnjs, deci e nevoie de internet.

Rulare: python manage.py test tutor.tests_browser
"""
import os
import tempfile
from io import StringIO
from pathlib import Path
from unittest import SkipTest, mock

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from django.test import Client

from . import ai, chapters, verificare, workspace
from .models import Topic

try:
    from playwright.sync_api import Error as PlaywrightError, expect, sync_playwright
except ImportError:  # pragma: no cover - fără dependențele de dezvoltare
    sync_playwright = None

TIMEOUT_MS = 15_000


class BrowserTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        if sync_playwright is None:
            raise SkipTest("Playwright nu e instalat (pip install -r requirements-dev.txt).")
        # Playwright (sync) ține o buclă asyncio pe firul testului; ORM-ul Django ar refuza apelurile de acolo.
        os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
        super().setUpClass()
        cls.pw = sync_playwright().start()
        try:
            cls.browser = cls.pw.chromium.launch(channel="chrome")
        except PlaywrightError as e:
            cls.pw.stop()
            super().tearDownClass()
            raise SkipTest(f"Chrome nu poate fi pornit: {e}")

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        super().tearDownClass()

    def setUp(self):
        # Testele cu server golesc tabelele după fiecare test, inclusiv curriculumul pus de migrări.
        if not Topic.objects.exists():
            call_command("sync_curriculum", stdout=StringIO())
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        override = self.settings(WORKSPACE_ROOT=Path(tmp.name), PYTUTOR_SANDBOX="local")
        override.enable()
        self.addCleanup(override.disable)

        self.user = User.objects.create_user("elev", "", "x")
        workspace.create_project(self.user, "proiect")
        client = Client()
        client.force_login(self.user)
        self.context = self.browser.new_context()
        self.addCleanup(self.context.close)
        self.context.add_cookies([{
            "name": settings.SESSION_COOKIE_NAME, "value": client.cookies[settings.SESSION_COOKIE_NAME].value,
            "url": self.live_server_url,
        }])
        self.page = self.context.new_page()
        self.page.set_default_timeout(TIMEOUT_MS)
        expect.set_options(timeout=TIMEOUT_MS)

    def open_editor(self):
        """Deschide editorul și așteaptă și lista de lecții (se încarcă după fișiere și conversație)."""
        self.page.goto(self.live_server_url + "/")
        expect(self.page.locator("#tree .node", has_text="main.py")).to_be_visible()
        expect(self.page.locator(".course-module").first).to_be_visible()

    def tree_node(self, name):
        return self.page.locator("#tree .node .name", has_text=name)

    def run_in_terminal(self, command):
        self.page.fill("#termInput", command)
        self.page.press("#termInput", "Enter")


class ExplorerRefreshTests(BrowserTestCase):
    """Fișierele create sau șterse de o comandă din terminal apar / dispar singure în Explorer."""

    def test_file_created_by_command_appears(self):
        self.open_editor()
        self.run_in_terminal("""python -c "open('creat.txt', 'w').write('x')" """)
        expect(self.tree_node("creat.txt")).to_be_visible()

    def test_file_deleted_by_command_disappears(self):
        workspace.write_file(self.user, "proiect", "vechi.txt", "x")
        self.open_editor()
        expect(self.tree_node("vechi.txt")).to_be_visible()
        self.run_in_terminal("""python -c "import os; os.remove('vechi.txt')" """)
        expect(self.tree_node("vechi.txt")).to_have_count(0)


class ChatMarkdownTests(BrowserTestCase):
    def test_numbered_list_continues_after_code_block(self):
        """„1, 2, [cod], 3”: a doua listă (<ol start="3">) își pornește cerculețele de la 3, nu de la 1."""
        self.open_editor()
        resets = self.page.evaluate("""() => {
            const b = document.createElement("div");
            PTMarkdown.render(b, "1. Unu\\n2. Doi:\\n\\n```bash\\nx\\n```\\n\\n3. Trei");
            return [...b.querySelectorAll("ol")].map((ol) => ol.style.counterReset);
        }""")
        self.assertEqual(resets, ["", "step 2"])


class DjangoLessonTests(BrowserTestCase):
    def test_django_lesson_outside_django_project_creates_no_folder(self):
        """O lecție Django aleasă dintr-un proiect fără manage.py: un mesaj, fără folder de capitol pentru ea.
        (Folderul lecției curente, `capitole/01-…`, îl creează editorul la pornire.)"""
        self.open_editor()
        self.page.locator(".course-module summary", has_text="Django: fundamentele").click()
        self.page.locator(".course-link", has_text="Proiect și aplicații").click()
        expect(self.page.locator("#toast")).to_contain_text("lecție Django")
        root = workspace.project_dir(self.user, "proiect") / "capitole"
        self.assertEqual([p.name for p in root.glob("*django*")], [])


class ErrorBalloonTests(BrowserTestCase):
    def test_known_error_becomes_a_balloon_without_ai(self):
        """O eroare cunoscută (tutor/erori.py) apare ca balon pe rândul ei, cu link spre lecție; tutorele AI tace."""
        workspace.write_file(self.user, "proiect", "main.py", 'nume = "Ana"\nPrint(nume)\n')
        with mock.patch.object(ai, "chat_stream") as chat:
            self.open_editor()
            self.tree_node("main.py").click()
            expect(self.page.locator(".CodeMirror")).to_contain_text("Print(nume)")
            self.page.click("#runBtn")
            marker = self.page.locator(".note-marker").first
            expect(marker).to_be_visible()
            marker.click()
            balloon = self.page.locator(".note-balloon")
            expect(balloon).to_contain_text("print")
            expect(balloon.locator('a[href^="/progres/#"]')).to_have_count(1)
            expect(balloon.locator('a[href="#intreaba-ai"]')).to_have_count(1)
        chat.assert_not_called()


class ExerciseCheckTests(BrowserTestCase):
    """„Rulează și verifică” pe exercițiul fix: verdictul vine din teste (fără AI), cu balon și indiciu."""

    def setUp(self):
        super().setUp()
        patcher = mock.patch.object(ai, "formuleaza", side_effect=lambda user, project, verdict, fallback: fallback)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.path = chapters.ensure(self.user, "proiect", Topic.objects.get(slug="primul-program"))
        workspace.write_file(self.user, "proiect", self.path, 'print("Ana")\n')

    def test_wrong_then_right(self):
        self.open_editor()
        expect(self.page.locator(".CodeMirror")).to_contain_text('print("Ana")')
        self.page.click("#runBtn")
        expect(self.page.locator("#messages .msg.user").last).to_contain_text("Verifică exercițiul")
        marker = self.page.locator(".note-marker").first
        expect(marker).to_be_visible()
        marker.click()
        expect(self.page.locator(".note-balloon")).to_contain_text("Indiciu 1/3")

        solution = verificare.exercitiu("primul-program")["solutie"]
        self.page.evaluate("(code) => document.querySelector('.CodeMirror').CodeMirror.setValue(code)", solution)
        self.page.click("#runBtn")
        expect(self.page.locator("#toast")).to_contain_text("învățat")
        expect(self.page.locator(".note-marker")).to_have_count(0)


class LocalStepTests(BrowserTestCase):
    def test_next_step_answers_without_ai(self):
        """„Următorul pas” la un elev nou: lecția 1 și exercițiul ei, din curriculum, fără tutorele AI."""
        with mock.patch.object(ai, "chat_stream") as chat:
            self.open_editor()
            self.page.click('#quick [data-step="next"]')
            expect(self.page.locator("#messages .msg.assistant").last).to_contain_text("lecția 1")
        chat.assert_not_called()


class LessonSectionLinkTests(BrowserTestCase):
    def test_link_opens_the_lesson_at_the_section(self):
        """`/progres/#slug:s-...` (linkul din balonul unei erori) deschide lecția la secțiunea respectivă."""
        call_command("load_lessons", "--only", "08", stdout=StringIO(), stderr=StringIO())
        self.page.goto(self.live_server_url + "/progres/#if-else:s-1-lipsesc-cele-doua-puncte")
        heading = self.page.locator("#s-1-lipsesc-cele-doua-puncte")
        expect(heading).to_have_text("1. Lipsesc cele două puncte")
        expect(heading).to_be_in_viewport()


class IconTests(BrowserTestCase):
    def test_every_icon_points_to_a_symbol_in_the_page(self):
        self.open_editor()
        missing = self.page.evaluate("""() => [...document.querySelectorAll("use")]
            .map((u) => u.getAttribute("href"))
            .filter((h) => !h.startsWith("#") || !document.querySelector(h))""")
        self.assertEqual(missing, [])
