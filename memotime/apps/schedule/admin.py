import django.contrib

import apps.schedule

__all__ = ()


@django.contrib.admin.register(apps.schedule.models.Schedule)
class ScheduleAdmin(django.contrib.admin.ModelAdmin):
    list_display = ["user", "is_static", "start_date", "expiration_date"]
    list_filter = ["user", "is_static"]
    search_fields = ["user__username", "start_date"]


@django.contrib.admin.register(apps.schedule.models.Event)
class EventAdmin(django.contrib.admin.ModelAdmin):
    list_display = ["user", "name", "custom_name", "teacher", "event_type", "priority"]
    list_filter = ["user", "teacher", "event_type", "priority"]
    search_fields = ["user__username", "name", "custom_name"]
    autocomplete_fields = ["teacher"]


@django.contrib.admin.register(apps.schedule.models.TimeSchedule)
class TimeScheduleAdmin(django.contrib.admin.ModelAdmin):
    list_display = [
        "user",
        "schedule",
        "time_start",
        "time_end",
        "event",
        "even",
        "day_number",
    ]
    list_filter = ["user", "schedule", "even", "day_number"]
    search_fields = ["user__username", "schedule__id"]
    autocomplete_fields = ["event", "schedule"]

