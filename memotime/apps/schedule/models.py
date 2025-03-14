import django.contrib.auth
import django.db.models
import django.utils.timezone
from django.utils.translation import gettext_lazy as _

from apps.schedule.managers import (
    EventManager,
    ScheduleManager,
    TimeScheduleManager,
)
import apps.users.models

__all__ = ()

User = django.contrib.auth.get_user_model()


class Event(django.db.models.Model):
    class EventType(django.db.models.TextChoices):
        SUBJECT = "subject", _("Subject")
        CLUB = "club", _("Club")
        EVENT = "event", _("Event")

    disposable = django.db.models.BooleanField(
        _("disposable"),
        default=True,
        help_text=_("Determines if the note is used only once"),
    )
    heading = django.db.models.CharField(
        _("heading"),
        max_length=128,
        help_text=_("Note heading"),
    )
    description = django.db.models.TextField(
        _("description"),
        help_text=_("Event description"),
        max_length=10000,
        blank=True,
    )
    event_type = django.db.models.CharField(
        _("type"),
        max_length=20,
        choices=EventType.choices,
        help_text=_("Event type"),
    )
    user = django.db.models.ForeignKey(
        User,
        on_delete=django.db.models.CASCADE,
        related_name="events",
        help_text=_("User"),
    )

    objects = EventManager()

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")

    def __str__(self):
        max_length = 25
        if len(self.name) > max_length:
            return self.name[: max_length - 3] + "..."

        return self.name


class Schedule(django.db.models.Model):
    user = django.db.models.ForeignKey(
        User,
        on_delete=django.db.models.CASCADE,
        related_name="schedules",
        help_text=_("User"),
    )
    is_static = django.db.models.BooleanField(
        _("static"),
        default=True,
        help_text=_(
            "Determines if the schedule alternates (if False, the 'even' field in"
            " TimeSchedule is used)",
        ),
    )

    objects = ScheduleManager()

    class Meta:
        verbose_name = _("schedule")
        verbose_name_plural = _("schedules")

    def __str__(self):
        max_length = 45
        result = f"{self.user} - {self.start_date} - {self.expiration_date}"
        if len(result) > max_length:
            return result[: max_length - 3] + "..."

        return result


class TimeSchedule(django.db.models.Model):
    class DayNumber(django.db.models.IntegerChoices):
        MONDAY = 1, _("Monday")
        TUESDAY = 2, _("Tuesday")
        WEDNESDAY = 3, _("Wednesday")
        THURSDAY = 4, _("Thursday")
        FRIDAY = 5, _("Friday")
        SATURDAY = 6, _("Saturday")
        SUNDAY = 7, _("Sunday")

        __empty__ = _("Day")

    schedule = django.db.models.ForeignKey(
        Schedule,
        on_delete=django.db.models.CASCADE,
        related_name="timeschedules",
        help_text=_("Schedule"),
    )
    event = django.db.models.ForeignKey(
        Event,
        on_delete=django.db.models.CASCADE,
        related_name="timeschedules",
        help_text=_("Event"),
    )
    even = django.db.models.BooleanField(
        _("even week"),
        help_text=_("Even/odd week for the subject"),
    )
    user = django.db.models.ForeignKey(
        User,
        on_delete=django.db.models.CASCADE,
        related_name="timeschedules",
        help_text=_("User"),
    )
    day_number = django.db.models.IntegerField(
        _("day of the week"),
        choices=DayNumber.choices,
        help_text=_("Day of the week (1-7)"),
    )
    time_start = django.db.models.TimeField(
        _("start time"),
        null=True,
        help_text=_("Start time of the subject/event"),
    )
    time_end = django.db.models.TimeField(
        _("end time"),
        null=True,
        help_text=_("End time of the subject/event"),
    )
    objects = TimeScheduleManager()

    class Meta:
        verbose_name = _("time schedule")
        verbose_name_plural = _("time schedules")

    def __str__(self):
        max_length = 45
        result = f"{self.event} - {self.time_start} - {self.time_end}"
        if len(result) > max_length:
            return result[: max_length - 3] + "..."

        return result
