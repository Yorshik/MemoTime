from django.contrib import admin
import django.contrib.admin
from django.utils.translation import gettext_lazy as _

import apps.users.models
from apps.users.models import Group

__all__ = ()

django.contrib.admin.site.register(apps.users.models.User)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name_truncated", "creator_truncated")

    def name_truncated(self, obj):
        max_length = 15
        if len(obj.name) > max_length:
            return obj.name[: max_length - 3] + "..."

        return obj.name

    name_truncated.short_description = _(Group.name.field.verbose_name.capitalize())
    name_truncated.admin_order_field = Group.name.field.name

    def creator_truncated(self, obj):
        max_length = 15
        if obj.creator:
            username = obj.creator.get_username()
            if len(username) > max_length:
                return username[: max_length - 3] + "..."

            return username

        return "-"

    creator_truncated.short_description = _("Creator")
    creator_truncated.admin_order_field = "creator__username"
