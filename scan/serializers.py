__author__ = 'aammundi'

from rest_framework import serializers
from entity.serializers import EntitySerializer
from scan.models import ScannedEntity, BadgeTemplate
from entity.models import BaseEntityComponent


class ScannedEntitySerializer(EntitySerializer):
    class Meta:
        model = ScannedEntity
        fields = ('id', 'name', 'email', 'company', 'title', 'score', 'event_id')

    score = serializers.SerializerMethodField()

    def get_score(self, obj):
        return obj.lead_score()

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.SCANNED_USER)

        self.prepare(validated_data)
        obj = super(ScannedEntitySerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj


class BadgeTemplateSerializer(EntitySerializer):
    class Meta:
        model = BadgeTemplate
        fields = ('id', 'name', 'email', 'company', 'title', 'ext_fields', 'media', )

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.BADGE_TEMPLATE)

        self.prepare(validated_data)
        obj = super(BadgeTemplateSerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj

    def update(self, instance, validated_data):
        self.prepare(validated_data)
        obj = super(BadgeTemplateSerializer, self).update(instance, validated_data)
        self.post_create_update(obj, update=True)

        return obj
