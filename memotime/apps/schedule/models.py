import django.contrib.auth
import django.db.models
import django.utils.timezone
from django.utils.translation import gettext_lazy as _

from apps.schedule.managers import (
    EventManager,
    NoteManager,
    ScheduleManager,
    TeacherManager,
    TimeScheduleManager,
)
import apps.users.models

__all__ = ()

User = django.contrib.auth.get_user_model()


class Note(django.db.models.Model):
    disposable = django.db.models.BooleanField(
        _("disposable"),
        default=True,
        help_text=_("Determines if the note is used only once"),
    )
    global_note = django.db.models.BooleanField(
        _("global"),
        default=False,
        help_text=_("Global note"),
    )
    heading = django.db.models.CharField(
        _("heading"),
        max_length=128,
        help_text=_("Note heading"),
    )
    description = django.db.models.TextField(
        _("description"),
        help_text=_("Note description"),
        max_length=10000,
        blank=True,
    )
    user = django.db.models.ForeignKey(
        User,
        on_delete=django.db.models.CASCADE,
        related_name="notes",
        help_text=_("User"),
    )

    objects = NoteManager()

    class Meta:
        verbose_name = _("note")
        verbose_name_plural = _("notes")

    def __str__(self):
        max_length = 25
        if len(self.heading) > max_length:
            return self.heading[: max_length - 3] + "..."

        return self.heading


class Teacher(django.db.models.Model):
    name = django.db.models.CharField(
        _("name"),
        max_length=255,
        help_text=_("Teacher's name"),
    )
    user = django.db.models.ForeignKey(
        User,
        on_delete=django.db.models.CASCADE,
        related_name="teachers",
        help_text=_("User"),
    )

    objects = TeacherManager()

    class Meta:
        verbose_name = _("teacher")
        verbose_name_plural = _("teachers")

    def __str__(self):
        max_length = 25
        if len(self.name) > max_length:
            return self.name[: max_length - 3] + "..."

        return self.name


class Event(django.db.models.Model):
    class EventType(django.db.models.TextChoices):
        SUBJECT = "subject", _("Subject")
        CLUB = "club", _("Club")
        EVENT = "event", _("Event")

    class EventPriority(django.db.models.TextChoices):
        HIGH = "high", _("High")
        MEDIUM = "medium", _("Medium")
        LOW = "low", _("Low")

    name = django.db.models.CharField(
        _("name"),
        max_length=255,
        help_text=_("Event name"),
    )
    custom_name = django.db.models.CharField(
        _("custom name"),
        max_length=255,
        help_text=_("Custom event name"),
        blank=True,
    )
    description = django.db.models.TextField(
        _("description"),
        help_text=_("Event description"),
        max_length=10000,
        blank=True,
    )
    teacher = django.db.models.ForeignKey(
        Teacher,
        on_delete=django.db.models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        help_text=_("Teacher"),
    )
    event_type = django.db.models.CharField(
        _("type"),
        max_length=20,
        choices=EventType.choices,
        help_text=_("Event type"),
    )
    priority = django.db.models.CharField(
        _("priority"),
        max_length=20,
        choices=EventPriority.choices,
        help_text=_(
            "If high, the event is displayed over the subject. If medium priority,"
            " conflicts may arise. If low, the subject overlaps the event.",
        ),
    )
    user = django.db.models.ForeignKey(
        User,
        on_delete=django.db.models.CASCADE,
        related_name="events",
        help_text=_("User"),
    )
    notes = django.db.models.ForeignKey(
        Note,
        on_delete=django.db.models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        help_text=_("Notes related to the event"),
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
    group = django.db.models.ForeignKey(
        apps.users.models.Group,
        on_delete=django.db.models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedules",
        verbose_name=_("group"),
    )
    is_static = django.db.models.BooleanField(
        _("static"),
        default=True,
        help_text=_(
            "Determines if the schedule alternates (if False, the 'even' field in"
            " TimeSchedule is used)",
        ),
    )
    start_date = django.db.models.DateField(
        _("start date"),
        default=django.utils.timezone.now,
        help_text=_("Schedule start date"),
    )
    expiration_date = django.db.models.DateField(
        _("expiration date"),
        null=True,
        default=None,
        blank=True,
        help_text=_("Schedule expiration date"),
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
    time_start = django.db.models.TimeField(
        _("start time"),
        help_text=_("Start time of the subject/event"),
    )
    time_end = django.db.models.TimeField(
        _("end time"),
        help_text=_("End time of the subject/event"),
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
