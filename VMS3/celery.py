from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VMS3.settings')

app = Celery('VMS3')

# Using Redis as the broker
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(
    broker_url='redis://localhost:6379/0',  # Use Redis as the broker
)
app.autodiscover_tasks()
