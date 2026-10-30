from django.urls import path

from . import views

urlpatterns = [
    path("", views.ListaArticole.as_view(), name="lista"),
    path("articol/<int:nr>/", views.DetaliuArticol.as_view(), name="detaliu"),
    path("articol/<int:nr>/comentariu/", views.adauga_comentariu, name="comentariu"),
    path("articol/nou/", views.ArticolNou.as_view(), name="articol_nou"),
    path("articol/<int:nr>/editeaza/", views.ArticolEditeaza.as_view(), name="articol_editeaza"),
    path("articol/<int:nr>/sterge/", views.ArticolSterge.as_view(), name="articol_sterge"),
    path("despre/", views.Despre.as_view(), name="despre"),
    path("contact/", views.Contact.as_view(), name="contact"),
    path("conturi/inregistrare/", views.inregistrare, name="inregistrare"),
]
