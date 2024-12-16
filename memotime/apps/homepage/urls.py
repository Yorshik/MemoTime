import django.urls
import django.views.generic

import apps.homepage.views

app_name = "homepage"

urlpatterns = [
    django.urls.path("", apps.homepage.views.HomeView.as_view(), name="homepage"),
    django.urls.path(
        "blocked/<expires_at>/",
        apps.homepage.views.BlockedView.as_view(),
        name="blocked",
    ),
]
