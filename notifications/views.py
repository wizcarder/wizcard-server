# Create your views here.
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from base_entity.views import BaseEntityComponentViewSet
from rest_framework.response import Response
from rest_framework import status

import pdb


class NotificationViewSet(BaseEntityComponentViewSet):
    queryset = Notification.objects.filter(is_async=True)
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """
        we have to filter on the celery read part of the notif table.
        """
        return Notification.objects.filter(is_async=True)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response(status=status.HTTP_200_OK)



