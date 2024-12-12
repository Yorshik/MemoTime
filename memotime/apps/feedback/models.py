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
        verbose_name=_("user"),
        on_delete=django.db.models.DO_NOTHING,
        help_text=_("User who submitted the feedback"),
        blank=True,
        null=True,
    )
    name = django.db.models.TextField(
        _("name"),
        max_length=100,
        help_text=_("Feedback author"),
        blank=True,
        null=True,
    )
    email = django.db.models.EmailField(
        _("email"),
        help_text=_("Feedback author's email"),
        max_length=200,
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.name[:15]


class Feedback(django.db.models.Model):
    class StatusChoices(django.db.models.TextChoices):
        RECEIVED = "received", _("received")
        IN_PROCESSING = "in processing", _("in processing")
        RESPONSE_GIVEN = "response given", _("response given")

    status = django.db.models.CharField(
        _("processing status"),
        blank=False,
        help_text=_("Processing status"),
        choices=StatusChoices.choices,
        default=StatusChoices.RECEIVED,
        max_length=20,
    )
    text = django.db.models.TextField(
        _("text"),
        max_length=10240,
        help_text=_("Feedback content"),
        blank=False,
        null=False,
    )
    created_on = django.db.models.DateTimeField(
        _("created"),
        auto_now_add=True,
        help_text=_("Date of feedback creation"),
    )
    personal_data = django.db.models.OneToOneField(
        to=PersonalData,
        default=None,
        null=True,
        on_delete=django.db.models.PROTECT,
        verbose_name=_("personal data"),
        help_text=_("Author's personal data"),
        related_name="feedback",
    )

    class Meta:
        verbose_name = _("feedback")
        verbose_name_plural = _("feedbacks")

    def __str__(self):
        return self.personal_data.name[:15]


@django.dispatch.receiver(django.db.models.signals.pre_save, sender=Feedback)
def ensure_timestamps_feedback(sender, instance, **kwargs):
    if not instance.created_on:
        instance.created_on = django.utils.timezone.now()


class StatusLog(django.db.models.Model):
    user = django.db.models.ForeignKey(
        User,
        verbose_name=_("user"),
        on_delete=django.db.models.DO_NOTHING,
        help_text=_("User who changed the status"),
        db_column="User_key",
        related_name="status_logs",
    )
    feedback = django.db.models.ForeignKey(
        Feedback,
        verbose_name=_("feedback"),
        on_delete=django.db.models.CASCADE,
        help_text=_("Feedback for which the status was changed"),
        related_name="status_logs",
    )
    timestamp = django.db.models.DateTimeField(
        _("time"),
        auto_now_add=True,
        help_text=_("Time of status change"),
    )
    from_status = django.db.models.CharField(
        _("from status"),
        max_length=20,
        db_column="from",
        help_text=_("From which status"),
    )
    to = django.db.models.CharField(
        _("to status"),
        max_length=20,
        db_column="to",
        help_text=_("To which status"),
    )

    class Meta:
        verbose_name = _("status change log")
        verbose_name_plural = _("status change logs")

    def __str__(self):
        return f"{self.feedback} ({self.from_status} → {self.to})"


@django.dispatch.receiver(django.db.models.signals.pre_save, sender=StatusLog)
def ensure_timestamps_statuslog(sender, instance, **kwargs):
    if not instance.timestamp:
        instance.timestamp = django.utils.timezone.now()
