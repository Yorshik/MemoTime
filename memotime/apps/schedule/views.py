from django.http import JsonResponse
import django.shortcuts
from django.urls import reverse_lazy
import django.views.generic

from apps.schedule import forms, models

__all__ = ()


class ScheduleCreateView(django.views.generic.CreateView):
    model = models.Schedule
    form_class = forms.ScheduleForm
    template_name = "schedule/schedule_form.html"
    success_url = reverse_lazy("schedule:schedule-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ScheduleListView(django.views.generic.ListView):
    model = models.Schedule
    template_name = "schedule/schedule_list.html"
    context_object_name = "schedules"

    def get_queryset(self):
        return models.Schedule.objects.filter(user=self.request.user)


class ScheduleUpdateView(django.views.generic.UpdateView):
    model = models.Schedule
    form_class = forms.ScheduleForm
    template_name = "schedule/schedule_form.html"
    success_url = reverse_lazy("schedule:schedule-list")


class ScheduleDeleteView(django.views.generic.DeleteView):
    model = models.Schedule
    template_name = "schedule/schedule_confirm_delete.html"
    success_url = reverse_lazy("schedule:schedule-list")


class ScheduleDetailView(django.views.generic.DetailView):
    model = models.Schedule
    template_name = "schedule/schedule_detail.html"
    context_object_name = "schedule"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["time_schedules"] = models.TimeSchedule.objects.filter(
            schedule=self.object,
        )
        return context


class TimeScheduleCreateView(django.views.generic.CreateView):
    model = models.TimeSchedule
    form_class = forms.AddTimeScheduleForm
    template_name = "schedule/timeschedule_form.html"

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
        context["event_form"] = forms.EventForm()
        context["teachers"] = models.Teacher.objects.filter(
            user=self.request.user,
        ).values_list(
            "id",
            "name",
        )
        return context

    def form_valid(self, form):
        schedule_id = self.kwargs["schedule_id"]
        schedule = models.Schedule.objects.get(pk=schedule_id)
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


class TimeScheduleUpdateView(django.views.generic.UpdateView):
    model = models.TimeSchedule
    form_class = forms.TimeScheduleForm
    template_name = "schedule/timeschedule_form.html"

    def get_success_url(self):
        return django.urls.reverse(
            "schedule:schedule-detail",
            kwargs={"pk": self.object.schedule.id},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_form"] = forms.EventForm()
        context["events"] = models.Event.objects.filter(
            user=self.request.user,
        ).values_list(
            "id",
            "name",
        )
        context["teachers"] = models.Teacher.objects.filter(
            user=self.request.user,
        ).values_list(
            "id",
            "name",
        )
        return context


class TimeScheduleDeleteView(django.views.generic.DeleteView):
    model = models.TimeSchedule
    template_name = "schedule/timeschedule_confirm_delete.html"

    def get_success_url(self):
        return django.urls.reverse(
            "schedule:schedule-detail",
            kwargs={"pk": self.object.schedule.id},
        )


class EventCreateView(django.views.generic.CreateView):
    model = models.Eventы
    form_class = forms.EventForm

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        events = models.Event.objects.filter(user=self.request.user).values_list(
            "id",
            "name",
        )
        return JsonResponse({"events": list(events)})


class TeacherCreateView(django.views.generic.CreateView):
    model = models.Teacher
    form_class = forms.TeacherForm

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        teachers = models.Teacher.objects.filter(user=self.request.user).values_list(
            "id",
            "name",
        )
        return JsonResponse({"teachers": list(teachers)})
