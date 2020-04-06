import logging
logger = logging.getLogger(__name__)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import Http404
#from django.utils.http
from .models import Post, Uzytkownik, Blog, Komentarz, Historia, Kategoria
from .forms import RejestracjaForm, LogowanieForm, BlogForm, CommentForm, PostForm, OdblokujForm, WyszukiwarkaForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from django.core.exceptions import PermissionDenied
from datetime import datetime

def panel(request):
    queryset_list=Post.objects.active()
    if request.user.is_staff or request.user.is_supperuser:
        queryset_list=Post.objects.all()
    query=request.GET.get("q")
    if query:
        queryset_list=queryset_list.filter(
             Q(Autor_icontains=query)|
             Q(Tytul_icontains=query)
            ).distinct()
    paginator =Paginator(queryset_list,1)
    page_request_var="page"
    page=request.GET.get(page_request_var)
    try:
        queryset= paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset =paginator.page(paginator.num_pages)

    context={
        "object_list": queryset,
        "title":"List",
        "page_request_var": page_request_var,
        }
    return render(request, "polls/panel.html",context)


def post_list(request):
    lista_postow = Post.objects.all().order_by('-data')
    context = {'lista_postow' : lista_postow}
    return render(request, 'polls/post_list.html', context)

def post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        lista_komentarzy = Komentarz.objects.filter(post = post).order_by('-kiedy')
        if request.user.is_authenticated:
            try:
                wpis = Historia.objects.get(post=post, uzytkownik=request.user)
                wpis.data = datetime.now()
                wpis.licznik_odwiedzin = wpis.licznik_odwiedzin + 1
                wpis.save()
            except Historia.DoesNotExist:
                wpis = Historia()
                wpis.post = post
                wpis.uzytkownik = request.user
                if not post.haslo:
                    wpis.czy_odblokowany = True
                wpis.save()
            odblokowany = wpis.czy_odblokowany
        elif not post.haslo:
            odblokowany = True
        else:
            odblokowany = False
    except Post.DoesNotExist:
        raise Http404("Ten post nie istnieje")

    if request.method == 'POST':
        odblokowany = True
        wpis.save()
        form = CommentForm(request.POST)
        if form.is_valid():
            komentarz=form.save(commit=False)
            komentarz.post=post
            komentarz.kto=request.user
            komentarz.save()

    form = CommentForm()

    if odblokowany:
        if post.haslo:
            wpis.czy_odblokowany = False
            wpis.save()
        wyswietlenia = Historia.objects.filter(post=post)
        plusy = 0
        minusy = 0
        for wyswietlenie in wyswietlenia:
            if wyswietlenie.czy_plus:
                plusy = plusy + 1
            elif wyswietlenie.czy_minus:
                minusy = minusy + 1
        ocena = plusy + minusy
        plusy = plusy - minusy
        return render(request, 'polls/post.html', {'post': post, 'lista_komentarzy': lista_komentarzy, 'form': form, 'plusy': plusy, 'ocena': ocena, 'licznik_odwiedzin': wyswietlenia.count()})
    else:
        return redirect('odblokuj_post', post_id)

def odblokuj_post(request, post_id):
    if not request.user.is_authenticated:
        return redirect('logowanie')
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        raise Http404("Ten post nie istnieje")
    if post.haslo:
        haslo = None
        historia = Historia.objects.get(post=post_id, uzytkownik=request.user)
        if request.method == 'POST':
            form = OdblokujForm(request.POST)
            if form.is_valid():
                haslo = form.cleaned_data['haslo']
                if post.haslo == haslo:
                    historia.czy_odblokowany = True
                    historia.save()
                    return redirect('post', post_id)
                else:
                    return render(request, 'polls/odblokuj_post.html', {'post': post, 'form': form, 'invalid': True})
        else:
            form = OdblokujForm()
        return render(request, 'polls/odblokuj_post.html', {'post': post, 'form': form, 'invalid': False})
    else:
        return redirect('post', post_id)

def usun_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    if post.blog.autor == request.user:
        post.delete()
        return redirect('post_list')
    else:
        raise PermissionDenied
        return redirect('/')

def edytuj_post(request, post_id):
    template = 'polls/dodaj_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.blog.autor == request.user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES, instance=post)
            if form.is_valid():
                form.save()
                return redirect('post', post_id)
        else:
            form = PostForm(instance=post)
        context = {
            'form': form,
            'post': post,
        }
        return render(request, template, context)
    else:
        raise PermissionDenied
        return redirect('/')

