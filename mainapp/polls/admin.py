from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

# Register your models here.

from .models import Uzytkownik
from .models import Blog
from .models import Post
from .models import Kategoria
from .models import Komentarz
from .models import Historia

from .forms import RejestracjaForm

admin.site.register(Blog)
admin.site.register(Post)
admin.site.register(Kategoria)
admin.site.register(Komentarz)
admin.site.register(Historia)

class UzytkownikAdmin(UserAdmin):
    add_form = RejestracjaForm
    model = Uzytkownik
    list_display = ['username']

admin.site.register(Uzytkownik, UzytkownikAdmin)