from django import forms
from .models import Uzytkownik, Blog, Komentarz, Post, Kategoria

class RejestracjaForm(forms.ModelForm):
    username = forms.CharField(error_messages={'required': 'Wprowadz login!'}, widget=forms.TextInput(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}), error_messages={'required': 'Wprowadz haslo!'})
    email = forms.CharField(widget=forms.EmailInput(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}), error_messages={'required': 'Wprowadz adres e-mail!'})
    class Meta:
        model = Uzytkownik
        fields = ['username', 'email', 'password']

class LogowanieForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}), error_messages={'required': 'Podaj haslo!'})
    username = forms.CharField(error_messages={'required': 'Podaj login!'}, widget=forms.TextInput(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}))

class BlogForm(forms.ModelForm):
    nazwa = forms.CharField(error_messages={'required': 'Wprowadz nazwe bloga!'}, widget=forms.TextInput(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}))
    motto = forms.CharField(required=False, widget=forms.TextInput(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}))
    class Meta:
        model = Blog
        fields = ['nazwa', 'motto']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Komentarz
        fields = ['tresc']
        widgets = {
            'tresc': forms.Textarea(attrs={'style': 'height: 50px; min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'})
        }

class PostForm(forms.ModelForm):
    tytul = forms.CharField(initial='[Bez tytulu]', error_messages={'required': 'Tytul nie moze byc pusty!'}, widget=forms.TextInput(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}))
    obrazek = forms.ImageField(required=False)
    haslo = forms.CharField(required=False, widget=forms.TextInput(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}))
    class Meta:
        model = Post
        fields = ['tytul', 'zawartosc', 'kategoria', 'haslo', 'obrazek']
        widgets = {
            'zawartosc': forms.Textarea(attrs={'style': 'height: 300px; min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}),
            'kategoria': forms.Select(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'})
        }

class OdblokujForm(forms.Form):
    haslo = forms.CharField(error_messages={'required': 'Podaj haslo!'}, widget=forms.PasswordInput(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}))

class WyszukiwarkaForm(forms.Form):
    slowa_kluczowe = forms.CharField(required=False, widget=forms.TextInput(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}))
    blog = forms.CharField(required=False, widget=forms.TextInput(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}))
    kategoria = forms.ModelChoiceField(required=False, queryset=Kategoria.objects.all(), widget=forms.Select(attrs={'style': 'min-width: 100%; autocomplete: off; resize: none; border-radius: 10px; padding: 5px'}))