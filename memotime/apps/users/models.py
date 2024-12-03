import sys
import uuid

import django.contrib.auth.models
import django.db.models
import pytz

import apps.users.email_normalizer

__all__ = ()

DjangoUser = django.contrib.auth.get_user_model()

if "makemigrations" not in sys.argv and "migrate" not in sys.argv:
    DjangoUser._meta.get_field(
        "email",
    )._unique = True

normalizer = apps.users.email_normalizer.EmailNormalizer()


class User(django.contrib.auth.models.AbstractUser, apps.core.models.BaseImageModel):
    TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.common_timezones]

    objects = apps.users.managers.UserManager()

    def upload_to_path(self, filename):
        extension = filename.split(".")[-1]
        new_filename = f"{uuid.uuid4()}.{extension}"
        return f"uploads/users/avatars/{uuid.uuid4()}/{new_filename}"

    timezone = django.db.models.CharField(choices=TIMEZONE_CHOICES)
    subscription_end_date = django.db.models.DateTimeField(
        verbose_name="дата окончания подписки",
        help_text="дата окончания подписки, после чего она отключается",
    )
    is_email_subscribed = django.db.models.BooleanField(
        verbose_name="почтовые уведомления",
        help_text="подключены ли уведомления на почту",
    )
    is_telegram_subscribed = django.db.models.BooleanField(
        verbose_name="уведомления в Телеграм",
        help_text="подключены ли уведомления в Телеграм",
    )
