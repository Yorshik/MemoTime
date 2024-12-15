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
        "password_reset/done/",
        apps.users.views.CustomPasswordResetDoneView.as_view(),
        name="password-reset-done",
    ),
    django.urls.path(
        "password_reset/",
        apps.users.views.CustomPasswordResetView.as_view(),
        name="password-reset",
    ),
    django.urls.path(
        "password_reset/done/",
        apps.users.views.CustomPasswordResetDoneView.as_view(),
        name="password-reset-done",
    ),
    django.urls.path(
        "reset/done/",
        apps.users.views.CustomPasswordResetCompleteView.as_view(),
        name="password-reset-complete",
    ),
    django.urls.path(
        "reset/<uidb64>/<token>/",
        apps.users.views.CustomPasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    django.urls.path(
        "profile/",
        apps.users.views.ProfileView.as_view(),
        name="profile",
    ),
    django.urls.path(
        "signup/",
        apps.users.views.RegisterView.as_view(),
        name="signup",
    ),
]
