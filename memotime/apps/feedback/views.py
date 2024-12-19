import django.contrib.auth.models
import django.contrib.messages
import django.shortcuts
import django.urls
import django.utils.translation
from django.utils.translation import gettext_lazy as _
import django.views.generic.edit

import apps.core.celery_tasks
import apps.feedback.forms

__all__ = ()


class FeedbackView(django.views.generic.edit.FormView):
    template_name = "feedback/feedback.html"
    form_class = apps.feedback.forms.ProfileUpdateMultiForm
    success_url = django.urls.reverse_lazy("feedback:feedback")

    def form_valid(self, form):
        author = form["author"].save(commit=False)
        if not self.request.user.is_anonymous:
            author.user = self.request.user

        author.save()
        feedback = form["feedback"].save(commit=False)
        feedback.personal_data = author
        feedback.save()

        apps.core.celery_tasks.send_email_task.delay(
            _(f"Thanks for the feedback, {author.name}!"),
            "feedback/email/feedback_confirmation.html",
            {
                "author_name": author.name,
                "feedback_text": form["feedback"].cleaned_data["text"],
            },
            [author.email],
        )

        django.contrib.messages.success(
            self.request,
            _("Thank you! Your feedback has been sent successfully."),
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        if not form.is_valid():
            django.contrib.messages.error(
                self.request,
                _("An error occurred while submitting the form."),
            )

        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
