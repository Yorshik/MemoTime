import django.contrib
import django.contrib.admin
import django.contrib.auth
import django.contrib.auth.admin
import django.contrib.auth.models

import apps.users.models

__all__ = ()


class UserAdmin(django.contrib.auth.admin.UserAdmin):
    pass


django.contrib.admin.site.unregister(django.contrib.auth.models.User)
django.contrib.admin.site.register(apps.users.models.User, UserAdmin)
