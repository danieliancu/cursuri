from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista, name="lista"),
    path("articol/<int:nr>/", views.detaliu, name="detaliu"),
    path("despre/", views.despre, name="despre"),
    path("contact/", views.contact, name="contact"),
]
