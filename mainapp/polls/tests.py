from django.test import TestCase
from .models import Historia, Post, Kategoria, Blog, Uzytkownik

class HistoriaTests(TestCase):
    def test_prawidlowe_wpisy(self):
        uzytkownik = Uzytkownik(username="jan", password="scisletajne", email="jan@o2.pl")
        uzytkownik.save()
        blog = Blog(nazwa="Blog", autor=uzytkownik)
        blog.save()
        post = Post(zawartosc="Hello world!", tytul="Wyswietlony post", blog=blog)
        post.save()
        wpis = Historia(uzytkownik=uzytkownik, post=post)
        wpis.save()
        self.assertEqual((wpis.licznik_odwiedzin >= 0), True)
        try:
            pobrany_wpis = Historia.objects.get(uzytkownik=uzytkownik, post=post)
        except:
            pobrany_wpis = None
        self.assertEqual(pobrany_wpis == None, False)

class KategorieTests(TestCase):
    def test_niepuste_kategorie(self):
        kategoria = Kategoria(nazwa="Domyslna")
        kategoria.save()
        n = Kategoria.objects.count()
        self.assertEqual(n > 0, True)

    def test_prawidlowe_kategorie(self):
        kategoria = Kategoria(nazwa="Domyslna")
        kategoria.save()
        try:
            pobrana = Kategoria.objects.get(nazwa="Domyslna")
        except Kategoria.DoesNotExist:
            pobrana = None
        self.assertEqual(pobrana == None, False)

class PostTests(TestCase):
    def test_prawidlowe_posty(self):
        uzytkownik = Uzytkownik(username="jan", password="scisletajne", email="jan@o2.pl")
        uzytkownik.save()
        blog = Blog(nazwa="Blog", autor=uzytkownik)
        blog.save()
        post = Post(zawartosc="Hello world!", blog=blog)
        post.save()
        self.assertEqual(len(post.zawartosc) > 0, True)
        self.assertEqual(len(post.tytul) > 0, True)
        self.assertEqual(post.blog == None, False)
        self.assertEqual(post.obrazek == True or post.obrazek == None, True)

class BlogTests(TestCase):
    def test_prawidlowe_blogi(self):
        uzytkownik = Uzytkownik(username="jan", password="scisletajne", email="jan@o2.pl")
        uzytkownik.save()
        blog = Blog(nazwa="Blog", autor=uzytkownik)
        blog.save()
        self.assertEqual(blog.autor == None, False)
        self.assertEqual(blog.nazwa == None, False)

class UzytkownikTests(TestCase):
    def test_prawidlowi_uzytkownicy(self):
        uzytkownik = Uzytkownik(username="jan", password="scisletajne", email="jan@o2.pl")
        uzytkownik.save()
        self.assertEqual(len(uzytkownik.username) > 0, True)
        self.assertEqual(len(uzytkownik.password) > 0, True)
        self.assertEqual(len(uzytkownik.email) > 0, True)