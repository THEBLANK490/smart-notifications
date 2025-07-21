import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings

from smartnotify.settings.configurations import BaseConfiguration as project_config


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartnotify.settings.base")

app = Celery("smartnotify")  # Replace 'your_project' with your project's name.

# Configure Celery using settings from Django settings.py.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load tasks from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(
    broker_url= project_config.CELERY_BROKER_URL.value,  
    timezone='Asia/Kathmandu',     
)

app.conf.beat_schedule = {
    "send-weekly-summary": {
        "task": "apps.core.tasks.send_weekly_summary",
        "schedule": crontab(day_of_week="sunday", hour=8, minute=0),
    },
}