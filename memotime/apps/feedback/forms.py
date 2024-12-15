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
            apps.feedback.models.PersonalData.mail.field.name,
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
                "The content of the appeal",
            ),
        }
        exclude = [
            apps.feedback.models.Feedback.created_on.field.name,
            apps.feedback.models.Feedback.status.field.name,
            apps.feedback.models.Feedback.personal_data.field.name,
        ]


class MultipleFileInput(django.forms.ClearableFileInput):
    template_name = "feedback/widgets/multiple_file_input.html"
    allow_multiple_selected = True

    class Media:
        css = {"all": ("css/custom_file_input.css",)}
        js = ("js/custom_file_input.js",)


class MultipleFileField(django.forms.FileField):
    def __init__(self, *args, max_size=5 * 1024 * 1024, max_files=5, **kwargs):
        widget = MultipleFileInput(
            attrs={
                "data_max_size": max_size,
                "data_max_files": max_files,
            },
        )
        kwargs.setdefault("widget", widget)
        super().__init__(*args, **kwargs)
        self.max_size = max_size
        self.max_files = max_files

    def clean(self, data, initial=None):
        if not data:
            return []

        files = []
        if isinstance(data, (list, tuple)):
            files.extend(data)
        elif hasattr(data, "name"):
            files.append(data)

        if self.max_files and len(files) > self.max_files:
            raise django.core.exceptions.ValidationError(
                _(
                    "The maximum number of files that can be uploaded: %(max_files)d.",
                ),
                params={"max_files": self.max_files},
            )

        cleaned_files = []
        for file in files:
            if file:
                cleaned_file = super().clean(file, initial)
                if hasattr(cleaned_file, "size") and cleaned_file.size > self.max_size:
                    raise django.core.exceptions.ValidationError(
                        _(
                            "The maximum file size that can be"
                            " uploaded: %(max_size).1f MB.",
                        ),
                        params={"max_size": self.max_size / (1024 * 1024)},
                    )

                cleaned_files.append(cleaned_file)

        return cleaned_files


class FilesForm(apps.core.forms.BaseForm, django.forms.ModelForm):
    files = MultipleFileField(
        label=_("Attached files"),
        required=False,
        max_size=10 * 1024 * 1024,
        max_files=5,
    )

    class Meta:
        model = apps.feedback.models.FeedbackFile
        fields = ["files"]

    def __init__(self, *args, **kwargs):
        self.files = kwargs.pop("files", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.files and (files_list := self.files.getlist("files")):
            cleaned_data["files"] = files_list

        return cleaned_data

    def save(self, feedback):
        files = self.cleaned_data.get("files", [])
        if not isinstance(files, (list, tuple)):
            files = [files] if files else []

        return [
            apps.feedback.models.FeedbackFile.objects.create(
                file=file,
                feedback=feedback,
            )
            for file in files
            if file
        ]


class ProfileUpdateMultiForm(
    apps.core.forms.BaseForm,
    betterforms.multiform.MultiForm,
):
    form_classes = {
        "author": AuthorForm,
        "feedback": FeedbackForm,
        "files_form": FilesForm,
    }

    def __init__(self, *args, **kwargs):
        files = kwargs.pop("files", None)
        super().__init__(*args, **kwargs)
        if files:
            self.forms["files_form"].files = files
