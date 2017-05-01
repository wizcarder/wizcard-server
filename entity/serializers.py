__author__ = 'aammundi'
from rest_framework import serializers
from media_mgr.serializers import MediaObjectsSerializer
from rest_framework.validators import ValidationError
from entity.models import BaseEntity, Event, Product, Business, VirtualTable, UserEntity, Speaker
from django.contrib.auth.models import User
from media_mgr.signals import media_create
from location_mgr.models import LocationMgr
from location_mgr.serializers import LocationSerializerField

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

class EntitySerializer(serializers.ModelSerializer):
    media = MediaObjectsSerializer(many=True)
    owners = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    related = RelatedSerializerField(many=True, required=False)
    location = LocationSerializerField(required=False)

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

        #Generate Tags
        #entity.add_tags()

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
                instance.add_subentity(**s)

        location = validated_data.pop('location', None)
        if location:
            instance.create_or_update_location(location['lat'], location['lng'])

        instance.save()
        return instance

class SpeakerSerializer(serializers.ModelSerializer):

    media = MediaObjectsSerializer(many=True, required=False)
    ext_fields = serializers.DictField()

    class Meta:
        model = Speaker
        fields = "__all__"
        read_only_fields = ('vcard',)

    def create(self, validated_data):
        media = validated_data.pop('media', None)

        s = Speaker.objects.create(**validated_data)
        if media:
            media_create.send(sender=s, objs=media)

        return s

    def update(self, instance, validated_data):
        instance.first_name = validated_data.pop("first_name", instance.first_name)
        instance.last_name = validated_data.pop("last_name", instance.last_name)
        instance.phone = validated_data.pop("phone", instance.phone)
        instance.email = validated_data.pop("email", instance.email)
        instance.org = validated_data.pop("org", instance.org)
        instance.designation = validated_data.pop("designation", instance.designation)
        instance.ext_fields = validated_data.pop("ext_fields", instance.ext_fields)
        instance.description = validated_data.pop("description", instance.description)

        media = validated_data.pop('media', None)
        if media:
            instance.media.all().delete()
            media_create.send(sender=instance, objs=media)

        instance.save()
        return instance

class EventSerializer(EntitySerializer):

    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    speakers = serializers.PrimaryKeyRelatedField(many=True, queryset=Speaker.objects.all())

    class Meta:
        model = Event
        fields = '__all__'

    def create(self, validated_data):
        speakers = validated_data.pop('speakers', None)
        event = super(EventSerializer, self).create(validated_data)

        for s in speakers:
            event.add_speaker(s)

        return event

    def update(self, instance, validated_data):
        instance.start = validated_data.pop("start", instance.start)
        instance.end = validated_data.pop("end", instance.end)
        speakers = validated_data.pop('speakers', None)
        instance = super(EventSerializer, self).update(instance, validated_data)

        if speakers:
            instance.speakers.clear()
            for s in speakers:
                instance.add_speaker(s)

        return instance

class EventSerializerExpanded(EventSerializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    speakers = SpeakerSerializer(many=True)

    class Meta:
        model = Event
        fields = '__all__'


class ProductSerializer(EntitySerializer):
    media = MediaObjectsSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = '__all__'

class BusinessSerializer(EntitySerializer):
    class Meta:
        model = Business
        fields = '__all__'

class TableSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    location = LocationSerializerField()

    class Meta:
        model = VirtualTable
        fields = '__all__'

    def create(self, validated_data):
        users = validated_data.pop('users', None)
        location = validated_data.pop('location', None)
        owners = validated_data.pop('owners', None)

        table = VirtualTable.objects.create(**validated_data)

        for u in users:
            UserEntity.user_join(u, table)

        if location:
            table.create_location(location.lat, location.lng)

        return table