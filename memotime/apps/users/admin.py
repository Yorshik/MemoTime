from django.contrib import admin
import django.contrib.admin

import apps.users.models
from apps.users.models import Group

__all__ = ()


django.contrib.admin.site.register(apps.users.models.User)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "creator")
