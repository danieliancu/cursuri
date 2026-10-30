from django.shortcuts import get_object_or_404, render

from .models import Articol


def lista(request):
    articole = Articol.objects.filter(publicat=True).select_related("categorie")
    return render(request, "articole/lista.html", {"articole": articole})


def detaliu(request, nr):
    articol = get_object_or_404(Articol, id=nr, publicat=True)
    return render(request, "articole/detaliu.html", {"articol": articol})


def despre(request):
    return render(request, "articole/despre.html")
