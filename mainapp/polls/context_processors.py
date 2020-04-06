from polls.models import Blog

def twoj_blog(request):
    uzytkownik = request.user
    if uzytkownik.is_authenticated:
        try:
            blog = Blog.objects.get(autor=uzytkownik)
        except Blog.DoesNotExist:
            blog = None
        return {'twoj_blog': blog, 'uzytkownik': uzytkownik}
    else:
        return {'twoj_blog': None, 'uzytkownik': uzytkownik}