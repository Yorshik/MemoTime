import django.contrib.auth.mixins
import django.http
import django.shortcuts
import django.urls
from django.utils.translation import gettext_lazy as _
import django.views.generic

from apps.schedule import forms, models

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
        form = super().get_form(form_class)
        form.fields["group"].queryset = self.request.user.created_groups.all()
        return form

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
        form = super().get_form(form_class)
        form.fields["group"].queryset = self.get_object().user.created_groups.all()
        return form

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
            if not schedule.group:
                raise django.http.Http404(_("You cannot view this content."))

            if request.user not in schedule.group.user_set.all():
                raise django.http.Http404(_("You cannot view this content."))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["time_schedules"] = (
            models.TimeSchedule.objects.get_timeschedules_for_schedule(
                schedule=self.object,
            )
        )

        context["time_slots"] = models.TimeSchedule.objects.get_time_slots_for_schedule(
            schedule=self.object,
        )

        context["days"] = [
            {"number": 1, "name": _("Monday")},
            {"number": 2, "name": _("Tuesday")},
            {"number": 3, "name": _("Wednesday")},
            {"number": 4, "name": _("Thursday")},
            {"number": 5, "name": _("Friday")},
            {"number": 6, "name": _("Saturday")},
            {"number": 7, "name": _("Sunday")},
        ]

        return context


class TimeScheduleCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):

    model = models.TimeSchedule
    template_name = "schedule/timeschedule_form.html"
    owner_field = "schedule__user"

    def get_form_class(self):
        return forms.AddTimeScheduleForm

    def get_success_url(self):
        return django.urls.reverse(
            "schedule:schedule-detail",
            kwargs={"pk": self.kwargs["schedule_id"]},
        )

    def get_initial(self):
        return {"schedule": self.kwargs["schedule_id"]}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_form"] = forms.EventForm(user=self.request.user)
        context["events"] = models.Event.objects.get_events_for_user(
            user=self.request.user,
        )
        context["teachers"] = models.Teacher.objects.get_teachers_for_user(
            user=self.request.user,
        )
        context["schedule"] = models.Schedule.objects.get_schedule_by_pk_and_user(
            pk=self.kwargs["schedule_id"],
            user=self.request.user,
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        schedule = models.Schedule.objects.get_schedule_by_pk_and_user(
            pk=self.kwargs["schedule_id"],
            user=self.request.user,
        )
        form.instance.user = self.request.user
        form.instance.schedule = schedule
        form.save()
        return django.shortcuts.redirect(self.get_success_url())

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            schedule = models.Schedule.objects.filter(
                pk=self.kwargs["schedule_id"],
                user=self.request.user,
            ).first()
            if not schedule:
                raise django.http.Http404(
                    _("You cannot add time to someone else's schedule."),
                )

            return super().dispatch(
                request,
                *args,
                **kwargs,
            )

        raise django.http.Http404(
            _("You cannot view this content."),
        )


class TimeScheduleUpdateView(AccessMixin, django.views.generic.UpdateView):

    model = models.TimeSchedule
    template_name = "schedule/timeschedule_form.html"

    def get_form_class(self):
        return forms.TimeScheduleForm

    def get_success_url(self):
        return django.urls.reverse(
            "schedule:schedule-detail",
            kwargs={"pk": self.object.schedule.id},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_form"] = forms.EventForm(user=self.request.user)
        context["events"] = models.Event.objects.get_events_for_user(
            user=self.request.user,
        )
        context["teachers"] = models.Teacher.objects.get_teachers_for_user(
            user=self.request.user,
        )
        context["schedule"] = self.object.schedule
        return context

    def get_object(self, queryset=None):
        return models.TimeSchedule.objects.get_timeschedule_by_pk_and_user(
            pk=self.kwargs["pk"],
            user=self.request.user,
        )


class TimeScheduleDeleteView(AccessMixin, django.views.generic.View):

    model = models.TimeSchedule

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs.get("pk"))
        except models.TimeSchedule.DoesNotExist:
            raise django.http.Http404(_("TimeSchedule not found"))

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        success_url = django.urls.reverse(
            "schedule:schedule-detail",
            kwargs={"pk": obj.schedule.id},
        )
        obj.delete()
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
    form_class = forms.EventForm

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
        return models.Event.objects.get_events_for_user(user=self.request.user)


class EventUpdateView(AccessMixin, django.views.generic.UpdateView):
    model = models.Event
    template_name = "schedule/event_form.html"
    success_url = django.urls.reverse_lazy("schedule:event-list")
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
        # Убрал, так как instance уже передается в super
        # kwargs["instance"] = self.get_object()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_object"] = self.get_object()
        return context

    def form_valid(self, form):
        print("----- form_valid начало -----")
        print(f"Полученные данные: {form.cleaned_data}")
        print(f"Текущий объект: {self.object}")
        print(
            "ID учителя из формы:"
            f" {form.cleaned_data['teacher'].pk if form.cleaned_data['teacher'] else None}",
        )
        print(
            "ID учителя до сохранения:"
            f" {self.object.teacher.pk if self.object.teacher else None}",
        )

        # Убрал, так как сохранение уже выполняется автоматически
        # response = super().form_valid(form)

        print(
            "ID учителя после сохранения:"
            f" {self.object.teacher.pk if self.object.teacher else None}",
        )
        print("----- form_valid конец -----\n")
        # return response
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
        return models.Teacher.objects.get_teachers_for_user(user=self.request.user)


class TeacherUpdateView(AccessMixin, django.views.generic.UpdateView):

    model = models.Teacher
    form_class = forms.TeacherForm
    template_name = "schedule/teacher_form.html"
    success_url = django.urls.reverse_lazy("schedule:teacher-list")

    def get_object(self, queryset=None):
        if not hasattr(self, "_teacher_object"):
            self._teacher_object = models.Teacher.objects.get_teacher_by_pk_and_user(
                pk=self.kwargs.get(self.pk_url_kwarg),
                user=self.request.user,
            )

        return self._teacher_object

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.get_object()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teacher_object"] = self.get_object()
        return context


class TeacherDeleteView(AccessMixin, django.views.generic.DeleteView):

    model = models.Teacher
    template_name = "schedule/teacher_confirm_delete.html"
    success_url = django.urls.reverse_lazy("schedule:teacher-list")


class NoteCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):

    model = models.Note
    template_name = "schedule/note_form.html"
    success_url = django.urls.reverse_lazy("schedule:note-list")
    form_class = forms.NoteForm

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
        return models.Note.objects.get_notes_for_user(user=self.request.user)


class NoteUpdateView(AccessMixin, django.views.generic.UpdateView):
    model = models.Note
    form_class = forms.NoteForm
    template_name = "schedule/note_form.html"
    success_url = django.urls.reverse_lazy("schedule:note-list")

    def get_object(self, queryset=None):
        if not hasattr(self, "_note_object"):
            self._note_object = (
                models.Note.objects.select_related("user")
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
                .get(pk=self.kwargs.get(self.pk_url_kwarg), user=self.request.user)
            )

        return self._note_object

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["instance"] = self.get_object()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["note_object"] = self.get_object()
        return context


class NoteDeleteView(AccessMixin, django.views.generic.View):

    model = models.Note

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs.get("pk"))
        except models.Note.DoesNotExist:
            raise django.http.Http404(_("Note not found"))

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        success_url = django.urls.reverse_lazy("schedule:note-list")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return django.http.JsonResponse({"status": "ok"})

        return django.http.HttpResponseRedirect(success_url)
