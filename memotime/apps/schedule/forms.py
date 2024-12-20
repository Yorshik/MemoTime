from django.core.exceptions import ValidationError
import django.forms
from django.utils.translation import gettext_lazy as _

from apps.schedule import models

__all__ = []


class NoteForm(django.forms.ModelForm):
    event = django.forms.ModelChoiceField(
        queryset=None,
        widget=django.forms.Select(
            attrs={"class": "selectpicker", "data-live-search": "true"},
        ),
        required=False,
        label=_("Event"),
    )

    class Meta:
        model = models.Note
        fields = ["heading", "description", "disposable", "event"]
        labels = {"disposable": _("One time reminder")}

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["event"].queryset = models.Event.objects.filter(user=user)

    def save(self, commit=True):
        note = super().save(commit=False)
        if commit:
            note.save()

        return note


class ScheduleForm(django.forms.ModelForm):
    group = django.forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_("Group"),
        widget=django.forms.Select(
            attrs={"class": "selectpicker", "data-live-search": "true"},
        ),
    )

    class Meta:
        model = models.Schedule
        fields = ["is_static", "start_date", "expiration_date", "group"]
        labels = {"is_static": _("Changes by week")}
        widgets = {
            "start_date": django.forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "expiration_date": django.forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group"].queryset = user.groups.all()
        self.fields["start_date"].input_formats = ["%Y-%m-%d"]
        self.fields["expiration_date"].input_formats = ["%Y-%m-%d"]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        expiration_date = cleaned_data.get("expiration_date")

        if start_date and expiration_date and start_date > expiration_date:
            self.add_error(
                "expiration_date",
                ValidationError(
                    _("Start date must be earlier than the end date."),
                ),
            )

        return cleaned_data


class EventForm(django.forms.ModelForm):
    class Meta:
        model = models.Event
        fields = [
            "name",
            "custom_name",
            "description",
            "teacher",
            "event_type",
            "priority",
        ]
        widgets = {
            "teacher": django.forms.Select(
                attrs={"class": "selectpicker", "data-live-search": "true"},
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["teacher"].queryset = models.Teacher.objects.filter(user=user)


class TeacherForm(django.forms.ModelForm):
    class Meta:
        model = models.Teacher
        fields = ["name"]


class TimeScheduleForm(django.forms.ModelForm):
    class Meta:
        model = models.TimeSchedule
        fields = [
            "time_start",
            "time_end",
            "event",
            "day_number",
            "even",
        ]
        widgets = {
            "time_start": django.forms.TimeInput(attrs={"type": "time"}),
            "time_end": django.forms.TimeInput(attrs={"type": "time"}),
            "event": django.forms.Select(
                attrs={"class": "selectpicker", "data-live-search": "true"},
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["event"].queryset = models.Event.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()
        time_start = cleaned_data.get("time_start")
        time_end = cleaned_data.get("time_end")
        day_number = cleaned_data.get("day_number")
        event = cleaned_data.get("event")
        even = cleaned_data.get("even")

        if (
            not time_start
            or not time_end
            or not day_number
            or not event
            or even is None
        ):
            return cleaned_data

        if time_start >= time_end:
            raise ValidationError(
                _("Start time must be earlier than end time."),
            )

        if event.event_type != models.Event.EventType.SUBJECT:
            return cleaned_data

        schedule_id = (
            self.instance.schedule.id
            if self.instance and self.instance.schedule
            else None
        )

        if not schedule_id:
            return cleaned_data

        existing_schedules = models.TimeSchedule.objects.filter(
            schedule_id=schedule_id,
            day_number=day_number,
            even=even,
            event__event_type=models.Event.EventType.SUBJECT,
        ).exclude(pk=self.instance.pk if self.instance else None)

        for schedule in existing_schedules:
            if (time_start < schedule.time_end) and (time_end > schedule.time_start):
                raise ValidationError(
                    _("Time overlaps with an existing event."),
                )

        return cleaned_data


class AddTimeScheduleForm(django.forms.ModelForm):
    schedule = django.forms.ModelChoiceField(
        queryset=models.Schedule.objects.all(),
        widget=django.forms.HiddenInput(),
    )

    class Meta:
        model = models.TimeSchedule
        fields = [
            "schedule",
            "time_start",
            "time_end",
            "event",
            "day_number",
            "even",
        ]
        widgets = {
            "time_start": django.forms.TimeInput(attrs={"type": "time"}),
            "time_end": django.forms.TimeInput(attrs={"type": "time"}),
            "event": django.forms.Select(
                attrs={"class": "selectpicker"},
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["event"].queryset = models.Event.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()
        time_start = cleaned_data.get("time_start")
        time_end = cleaned_data.get("time_end")
        day_number = cleaned_data.get("day_number")
        event = cleaned_data.get("event")
        even = cleaned_data.get("even")
        schedule = cleaned_data.get("schedule")

        if (
            not time_start
            or not time_end
            or not day_number
            or not event
            or even is None
            or not schedule
        ):
            return cleaned_data

        if time_start >= time_end:
            raise ValidationError(
                _("Start time must be earlier than end time."),
            )

        if event.event_type != models.Event.EventType.SUBJECT:
            return cleaned_data

        existing_schedules = models.TimeSchedule.objects.filter(
            schedule=schedule,
            day_number=day_number,
            even=even,
            event__event_type=models.Event.EventType.SUBJECT,
        )

        for schedule in existing_schedules:
            if (time_start < schedule.time_end) and (time_end > schedule.time_start):
                raise ValidationError(
                    _("Time overlaps with an existing event."),
                )

        return cleaned_data
