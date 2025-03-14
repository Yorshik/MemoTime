import django.contrib.auth.models
import django.db.models
import django.utils.timezone
from django.utils.translation import gettext_lazy as _
import pytz

import apps.core.models
import apps.users.email_normalizer
import apps.users.managers

__all__ = ()

normalizer = apps.users.email_normalizer.EmailNormalizer()


class User(django.contrib.auth.models.AbstractUser, apps.core.models.BaseImageModel):
    TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.common_timezones]

    objects = apps.users.managers.UserManager()

    email = django.db.models.EmailField(
        _("email address"),
        unique=True,
        null=False,
        blank=False,
        help_text=_("Unique email address"),
    )
    timezone = django.db.models.CharField(
        _("timezone"),
        max_length=50,
        choices=TIMEZONE_CHOICES,
        default=TIMEZONE_CHOICES[-1],
        help_text=_("User's time zone"),
    )
    subscription_end_date = django.db.models.DateTimeField(
        _("subscription end date"),
        null=True,
        default=None,
        blank=True,
        help_text=_("Date when the subscription ends and is deactivated"),
    )
    is_email_subscribed = django.db.models.BooleanField(
        _("email notifications"),
        default=True,
        blank=True,
        help_text=_("Whether email notifications are enabled"),
    )
    is_telegram_subscribed = django.db.models.BooleanField(
        _("Telegram notifications"),
        default=True,
        blank=True,
        help_text=_("Whether Telegram notifications are enabled"),
    )

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


class Group(django.contrib.auth.models.Group):
    creator = django.db.models.ForeignKey(
        User,
        on_delete=django.db.models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_groups",
        verbose_name=_("creator"),
    )

    class Meta:
        verbose_name = _("group")
        verbose_name_plural = _("groups")

    def __str__(self):
        max_length = 15
        if len(self.name) > max_length:
            return self.name[: max_length - 3] + "..."

        return self.name
