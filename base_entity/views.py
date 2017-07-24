from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from base_entity.models import BaseEntity

class BaseEntityViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        queryset = BaseEntity.objects.users_entities(user)
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save(creator=self.request.user)
        instance.join(self.request.user)

    def get_serializer_context(self):
        return {'user': self.request.user}
