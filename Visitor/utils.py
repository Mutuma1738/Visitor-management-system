from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import models
from models import *
from datetime import timedelta
from django.contrib.auth.models import User
import os
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail


def send_email(subject, to, message):

    from_email = os.getenv("SMTP_USERNAME", settings.EMAIL_HOST_USER)  # Default to settings if env var not set
    send_mail(
        subject,
        message,
        from_email=from_email,  # Use the dynamically fetched email here
        recipient_list=[VisitLog.employee.email],
        fail_silently=False,
    )
