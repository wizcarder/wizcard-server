from django.shortcuts import render
from base_entity.views import BaseEntityComponentViewSet
from scan.models import ScannedEntity, BadgeTemplate
from scan.serializers import ScannedEntitySerializer, BadgeTemplateSerializer

# Create your views here.


class ScannedEntityViewSet(BaseEntityComponentViewSet):
    queryset = ScannedEntity.objects.all()
    serializer_class = ScannedEntitySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = ScannedEntity.objects.owners_entities(user)
        return queryset


class BadgeTemplateViewSet(BaseEntityComponentViewSet):
    queryset = BadgeTemplate.objects.all()
    serializer_class = BadgeTemplateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = BadgeTemplate.objects.owners_entities(user)
        return queryset

