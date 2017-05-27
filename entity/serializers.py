__author__ = 'aammundi'
from rest_framework import serializers
from media_mgr.serializers import MediaObjectsSerializer
from media_mgr.models import MediaObjects
from rest_framework.validators import ValidationError
from entity.models import BaseEntity, Event, Product, Business, VirtualTable, UserEntity, Speaker
from entity.models import EntityEngagementStats
from django.contrib.auth.models import User
from media_mgr.signals import media_create
from location_mgr.serializers import LocationSerializerField
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from wizcardship.serializers import WizcardSerializerThumbnail, WizcardSerializerL1
from wizcardship.models import Wizcard
from wizserver import fields
from random import sample


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
            serializer = ProductSerializer(value.object, context=self.context)
        elif isinstance(value.object, Business):
            serializer = BusinessSerializer(value.object, context=self.context)
        elif isinstance(value.object, VirtualTable):
            serializer = TableSerializer(value.object, context=self.context)
        return serializer.data


class EntityEngagementSerializer(serializers.Serializer):
    class Meta:
        model = EntityEngagementStats
        fields = ('like_count', 'agg_like_level')

    like_count = serializers.IntegerField(read_only=True)
    agg_like_level = serializers.FloatField(read_only=True)
    like_level = serializers.SerializerMethodField(read_only=True)

    def get_like_level(self, obj):
        like_level = self.context.get('like_level', 0)
        return like_level

# these shouldn't be directly used.
class EntitySerializerL0(serializers.ModelSerializer):
    class Meta:
        model = BaseEntity
        fields = ('id', 'entity_type', 'num_users')

# these shouldn't be directly used.
class EntitySerializerL1(EntitySerializerL0):
    media = MediaObjectsSerializer(many=True)
    location = LocationSerializerField(required=False)
    users = serializers.SerializerMethodField(read_only=True)
    friends = serializers.SerializerMethodField(read_only=True)
    joined = serializers.SerializerMethodField(read_only=True)
    tags = TagListSerializerField(required=False)
    creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    liked = serializers.SerializerMethodField(read_only=True)

    MAX_THUMBNAIL_UI_LIMIT = 4

    class Meta(EntitySerializerL0.Meta):
        model = BaseEntity
        my_fields = ('media', 'name', 'address', 'tags', 'location', 'friends', 'users', 'creator', 'joined', 'liked')
        fields = EntitySerializerL0.Meta.fields + my_fields

    def get_users(self, obj):
        qs = obj.users.exclude(wizcard__isnull=True)
        count = qs.count()
        qs = qs.exclude(wizcard__thumbnail_image='')
        thumb_count = qs.count()
        if thumb_count > self.MAX_THUMBNAIL_UI_LIMIT:
            # lets make it interesting and give out different slices each time
            rand_ids = sample(xrange(1, thumb_count), self.MAX_THUMBNAIL_UI_LIMIT)
            qs = [qs[x] for x in rand_ids]

        wizcards = map(lambda u: u.wizcard, qs)

        out = dict(
            count=count,
            data=WizcardSerializerThumbnail(wizcards, many=True).data
        )
        return out

    def get_friends(self, obj):
        user = self.context.get('user', None)
        if user:
            friends_wizcards = obj.users_friends(user, self.MAX_THUMBNAIL_UI_LIMIT)
            out = dict(
                count=len(friends_wizcards),
                data=WizcardSerializerThumbnail(friends_wizcards, many=True).data
            )
            return out

        return None

    def get_joined(self, obj):
        user = self.context.get('user', None)
        if user:
            return obj.is_joined(self.context.get('user'))

        return False

    def get_liked(self, obj):
        user = self.context.get('user', None)
        if user and obj.engagements:
            return obj.engagements.user_liked(user)


