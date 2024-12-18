import django.forms

from apps.schedule import models

__all__ = ()


class NoteForm(django.forms.ModelForm):
    event = django.forms.ModelChoiceField(
        queryset=None,
        widget=django.forms.Select(
            attrs={"class": "selectpicker", "data-live-search": "true"},
        ),
        required=False,
        label="Event",
    )

    class Meta:
        model = models.Note
        fields = ["heading", "description", "disposable", "global_note"]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["event"].queryset = models.Event.objects.filter(user=user)
        if self.instance.pk:
            event_related = models.Event.objects.filter(notes=self.instance).first()
            if event_related:
                self.initial["event"] = event_related

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def save(self, commit=True):
        note = super().save(commit=False)
        selected_event = self.cleaned_data["event"]

        if selected_event:
            note.event = selected_event
        else:
            note.event = None

        if commit:
            note.save()

        return note


class ScheduleForm(django.forms.ModelForm):
    class Meta:
        model = models.Schedule
        fields = ["is_static", "start_date", "expiration_date"]
        widgets = {
            "start_date": django.forms.DateInput(attrs={"type": "date"}),
            "expiration_date": django.forms.DateInput(attrs={"type": "date"}),
        }

    def clean_expiration_date(self):
        expiration_date = self.cleaned_data.get("expiration_date")
        if not expiration_date:
            return None

        return expiration_date


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
            "notes",
        ]
        widgets = {
            "teacher": django.forms.Select(
                attrs={"class": "selectpicker", "data-live-search": "true"},
            ),
            "notes": django.forms.Select(
                attrs={"class": "selectpicker", "data-live-search": "true"},
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["teacher"].queryset = models.Teacher.objects.filter(user=user)
        self.fields["notes"].queryset = models.Note.objects.filter(user=user)


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
            "even",
            "day_number",
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
            raise django.core.exceptions.ValidationError(
                "Время начала должно быть раньше времени окончания.",
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
                raise django.core.exceptions.ValidationError(
                    "Время пересекается с существующим событием.",
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
            "even",
            "day_number",
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
            raise django.core.exceptions.ValidationError(
                "Время начала должно быть раньше времени окончания.",
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
                raise django.core.exceptions.ValidationError(
                    "Время пересекается с существующим событием.",
                )

        return cleaned_data
