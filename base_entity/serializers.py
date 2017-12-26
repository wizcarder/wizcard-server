from rest_framework import serializers
from rest_framework.validators import ValidationError
from django.contrib.auth.models import User
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from base.mixins import MediaMixin
from media_components.signals import media_create
from location_mgr.serializers import LocationSerializerField
from base_entity.models import BaseEntity, EntityEngagementStats, BaseEntityComponent, EntityUserStats, UserEntity
from entity.models import CoOwners
from media_components.serializers import MediaEntitiesSerializer
from wizcardship.serializers import WizcardSerializerL0, WizcardSerializerL1
from random import sample
import pdb


class RelatedSerializerField(serializers.RelatedField):

    def get_queryset(self):
        pass

    def to_internal_value(self, data):

        ids = data.get('ids', None)
        etype = data.get('type', None)
        overwrite = data.get('overwrite', False)

        # Perform the data validation.
        if ids is None:
            raise ValidationError({
                'ids': 'This field is required.'
            })
        if not type:
            raise ValidationError({
                'type': 'This field is required.'
            })

        value_dict = {'ids': ids, 'type': etype, 'overwrite': overwrite} if overwrite else {'ids': ids, 'type': etype}

        return value_dict

    def to_representation(self, value):
        pass


class EntityEngagementSerializer(serializers.Serializer):
    class Meta:
        model = EntityEngagementStats
        fields = ('like_count', 'agg_like_level', 'views', 'follows', 'unfollows')

    like_level = serializers.SerializerMethodField(read_only=True)

    def get_like_level(self, obj):
        user = self.context.get('user')
        if EntityUserStats.objects.filter(user=user, stats=obj).exists():
            user_stat = EntityUserStats.objects.get(user=user, stats=obj)
            return user_stat.like_level

        return EntityUserStats.MIN_ENGAGEMENT_LEVEL


class EntitySerializerL0(serializers.ModelSerializer):
    class Meta:
        model = BaseEntity
        fields = ('id', 'entity_type', 'num_users')


class EntityEngagementSerializerL1(EntityEngagementSerializer):
    class Meta:
        model = EntityEngagementStats
        my_fields = ('entity',)
        fields = EntityEngagementSerializer.Meta.fields + my_fields

    entity = EntitySerializerL0(read_only=True, source='engagements_baseentity_related')


"""
One Serializer with everything in it. This can be subclassed and individual fields
can be defined as needed and methods overridden.
This serializer should not be directly used
"""
class EntitySerializer(EntitySerializerL0):
    media = serializers.SerializerMethodField()
    location = LocationSerializerField(required=False)
    users = serializers.SerializerMethodField()
    friends = serializers.SerializerMethodField()
    joined = serializers.SerializerMethodField()
    tags = TagListSerializerField(required=False)
    like = serializers.SerializerMethodField()
    engagements = EntityEngagementSerializer(read_only=True)
    creator = serializers.SerializerMethodField()
    owners = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CoOwners.objects.all(),
        required=False,
        write_only=True
    )
    related = RelatedSerializerField(write_only=True, required=False, many=True)
    ext_fields = serializers.DictField(required=False)
    is_activated = serializers.BooleanField(write_only=True, default=False)
    status = serializers.SerializerMethodField()

    MAX_THUMBNAIL_UI_LIMIT = 4

    class Meta(EntitySerializerL0.Meta):
        model = BaseEntity
        my_fields = ('name', 'address', 'venue',  'secure', 'description', 'email', 'website', 'phone',
                      'media', 'location', 'users', 'joined', 'friends', 'tags', 'like',
                     'engagements', 'creator', 'owners', 'related', 'ext_fields', 'is_activated', 'status')

        fields = EntitySerializerL0.Meta.fields + my_fields

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA),
            many=True,
            context=self.context
        ).data

    def get_users(self, obj):
        return ""

    def get_creator(self, obj):
        return ""

    def get_friends(self, obj):
        return ""

    def get_joined(self, obj):
        return obj.is_joined(self.context.get('user'))

    def get_like(self, obj):
        liked, level = obj.engagements.user_liked(self.context.get('user'))
        return dict(liked=liked, like_level=level)

    def get_status(self, obj):
        if obj.expired:
            return "expired"
        elif obj.is_activated:
            return "live"
        else:
            return "unpublished"

    def prepare(self, validated_data):
        self.tags = validated_data.pop('tags', None)
        self.owners = validated_data.pop('owners', None)
        self.sub_entities = validated_data.pop('related', None)
        self.location = validated_data.pop('location', None)
        self.users = validated_data.pop('users', None)
        self.creator = validated_data.pop('creator', None)

    def create(self, validated_data):
        cls, ser = BaseEntityComponent.entity_cls_ser_from_type(validated_data['entity_type'])

        obj = BaseEntityComponent.create(
            cls,
            owner=self.context.get('user'),
            is_creator=True,
            **validated_data
        )

        return obj

    def post_create(self, entity):
        if self.owners:
            BaseEntityComponent.add_owners(entity, self.owners)

        if self.sub_entities:
            for s in self.sub_entities:
                entity.add_subentities(**s)

        if self.location:
            entity.create_or_update_location(self.location['lat'], self.location['lng'])

        if self.users:
            for u in self.users:
                UserEntity.user_join(u, entity)

        # TODO: Handle owners and create linkage to existing owners

        # Generate Tags
        if self.tags:
            entity.add_tags(self.tags)

        return entity

    def update(self, instance, validated_data):
        if hasattr(instance, 'name'):
            instance.name = validated_data.pop('name', instance.name)
        if hasattr(instance, 'address'):
            instance.address = validated_data.pop('address', instance.address)
        if hasattr(instance, 'venue'):
            instance.address = validated_data.pop('venue', instance.venue)
        if hasattr(instance, 'website'):
            instance.website = validated_data.pop('website', instance.website)
        if hasattr(instance, 'description'):
            instance.description = validated_data.pop('description', instance.description)
        if hasattr(instance, 'phone'):
            instance.phone = validated_data.pop('phone', instance.phone)
        if hasattr(instance, 'email'):
            instance.email = validated_data.pop('email', instance.email)
        if hasattr(instance, 'activated'):
            instance.is_activated = validated_data.pop('is_activated', instance.is_activated)

        owners = validated_data.pop('owners', None)
        if owners is not None:
            for o in owners:
                instance.add_owner(o)

        sub_entities = validated_data.pop('related', None)
        if sub_entities is not None:
            for s in sub_entities:
                overwrite = s.pop('overwrite', False)
                if overwrite:
                    instance.remove_sub_entities_of_type(s['type'])
                instance.add_subentities(**s)

        location = validated_data.pop('location', None)
        if location:
            instance.create_or_update_location(location['lat'], location['lng'])

        tags = validated_data.pop('tags', None)
        if tags:
            instance.add_tags(tags)

        instance.save()
        return instance


