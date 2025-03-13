import django.db.models
from django.db.models import BooleanField, Case, Q, When

import apps.users.models

__all__ = ()


class EventManager(django.db.models.Manager):
    def get_events_for_user(self, user):
        return self.filter(user=user)

    def get_event_by_pk_and_user(self, pk, user):
        return (
            self.select_related("user", "teacher")
            .prefetch_related("notes")
            .only(
                "id",
                "name",
                "custom_name",
                "description",
                "event_type",
                "priority",
                "user_id",
                "teacher_id",
                "user__id",
                "user__username",
                "teacher__id",
                "teacher__name",
            )
            .get(pk=pk, user=user)
        )


class ScheduleManager(django.db.models.Manager):
    def get_schedules_for_user(self, user):
        return (
            self.filter(Q(user=user) | Q(group__in=user.groups.all()))
            .select_related("user")
            .annotate(
                is_owner=Case(
                    When(user=user, then=True),
                    default=False,
                    output_field=BooleanField(),
                ),
            )
            .distinct()
        )

    def get_schedule_by_pk(self, pk):
        return (
            self.select_related("user", "group__creator")
            .prefetch_related("group__user_set")
            .get(pk=pk)
        )

    def get_schedule_by_pk_and_user(self, pk, user):
        return (
            self.select_related(
                "user",
                "group__creator",
            )
            .prefetch_related(
                django.db.models.Prefetch(
                    "user__created_groups",
                    queryset=apps.users.models.Group.objects.all(),
                ),
            )
            .only(
                "id",
                "user_id",
                "group_id",
                "is_static",
                "start_date",
                "expiration_date",
                "user__id",
                "user__username",
                "group__group_ptr_id",
                "group__name",
                "group__creator_id",
            )
            .get(pk=pk, user=user)
        )

    def get_object_for_user(self, pk, user):
        return self.get_schedule_by_pk_and_user(pk, user)


class TimeScheduleManager(django.db.models.Manager):
    def get_timeschedules_for_schedule(self, schedule):
        return (
            self.filter(schedule=schedule)
            .select_related("event")
            .order_by("day_number", "time_start")
        )

    def get_timeschedule_by_pk_and_user(self, pk, user):
        return self.select_related("schedule__user").get(pk=pk, schedule__user=user)

    def get_time_slots_for_schedule(self, schedule):
        return (
            self.filter(schedule=schedule)
            .values("time_start", "time_end")
            .distinct()
            .order_by("time_start")
        )
