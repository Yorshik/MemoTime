import pathlib

import decouple
from django.utils.translation import gettext_lazy as _

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


SECRET_KEY = decouple.config("MEMOTIME_SECRET_KEY", default="YOURSECRETKEY")

DEBUG = decouple.config(
    "DJANGO_DEBUG",
    default=False,
    cast=bool,
)

ALLOWED_HOSTS = decouple.config(
    "MEMOTIME_ALLOWED_HOSTS",
    default="*",
    cast=decouple.Csv(),
)

INSTALLED_APPS = [
    # Самописные приложения
    # Нативные Django-приложения # noqa: CM001
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Внешние приложения
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE.append(
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )
    INSTALLED_APPS.append(
        "debug_toolbar",
    )
    INTERNAL_IPS = [
        "127.0.0.1",
    ]

ROOT_URLCONF = "memotime.urls"

TEMPLATES_DIR = [BASE_DIR / "templates/"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "memotime.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": decouple.config("MEMOTIME_DATABASE_NAME", default="MemoTime"),
        "USER": decouple.config("MEMOTIME_DATABASE_USER", default=None),
        "PASSWORD": decouple.config("MEMOTIME_DATABASE_PASSWORD", default=None),
        "HOST": decouple.config("MEMOTIME_DATABASE_HOST", default="localhost"),
        "PORT": decouple.config("MEMOTIME_DATABASE_PORT", default="5432"),
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-ru"

LANGUAGES = [
    ("ru-ru", _("Russian")),
    ("en-us", _("English")),
]


TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [BASE_DIR / "locale/"]

STATIC_URL = "static/"

STATICFILES_DIRS = [BASE_DIR / "static_dev"]

STATIC_ROOT = BASE_DIR / "static"

MEDIA_ROOT = BASE_DIR / "media/"

MEDIA_URL = "media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