def edytuj_bloga(request):
    if request.user.is_authenticated():
        try:
            twoj_blog = Blog.objects.get(autor=request.user)
        except Blog.DoesNotExist:
            return redirect('zaloz_bloga')
        template = 'polls/zaloz_bloga.html'
        if request.method == 'POST':
            form = BlogForm(request.POST, instance=twoj_blog)
            if form.is_valid():
                form.save()
                return redirect('blog', twoj_blog.nazwa)
        else:
            form = BlogForm(instance=twoj_blog)
        return render(request, template, {'form': form})
    else:
        return redirect('logowanie')

def historia_odwiedzanych(request):
    wpisy = Historia.objects.filter(uzytkownik=request.user).order_by('-data')
    lista_postow = list()
    for wpis in wpisy:
        lista_postow.append(wpis.post)
    return render(request, 'polls/historia.html', {'lista_postow': lista_postow, 'wpisy': wpisy})

def historia_plusowanych(request):
    wpisy = Historia.objects.filter(uzytkownik=request.user, czy_plus=True).order_by('-data')
    lista_postow = list()
    for wpis in wpisy:
        lista_postow.append(wpis.post)
    return render(request, 'polls/historia.html', {'lista_postow': lista_postow})

def historia_minusowanych(request):
    wpisy = Historia.objects.filter(uzytkownik=request.user, czy_minus=True).order_by('-data')
    lista_postow = list()
    for wpis in wpisy:
        lista_postow.append(wpis.post)
    return render(request, 'polls/historia.html', {'lista_postow': lista_postow})

def historia_komentarzy(request):
    lista_komentarzy = Komentarz.objects.filter(kto=request.user).order_by('-kiedy')
    return render(request, 'polls/historia_komentarzy.html', {'lista_komentarzy': lista_komentarzy})

def kontakt(request):
    return render(request, "polls/kontakt.html")

def uzytkownicy(request):
    lista_autorow = Uzytkownik.objects.order_by("username")
    return render(request, "polls/autorzy.html", {'lista_autorow': lista_autorow})

def blog_uzytkownika(request, uzytkownik_id):
    try:
        uzytkownik = Uzytkownik.objects.get(pk=uzytkownik_id)
        blog = Blog.objects.get(autor=uzytkownik)
        return redirect('blog', blog.nazwa)
    except Blog.DoesNotExist:
        return render(request,'polls/brak_postow.html')
    except Uzytkownik.DoesNotExist:
        raise Http404("Taki uzytkownik nie istnieje")


def zaloz_bloga(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = BlogForm(request.POST)
            if form.is_valid():
                blog = form.save(commit=False)
                blog.nazwa = form.cleaned_data['nazwa']
                blog.motto = form.cleaned_data['motto']
                blog.autor = request.user
                blog.save()
                return redirect('/')
        else:
            form = BlogForm()
        return render(request, 'polls/zaloz_bloga.html', {'form': form})
    else:
        return redirect('/logowanie')

def blog(request, blog_nazwa):
    try:
        blog = Blog.objects.get(nazwa=blog_nazwa)
        lista_postow = Post.objects.filter(blog=blog).order_by('-data')
    except Blog.DoesNotExist:
        raise Http404("Taki blog nie istnieje")
    except:
        lista_postow = None
    return render(request, 'polls/blog.html', {'blog': blog, 'lista_postow': lista_postow})

def dodaj_post(request):
    try:
        twoj_blog = Blog.objects.get(autor=request.user)
    except Blog.DoesNotExist:
        return redirect('zaloz_bloga')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.blog = twoj_blog
            post.zawartosc = form.cleaned_data['zawartosc']
            post.tytul = form.cleaned_data['tytul']
            post.kategoria = form.cleaned_data['kategoria']
            post.haslo = form.cleaned_data['haslo']
            try:
                post.obrazek = request.FILES['obrazek']
            except:
                post.obrazek = None
            post.save()
            wpis = Historia()
            wpis.uzytkownik = request.user
            wpis.czy_plus = True
            wpis.post = post
            wpis.czy_odblokowany = True
            wpis.save()
            return redirect('post', post.id)
    else:
        form = PostForm()
    return render(request, 'polls/dodaj_post.html', {'twoj_blog': twoj_blog, 'form': form})

def plusuj_post(request, post_id):
    if request.user.is_authenticated:
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Http404("Taki post nie istnieje")
        wpis = Historia.objects.get(uzytkownik=request.user, post=post)
        if wpis.czy_minus:
            wpis.czy_minus = False
        wpis.czy_plus = True
        wpis.save()
        return redirect('post', post_id)

def minusuj_post(request, post_id):
    if request.user.is_authenticated:
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Http404("Taki post nie istnieje")
        wpis = Historia.objects.get(uzytkownik=request.user, post=post)
        if wpis.czy_plus:
            wpis.czy_plus = False
        wpis.czy_minus = True
        wpis.save()
        return redirect('post', post_id)

def usun_komentarz(request, komentarz_id):
    komentarz = Komentarz.objects.get(pk=komentarz_id)
    post = komentarz.post
    if komentarz.kto == request.user:
        komentarz.delete()
    return redirect('post', post.id)

def rejestracja(request):
    if request.method == 'POST':
        form = RejestracjaForm(request.POST)
        if form.is_valid():
            uzytkownik = form.save(commit=False)
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            uzytkownik.set_password(password)
            uzytkownik.username = username
            uzytkownik.email = email
            uzytkownik.is_active = False
            uzytkownik.save()
            current_site = get_current_site(request)
            message = render_to_string('polls/acc_active_email.html', {
                'user': uzytkownik,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(uzytkownik.pk)).decode(),
                'token': account_activation_token.make_token(uzytkownik),
            })
            mail_subject =['Rejestarcja - Aktywacja - Blogosfera - Potwierdzenie']
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return render(request, 'polls/register.html', {'aktywacja': True})
    else:
        form = RejestracjaForm()
    return render(request, 'polls/register.html', {'form': form})

