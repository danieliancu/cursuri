"""Adresele proiectului: fiecare cerere e trimisă mai departe după începutul căii."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("articole.urls")),
]
