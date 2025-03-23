import django.contrib.auth.mixins
import django.http
import django.shortcuts
import django.urls
import django.utils.timezone
from django.utils.translation import gettext_lazy as _
import django.views.generic

import datetime

from apps.schedule import forms, models, celery_tasks

__all__ = []

User = django.contrib.auth.get_user_model()


class AccessMixin(django.contrib.auth.mixins.LoginRequiredMixin):
    _object = None
    model = None
    owner_field = "user"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.model.objects.filter(**{self.owner_field: self.request.user})

        raise django.http.Http404(_("You cannot view this content."))

    def dispatch(self, request, *args, **kwargs):
        self._object = self.get_object() if self._object is None else self._object
        if getattr(self._object, self.owner_field) != self.request.user:
            raise django.http.Http404(_("You cannot view this content."))

        return super().dispatch(request, *args, **kwargs)


class ScheduleCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):
    model = models.Schedule
    form_class = forms.ScheduleForm
    template_name = "schedule/schedule_form.html"
    success_url = django.urls.reverse_lazy("schedule:schedule-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_form(self, form_class=None):
        return super().get_form(form_class)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ScheduleUpdateView(
    AccessMixin,
    django.views.generic.UpdateView,
):
    model = models.Schedule
    form_class = forms.ScheduleForm
    template_name = "schedule/schedule_form.html"
    success_url = django.urls.reverse_lazy("schedule:schedule-list")

    def get_object(self, queryset=None):
        if not hasattr(self, "_schedule_object"):
            self._schedule_object = models.Schedule.objects.get_schedule_by_pk_and_user(
                pk=self.kwargs.get(self.pk_url_kwarg),
                user=self.request.user,
            )

        return self._schedule_object

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.get_object().user
        return kwargs

    def get_form(self, form_class=None):
        return super().get_form(form_class)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["schedule_object"] = self.get_object()
        return context


class ScheduleListView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.ListView,
):
    model = models.Schedule
    template_name = "schedule/schedule_list.html"
    context_object_name = "schedules"

    def get_queryset(self):
        return models.Schedule.objects.get_schedules_for_user(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        context["owned_schedules"] = [
            schedule for schedule in context["schedules"] if schedule.user_id == user_id
        ]
        context["shared_schedules"] = [
            schedule for schedule in context["schedules"] if schedule.user_id != user_id
        ]
        return context


class ScheduleDeleteView(AccessMixin, django.views.generic.View):
    model = models.Schedule

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs.get("pk"))
        except models.Schedule.DoesNotExist:
            raise django.http.Http404(_("Schedule not found"))

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        success_url = django.urls.reverse_lazy("schedule:schedule-list")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return django.http.JsonResponse({"status": "ok"})

        return django.http.HttpResponseRedirect(success_url)


class ScheduleDetailView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.DetailView,
):
    model = models.Schedule
    template_name = "schedule/schedule_detail.html"
    context_object_name = "schedule"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self._schedule_object = None

    def get_object(self, queryset=None):
        if self._schedule_object is None:
            self._schedule_object = models.Schedule.objects.get_schedule_by_pk(
                pk=self.kwargs["pk"],
            )

        return self._schedule_object

    def dispatch(self, request, *args, **kwargs):
        schedule = self.get_object()
        if schedule.user != request.user:
            raise django.http.Http404(_("You cannot view this content."))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        events = models.Event.objects.get_timeschedules_for_schedule(schedule=self.object)
        context["events"] = events

        time_slots = set()
        for ts in events:
            time_slots.add((ts.time_start, ts.time_end))

        context["time_slots"] = [
            {"start": start, "end": end} for start, end in sorted(time_slots)
        ]

        context["days"] = [
            {"number": 1, "name": _("Monday")},
            {"number": 2, "name": _("Tuesday")},
            {"number": 3, "name": _("Wednesday")},
            {"number": 4, "name": _("Thursday")},
            {"number": 5, "name": _("Friday")},
            {"number": 6, "name": _("Saturday")},
            {"number": 7, "name": _("Sunday")},
        ]

        context["only_view"] = False
        return context


class EventCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):
    model = models.Event
    template_name = "schedule/event_form.html"
    success_url = django.urls.reverse_lazy("schedule:schedule-list")
    form_class = forms.EventForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.schedule = models.Schedule.objects.get(pk=self.kwargs['schedule_pk'])
        response = super().form_valid(form)
        event = form.instance
        now = django.utils.timezone.now()
        event_time = event.time_start
        event_day = event.day_number
        current_weekday = now.isoweekday()
        days_until_event = (event_day - current_weekday) % 7
        if days_until_event == 0 and now.time() > event_time:
            days_until_event = 7

        event_date = now.date() + datetime.timedelta(days=days_until_event)
        event_datetime = django.utils.timezone.make_aware(
            datetime.datetime.combine(event_date, event_time),
            django.utils.timezone.get_current_timezone()
        )
        celery_tasks.send_event_reminder.apply_async(
            args=[event.id],
            eta=event_datetime,
        )

        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return django.urls.reverse_lazy(
            "schedule:schedule-detail",
            kwargs={"pk": self.kwargs["schedule_pk"]},
        )


class EventListView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.ListView,
):
    model = models.Event
    template_name = "schedule/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        return models.Event.objects.get_events_for_user(user=self.request.user)


class EventUpdateView(AccessMixin, django.views.generic.UpdateView):
    model = models.Event
    template_name = "schedule/event_form.html"
    success_url = django.urls.reverse_lazy("schedule:schedule-list")
    form_class = forms.EventForm

    def get_object(self, queryset=None):
        if not hasattr(self, "_event_object"):
            self._event_object = models.Event.objects.get_event_by_pk_and_user(
                pk=self.kwargs.get(self.pk_url_kwarg),
                user=self.request.user,
            )

        return self._event_object

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_object"] = self.get_object()
        return context

    def form_valid(self, form):
        return super().form_valid(form)


class EventDeleteView(AccessMixin, django.views.generic.View):
    model = models.Event

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs.get("pk"))
        except models.Event.DoesNotExist:
            raise django.http.Http404(_("Event not found"))

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        success_url = django.urls.reverse_lazy("schedule:schedule-list")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return django.http.JsonResponse({"status": "ok"})

        return django.http.HttpResponseRedirect(success_url)
