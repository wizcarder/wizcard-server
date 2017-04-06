__author__ = 'aammundi'
from rest_framework import serializers
from media_mgr.serializers import MediaObjectsSerializer
from rest_framework.validators import ValidationError
from userprofile.models import UserProfile
from entity.models import BaseEntity, Event, Product, Business, Speaker
from media_mgr.signals import media_create
from location_mgr.models import LocationMgr
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

class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocationMgr
        fields = ('lat', 'lng')

    # def get_queryset(self):
    #     pass
    #
    # def to_internal_value(self, data):
    #     lat = data.get('lat', None)
    #     lng = data.get('lng', None)
    #
    #     # Perform the data validation.
    #     if not lat:
    #         raise ValidationError({
    #             'lat': 'This field is required.'
    #         })
    #     if not lng:
    #         raise ValidationError({
    #             'lng': 'This field is required.'
    #         })
    #
    #     return {
    #         'lat': int(lat),
    #         'lng': int(lng)
    #     }
    #
    # def to_representation(self, value):
    #     pdb.set_trace()
    #     lat = value.lat
    #     lng = value.lng
    #     return 'lat: %d, lng: %s' % (lat, lng)


class EntitySerializer(serializers.ModelSerializer):
    media = MediaObjectsSerializer(many=True)
    owners = serializers.PrimaryKeyRelatedField(many=True, queryset=UserProfile.objects.all(), required=False)
    related = RelatedSerializerField(many=True, required=False)
    location = LocationSerializer(required=False,many=True)

    class Meta:
        model = BaseEntity
        depth = 1
        fields = ('pk', 'entity_type', 'name', 'address', 'website',
                  'phone', 'email', 'description', 'media', 'owners', 'related', 'location')

    def create(self, validated_data):
        media = validated_data.pop('media', None)
        tags = validated_data.pop('tags', None)
        owners = validated_data.pop('owners', None)
        sub_entities = validated_data.pop('related', None)
        location = validated_data.pop('location', None)

        #entity_type is a class member so not popping
        entity_type = validated_data['entity_type']

        cls, ser = BaseEntity.get_entity_from_type(entity_type)
        entity = cls.objects.create(**validated_data)

        if media:
            media_create.send(sender=entity, objs=media)
        if owners:
            for o in owners:
                entity.add_owner(o)
        if sub_entities:
            for s in sub_entities:
                entity.add_subentity(**s)
        if location:
            entity.create_or_update_location(location['lat'], location['lng'])

        return entity

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

        location = validated_data.pop('location', None)
        if location:
            instance.create_or_update_location(location['lat'], location['lng'])

        instance.save()
        return instance

class EventSerializer(EntitySerializer):
    class Meta:
        model = Event
        fields = '__all__'

    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

class ProductSerializer(EntitySerializer):
    class Meta:
        model = Product
        fields = '__all__'

class BusinessSerializer(EntitySerializer):
    class Meta:
        model = Business
        fields = '__all__'

class SpeakerSerializer(EntitySerializer):
    class Meta:
        model = Speaker
        fields = '__all__'
