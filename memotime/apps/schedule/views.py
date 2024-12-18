from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
import django.shortcuts
import django.urls
from django.utils.translation import gettext_lazy as _
import django.views.generic

from apps.schedule import forms, models

__all__ = ()


class ScheduleCreateView(LoginRequiredMixin, django.views.generic.CreateView):
    model = models.Schedule
    form_class = forms.ScheduleForm
    template_name = "schedule/schedule_form.html"
    success_url = django.urls.reverse_lazy("schedule:schedule-list")
    login_url = "/login/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ScheduleListView(LoginRequiredMixin, django.views.generic.ListView):
    model = models.Schedule
    template_name = "schedule/schedule_list.html"
    context_object_name = "schedules"
    login_url = "/login/"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Schedule.objects.filter(user=self.request.user)

        raise Http404("Вы не можете просматривать чужое расписание.")


class ScheduleUpdateView(LoginRequiredMixin, django.views.generic.UpdateView):
    model = models.Schedule
    form_class = forms.ScheduleForm
    template_name = "schedule/schedule_form.html"
    success_url = django.urls.reverse_lazy("schedule:schedule-list")
    login_url = "/login/"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Schedule.objects.filter(user=self.request.user)

        raise Http404("Вы не можете изменять чужое расписание.")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("Вы не можете изменять чужое расписание.")

        return super().dispatch(request, *args, **kwargs)


class ScheduleDeleteView(LoginRequiredMixin, django.views.generic.DeleteView):
    model = models.Schedule
    template_name = "schedule/schedule_confirm_delete.html"
    success_url = django.urls.reverse_lazy("schedule:schedule-list")
    login_url = "/login/"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Schedule.objects.filter(user=self.request.user)

        raise Http404("Вы не можете удалять чужое расписание.")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("Вы не можете удалить чужое расписание.")

        return super().dispatch(request, *args, **kwargs)


class ScheduleDetailView(LoginRequiredMixin, django.views.generic.DetailView):
    model = models.Schedule
    template_name = "schedule/schedule_detail.html"
    context_object_name = "schedule"
    login_url = "/login/"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Schedule.objects.filter(user=self.request.user)

        raise Http404("Вы не можете просматривать чужое расписание.")

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
            raise Http404("Вы не можете просматривать чужое расписание.")

        return super().dispatch(request, *args, **kwargs)


class TimeScheduleCreateView(LoginRequiredMixin, django.views.generic.CreateView):
    model = models.TimeSchedule
    template_name = "schedule/timeschedule_form.html"
    login_url = "/login/"

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
            raise Http404("Вы не можете добавить время к чужому расписанию.")

        return super().dispatch(request, *args, **kwargs)


class TimeScheduleUpdateView(LoginRequiredMixin, django.views.generic.UpdateView):
    model = models.TimeSchedule
    template_name = "schedule/timeschedule_form.html"
    login_url = "/login/"

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

        raise Http404("Вы не можете изменять чужое время.")

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
            raise Http404("Вы не можете изменять чужое время.")

        return super().dispatch(request, *args, **kwargs)


class TimeScheduleDeleteView(LoginRequiredMixin, django.views.generic.DeleteView):
    model = models.TimeSchedule
    template_name = "schedule/timeschedule_confirm_delete.html"
    login_url = "/login/"

    def get_success_url(self):
        return django.urls.reverse(
            "schedule:schedule-detail",
            kwargs={"pk": self.object.schedule.id},
        )

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.TimeSchedule.objects.filter(user=self.request.user)

        raise Http404("Вы не можете удалять чужое время.")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("Вы не можете удалять чужое время.")

        return super().dispatch(request, *args, **kwargs)


class TimeScheduleEventCreateView(LoginRequiredMixin, django.views.generic.CreateView):
    model = models.Event
    form_class = forms.EventForm
    template_name = "schedule/event_form_from_timeschedule.html"
    login_url = "/login/"

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


class EventCreateView(LoginRequiredMixin, django.views.generic.CreateView):
    model = models.Event
    template_name = "schedule/event_form.html"
    success_url = django.urls.reverse_lazy("schedule:event-list")
    login_url = "/login/"

    def get_form_class(self):
        return forms.EventForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class EventListView(LoginRequiredMixin, django.views.generic.ListView):
    model = models.Event
    template_name = "schedule/event_list.html"
    context_object_name = "events"
    login_url = "/login/"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Event.objects.filter(user=self.request.user)

        raise Http404("Вы не можете просматривать чужие события.")


