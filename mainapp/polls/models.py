from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

class Uzytkownik(AbstractUser):
    class Meta:
        verbose_name_plural = "Uzytkownicy"
    username = models.CharField(max_length=30, unique = True, error_messages={'unique': 'Nazwa uzytkownika jest juz zajeta.'})
    def __str__(self):
        return self.username

class Blog(models.Model):
    class Meta:
        verbose_name_plural = "Blogi"
    nazwa = models.CharField(max_length = 100, unique = True, error_messages={'unique': 'Nazwa bloga jest juz zajeta.'})
    autor = models.ForeignKey(Uzytkownik, on_delete = models.CASCADE)
    motto = models.CharField(max_length = 300)
    def __str__(self):
        return self.nazwa

class Kategoria(models.Model):
    class Meta:
        verbose_name_plural = "Kategorie"
    nazwa = models.CharField(max_length = 30)
    def __str__(self):
        return self.nazwa

class Post(models.Model):
    class Meta:
        verbose_name_plural = "Posty"
    blog = models.ForeignKey(Blog, on_delete = models.CASCADE)
    obrazek = models.ImageField(upload_to="obrazki/", null = True, blank = True)
    haslo = models.CharField(max_length = 30, null = True, blank = True)
    zawartosc = models.TextField(null = True, blank = True)
    kategoria = models.ForeignKey(Kategoria, default=1)
    data = models.DateTimeField(default = datetime.now, blank = True)
    tytul = models.CharField(max_length = 100, default="[Brak tytulu]")
    def __str__(self):
        return self.tytul

class Komentarz(models.Model):
    class Meta:
        verbose_name_plural = "Komentarze"
    kto = models.ForeignKey(Uzytkownik, null = True)
    kiedy = models.DateTimeField(default = datetime.now, blank = True)
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    tresc = models.TextField(null = True, blank = True)
    def __str__(self):
        return str(self.id)

class Historia(models.Model):
    class Meta:
        verbose_name_plural = "Historie"
    uzytkownik = models.ForeignKey(Uzytkownik, null = True)
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    licznik_odwiedzin = models.IntegerField(default=0)
    czy_plus = models.BooleanField(default = False)
    czy_minus = models.BooleanField(default = False)
    czy_odblokowany = models.BooleanField(default = False)
    data = models.DateTimeField(default = datetime.now, blank = True)
    def __str__(self):
        return str(self.id)

