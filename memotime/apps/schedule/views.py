import django.contrib.auth.mixins
import django.http
import django.shortcuts
import django.urls
from django.utils.translation import gettext_lazy as _
import django.views.generic

from apps.schedule import forms, models

__all__ = ()


class ScheduleCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):
    model = models.Schedule
    form_class = forms.ScheduleForm
    template_name = "schedule/schedule_form.html"
    success_url = django.urls.reverse_lazy("schedule:schedule-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ScheduleListView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.ListView,
):
    model = models.Schedule
    template_name = "schedule/schedule_list.html"
    context_object_name = "schedules"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Schedule.objects.filter(user=self.request.user)

        raise django.http.Http404("Вы не можете просматривать чужое расписание.")


class ScheduleUpdateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.UpdateView,
):
    model = models.Schedule
    form_class = forms.ScheduleForm
    template_name = "schedule/schedule_form.html"
    success_url = django.urls.reverse_lazy("schedule:schedule-list")

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Schedule.objects.filter(user=self.request.user)

        raise django.http.Http404("Вы не можете изменять чужое расписание.")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise django.http.Http404("Вы не можете изменять чужое расписание.")

        return super().dispatch(request, *args, **kwargs)


class ScheduleDeleteView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.View,
):
    model = models.Schedule

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Schedule.objects.filter(user=self.request.user)

        raise django.http.Http404(_("Вы не можете удалять чужое расписание."))

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise django.http.Http404(_("Вы не можете удалять чужое расписание."))

        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs.get("pk"))
        except models.Schedule.DoesNotExist:
            raise django.http.Http404(_("Расписание не найдено"))

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

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Schedule.objects.filter(user=self.request.user)

        raise django.http.Http404("Вы не можете просматривать чужое расписание.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_schedules = models.TimeSchedule.objects.filter(
            schedule=self.object,
            user=self.request.user,
        ).order_by("time_start")

        context["time_schedules"] = time_schedules
        context["days"] = [
            {"number": 1, "name": _("Monday")},
            {"number": 2, "name": _("Tuesday")},
            {"number": 3, "name": _("Wednesday")},
            {"number": 4, "name": _("Thursday")},
            {"number": 5, "name": _("Friday")},
            {"number": 6, "name": _("Saturday")},
            {"number": 7, "name": _("Sunday")},
        ]

        time_slots = []
        for ts in time_schedules:
            found = False
            for slot in time_slots:
                if slot["start"] == ts.time_start and slot["end"] == ts.time_end:
                    found = True
                    break

            if not found:
                time_slots.append({"start": ts.time_start, "end": ts.time_end})

        context["time_slots"] = time_slots

        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise django.http.Http404("Вы не можете просматривать чужое расписание.")

        return super().dispatch(request, *args, **kwargs)


class TimeScheduleCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):
    model = models.TimeSchedule
    template_name = "schedule/timeschedule_form.html"

    def get_form_class(self):
        return forms.AddTimeScheduleForm

    def get_success_url(self):
        return django.urls.reverse(
            "schedule:schedule-detail",
            kwargs={"pk": self.kwargs["schedule_id"]},
        )

    def get_initial(self):
        initial = super().get_initial()
        initial["schedule"] = self.kwargs["schedule_id"]
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_form"] = forms.EventForm(user=self.request.user)
        context["events"] = models.Event.objects.filter(
            user=self.request.user,
        )
        context["teachers"] = models.Teacher.objects.filter(
            user=self.request.user,
        )
        context["schedule"] = models.Schedule.objects.get(
            pk=self.kwargs["schedule_id"],
            user=self.request.user,
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        schedule_id = self.kwargs["schedule_id"]
        schedule = models.Schedule.objects.get(pk=schedule_id, user=self.request.user)
        form.instance.user = self.request.user
        form.instance.schedule = schedule

        models.TimeSchedule.objects.create(
            schedule=schedule,
            time_start=form.cleaned_data["time_start"],
            time_end=form.cleaned_data["time_end"],
            event=form.cleaned_data["event"],
            even=form.cleaned_data["even"],
            day_number=form.cleaned_data["day_number"],
            user=self.request.user,
        )
        return django.shortcuts.redirect(self.get_success_url())

    def dispatch(self, request, *args, **kwargs):
        schedule = models.Schedule.objects.filter(
            pk=self.kwargs["schedule_id"],
            user=self.request.user,
        ).first()
        if not schedule:
            raise django.http.Http404(
                "Вы не можете добавить время к чужому расписанию.",
            )

        return super().dispatch(request, *args, **kwargs)


class TimeScheduleUpdateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.UpdateView,
):
    model = models.TimeSchedule
    template_name = "schedule/timeschedule_form.html"

    def get_form_class(self):
        return forms.TimeScheduleForm

    def get_success_url(self):
        return django.urls.reverse(
            "schedule:schedule-detail",
            kwargs={"pk": self.object.schedule.id},
        )

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.TimeSchedule.objects.filter(user=self.request.user)

        raise django.http.Http404("Вы не можете изменять чужое время.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_form"] = forms.EventForm(user=self.request.user)
        context["events"] = models.Event.objects.filter(
            user=self.request.user,
        )
        context["teachers"] = models.Teacher.objects.filter(
            user=self.request.user,
        )
        context["schedule"] = self.object.schedule
        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise django.http.Http404("Вы не можете изменять чужое время.")

        return super().dispatch(request, *args, **kwargs)


