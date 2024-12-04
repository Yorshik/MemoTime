import django.contrib
import django.contrib.admin
import django.contrib.auth
import django.contrib.auth.admin
import django.contrib.auth.models

import apps.users.models

__all__ = ()


django.contrib.admin.site.register(apps.users.models.User)
