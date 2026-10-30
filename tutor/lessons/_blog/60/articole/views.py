from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import ArticolForm, ComentariuForm, ContactForm
from .models import Articol


class ListaArticole(ListView):
    queryset = Articol.objects.filter(publicat=True).select_related("categorie", "autor")
    template_name = "articole/lista.html"
    context_object_name = "articole"


class DetaliuArticol(DetailView):
    queryset = Articol.objects.filter(publicat=True)
    template_name = "articole/detaliu.html"
    context_object_name = "articol"
    pk_url_kwarg = "nr"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formular"] = ComentariuForm()
        return context


class ArticolNou(LoginRequiredMixin, CreateView):
    model = Articol
    form_class = ArticolForm
    template_name = "articole/formular_articol.html"
    extra_context = {"titlu": "Articol nou"}

    def form_valid(self, form):
        form.instance.autor = self.request.user
        messages.success(self.request, "Articolul a fost salvat.")
        return super().form_valid(form)


class DoarAutorul(UserPassesTestMixin):
    """Lasă mai departe doar autorul articolului; ceilalți primesc 403."""

    def test_func(self):
        return self.get_object().autor == self.request.user


class ArticolEditeaza(LoginRequiredMixin, DoarAutorul, UpdateView):
    model = Articol
    form_class = ArticolForm
    template_name = "articole/formular_articol.html"
    pk_url_kwarg = "nr"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titlu"] = f"Editează: {self.object.titlu}"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Modificările au fost salvate.")
        return super().form_valid(form)


class ArticolSterge(LoginRequiredMixin, DoarAutorul, DeleteView):
    model = Articol
    template_name = "articole/confirma_stergere.html"
    pk_url_kwarg = "nr"
    success_url = reverse_lazy("lista")


class Despre(TemplateView):
    template_name = "articole/despre.html"


class Contact(FormView):
    form_class = ContactForm
    template_name = "articole/contact.html"
    success_url = reverse_lazy("contact")

    def form_valid(self, form):
        nume = form.cleaned_data["nume"]
        messages.success(self.request, f"Mulțumim, {nume}! Ana îți va răspunde în curând.")
        return super().form_valid(form)


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


def inregistrare(request):
    if request.method == "POST":
        formular = UserCreationForm(request.POST)
        if formular.is_valid():
            utilizator = formular.save()
            login(request, utilizator)
            messages.success(request, f"Bun venit, {utilizator.username}!")
            return redirect("lista")
    else:
        formular = UserCreationForm()
    return render(request, "registration/inregistrare.html", {"formular": formular})
