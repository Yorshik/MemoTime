import betterforms.multiform
import django.contrib.auth.models
import django.core.exceptions
import django.forms
from django.utils.translation import gettext_lazy as _

import apps.core.forms
import apps.feedback.models

__all__ = ()


class AuthorForm(apps.core.forms.BaseForm, django.forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[apps.feedback.models.PersonalData.name.field.name].initial = None
        self.fields[apps.feedback.models.PersonalData.name.field.name].required = False

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get(apps.feedback.models.PersonalData.name.field.name):
            cleaned_data[apps.feedback.models.PersonalData.name.field.name] = _(
                "Anonymous",
            )

        return cleaned_data

    class Meta:
        model = apps.feedback.models.PersonalData
        fields = (
            apps.feedback.models.PersonalData.name.field.name,
            apps.feedback.models.PersonalData.email.field.name,
        )
        widgets = {
            apps.feedback.models.PersonalData.name.field.name: django.forms.TextInput(
                attrs={"placeholder": _(" ")},
            ),
            apps.feedback.models.PersonalData.mail.field.name: django.forms.EmailInput(
                attrs={"placeholder": _(" ")},
            ),
        }


class FeedbackForm(apps.core.forms.BaseForm, django.forms.ModelForm):
    class Meta:
        model = apps.feedback.models.Feedback
        fields = (apps.feedback.models.Feedback.text.field.name,)
        labels = {apps.feedback.models.Feedback.text.field.name: _("Description")}
        help_texts = {
            apps.feedback.models.Feedback.text.field.name: _(
                "Content of your feedback",
            ),
        }
        exclude = [
            apps.feedback.models.Feedback.created_on.field.name,
            apps.feedback.models.Feedback.status.field.name,
            apps.feedback.models.Feedback.personal_data.field.name,
        ]


class ProfileUpdateMultiForm(
    apps.core.forms.BaseForm,
    betterforms.multiform.MultiForm,
):
    form_classes = {
        "author": AuthorForm,
        "feedback": FeedbackForm,
    }
