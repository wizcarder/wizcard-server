__author__ = 'aammundi'
from rest_framework import serializers
from media_mgr.serializers import MediaObjectsSerializer
from rest_framework.validators import ValidationError
from entity.models import BaseEntity, Event, Product, Business, VirtualTable, UserEntity, Speaker
from entity.models import EntityEngagementStats
from django.contrib.auth.models import User
from media_mgr.signals import media_create
from location_mgr.models import LocationMgr
from location_mgr.serializers import LocationSerializerField
import simplejson as json
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from wizcardship.models import Wizcard
from wizserver import fields

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
        if isinstance(value.object, Product):
            serializer = ProductSerializer(value.object)
        elif isinstance(value.object, Business):
            serializer = BusinessSerializer(value.object)
        elif isinstance(value.object, VirtualTable):
            serializer = TableSerializer(value.object)
        return serializer.data

class UserCountField(serializers.RelatedField):
    def to_representation(self, value):
        if self.context:
            if 'user' in self.context:
                user = self.context['user']
            expanded = False
            if 'expanded' in self.context:
                expanded = self.context['expanded']
            attendees = value.all()
            try:
                wizcard = user.wizcard
                attendee_resp = []
                friends_count = 0
                for member in attendees:
                    if not expanded:
                        attend_data = member.wizcard.serialize(template=fields.wizcard_template_thumbnail_only)
                    else:
                        attend_data = member.wizcard.serialize()
                    isfriend = Wizcard.objects.are_wizconnections(wizcard, member.wizcard)
                    friends_count += 1
                    member_data = {"attendee":attend_data, "isFriend" : isfriend}
                    attendee_resp.append(member_data)

                return {"friends": friends_count, "attendees": attendee_resp}
            except:
                if not expanded:
                    return {"attendees": len(attendees)}


class EntityEngagementSerializerField(serializers.Serializer):
    class Meta:
        model = EntityEngagementStats
        fields = ('like_count', 'agg_like_level')

    like_count = serializers.IntegerField(read_only=True)
    agg_like_level = serializers.FloatField(read_only=True)


class EntitySerializer(TaggitSerializer, serializers.ModelSerializer):
    media = MediaObjectsSerializer(many=True, required=False)
    owners = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    related = RelatedSerializerField(many=True, required=False)
    location = LocationSerializerField(required=False)
    tags = TagListSerializerField(required=False)
    users = UserCountField(required=False, read_only=True)
    extFields = serializers.DictField()
    engagements = EntityEngagementSerializerField(read_only=True)

    class Meta:
        model = BaseEntity
        depth = 1
        fields = ('pk', 'name', 'address', 'website', 'tags', 'category', 'extFields',
                  'engagements', 'phone', 'email', 'description', 'media', 'owners', 'related', 'location', 'users',)
        read_only_fields = ('entity_type',)

    def prepare(self, validated_data):
        self.media = validated_data.pop('media', None)
        self.tags = validated_data.pop('tags', None)
        self.owners = validated_data.pop('owners', None)
        self.sub_entities = validated_data.pop('related', None)
        self.location = validated_data.pop('location', None)
        self.users = validated_data.pop('users', None)

    def post_create(self, entity):
        if self.media:
            media_create.send(sender=entity, objs=self.media)
        if self.owners:
            for o in self.owners:
                entity.add_owner(o)
        if self.sub_entities:
            for s in self.sub_entities:
                entity.add_subentity(**s)
        if self.location:
            entity.create_or_update_location(self.location['lat'], self.location['lng'])

        if self.users:
            for u in self.users:
                UserEntity.user_join(u, entity)

        # Generate Tags
        if self.tags:
            entity.add_tags(self.tags)

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
        tags = validated_data.pop('tags', None)
        if tags:
            instance.add_tags(tags)

        instance.save()
        return instance


class EntityMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseEntity
        fields = ('id', 'entity_type')


class SpeakerSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(SpeakerSerializer, self).__init__(many=many, *args, **kwargs)

    media = MediaObjectsSerializer(many=True, required=False)
    extFields = serializers.DictField()

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
        instance.extFields = validated_data.pop("extFields", instance.extFields)
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

    def create(self, validated_data, **kwargs):
        speakers = validated_data.pop('speakers', None)
        self.prepare(validated_data)
        event = Event.objects.create(entity_type=BaseEntity.EVENT, **validated_data)
        self.post_create(event)

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

class EventSerializerExpanded(EntitySerializer):

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

    def create(self, validated_data, **kwargs):
        self.prepare(validated_data)
        product = Product.objects.create(entity_type=BaseEntity.PRODUCT, **validated_data)
        self.post_create(product)

        return product


class BusinessSerializer(EntitySerializer):
    class Meta:
        model = Business
        fields = '__all__'

    def create(self, validated_data, **kwargs):
        self.prepare(validated_data)
        biz = Business.objects.create(entity_type=BaseEntity.BUSINESS, **validated_data)
        self.post_create(biz)

        return biz


class TableSerializer(EntitySerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = VirtualTable
        fields = '__all__'

    def create(self, validated_data):

        self.prepare(validated_data)
        table = VirtualTable.objects.create(entity_type=BaseEntity.TABLE, **validated_data)
        self.post_create(table)

        return table


class EntityEngagementSerializer(EntityEngagementSerializerField):
    class Meta(EntityEngagementSerializerField.Meta):
        model = EntityEngagementStats
        fields = ('like_count', 'agg_like_level', 'entity')

    entity = EntityMiniSerializer(read_only=True, source='engagements_baseentity_related')
