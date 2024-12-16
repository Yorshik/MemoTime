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
        _("email"),
        unique=True,
        null=False,
        blank=False,
        help_text=_("уникальный адрес электронной почты"),
    )
    timezone = django.db.models.CharField(
        _("часовой пояс"),
        max_length=50,
        choices=TIMEZONE_CHOICES,
        default=TIMEZONE_CHOICES[-1],
        help_text=_("Часовой пояс пользователя"),
    )
    subscription_end_date = django.db.models.DateTimeField(
        _("дата окончания подписки"),
        null=True,
        default=None,
        help_text=_("дата окончания подписки, после чего она отключается"),
    )
    is_email_subscribed = django.db.models.BooleanField(
        _("почтовые уведомления"),
        default=True,
        help_text=_("подключены ли уведомления на почту"),
    )
    is_telegram_subscribed = django.db.models.BooleanField(
        _("уведомления в Телеграм"),
        default=True,
        help_text=_("подключены ли уведомления в Телеграм"),
    )

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
