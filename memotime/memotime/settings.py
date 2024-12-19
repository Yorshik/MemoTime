import pathlib
import re

import decouple
from django.utils.translation import gettext_lazy as _

__all__ = ()

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


SECRET_KEY = decouple.config("MEMOTIME_SECRET_KEY", default="YOURSECRETKEY")

DEBUG = decouple.config(
    "MEMOTIME_DEBUG",
    default=False,
    cast=bool,
)

DEFAULT_USER_IS_ACTIVE = decouple.config(
    "MEMOTIME_DEFAULT_USER_IS_ACTIVE",
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
    "apps.core.apps.CoreConfig",
    "apps.feedback.apps.FeedbackConfig",
    "apps.homepage.apps.HomepageConfig",
    "apps.schedule.apps.ScheduleConfig",
    "apps.users.apps.UsersConfig",
    # Нативные Django-приложения :noqa CM001
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
    # Внешние приложения,
    "captcha",
    "django_ratelimit",
    "django_redis",
    "django_celery_results",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "memotime.middleware.RedirectBlockedUserMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

if DEBUG:
    INSTALLED_APPS += ("debug_toolbar",)
    MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)
    INTERNAL_IPS = ["127.0.0.1"]


ROOT_URLCONF = "memotime.urls"

TEMPLATES_DIR = [BASE_DIR / "templates"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": TEMPLATES_DIR,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "memotime.wsgi.application"


def postgres_port_cast(value):
    match = re.search(r":(\d+)", value)
    if match:
        return int(match.group(1))

    return value


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": decouple.config("POSTGRES_DB", default="postgres"),
        "USER": decouple.config("POSTGRES_USER", default="postgres"),
        "PASSWORD": decouple.config("POSTGRES_PASSWORD", default=None),
        "HOST": decouple.config("POSTGRES_HOST", default="postgres"),
        "PORT": decouple.config(
            "POSTGRES_PORT",
            default="5432",
            cast=postgres_port_cast,
        ),
    },
}

AUTH_USER_MODEL = "users.User"

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


LOGIN_URL = "/users/login/"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = "/users/login/"

PASSWORD_RESET_REDIRECT_URL = "/users/login/"

PASSWORD_CHANGE_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = [
    "apps.users.backends.EmailBackend",
]


LANGUAGE_CODE = "en-us"

LANGUAGES = [
    ("ru-ru", _("Russian")),
    ("en-us", _("English")),
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [BASE_DIR / "locale/"]


STATIC_URL = "static/"

STATICFILES_DIRS = [BASE_DIR / "static_dev"]

STATIC_ROOT = BASE_DIR / "static"


MEDIA_ROOT = BASE_DIR / "media/"

MEDIA_URL = "media/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.yandex.ru"
EMAIL_PORT = 465
EMAIL_HOST_USER = decouple.config("MEMOTIME_EMAIL", default="Your email")
EMAIL_HOST_PASSWORD = decouple.config(
    "MEMOTIME_EMAIL_PASSWORD",
    default="Your app password",
)
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = f"MemoTime <{EMAIL_HOST_USER}>"


RATE_LIMIT = decouple.config("MEMOTIME_RATE_LIMIT", default=False)
RATE_LIMIT_TIMEOUT = decouple.config(
    "MEMOTIME_RATE_LIMIT_TIMEOUT",
    default=60 * 60 * 24,
    cast=int,
)


CAPTCHA_LENGTH = 6
CAPTCHA_IMAGE_SIZE = (300, 120)
CAPTCHA_FONT_SIZE = 40


CELERY_BROKER_URL = decouple.config(
    "CELERY_BROKER_URL",
    default="redis://redis:6379/0",
)
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "django-cache"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_MAX_LOOP_INTERVAL = 15

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CELERY_BROKER_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        },
    },
}
