import django.urls

import apps.feedback.views

app_name = "feedback"

urlpatterns = [
    django.urls.path(
        "",
        apps.feedback.views.FeedbackView.as_view(),
        name="feedback",
    ),
]