class EventUpdateView(LoginRequiredMixin, django.views.generic.UpdateView):
    model = models.Event
    template_name = "schedule/event_form.html"
    success_url = django.urls.reverse_lazy("schedule:event-list")
    login_url = "/login/"

    def get_form_class(self):
        return forms.EventForm

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Event.objects.filter(user=self.request.user)

        raise Http404("Вы не можете изменять чужое событие.")

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
            raise Http404("Вы не можете изменять чужое событие.")

        return super().dispatch(request, *args, **kwargs)


class EventDeleteView(LoginRequiredMixin, django.views.generic.DeleteView):
    model = models.Event
    template_name = "schedule/event_confirm_delete.html"
    success_url = django.urls.reverse_lazy("schedule:event-list")
    login_url = "/login/"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Event.objects.filter(user=self.request.user)

        raise Http404("Вы не можете удалять чужое событие.")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("Вы не можете удалять чужое событие.")

        return super().dispatch(request, *args, **kwargs)


class TeacherCreateView(LoginRequiredMixin, django.views.generic.CreateView):
    model = models.Teacher
    form_class = forms.TeacherForm
    template_name = "schedule/teacher_form.html"
    success_url = django.urls.reverse_lazy("schedule:teacher-list")
    login_url = "/login/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TeacherListView(LoginRequiredMixin, django.views.generic.ListView):
    model = models.Teacher
    template_name = "schedule/teacher_list.html"
    context_object_name = "teachers"
    login_url = "/login/"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Teacher.objects.filter(user=self.request.user)

        raise Http404("Вы не можете просматривать чужих преподавателей.")


class TeacherUpdateView(LoginRequiredMixin, django.views.generic.UpdateView):
    model = models.Teacher
    form_class = forms.TeacherForm
    template_name = "schedule/teacher_form.html"
    success_url = django.urls.reverse_lazy("schedule:teacher-list")
    login_url = "/login/"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Teacher.objects.filter(user=self.request.user)

        raise Http404("Вы не можете изменять чужого преподавателя.")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("Вы не можете изменять чужого преподавателя.")

        return super().dispatch(request, *args, **kwargs)


class TeacherDeleteView(LoginRequiredMixin, django.views.generic.DeleteView):
    model = models.Teacher
    template_name = "schedule/teacher_confirm_delete.html"
    success_url = django.urls.reverse_lazy("schedule:teacher-list")
    login_url = "/login/"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Teacher.objects.filter(user=self.request.user)

        raise Http404("Вы не можете удалять чужого преподавателя.")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("Вы не можете удалять чужого преподавателя.")

        return super().dispatch(request, *args, **kwargs)


class NoteCreateView(LoginRequiredMixin, django.views.generic.CreateView):
    model = models.Note
    template_name = "schedule/note_form.html"
    success_url = django.urls.reverse_lazy("schedule:note-list")
    login_url = "/login/"

    def get_form_class(self):
        return forms.NoteForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class NoteListView(LoginRequiredMixin, django.views.generic.ListView):
    model = models.Note
    template_name = "schedule/note_list.html"
    context_object_name = "notes"
    login_url = "/login/"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Note.objects.filter(user=self.request.user)

        raise Http404("Вы не можете просматривать чужие заметки.")


class NoteUpdateView(LoginRequiredMixin, django.views.generic.UpdateView):
    model = models.Note
    form_class = forms.NoteForm
    template_name = "schedule/note_form.html"
    success_url = django.urls.reverse_lazy("schedule:note-list")
    login_url = "/login/"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Note.objects.filter(user=self.request.user)

        raise Http404("Вы не можете изменять чужую заметку.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("Вы не можете изменять чужую заметку.")

        return super().dispatch(request, *args, **kwargs)


class NoteDeleteView(LoginRequiredMixin, django.views.generic.DeleteView):
    model = models.Note
    template_name = "schedule/note_confirm_delete.html"
    success_url = django.urls.reverse_lazy("schedule:note-list")
    login_url = "/login/"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.Note.objects.filter(user=self.request.user)

        raise Http404("Вы не можете удалять чужую заметку.")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("Вы не можете удалять чужую заметку.")

        return super().dispatch(request, *args, **kwargs)
