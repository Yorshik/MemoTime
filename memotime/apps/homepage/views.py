import django.views.generic


class HomeView(django.views.generic.TemplateView):
    template_name = "homepage/index.html"


__all__ = ()
