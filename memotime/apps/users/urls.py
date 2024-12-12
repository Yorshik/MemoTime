import django.contrib.auth.views
import django.urls

import apps.users.views

app_name = "users"

urlpatterns = [
    django.urls.path(
        "activate/resend/",
        apps.users.views.ActivateResendView.as_view(),
        name="activate-resend",
    ),
    django.urls.path(
        "activate/<pk>/",
        apps.users.views.ActivateView.as_view(),
        name="activate",
    ),
    django.urls.path(
        "login/",
        django.contrib.auth.views.LoginView.as_view(
            template_name="users/login.html",
        ),
        name="login",
    ),
    django.urls.path(
        "logout/",
        django.contrib.auth.views.LogoutView.as_view(
            template_name="users/logout.html",
        ),
        name="logout",
    ),
    django.urls.path(
        "password_change/",
        django.contrib.auth.views.PasswordChangeView.as_view(
            template_name="users/password_change.html",
        ),
        name="password-change",
    ),
    django.urls.path(
        "password_change/done/",
        django.contrib.auth.views.PasswordChangeDoneView.as_view(
            template_name="users/password_change_done.html",
        ),
        name="password-change-done",
    ),
    django.urls.path(
        "password_reset/",
        django.contrib.auth.views.PasswordResetView.as_view(
            template_name="users/password_reset.html",
            email_template_name="users/email/password_reset_email.html",
            success_url=django.urls.reverse_lazy("users:password-reset-done"),
        ),
        name="password-reset",
    ),
    django.urls.path(
        "password_reset/done/",
        django.contrib.auth.views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html",
        ),
        name="password-reset-done",
    ),
    django.urls.path(
        "reset/done/",
        django.contrib.auth.views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html",
        ),
        name="password-reset-complete",
    ),
    django.urls.path(
        "reset/<uidb64>/<token>/",
        django.contrib.auth.views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
        ),
        name="password-reset-confirm",
    ),
    django.urls.path(
        "signup/",
        apps.users.views.RegisterView.as_view(),
        name="signup",
    ),
]
