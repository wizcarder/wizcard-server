# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template.context import RequestContext
from .utils import slug2id
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from base_entity.views import BaseEntityComponentViewSet
from entity.models import Event


class NotificationViewSet(BaseEntityComponentViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    #
    # def get_queryset(self):
    #     """
    #     we have to filter on the celery read part of the notif table.
    #     """
    #     pass

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()



