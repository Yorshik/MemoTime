import django.conf
import django.contrib.auth.models
import django.contrib.messages
import django.core.mail
import django.shortcuts
import django.urls
from django.utils.translation import gettext_lazy as _
import django.views.generic.edit

import apps.feedback.forms

__all__ = ()


class FeedbackView(django.views.generic.edit.FormView):
    template_name = "feedback/feedback.html"
    form_class = apps.feedback.forms.ProfileUpdateMultiForm
    success_url = django.urls.reverse_lazy("feedback:feedback")

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), "files": self.request.FILES}

    def _send_confirmation_email(self, author, feedback_text):
        django.core.mail.send_mail(
            _(f"Спасибо за отзыв, {author.name}!"),
            feedback_text,
            django.conf.settings.EMAIL_HOST_USER,
            [author.mail],
            fail_silently=False,
        )

    def form_valid(self, form):
        author = form["author"].save(commit=False)
        if not self.request.user.is_anonymous:
            author.user = self.request.user

        author.save()
        feedback = form["feedback"].save(commit=False)
        feedback.personal_data = author
        feedback.save()
        form["files_form"].save(feedback)
        self._send_confirmation_email(
            author,
            form["feedback"].cleaned_data["text"],
        )

        django.contrib.messages.success(
            self.request,
            _("Спасибо! Ваш отзыв был успешно отправлен."),
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        if not form.is_valid():
            django.contrib.messages.error(
                self.request,
                _("Произошла ошибка при отправке формы."),
            )

        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
