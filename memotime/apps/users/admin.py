import django.contrib.admin

import apps.users.models

__all__ = ()

django.contrib.admin.site.register(apps.users.models.User)