def aktywacja(request, uidb64, token):
    try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = Uzytkownik.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
    if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            # return redirect('home')
            return HttpResponse('Dziekujemy za rejestracje. Teraz konto jest juz aktywne, mozesz sie zalogowac i blogowac na sferze bez blokad.')
    else:
            return HttpResponse('Link aktywacji padniety!')

def logowanie(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = LogowanieForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                uzytkownik = authenticate(username=username, password=password)
                if uzytkownik is not None:
                    if uzytkownik.is_active:
                        login(request, uzytkownik)
                        return redirect('/')
                else:
                    return render(request, 'polls/logowanie.html', {'form': form, 'invalid': True})
        else:
            form = LogowanieForm()
        return render(request, 'polls/logowanie.html', {'form': form})
    else:
        return redirect('/')

def wyloguj(request):
    logout(request)
    return redirect('/')

def kategoria(request, kategoria_nazwa):
    try:
        kategoria = Kategoria.objects.get(nazwa=kategoria_nazwa)
    except Kategoria.DoesNotExist:
        raise Http404("Nie ma takiej kategorii")
    lista_postow = Post.objects.filter(kategoria=kategoria).order_by('-data')
    return render(request, 'polls/kategoria.html', {'kategoria': kategoria, 'lista_postow': lista_postow})

def szukaj(request):
    if request.method == 'POST':
        form = WyszukiwarkaForm(request.POST)
        if form.is_valid():
            slowa_kluczowe = form.cleaned_data['slowa_kluczowe']
            blog = form.cleaned_data['blog']
            kategoria = form.cleaned_data['kategoria']
            if not slowa_kluczowe:
                slowa_kluczowe = " "
            if not kategoria:
                kategoria = " "
            if not blog:
                blog = " "
            return redirect('wyniki_wyszukiwania', slowa_kluczowe, blog, kategoria)
    else:
        form = WyszukiwarkaForm()
    return render(request, 'polls/wyszukiwarka.html', {'form': form})

def wyniki_wyszukiwania(request, slowa_kluczowe, blog, kategoria):
    wyniki = Post.objects.all()
    if not slowa_kluczowe == " ":
        lista_slow = slowa_kluczowe.split()
        for slowo in lista_slow:
            wyniki = wyniki.filter(zawartosc__contains=slowo)
            wyniki = wyniki | Post.objects.filter(tytul__contains=slowo)
    if not blog == " ":
        try:
            znaleziony_blog = Blog.objects.filter(nazwa__contains=blog)
            wyniki = wyniki.filter(blog=znaleziony_blog)
        except Blog.DoesNotExist:
            wyniki = None
    if not kategoria == " ":
        try:
            znaleziona_kategoria = Kategoria.objects.filter(nazwa=kategoria)
            wyniki = wyniki.filter(kategoria=znaleziona_kategoria)
        except Kategoria.DoesNotExist:
            wyniki = None
    return render(request, 'polls/wyniki_wyszukiwania.html', {'lista_postow': wyniki})