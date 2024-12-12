import django.forms
import django.utils.timezone
from django.utils.translation import gettext_lazy as _

from apps.schedule import models

__all__ = ()


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
                attrs={"class": "selectpicker", "data-live-search": "true"},
            ),
        }
