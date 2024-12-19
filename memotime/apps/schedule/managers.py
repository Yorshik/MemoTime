import django.db.models

import apps.users.models

__all__ = ()


class NoteManager(django.db.models.Manager):
    def get_notes_for_user(self, user):
        return self.filter(user=user)

    def get_note_by_pk_and_user(self, pk, user):
        return (
            self.select_related("user")
            .only(
                "id",
                "disposable",
                "global_note",
                "heading",
                "description",
                "user_id",
                "user__id",
                "user__username",
            )
            .get(pk=pk, user=user)
        )


class TeacherManager(django.db.models.Manager):
    def get_teachers_for_user(self, user):
        return self.filter(user=user)

    def get_teacher_by_pk_and_user(self, pk, user):
        return (
            self.select_related("user")
            .only("id", "name", "user__id", "user__username")
            .get(pk=pk, user=user)
        )


class EventManager(django.db.models.Manager):
    def get_events_for_user(self, user):
        return self.filter(user=user)

    def get_event_by_pk_and_user(self, pk, user):
        return (
            self.select_related("user", "teacher", "notes")
            .only(
                "id",
                "name",
                "custom_name",
                "description",
                "event_type",
                "priority",
                "user_id",
                "teacher_id",
                "notes_id",
                "user__id",
                "user__username",
                "teacher__id",
                "teacher__name",
                "notes__id",
                "notes__heading",
            )
            .get(pk=pk, user=user)
        )


class ScheduleManager(django.db.models.Manager):
    def get_schedules_for_user(self, user):
        return self.filter(user=user)

    def get_schedule_by_pk(self, pk):
        return self.select_related("user").get(pk=pk)

    def get_schedule_by_pk_and_user(self, pk, user):
        return (
            self.select_related("user", "group")
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
            )
            .get(pk=pk, user=user)
        )


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
            .annotate(
                start=django.db.models.F("time_start"),
                end=django.db.models.F("time_end"),
            )
            .values(
                "id",
                "start",
                "end",
                "event__name",
            )
            .distinct()
        )
