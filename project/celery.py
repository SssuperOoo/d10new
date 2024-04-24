import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'action_every_monday8am': {
        'task': 'news.tasks.weekly_post',
        'schedule': crontab(hour=5, minute=0, day_of_week='monday')
    }
}

app.conf.timezone = "UTC"