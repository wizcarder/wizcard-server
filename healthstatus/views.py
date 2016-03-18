""" .. autofunction:: wizconnection_request

.. autofunction:: wizconnection_accept

.. autofunction:: wizconnection_decline

.. autofunction:: wizconnection_cancel

.. autofunction:: wizconnection_delete

.. autofunction:: user_block

.. autofunction:: user_unblock
"""
import json
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth.models import User
from django.core import serializers
from django.core.files.storage import default_storage
from django.contrib.contenttypes.models import ContentType
from userprofile.models import UserProfile
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings


class HealthStatusHandler(View):
    def get(self,request,*args, **kwargs):
        self.request = request
        username = "Healthcheck"
        user, created = User.objects.get_or_create(username=username)
        if user:
            response = HttpResponse("Healthcheck succeeded")
            return response
        else:
            response = HttpResponse("Healthcheck Failed", status=404)
            return response



healthstatus_handler = HealthStatusHandler.as_view()
#wizconnection_request = login_required(WizConnectionRequestView.as_view())
