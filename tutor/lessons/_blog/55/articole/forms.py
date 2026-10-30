from django import forms


class ContactForm(forms.Form):
    nume = forms.CharField(max_length=80)
    email = forms.EmailField()
    mesaj = forms.CharField(widget=forms.Textarea, min_length=10)
