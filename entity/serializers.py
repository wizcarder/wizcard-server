__author__ = 'aammundi'
from rest_framework import serializers
from media_mgr.serializers import MediaObjectsSerializer
from rest_framework.validators import ValidationError
from userprofile.models import UserProfile
from entity.models import Event
from media_mgr.signals import media_create
import pdb


class RelatedSerializerField(serializers.RelatedField):

    def get_queryset(self):
        pass

    def to_internal_value(self, data):
        id = data.get('id', None)
        type = data.get('type', None)

        # Perform the data validation.
        if not id:
            raise ValidationError({
                'id': 'This field is required.'
            })
        if not type:
            raise ValidationError({
                'type': 'This field is required.'
            })

        return {
            'id': int(id),
            'type': type
        }

    def to_representation(self, value):
        obj_id = value.object.id
        type = value.alias
        return 'id: %d, type: %s' % (obj_id, type)


class EventSerializer(serializers.ModelSerializer):
    media = MediaObjectsSerializer(many=True)
    owners = serializers.PrimaryKeyRelatedField(many=True, queryset=UserProfile.objects.all())
    related = RelatedSerializerField(many=True)

    class Meta:
        model = Event
        depth = 1
        fields = ('pk', 'entity_type', 'name', 'address', 'website', 'description', 'media', 'owners', 'related')

    def create(self, validated_data):
        media = validated_data.pop('media', None)
        tags = validated_data.pop('tags', None)
        owners = validated_data.pop('owners', None)
        sub_entities = validated_data.pop('related', None)

        event = Event.objects.create(**validated_data)
        if media:
            media_create.send(sender=event, objs=media)
        if owners:
            for o in owners:
                event.add_owner(o)
        if sub_entities:
            for s in sub_entities:
                event.add_subentity_by_id(**s)

        return event

    def update(self, instance, validated_data):
        instance.name = validated_data.pop('name', instance.name)
        instance.address = validated_data.pop('address', instance.address)
        instance.website = validated_data.pop('website', instance.website)
        instance.description = validated_data.pop('description', instance.description)

        # handle related objects. It's a replace
        media = validated_data.pop('media', None)
        if media:
            instance.media.all().delete()
            media_create.send(sender=instance, objs=media)

        owners = validated_data.pop('owners', None)
        if owners:
            instance.owners.clear()
            for o in owners:
                instance.add_owner(o)

        sub_entities = validated_data.pop('related', None)
        if sub_entities:
            instance.related.all().delete()
            for s in sub_entities:
                instance.add_subentity_by_id(**s)

        instance.save()
        return instance

