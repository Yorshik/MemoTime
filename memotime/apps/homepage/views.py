import django.views.generic

__all__ = ()


class HomeView(django.views.generic.TemplateView):
    template_name = "homepage/index.html"
