import django.views.generic


class HomeView(django.views.generic.TemplateView):
    template_name = "homepage/homepage.html"


__all__ = ()
