import django.urls

import apps.homepage.views

__all__ = ()


app_name = "homepage"


urlpatterns = [
    django.urls.path("", apps.homepage.views.HomeView.as_view(), name="homepage"),
]
