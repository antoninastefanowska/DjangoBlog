from polls.models import Post, Historia
from django import template

register = template.Library()

class PolecanyPost(object):
    post = Post()
    waga = 0
    def __init__(self, post):
        self.post = post
    def zwieksz_wage(self):
        self.waga = self.waga + 1

@register.inclusion_tag('polls/templatetags/polecane.html', takes_context=True)
def polecane(context):
    uzytkownik = context['request'].user
    lista_polecanych = list()
    brak_polubien = False
    brak_nowych = False
    if uzytkownik.is_authenticated:
        polecane = list()
        polubione = Historia.objects.filter(uzytkownik=uzytkownik, czy_plus=True)
        if polubione.count() > 0:
            for polubiony_wpis in polubione:
                post = polubiony_wpis.post
                cudze_wpisy = Historia.objects.filter(post=post)
                cudze_wpisy = cudze_wpisy.exclude(uzytkownik=uzytkownik, czy_odblokowany=False)
                for cudzy_wpis in cudze_wpisy:
                    podobny_uzytkownik = cudzy_wpis.uzytkownik
                    podobne_wpisy = Historia.objects.filter(uzytkownik=podobny_uzytkownik, czy_plus=True)
                    for podobny_wpis in podobne_wpisy:
                        podobny_post = podobny_wpis.post
                        try:
                            Historia.objects.get(uzytkownik=uzytkownik, post=podobny_post)
                        except Historia.DoesNotExist:
                            polecany = podobny_post
                            temp = list(filter(lambda x: x.post == polecany, polecane))
                            if len(temp) > 0:
                                istniejacy = temp[0]
                                istniejacy.zwieksz_wage()
                            else:
                                istniejacy = PolecanyPost(polecany)
                                istniejacy.zwieksz_wage()
                                polecane.append(istniejacy)
            polecane = sorted(polecane, key=lambda x: x.waga, reverse=True)
            i = 0
            for p in polecane:
                if i > 5:
                    break
                lista_polecanych.append(p.post)
                i = i + 1
            if len(polecane) == 0:
                brak_nowych = True
        else:
            brak_polubien = True
    return {'lista_polecanych': lista_polecanych, 'brak_polubien': brak_polubien, 'brak_nowych': brak_nowych, 'uzytkownik': uzytkownik}