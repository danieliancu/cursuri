from datetime import date

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Articol


class ArticolApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = User.objects.create_user("ana", password="parola-ana-2026")
        cls.mihai = User.objects.create_user("mihai", password="parola-mihai-2026")
        cls.articol = Articol.objects.create(
            titlu="De ce am ales Django",
            continut="Text.",
            data_publicarii=date(2026, 10, 2),
            autor=cls.ana,
        )

    def test_lista_e_publica(self):
        raspuns = self.client.get("/api/articole/")
        self.assertEqual(raspuns.status_code, 200)
        self.assertEqual(raspuns.json()[0]["titlu"], "De ce am ales Django")

    def test_fara_cont_nu_poti_scrie(self):
        raspuns = self.client.post("/api/articole/", {"titlu": "Nou", "continut": "Text."})
        self.assertEqual(raspuns.status_code, 403)

    def test_autorul_e_utilizatorul_logat(self):
        self.client.force_authenticate(self.mihai)
        raspuns = self.client.post("/api/articole/", {"titlu": "Nou", "continut": "Text."})
        self.assertEqual(raspuns.status_code, 201)
        self.assertEqual(raspuns.json()["autor"], "mihai")

    def test_doar_autorul_poate_modifica(self):
        self.client.force_authenticate(self.mihai)
        raspuns = self.client.patch(f"/api/articole/{self.articol.id}/", {"titlu": "Altul"})
        self.assertEqual(raspuns.status_code, 403)