class TimeScheduleDeleteView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.View,
):
    model = models.TimeSchedule

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.TimeSchedule.objects.filter(event__user=self.request.user)

        raise django.http.Http404("Вы не можете удалять чужое время.")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.event.user != self.request.user:
            raise django.http.Http404("Вы не можете удалять чужое время.")

        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs.get("pk"))
        except models.TimeSchedule.DoesNotExist:
            raise django.http.Http404("Расписание не найдено")

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        success_url = django.urls.reverse(
            "schedule:schedule-detail",
            kwargs={"pk": obj.schedule.id},
        )

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return django.http.JsonResponse({"status": "ok"})

        return django.http.HttpResponseRedirect(success_url)


class TimeScheduleEventCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):
    model = models.Event
    form_class = forms.EventForm
    template_name = "schedule/event_form_from_timeschedule.html"

    def get_success_url(self):
        return django.urls.reverse(
            "schedule:timeschedule-create",
            kwargs={"schedule_id": self.kwargs["schedule_id"]},
        )

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()

        return django.shortcuts.redirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class EventCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):
    model = models.Event
    template_name = "schedule/event_form.html"
    success_url = django.urls.reverse_lazy("schedule:event-list")

    def get_form_class(self):
        return forms.EventForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class EventListView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.ListView,
):
    model = models.Event
    template_name = "schedule/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Event.objects.filter(user=self.request.user)

        raise django.http.Http404("Вы не можете просматривать чужие события.")


class EventUpdateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.UpdateView,
):
    model = models.Event
    template_name = "schedule/event_form.html"
    success_url = django.urls.reverse_lazy("schedule:event-list")

    def get_form_class(self):
        return forms.EventForm

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Event.objects.filter(user=self.request.user)

        raise django.http.Http404("Вы не можете изменять чужое событие.")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise django.http.Http404("Вы не можете изменять чужое событие.")

        return super().dispatch(request, *args, **kwargs)


class EventDeleteView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.View,
):
    model = models.Event

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Event.objects.filter(user=self.request.user)

        raise django.http.Http404(_("Вы не можете удалять чужое событие."))

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise django.http.Http404(_("Вы не можете удалять чужое событие."))

        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs.get("pk"))
        except models.Event.DoesNotExist:
            raise django.http.Http404(_("Событие не найдено"))

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        success_url = django.urls.reverse_lazy("schedule:event-list")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return django.http.JsonResponse({"status": "ok"})

        return django.http.HttpResponseRedirect(success_url)


class TeacherCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):
    model = models.Teacher
    form_class = forms.TeacherForm
    template_name = "schedule/teacher_form.html"
    success_url = django.urls.reverse_lazy("schedule:teacher-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TeacherListView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.ListView,
):
    model = models.Teacher
    template_name = "schedule/teacher_list.html"
    context_object_name = "teachers"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Teacher.objects.filter(user=self.request.user)

        raise django.http.Http404("Вы не можете просматривать чужих преподавателей.")


class TeacherUpdateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.UpdateView,
):
    model = models.Teacher
    form_class = forms.TeacherForm
    template_name = "schedule/teacher_form.html"
    success_url = django.urls.reverse_lazy("schedule:teacher-list")

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Teacher.objects.filter(user=self.request.user)

        raise django.http.Http404("Вы не можете изменять чужого преподавателя.")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise django.http.Http404("Вы не можете изменять чужого преподавателя.")

        return super().dispatch(request, *args, **kwargs)


class TeacherDeleteView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.DeleteView,
):
    model = models.Teacher
    template_name = "schedule/teacher_confirm_delete.html"
    success_url = django.urls.reverse_lazy("schedule:teacher-list")

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Teacher.objects.filter(user=self.request.user)

        raise django.http.Http404("Вы не можете удалять чужого преподавателя.")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise django.http.Http404("Вы не можете удалять чужого преподавателя.")

        return super().dispatch(request, *args, **kwargs)


class NoteCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):
    model = models.Note
    template_name = "schedule/note_form.html"
    success_url = django.urls.reverse_lazy("schedule:note-list")

    def get_form_class(self):
        return forms.NoteForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class NoteListView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.ListView,
):
    model = models.Note
    template_name = "schedule/note_list.html"
    context_object_name = "notes"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Note.objects.filter(user=self.request.user)

        raise django.http.Http404("Вы не можете просматривать чужие заметки.")


class NoteUpdateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.UpdateView,
):
    model = models.Note
    form_class = forms.NoteForm
    template_name = "schedule/note_form.html"
    success_url = django.urls.reverse_lazy("schedule:note-list")

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Note.objects.filter(user=self.request.user)

        raise django.http.Http404("Вы не можете изменять чужую заметку.")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise django.http.Http404("Вы не можете изменять чужую заметку.")

        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        return form_class(user=self.request.user, **self.get_form_kwargs())


class NoteDeleteView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.View,
):
    model = models.Note

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Note.objects.filter(user=self.request.user)

        raise django.http.Http404(_("Вы не можете удалять чужую заметку."))

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise django.http.Http404(_("Вы не можете удалять чужую заметку."))

        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs.get("pk"))
        except models.Note.DoesNotExist:
            raise django.http.Http404(_("Заметка не найдена"))

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        success_url = django.urls.reverse_lazy("schedule:note-list")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return django.http.JsonResponse({"status": "ok"})

        return django.http.HttpResponseRedirect(success_url)
