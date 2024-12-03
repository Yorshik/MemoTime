import django.conf
import django.contrib.auth.decorators
import django.contrib.auth.mixins
import django.contrib.messages
import django.core.mail
import django.core.signing
import django.http
import django.shortcuts
import django.urls
import django.utils.timezone
from django.utils.translation import gettext_lazy as _
import django.views.generic

import apps.users.forms
import apps.users.models
import apps.users.tokens

__all__ = ()

signer = django.core.signing.TimestampSigner()


class RegisterView(django.views.generic.edit.FormView):
    template_name = "users/signup.html"
    form_class = apps.users.forms.UserCreationForm
    success_url = django.urls.reverse_lazy("users:signup")

    def form_valid(self, form):
        user = form.save(active=django.conf.settings.DEFAULT_USER_IS_ACTIVE)
        if not user.is_active:
            link = self.request.build_absolute_uri(
                django.urls.reverse(
                    "users:activate",
                    args=[apps.users.tokens.make_token(user)],
                ),
            )
            django.core.mail.send_mail(
                _(f"Активация учетной записи, {user.username}"),
                f"{link}\n{user.username}",
                django.conf.settings.SPAM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            django.contrib.messages.success(
                self.request,
                _(
                    "Ссылка для активации учетной записи отправлена на указанный email",
                ),
            )
        else:
            django.contrib.messages.success(
                self.request,
                _("Вы успешно зарегистрировались"),
            )

        return super().form_valid(form)


class ActivateView(django.views.View):
    template_name = "users/activation.html"

    def get(self, request, pk, *args, **kwargs):
        token = apps.users.tokens.check_token(pk)
        if token:
            if token["status"] == "expired":
                return django.shortcuts.render(
                    request,
                    self.template_name,
                    {"activation_status": "expired", "token": pk},
                )

            user = apps.users.models.User.objects.filter(
                pk=token["user_id"],
            ).first()
            if user:
                if user.is_active:
                    return django.shortcuts.render(
                        request,
                        self.template_name,
                        {"activation_status": "already_activated"},
                    )

                user.is_active = True
                user.save()
                return django.shortcuts.render(
                    request,
                    self.template_name,
                    {"activation_status": "success"},
                )

            return django.shortcuts.render(
                request,
                self.template_name,
                {"activation_status": "not_found"},
            )

        return django.http.HttpResponseNotFound()


class ActivateResendView(django.views.View):
    def post(self, request, *args, **kwargs):
        token = request.POST.get("token")
        if not token:
            return django.http.HttpResponseBadRequest()

        token_data = apps.users.tokens.check_token(token)

        if not token_data or token_data.get("status") not in [
            "valid",
            "expired",
        ]:
            django.contrib.messages.error(
                request,
                _("Недействительный токен активации."),
            )
            return django.shortcuts.redirect("users:signup")

        user = apps.users.models.User.objects.filter(
            pk=token_data["user_id"],
        ).first()

        if not user:
            return django.shortcuts.render(
                request,
                "users/activation.html",
                {"activation_status": "not_found"},
            )

        if user.is_active:
            return django.shortcuts.render(
                request,
                "users/activation.html",
                {"activation_status": "already_activated"},
            )

        if token_data["operation"] == "unblock":
            new_token = apps.users.tokens.make_token(user, operation="unblock")
        elif token_data["operation"] == "activate":
            new_token = apps.users.tokens.make_token(
                user,
                operation="activate",
            )
        else:
            return django.http.HttpResponseServerError()

        link = request.build_absolute_uri(
            django.urls.reverse(
                "users:activate",
                args=[new_token],
            ),
        )
        django.core.mail.send_mail(
            _(f"Повторная активация учетной записи, {user.username}"),
            f"{link}\n{user.username}",
            django.conf.settings.SPAM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        django.contrib.messages.success(
            request,
            _("Новая ссылка для активации отправлена на ваш email."),
        )

        return django.shortcuts.redirect("users:login")
