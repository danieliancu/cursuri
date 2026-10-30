from django import forms

from .models import Articol, Comentariu


class ContactForm(forms.Form):
    nume = forms.CharField(max_length=80)
    email = forms.EmailField()
    mesaj = forms.CharField(widget=forms.Textarea, min_length=10)


class ComentariuForm(forms.ModelForm):
    class Meta:
        model = Comentariu
        fields = ["autor", "text"]
        labels = {"autor": "Numele tău", "text": "Comentariu"}
        widgets = {"text": forms.Textarea(attrs={"rows": 4})}


class ArticolForm(forms.ModelForm):
    class Meta:
        model = Articol
        fields = ["titlu", "continut", "categorie", "etichete", "data_publicarii", "publicat"]
        labels = {"continut": "Conținut", "data_publicarii": "Data publicării"}

    def clean_titlu(self):
        """Validare proprie: titlul nu e scris numai cu majuscule."""
        titlu = self.cleaned_data["titlu"].strip()
        if titlu.isupper():
            raise forms.ValidationError("Nu scrie titlul numai cu majuscule.")
        return titlu
