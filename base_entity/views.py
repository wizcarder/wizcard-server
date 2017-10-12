
# Create your views here.
from base_entity.models import BaseEntity, BaseEntityComponent
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.http import Http404
from django.shortcuts import get_object_or_404

import pdb

class BaseEntityViewSet(viewsets.ModelViewSet):


    def get_object_or_404(self, *args, **kwargs):
        return get_object_or_404(BaseEntity, *args, **kwargs)


    def get_queryset(self):
        user = self.request.user
        queryset = BaseEntity.objects.owners_entities(user)
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save(creator=self.request.user)
        instance.join(self.request.user)

    def get_serializer_context(self):
        return {'user': self.request.user}

    def perform_destroy(self, instance):
        parents = instance.get_parent_entities()
        if parents:
            return Response(data="Instance is being used", status=status.HTTP_403_FORBIDDEN)

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
            inst.notify_update()
        else:
            raise Http404

        return Response(serializer.data)


class BaseEntityComponentViewSet(viewsets.ModelViewSet):

    def get_object_or_404(*args, **kwargs):
        return get_object_or_404(BaseEntityComponent, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = BaseEntityComponent.objects.owners_entities(user, entity_type=None)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}

    def perform_destroy(self, instance):
        parents = instance.get_parent_entities()
        if parents:
            return Response(data="Instance is being used", status=status.HTTP_403_FORBIDDEN)
        else:
            instance.related.all().delete()
            instance.delete()
            return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

