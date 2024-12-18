import django.urls
import django.views.generic

import apps.homepage.views

__all__ = ()


app_name = "homepage"


class FloatConverter:
    regex = r"[0-9]+(\.[0-9]+)?"

    def to_python(self, value):
        return float(value)

    def to_url(self, value):
        return str(value)


django.urls.register_converter(FloatConverter, "myfloat")

urlpatterns = [
    django.urls.path("", apps.homepage.views.HomeView.as_view(), name="homepage"),
    django.urls.path(
        "blocked/<myfloat:expires_at>/",
        apps.homepage.views.BlockedView.as_view(),
        name="blocked",
    ),
]
