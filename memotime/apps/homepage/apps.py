import django.apps
from django.utils.translation import gettext_lazy as _


class HomepageConfig(django.apps.AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.homepage"
    verbose_name = _("Домашнаяя страница")


__all__ = ()
