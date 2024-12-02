import django.conf
import django.contrib.admin
import django.urls

import apps.homepage.urls

urlpatterns = [
    django.urls.path("", django.urls.include(apps.homepage.urls)),
    django.urls.path("admin/", django.contrib.admin.site.urls),
]

if django.conf.settings.DEBUG:
    urlpatterns.append(
        django.urls.path("__debug__", django.urls.include("debug_toolbar.urls")),
    )
