import django.urls

from apps.schedule import views

app_name = "schedule"

urlpatterns = [
    django.urls.path(
        "create/",
        views.ScheduleCreateView.as_view(),
        name="schedule-create",
    ),
    django.urls.path(
        "",
        views.ScheduleListView.as_view(),
        name="schedule-list",
    ),
    django.urls.path(
        "<int:pk>/update/",
        views.ScheduleUpdateView.as_view(),
        name="schedule-update",
    ),
    django.urls.path(
        "<int:pk>/delete/",
        views.ScheduleDeleteView.as_view(),
        name="schedule-delete",
    ),
    django.urls.path(
        "teacher/create/",
        views.TeacherCreateView.as_view(),
        name="teacher-create",
    ),
    django.urls.path(
        "<int:pk>/",
        views.ScheduleDetailView.as_view(),
        name="schedule-detail",
    ),
    django.urls.path(
        "<int:schedule_id>/timeschedule/create/",
        views.TimeScheduleCreateView.as_view(),
        name="timeschedule-create",
    ),
    django.urls.path(
        "timeschedule/<int:pk>/update/",
        views.TimeScheduleUpdateView.as_view(),
        name="timeschedule-update",
    ),
    django.urls.path(
        "timeschedule/<int:pk>/delete/",
        views.TimeScheduleDeleteView.as_view(),
        name="timeschedule-delete",
    ),
    django.urls.path(
        "event/create/",
        views.EventCreateView.as_view(),
        name="event-create",
    ),
]
