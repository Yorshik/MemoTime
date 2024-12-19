# memotime/__init__.py

from memotime.celery import app as celery_app

__all__ = ("celery_app",)
