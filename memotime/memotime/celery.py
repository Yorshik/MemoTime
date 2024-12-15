import os

from celery import Celery

__all__ = ()


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "memotime.settings")
app = Celery("memotime")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
