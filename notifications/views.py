# Create your views here.
from notifications.models import SyncNotification
from notifications.serializers import SyncNotificationSerializer
from base_entity.views import BaseEntityComponentViewSet
from rest_framework.response import Response
from rest_framework import status
from wizserver import verbs

import pdb


class NotificationViewSet(BaseEntityComponentViewSet):
    queryset = SyncNotification.objects.filter(notif_type=verbs.NOTIF_ENTITY_BROADCAST)
    serializer_class = SyncNotificationSerializer

    def get_queryset(self):
        """
        we have to filter on the celery read part of the notif table.
        """
        return SyncNotification.objects.filter(notif_type=verbs.NOTIF_ENTITY_BROADCAST)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response(status=status.HTTP_200_OK)

    def get_serializer_context(self):
        return {'user': self.request.user}



