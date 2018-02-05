# Create your views here.
from notifications.models import AsyncNotification
from notifications.serializers import AsyncNotificationSerializer
from base_entity.views import BaseEntityComponentViewSet
from rest_framework.response import Response
from rest_framework import status
from wizserver import verbs

import pdb


class NotificationViewSet(BaseEntityComponentViewSet):
    queryset = AsyncNotification.objects.filter(notif_type=verbs.NOTIF_ENTITY_BROADCAST)
    serializer_class = AsyncNotificationSerializer

    def get_queryset(self):
        """
        we have to filter on the celery read part of the notif table.
        """

        # AA: Fix. Should probably restrict to owned rows ?
        return AsyncNotification.objects.filter(notif_type=verbs.NOTIF_ENTITY_BROADCAST)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response(status=status.HTTP_200_OK)

    def get_serializer_context(self):
        return {'user': self.request.user}



