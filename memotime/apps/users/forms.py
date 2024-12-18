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

normalizer = apps.users.email_normalizer.EmailNormalizer()
User = django.contrib.auth.get_user_model()


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
                _("User already exists"),
            )

        return username

    def clean_password2(self):
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]

        if password1 and password2 and password1 != password2:
            raise django.core.exceptions.ValidationError(
                _("Passwords do not match"),
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


class UserProfileForm(
    apps.core.forms.BaseForm,
    django.contrib.auth.forms.UserChangeForm,
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields[apps.users.models.User.password.field.name]

    class Meta(django.contrib.auth.forms.UserChangeForm.Meta):
        model = apps.users.models.User
        fields = (
            apps.users.models.User.username.field.name,
            apps.users.models.User.email.field.name,
            apps.users.models.User.first_name.field.name,
            apps.users.models.User.last_name.field.name,
            apps.users.models.User.timezone.field.name,
            apps.users.models.User.is_email_subscribed.field.name,
            apps.users.models.User.image.field.name,
        )
        widgets = {
            "image": django.forms.FileInput,
        }

    def clean_username(self):
        username = self.cleaned_data[apps.users.models.User.username.field.name].lower()
        if username != self.instance.username:
            new = apps.users.models.User.objects.filter(username=username)
            if new.count():
                raise django.core.exceptions.ValidationError(
                    _("Пользователь уже существует"),
                )

        return username

    def clean_email(self):
        email = self.cleaned_data[apps.users.models.User.email.field.name]
        if email != self.instance.email:
            new = apps.users.models.User.objects.filter(email=email)
            if new.count():
                raise django.core.exceptions.ValidationError(
                    _("Пользователь с таким email уже существует"),
                )

        return email

    def clean_password_change_link(self):
        return self.instance.password


class CustomPasswordResetForm(django.contrib.auth.forms.PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        normalized_email = normalizer.normalize(email)

        if not User.objects.filter(email=normalized_email).exists():
            raise django.forms.ValidationError(
                "Пользователя с такой почтой не существует.",
            )

        return normalized_email

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.html",
        use_https=False,
        token_generator=None,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        email = self.cleaned_data["email"]

        for user in self.get_users(email):
            if not domain_override:
                current_site = django.contrib.sites.shortcuts.get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override

            context = {
                "email": email,
                "domain": domain,
                "site_name": site_name,
                "uid": django.utils.http.urlsafe_base64_encode(
                    django.utils.encoding.force_bytes(user.pk),
                ),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                email,
                html_email_template_name=html_email_template_name,
            )


class LoginForm(django.contrib.auth.forms.AuthenticationForm):
    captcha = captcha.fields.CaptchaField()
