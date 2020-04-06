from polls.models import Kategoria
from django import template

register = template.Library()

@register.inclusion_tag('polls/templatetags/kategorie.html')
def kategorie():
    lista_kategorii = Kategoria.objects.all
    return {'lista_kategorii': lista_kategorii}