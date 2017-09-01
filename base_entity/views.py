
# Create your views here.
from base_entity.models import BaseEntity, BaseEntityComponent
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.response import Response


class BaseEntityViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('expired', 'is_activated')

    def get_queryset(self):
        user = self.request.user
        queryset = BaseEntity.objects.users_entities(user)
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
        else:
            instance.related.all().delete
            instance.delete()
            return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

class BaseEntityComponentViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        user = self.request.user
        queryset = BaseEntityComponent.objects.users_entities(user)
        return queryset

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
