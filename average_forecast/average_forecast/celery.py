import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "average_forecast.settings")
app = Celery("average_forecast")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()