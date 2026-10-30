from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista, name="lista"),
    path("articol/<int:nr>/", views.detaliu, name="detaliu"),
    path("articol/<int:nr>/comentariu/", views.adauga_comentariu, name="comentariu"),
    path("articol/nou/", views.articol_nou, name="articol_nou"),
    path("articol/<int:nr>/editeaza/", views.articol_editeaza, name="articol_editeaza"),
    path("despre/", views.despre, name="despre"),
    path("contact/", views.contact, name="contact"),
    path("conturi/inregistrare/", views.inregistrare, name="inregistrare"),
]
