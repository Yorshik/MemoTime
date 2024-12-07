import django.conf
import django.contrib.auth
import django.core.validators
import django.db.models
import django.db.models.signals
import django.dispatch
import django.utils
import django.utils.timezone
from django.utils.translation import gettext_lazy as _

__all__ = ()


User = django.contrib.auth.get_user_model()


class PersonalData(django.db.models.Model):
    user = django.db.models.ForeignKey(
        User,
        verbose_name=_("пользователь"),
        on_delete=django.db.models.DO_NOTHING,
        help_text=_("Пользователь, отправивший фидбек"),
        blank=True,
        null=True,
    )
    name = django.db.models.TextField(
        _("имя"),
        max_length=100,
        help_text=_("Автор фидбэка"),
        blank=True,
        null=True,
    )
    mail = django.db.models.EmailField(
        _("почта"),
        help_text=_("Почта автора фидбэка"),
        max_length=200,
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.name[:15]


class Feedback(django.db.models.Model):
    class StatusChoices(django.db.models.TextChoices):
        RECEIVED = "получено", _("получено")
        IN_PROCESSING = "в обработке", _("в обработке")
        RESPONSE_GIVEN = "ответ дан", _("ответ дан")

    status = django.db.models.CharField(
        _("статус обработки"),
        blank=False,
        help_text=_("Статус обработки"),
        choices=StatusChoices.choices,
        default=StatusChoices.RECEIVED,
        max_length=20,
    )
    text = django.db.models.TextField(
        _("текст"),
        max_length=10240,
        help_text=_("Содержание фидбэка"),
        blank=False,
        null=False,
    )
    created_on = django.db.models.DateTimeField(
        _("создан"),
        auto_now_add=True,
        help_text=_("Дата создания фидбэка"),
    )
    personal_data = django.db.models.OneToOneField(
        to=PersonalData,
        default=None,
        null=True,
        on_delete=django.db.models.PROTECT,
        verbose_name=_("персональные данные"),
        help_text=_("Персональные данные автора"),
        related_name="feedback",
    )

    class Meta:
        verbose_name = _("фидбэк")
        verbose_name_plural = _("фидбэки")

    def __str__(self):
        return self.personal_data.name[:15]


class FeedbackFile(django.db.models.Model):
    def get_upload_path(self, filename):
        return f"uploads/{self.feedback_id}/{filename}"

    file = django.db.models.FileField(
        _("файл"),
        upload_to=get_upload_path,
        help_text=_("Прикрепленный файл"),
    )
    feedback = django.db.models.ForeignKey(
        to=Feedback,
        on_delete=django.db.models.CASCADE,
        related_name="files",
        help_text=_("Ссылка на связанный фидбек, к которому прикреплен файл"),
    )

    class Meta:
        verbose_name = _("файл фидбэка")
        verbose_name_plural = _("файлы фидбэка")

    def __str__(self):
        return f"id: {self.pk}"


@django.dispatch.receiver(django.db.models.signals.pre_save, sender=Feedback)
def ensure_timestamps_feedback(sender, instance, **kwargs):
    if not instance.created_on:
        instance.created_on = django.utils.timezone.now()


class StatusLog(django.db.models.Model):
    user = django.db.models.ForeignKey(
        User,
        verbose_name=_("пользователь"),
        on_delete=django.db.models.DO_NOTHING,
        help_text=_("Пользователь, изменивший статус"),
        db_column="User_key",
        related_name="status_logs",
    )
    feedback = django.db.models.ForeignKey(
        Feedback,
        verbose_name=_("фидбэк"),
        on_delete=django.db.models.CASCADE,
        help_text=_("Фидбэк, для которого изменён статус"),
        related_name="status_logs",
    )
    timestamp = django.db.models.DateTimeField(
        _("время"),
        auto_now_add=True,
        help_text=_("Время изменения статуса"),
    )
    from_status = django.db.models.CharField(
        _("из статуса"),
        max_length=20,
        db_column="from",
        help_text=_("Из какого статуса"),
    )
    to = django.db.models.CharField(
        _("в статус"),
        max_length=20,
        db_column="to",
        help_text=_("В какой статус"),
    )

    class Meta:
        verbose_name = _("лог изменения статуса")
        verbose_name_plural = _("логи изменения статусов")

    def __str__(self):
        return f"{self.feedback} ({self.from_status} → {self.to})"


@django.dispatch.receiver(django.db.models.signals.pre_save, sender=StatusLog)
def ensure_timestamps_statuslog(sender, instance, **kwargs):
    if not instance.timestamp:
        instance.timestamp = django.utils.timezone.now()
