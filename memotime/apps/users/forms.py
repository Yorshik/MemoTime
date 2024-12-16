import captcha.fields
import django.conf
import django.contrib.auth.forms
import django.core.exceptions
import django.forms
import django.utils.timezone
from django.utils.translation import gettext_lazy as _

import apps.core.forms
import apps.users.models

__all__ = ()


class UserCreationForm(
    apps.core.forms.BaseForm,
    django.contrib.auth.forms.UserCreationForm,
):
    captcha = captcha.fields.CaptchaField()

    def clean_username(self):
        username = self.cleaned_data[apps.users.models.User.username.field.name].lower()
        new = apps.users.models.User.objects.filter(username=username)
        if new.count():
            raise django.core.exceptions.ValidationError(
                _("Пользователь уже существует"),
            )

        return username

    def clean_password2(self):
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]

        if password1 and password2 and password1 != password2:
            raise django.core.exceptions.ValidationError(
                _("Пароли не совпадают"),
            )

        return password2

    def save(self, commit=True, active=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data[apps.users.models.User.email.field.name]
        user.is_active = active

        if commit:
            user.save()

        return user

    class Meta(django.contrib.auth.forms.UserCreationForm.Meta):
        model = apps.users.models.User
        fields = (
            apps.users.models.User.username.field.name,
            apps.users.models.User.email.field.name,
            "password1",
            "password2",
        )


class LoginForm(django.contrib.auth.forms.AuthenticationForm):
    captcha = captcha.fields.CaptchaField()
