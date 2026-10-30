from datetime import date

from django.db import models
from django.urls import reverse


class Categorie(models.Model):
    nume = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["nume"]
        verbose_name = "categorie"
        verbose_name_plural = "categorii"

    def __str__(self):
        return self.nume


class Eticheta(models.Model):
    nume = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ["nume"]
        verbose_name = "etichetă"
        verbose_name_plural = "etichete"

    def __str__(self):
        return self.nume


class Articol(models.Model):
    titlu = models.CharField(max_length=200)
    continut = models.TextField()
    data_publicarii = models.DateField(default=date.today)
    publicat = models.BooleanField(default=True)
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articole",
    )
    etichete = models.ManyToManyField(Eticheta, blank=True, related_name="articole")

    class Meta:
        ordering = ["-data_publicarii"]
        verbose_name = "articol"
        verbose_name_plural = "articole"

    def __str__(self):
        return self.titlu

    def get_absolute_url(self):
        """Adresa paginii articolului; o folosesc redirect() și view-urile generice."""
        return reverse("detaliu", args=[self.id])


class Comentariu(models.Model):
    articol = models.ForeignKey(Articol, on_delete=models.CASCADE, related_name="comentarii")
    autor = models.CharField(max_length=80)
    text = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["data"]
        verbose_name = "comentariu"
        verbose_name_plural = "comentarii"

    def __str__(self):
        return f"{self.autor} despre „{self.articol}”"
