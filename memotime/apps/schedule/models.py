import django.contrib.auth
import django.db.models
from django.utils.translation import gettext_lazy as _

__all__ = ()


class Schedule(django.db.models.Model):
    user = django.db.models.ForeignKey(django.contrib.auth.get_user_model(), on_delete=django.db.models.CASCADE, verbose_name=_("user"), help_text=_("user, who owns this schedule"), related_name="schedule", related_query_name="schedules")
    start_date = django.db.models.DateField(verbose_name=_("schedule start date"), help_text=_("the day, from which this schedule is active"))
    expiration_date = django.db.models.DateField(verbose_name=_("schedule expiration date"), help_text=_("the day, when schedule will be destroyed"))

    class Meta:
        verbose_name = _("schedule")
        verbose_name_plural = _("schedules")


class DaySchedule(django.db.models.Model):
    DAY_NUMBER_CHOICES = (
        ("1", _("Monday")),
        ("2", _("Tuesday")),
        ("3", _("Wednesday")),
        ("4", _("Thursday")),
        ("5", _("Friday")),
        ("6", _("Saturday")),
        ("7", _("Sunday")),
    )
    user = django.db.models.ForeignKey(django.contrib.auth.get_user_model(), on_delete=django.db.models.CASCADE, verbose_name=_("user"), help_text=_("user, who owns this day schedule"), related_name="day_schedule", related_query_name="day_schedules")
    day_number = django.db.models.CharField(max_length=1, choices=DAY_NUMBER_CHOICES)
    schedule = django.db.models.ForeignKey(Schedule, on_delete=django.db.models.CASCADE, related_name="day_schedule", related_query_name="day_schedules", verbose_name=_("schedule"), help_text=_("main schedule"))

    class Meta:
        verbose_name = _("day schedule")
        verbose_name_plural = _("day schedules")


class TimeSchedule(django.db.models.Model):
    user = django.db.models.ForeignKey(django.contrib.auth.get_user_model(), on_delete=django.db.models.CASCADE, verbose_name=_("user"), help_text=_("user, who owns this day schedule"), related_name="time_schedule", related_query_name="time_schedules")
    time_start = django.db.models.DateTimeField(verbose_name=_("start time"), help_text=_("time when the day starts"))
    time_end = django.db.models.DateTimeField(verbose_name=_("end time"), help_text=_("time when the day ends"))
    even = django.db.models.BooleanField(verbose_name=_("even week"), help_text=_("shows whether week is even or odd"))

    class Meta:
        verbose_name = _("time schedule")
        verbose_name_plural = _("time schedules")


class Event(django.db.models.Model):
    EVENT_TYPE_CHOICES = (
        ("subject", _("subject")),
        ("club", _("after-school activity")),
        ("relax", _("relax")),
    )

    user = django.db.models.ForeignKey(django.contrib.auth.get_user_model(), on_delete=django.db.models.CASCADE, verbose_name=_("user"), help_text=_("user, who owns this day schedule"), related_name="event", related_query_name="events")
    name = django.db.models.CharField(max_length=150, verbose_name=_("name"), help_text=_("name of the event"))
    custom_name = django.db.models.CharField(max_length=150, verbose_name=_("custom name"), help_text=_("custom name of the event"))
    event_type = django.db.models.CharField(max_length=20, db_column="type", verbose_name=_("type of the event"), help_text=_("one of the types: subject, after-school activity, relax"))

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")


class Notes(django.db.models.Model):
    user = django.db.models.ForeignKey(django.contrib.auth.get_user_model(), on_delete=django.db.models.CASCADE, verbose_name=_("user"), help_text=_("user, who owns this day schedule"), related_name="notes", related_query_name="notes")
    disposable = django.db.models.BooleanField(verbose_name=_("is the note disposable"), help_text=_("shows whether note is disposable or repeating"))
    time_link = django.db.models.ForeignKey(TimeSchedule, verbose_name=_("notification time"), help_text=_("time when notification will come"), related_name="notes", related_query_name="notes", on_delete=django.db.models.CASCADE)
    global_note = django.db.models.BooleanField(db_column="global", verbose_name=_("is note global"), help_text=_("shows whether note is global (displayed on dependent schedules) or local"))
    heading = django.db.models.CharField(max_length=150, verbose_name=_("heading"), help_text=_("heading of the note"))
    description = django.db.models.TextField(verbose_name=_("description"), help_text=_("description of the note, that you will see in the notification"))

    class Meta:
        verbose_name = _("note")
        verbose_name_plural = _("notes")


class Teacher(django.db.models.Model):
    name = django.db.models.CharField(max_length=150, verbose_name=_("name"), help_text=_("name of the teacher"))
    user = django.db.models.ForeignKey(django.contrib.auth.get_user_model(), on_delete=django.db.models.CASCADE, verbose_name=_("user"), help_text=_("user, who owns this day schedule"), related_name="teacher", related_query_name="teachers")

    class Meta:
        verbose_name = _("teacher")
        verbose_name_plural = _("teachers")
