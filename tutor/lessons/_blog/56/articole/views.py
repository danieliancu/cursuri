from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ArticolForm, ComentariuForm, ContactForm
from .models import Articol


def lista(request):
    articole = Articol.objects.filter(publicat=True).select_related("categorie")
    return render(request, "articole/lista.html", {"articole": articole})


def detaliu(request, nr):
    articol = get_object_or_404(Articol, id=nr, publicat=True)
    context = {"articol": articol, "formular": ComentariuForm()}
    return render(request, "articole/detaliu.html", context)


@require_POST
def adauga_comentariu(request, nr):
    articol = get_object_or_404(Articol, id=nr, publicat=True)
    formular = ComentariuForm(request.POST)
    if formular.is_valid():
        comentariu = formular.save(commit=False)
        comentariu.articol = articol
        comentariu.save()
        return redirect(articol.get_absolute_url() + "#comentarii")
    return render(request, "articole/detaliu.html", {"articol": articol, "formular": formular})


def articol_nou(request):
    if request.method == "POST":
        formular = ArticolForm(request.POST)
        if formular.is_valid():
            articol = formular.save()
            messages.success(request, "Articolul a fost salvat.")
            return redirect(articol)
    else:
        formular = ArticolForm()
    context = {"formular": formular, "titlu": "Articol nou"}
    return render(request, "articole/formular_articol.html", context)


def articol_editeaza(request, nr):
    articol = get_object_or_404(Articol, id=nr)
    if request.method == "POST":
        formular = ArticolForm(request.POST, instance=articol)
        if formular.is_valid():
            formular.save()
            messages.success(request, "Modificările au fost salvate.")
            return redirect(articol)
    else:
        formular = ArticolForm(instance=articol)
    context = {"formular": formular, "titlu": f"Editează: {articol.titlu}"}
    return render(request, "articole/formular_articol.html", context)


def despre(request):
    return render(request, "articole/despre.html")


def contact(request):
    if request.method == "POST":
        formular = ContactForm(request.POST)
        if formular.is_valid():
            nume = formular.cleaned_data["nume"]
            messages.success(request, f"Mulțumim, {nume}! Ana îți va răspunde în curând.")
            return redirect("contact")
    else:
        formular = ContactForm()
    return render(request, "articole/contact.html", {"formular": formular})
