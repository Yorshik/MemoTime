import django.conf
import django.contrib.auth
import django.contrib.auth.mixins
import django.contrib.auth.views
import django.contrib.messages
import django.core.mail
import django.core.signing
from django.db.models import BooleanField, Case, Q, Value, When
import django.http
import django.shortcuts
import django.urls
import django.utils.timezone
from django.utils.translation import gettext_lazy as _
import django.views.generic

import apps.core.celery_tasks
import apps.users.forms
import apps.users.models
import apps.users.tokens

__all__ = ()


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

            apps.core.celery_tasks.send_email_task.delay(
                _(f"Account activation, {user.username}"),
                "users/email/user_activation_email.html",
                {"link": link, "username": user.username},
                [user.email],
            )

            django.contrib.messages.success(
                self.request,
                _("An account activation link has been sent to your email address."),
            )
        else:
            django.contrib.messages.success(
                self.request,
                _("You have successfully registered."),
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

            user = apps.users.models.User.objects.filter(pk=token["user_id"]).first()
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

        if not token_data or token_data.get("status") not in ["valid", "expired"]:
            django.contrib.messages.error(request, _("Invalid activation token."))
            return django.shortcuts.redirect("users:signup")

        user = apps.users.models.User.objects.filter(pk=token_data["user_id"]).first()

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
            new_token = apps.users.tokens.make_token(user, operation="activate")
        else:
            return django.http.HttpResponseServerError()

        link = request.build_absolute_uri(
            django.urls.reverse("users:activate", args=[new_token]),
        )

        apps.core.celery_tasks.send_email_task.delay(
            _(f"Account reactivation, {user.username}"),
            "users/email/user_reactivation_email.html",
            {"link": link, "username": user.username},
            [user.email],
        )

        django.contrib.messages.success(
            request,
            _("A new activation link has been sent to your email address."),
        )

        return django.shortcuts.redirect("users:login")


class ProfileView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.UpdateView,
):
    template_name = "users/profile.html"
    form_class = apps.users.forms.UserProfileForm
    success_url = django.urls.reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        django.contrib.messages.success(
            self.request,
            _("Профиль успешно обновлен"),
        )
        return super().form_valid(form)


class CustomPasswordResetDoneView(django.contrib.auth.views.PasswordResetDoneView):
    template_name = "users/password_reset_done.html"

    def get_context_data(self, **kwargs):
        self.request.session["password_reset_done"] = True
        return super().get_context_data(**kwargs)


class CustomPasswordResetConfirmView(
    django.contrib.auth.views.PasswordResetConfirmView,
):
    template_name = "users/password_reset_confirm.html"

    def form_valid(self, form):
        django.contrib.messages.success(
            self.request,
            _("Пароль успешно изменен"),
        )
        self.request.session["password_reset_complete"] = True
        del self.request.session["password_reset_confirm"]
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        self.request.session["password_reset_confirm"] = True
        return super().get_context_data(**kwargs)


class CustomPasswordResetCompleteView(
    django.contrib.auth.views.PasswordResetCompleteView,
):
    template_name = "users/password_reset_complete.html"

    def dispatch(self, *args, **kwargs):
        if not self.request.session.get("password_reset_complete"):
            return django.shortcuts.redirect(
                django.urls.reverse_lazy("users:password-reset"),
            )

        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        self.request.session["password_reset_complete"] = True
        return super().get_context_data(**kwargs)


class CustomPasswordResetView(django.contrib.auth.views.PasswordResetView):
    template_name = "users/password_reset.html"
    email_template_name = "users/email/password_reset_email.html"
    form_class = apps.users.forms.CustomPasswordResetForm
    success_url = django.urls.reverse_lazy("users:password-reset-done")


class LoginView(django.contrib.auth.views.LoginView):
    form_class = apps.users.forms.LoginForm
    redirect_authenticated_user = True


class GroupCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):
    model = apps.users.models.Group
    form_class = apps.users.forms.GroupCreateForm
    template_name = "users/group_create.html"
    success_url = django.urls.reverse_lazy("users:group-list")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        super().form_valid(form)
        self.object.user_set.add(
            self.request.user,
        )
        return super().form_valid(form)


class GroupListView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.ListView,
):
    model = apps.users.models.Group
    template_name = "users/group_list.html"
    context_object_name = "groups"

    def get_queryset(self):
        user = self.request.user

        return (
            apps.users.models.Group.objects.filter(Q(creator=user) | Q(user=user))
            .prefetch_related("user_set")
            .annotate(
                is_creator=Case(
                    When(creator=user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
            )
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["created_groups"] = context["groups"].filter(is_creator=True)
        context["member_groups"] = context["groups"].filter(is_creator=False)
        return context


class GroupUpdateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.UpdateView,
):
    model = apps.users.models.Group
    form_class = apps.users.forms.GroupUpdateForm
    template_name = "users/group_update.html"
    success_url = django.urls.reverse_lazy("users:group-list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user != obj.creator:
            raise django.http.Http404(_("You are not the creator of this group."))

        return obj
