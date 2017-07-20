from rest_framework import serializers
from rest_framework.validators import ValidationError
from django.contrib.auth.models import User
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from entity_components.signals import media_create
from location_mgr.serializers import LocationSerializerField
from base_entity.models import BaseEntity, EntityEngagementStats, BaseEntityComponent, EntityUserStats, UserEntity
from entity_components.serializers import MediaEntitiesSerializer
from entity_components.models import MediaEntities
from wizcardship.serializers import WizcardSerializerL0, WizcardSerializerL1
from random import sample
import pdb


class RelatedSerializerField(serializers.RelatedField):

    def get_queryset(self):
        pass

    def to_internal_value(self, data):

        ids = data.get('ids', None)
        type = data.get('type', None)

        # Perform the data validation.
        if not ids:
            raise ValidationError({
                'ids': 'This field is required.'
            })
        if not type:
            raise ValidationError({
                'type': 'This field is required.'
            })

        return {
            'ids': ids,
            'type': type
        }

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

# these shouldn't be directly used.
class EntitySerializerL1(EntitySerializerL0):
    media = serializers.SerializerMethodField(read_only=True)
    location = LocationSerializerField(required=False)
    users = serializers.SerializerMethodField(read_only=True)
    friends = serializers.SerializerMethodField(read_only=True)
    joined = serializers.SerializerMethodField(read_only=True)
    tags = TagListSerializerField(required=False)
    like = serializers.SerializerMethodField(read_only=True)
    engagements = EntityEngagementSerializer(read_only=True)
    creator = serializers.SerializerMethodField(read_only=True)

    MAX_THUMBNAIL_UI_LIMIT = 4

    class Meta(EntitySerializerL0.Meta):
        model = BaseEntity
        my_fields = ('media', 'name', 'address', 'tags', 'location', 'friends',
                     'secure', 'users', 'joined', 'like', 'engagements', 'description')
        fields = EntitySerializerL0.Meta.fields + my_fields

    def get_creator(self, obj):
        return ""

    def get_media(self, obj):
        return ""

    def get_users(self, obj):
        qs = obj.users.exclude(wizcard__isnull=True)
        count = qs.count()

        #qs_thumbnail = qs.filter(wizcard__media__media_sub_type=MediaEntities.SUB_TYPE_THUMBNAIL)
        qs_thumbnail = qs
        thumb_count = qs_thumbnail.count()
        if thumb_count > self.MAX_THUMBNAIL_UI_LIMIT:
            # lets make it interesting and give out different slices each time
            rand_ids = sample(xrange(1, thumb_count), self.MAX_THUMBNAIL_UI_LIMIT)
            qs_thumbnail = [qs_thumbnail[x] for x in rand_ids]

        wizcards = map(lambda u: u.wizcard, qs_thumbnail)

        out = dict(
            count=count,
            data=WizcardSerializerL0(wizcards, many=True).data
        )
        return out

    def get_friends(self, obj):
        user = self.context.get('user')

        friends_wizcards = obj.users_friends(user, self.MAX_THUMBNAIL_UI_LIMIT)
        out = dict(
            count=len(friends_wizcards),
            data=WizcardSerializerL0(friends_wizcards, many=True).data
        )
        return out

    def get_joined(self, obj):
        return obj.is_joined(self.context.get('user'))

    def get_like(self, obj):
        liked, level = obj.engagements.user_liked(self.context.get('user'))
        return dict(liked=liked, like_level=level)


# these shouldn't be directly used.
class EntitySerializerL2(TaggitSerializer, EntitySerializerL1):
    media = serializers.SerializerMethodField()
    owners = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    related = RelatedSerializerField(write_only=True, required=False, many=True)
    ext_fields = serializers.DictField(required=False)

    class Meta(EntitySerializerL1.Meta):
        model = BaseEntity
        my_fields = ('website', 'category', 'ext_fields', 'phone', 'related',
                     'email', 'description', 'owners', 'users')
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

    # no need to send friends at L2. removing it from the fields list seems convoluted
    def get_friends(self, obj):
        return ""

    def get_media(self, obj):
        media = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA)
        s = MediaEntitiesSerializer(media, many=True)
        return s.data

    def prepare(self, validated_data):
        self.tags = validated_data.pop('tags', None)
        self.owners = validated_data.pop('owners', None)
        self.sub_entities = validated_data.pop('related', None)
        self.location = validated_data.pop('location', None)
        self.users = validated_data.pop('users', None)
        self.creator = validated_data.pop('creator')

    def post_create(self, entity):
        # add creator. Should always be there
        BaseEntityComponent.add_creator(entity, self.creator)

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

        # Generate Tags
        if self.tags:
            entity.add_tags(self.tags)

        return entity

    # AR TODO there are some obvious bugs here for the related fields.
    # when we update, if we wipe existing, then related is also lost
    def update(self, instance, validated_data):
        instance.name = validated_data.pop('name', instance.name)
        instance.address = validated_data.pop('address', instance.address)
        instance.website = validated_data.pop('website', instance.website)
        instance.description = validated_data.pop('description', instance.description)
        instance.phone = validated_data.pop('phone', instance.phone)
        instance.email = validated_data.pop('email', instance.email)

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
                instance.add_subentities(**s)

        location = validated_data.pop('location', None)
        if location:
            instance.create_or_update_location(location['lat'], location['lng'])
        tags = validated_data.pop('tags', None)
        if tags:
            instance.add_tags(tags)

        instance.save()
        return instance

class BaseEntityComponentSerializer(serializers.ModelSerializer):
    ext_fields = serializers.DictField(required=False)
    related = RelatedSerializerField(many=True, required=False, write_only=True)

    class Meta:
        model = BaseEntityComponent
        fields = '__all__'

    def prepare(self, validated_data):
        self.sub_entities = validated_data.pop('related', None)

    def post_create(self, obj):
        if self.sub_entities:
            for s in self.sub_entities:
                obj.add_subentities(**s)

        return obj

    def update(self, instance, validated_data):

        sub_entities = validated_data.pop('related', None)
        if sub_entities:
            instance.related.all().delete()
            for s in sub_entities:
                instance.add_subentities(**s)

        instance.save()

        return instance



