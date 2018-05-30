
# Create your views here.
from base_entity.models import BaseEntity, BaseEntityComponent
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from wizserver import verbs
import pdb


class BaseEntityViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        queryset = BaseEntity.objects.owners_entities(user)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}

    def perform_destroy(self, instance):
        parents = instance.get_parent_entities()

        if parents and not instance.can_destroy_when_linked():
            return Response(data="Instance is being used", status=status.HTTP_403_FORBIDDEN)

        # notif stuff. This will probably only happen for Event delete/expire since others will get rejected
        # on account of being linked to a parent.
        BaseEntityComponent.objects.notify_via_entity_parent(
            instance,
            verbs.WIZCARD_ENTITY_DELETE,
            verbs.NOTIF_OPERATION_DELETE
        )

        instance.delete()
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

    def update(self, request, pk=None, partial=True):
        inst = get_object_or_404(BaseEntity, pk=pk)
        ser = self.get_serializer_class()
        serializer = ser(inst, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseEntityComponentViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        user = self.request.user
        queryset = BaseEntityComponent.objects.owners_entities(user, entity_type=None)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}

    def perform_destroy(self, instance):
        parents = instance.get_parent_entities()

        if parents and not instance.can_destroy_when_linked():
            return Response(data="Instance is being used", status=status.HTTP_403_FORBIDDEN)
        else:
            instance.related.all().delete()
            instance.delete()
            return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

