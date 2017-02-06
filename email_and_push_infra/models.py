from django.db import models
from wizcardship.models import Wizcard
import datetime

# Create your models here.


class EmailAndPush(models.Model):
    wizcard = models.OneToOneField(Wizcard, related_name='email_and_push')
    onboarding_sent = models.BooleanField(default=False)
    pending_invite_exists = models.BooleanField(default=False)
    pending_invites_sent = models.DateField(default=datetime.date.today)
    new_connection_exists = models.BooleanField(default=False)
    new_connections_sent = models.DateField(default=datetime.date.today)
    new_recommendations_available = models.BooleanField(default=False)
    new_recommendations_sent = models.DateField(default=datetime.date.today)
