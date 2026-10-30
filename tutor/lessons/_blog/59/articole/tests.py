from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import ArticolForm
from .models import Articol, Categorie, Comentariu


class DateDeTest(TestCase):
    """Datele comune: create o singură dată pentru toată clasa, refăcute pentru fiecare test."""

    @classmethod
    def setUpTestData(cls):
        cls.ana = User.objects.create_user("ana", password="parola-ana-2026")
        cls.mihai = User.objects.create_user("mihai", password="parola-mihai-2026")
        programare = Categorie.objects.create(nume="Programare")
        cls.articol = Articol.objects.create(
            titlu="De ce am ales Django",
            continut="Django are toate acestea „din cutie”.",
            data_publicarii=date(2026, 10, 2),
            categorie=programare,
            autor=cls.ana,
        )
        cls.ciorna = Articol.objects.create(
            titlu="Ciornă", continut="Încă lucrez la el.", publicat=False
        )


class ModelTests(DateDeTest):
    def test_str_e_titlul(self):
        self.assertEqual(str(self.articol), "De ce am ales Django")

    def test_adresa_articolului(self):
        self.assertEqual(self.articol.get_absolute_url(), f"/articol/{self.articol.id}/")


class ListaTests(DateDeTest):
    def test_arata_doar_articolele_publicate(self):
        raspuns = self.client.get(reverse("lista"))
        self.assertEqual(raspuns.status_code, 200)
        self.assertContains(raspuns, "De ce am ales Django")
        self.assertNotContains(raspuns, "Ciornă")


class DetaliuTests(DateDeTest):
    def test_articol_existent(self):
        raspuns = self.client.get(self.articol.get_absolute_url())
        self.assertContains(raspuns, "<h1>De ce am ales Django</h1>", html=True)

    def test_articol_inexistent_da_404(self):
        raspuns = self.client.get("/articol/999/")
        self.assertEqual(raspuns.status_code, 404)

    def test_ciorna_nu_se_vede(self):
        raspuns = self.client.get(self.ciorna.get_absolute_url())
        self.assertEqual(raspuns.status_code, 404)


class ComentariuTests(DateDeTest):
    def test_comentariu_valid_e_salvat_si_redirectionat(self):
        adresa = reverse("comentariu", args=[self.articol.id])
        raspuns = self.client.post(adresa, {"autor": "Mihai", "text": "Foarte bun articol!"})
        self.assertRedirects(raspuns, self.articol.get_absolute_url() + "#comentarii")
        self.assertEqual(Comentariu.objects.get().text, "Foarte bun articol!")

    def test_comentariu_fara_text_nu_e_salvat(self):
        adresa = reverse("comentariu", args=[self.articol.id])
        raspuns = self.client.post(adresa, {"autor": "Mihai", "text": ""})
        self.assertEqual(raspuns.status_code, 200)
        self.assertFalse(Comentariu.objects.exists())


class ArticolNouTests(DateDeTest):
    def test_cere_autentificare(self):
        raspuns = self.client.get(reverse("articol_nou"))
        self.assertRedirects(raspuns, "/conturi/login/?next=/articol/nou/")

    def test_autorul_e_utilizatorul_logat(self):
        self.client.force_login(self.ana)
        date_formular = {
            "titlu": "Un articol nou",
            "continut": "Text.",
            "data_publicarii": "2026-10-29",
            "publicat": "on",
        }
        self.client.post(reverse("articol_nou"), date_formular)
        self.assertEqual(Articol.objects.get(titlu="Un articol nou").autor, self.ana)


class EditareTests(DateDeTest):
    def test_alt_utilizator_primeste_403(self):
        self.client.force_login(self.mihai)
        raspuns = self.client.get(reverse("articol_editeaza", args=[self.articol.id]))
        self.assertEqual(raspuns.status_code, 403)

    def test_autorul_poate_edita(self):
        self.client.force_login(self.ana)
        raspuns = self.client.get(reverse("articol_editeaza", args=[self.articol.id]))
        self.assertEqual(raspuns.status_code, 200)


class ArticolFormTests(TestCase):
    def test_titlu_numai_cu_majuscule_e_respins(self):
        date_formular = {"titlu": "TITLU", "continut": "Text.", "data_publicarii": "2026-10-29"}
        formular = ArticolForm(data=date_formular)
        self.assertFalse(formular.is_valid())
        self.assertEqual(formular.errors["titlu"], ["Nu scrie titlul numai cu majuscule."])