# these shouldn't be directly used.
class EntitySerializerL2(TaggitSerializer, EntitySerializerL1):
    media = MediaObjectsSerializer(many=True)
    owners = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    related = RelatedSerializerField(many=True, required=False)
    ext_fields = serializers.DictField()
    engagements = EntityEngagementSerializer(read_only=True)

    class Meta(EntitySerializerL1.Meta):
        model = BaseEntity
        my_fields = ('website', 'category', 'ext_fields', 'engagements', 'phone', 'media',
                     'email', 'description', 'owners', 'related', 'users', 'friends')
        fields = EntitySerializerL1.Meta.fields + my_fields

        read_only_fields = ('entity_type',)

    def get_users(self, obj):
        count = obj.users.count()
        wizcards = map(lambda u: u.wizcard, obj.users.exclude(wizcard__isnull=True))
        user = self.context.get('user', None)

        out = dict(
            count=count,
            data=WizcardSerializerL1(wizcards, many=True, context={'user': user}).data
        )
        return out

    def get_friends(self, obj):
        user = self.context.get('user', None)
        if user:
            friends_wizcards = obj.users_friends(user)
            out = dict(
                count=len(friends_wizcards),
                data=WizcardSerializerL1(friends_wizcards, many=True).data
            )
            return out
        return None

    # this is not really used in this class. It's used in sub-classes
    def get_media(self, obj):
        return MediaObjectsSerializer(
            obj.media.all(),
            many=True
        ).data

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


class SpeakerSerializer(serializers.ModelSerializer):
    # def __init__(self, *args, **kwargs):
    #     many = kwargs.pop('many', True)
    #     super(SpeakerSerializer, self).__init__(many=many, *args, **kwargs)

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

# this is used by portal REST API
class EventSerializer(EntitySerializerL2):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    speakers = serializers.PrimaryKeyRelatedField(many=True, queryset=Speaker.objects.all())

    class Meta:
        model = Event
        my_fields = ('start', 'end', 'speakers',)
        fields = EntitySerializerL2.Meta.fields + my_fields

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


# these are used by App.
class EventSerializerL1(EntitySerializerL1):
    start = serializers.DateTimeField(read_only=True)
    end = serializers.DateTimeField(read_only=True)
    media = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        my_fields = ('start', 'end', 'speakers',)
        fields = EntitySerializerL1.Meta.fields + my_fields

    def get_media(self, obj):
        return MediaObjectsSerializer(
            obj.media.filter(media_sub_type=MediaObjects.SUB_TYPE_BANNER),
            many=True
        ).data

# these are used by App.
class EventSerializerL2(EventSerializerL1, EntitySerializerL2):
    speakers = SpeakerSerializer(many=True)

    class Meta:
        model = Event
        my_fields = ('start', 'end', 'speakers',)
        fields = EntitySerializerL2.Meta.fields + my_fields

    def get_media(self, obj):
        return MediaObjectsSerializer(
            obj.media.all(),
            many=True
        ).data

# this is used by portal REST API
class ProductSerializer(EntitySerializerL2):

    class Meta:
        model = Product
        fields = EntitySerializerL2.Meta.fields

    def create(self, validated_data, **kwargs):
        self.prepare(validated_data)
        product = Product.objects.create(entity_type=BaseEntity.PRODUCT, **validated_data)
        self.post_create(product)

        return product


# this is used by portal REST API
class BusinessSerializer(EntitySerializerL2):
    class Meta:
        model = Business
        fields = EntitySerializerL2.Meta.fields

    def create(self, validated_data, **kwargs):
        self.prepare(validated_data)
        biz = Business.objects.create(entity_type=BaseEntity.BUSINESS, **validated_data)
        self.post_create(biz)

        return biz

# this is used by portal REST API
class TableSerializer(EntitySerializerL2):

    class Meta:
        model = VirtualTable
        fields = EntitySerializerL2.Meta.fields

    def create(self, validated_data):
        self.prepare(validated_data)
        table = VirtualTable.objects.create(entity_type=BaseEntity.TABLE, **validated_data)
        self.post_create(table)

        return table


class EntityEngagementSerializerL1(EntityEngagementSerializer):

    class Meta:
        model = EntityEngagementStats
        my_fields = ('entity',)
        fields = EntityEngagementSerializer.Meta.fields + my_fields

    entity = EntitySerializerL0(read_only=True, source='engagements_baseentity_related')
