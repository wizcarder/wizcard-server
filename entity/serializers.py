__author__ = 'aammundi'
from rest_framework import serializers
from media_mgr.serializers import MediaObjectsSerializer
from media_mgr.models import MediaObjects
from rest_framework.validators import ValidationError
from entity.models import BaseEntity, Event, Product, Business, VirtualTable, UserEntity, Speaker, EventComponent, Sponsor
from entity.models import EntityEngagementStats, EntityUserStats
from django.contrib.auth.models import User
from media_mgr.signals import media_create
from location_mgr.serializers import LocationSerializerField
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from wizcardship.serializers import WizcardSerializerL0, WizcardSerializerL1
from wizcardship.models import Wizcard
from django.utils import timezone
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

# this is used in the app path since related needs 'joined'
class RelatedSerializerFieldL2(RelatedSerializerField):
    def to_representation(self, value):
        if isinstance(value.object, Product):
            serializer = ProductSerializerL2(value.object, context=self.context)
        elif isinstance(value.object, Business):
            serializer = BusinessSerializer(value.object, context=self.context)
        elif isinstance(value.object, VirtualTable):
            serializer = TableSerializerL2(value.object, context=self.context)
        return serializer.data

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

# these shouldn't be directly used.
class EntitySerializerL0(serializers.ModelSerializer):
    class Meta:
        model = BaseEntity
        fields = ('id', 'entity_type', 'num_users')

# these shouldn't be directly used.
class EntitySerializerL1(EntitySerializerL0):
    media = serializers.SerializerMethodField(read_only=True)
    location = LocationSerializerField(required=False)
    users = serializers.SerializerMethodField(read_only=True)
    friends = serializers.SerializerMethodField(read_only=True)
    joined = serializers.SerializerMethodField(read_only=True)
    tags = TagListSerializerField(required=False)
    creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    like = serializers.SerializerMethodField(read_only=True)
    engagements = EntityEngagementSerializer(read_only=True)

    MAX_THUMBNAIL_UI_LIMIT = 4

    class Meta(EntitySerializerL0.Meta):
        model = BaseEntity
        my_fields = ('media', 'name', 'address', 'tags', 'location', 'friends',
                     'secure', 'users', 'creator', 'joined', 'like', 'engagements', 'description')
        fields = EntitySerializerL0.Meta.fields + my_fields

    def get_media(self, obj):
        return ""

    def get_users(self, obj):
        qs = obj.users.exclude(wizcard__isnull=True)
        count = qs.count()

        qs_thumbnail = qs.filter(wizcard__media__media_sub_type=MediaObjects.SUB_TYPE_THUMBNAIL)
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
    media = MediaObjectsSerializer(many=True, required=False)
    owners = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    related = RelatedSerializerFieldL2(many=True, required=False)
    ext_fields = serializers.DictField(required=False)

    class Meta(EntitySerializerL1.Meta):
        model = BaseEntity
        my_fields = ('website', 'category', 'ext_fields', 'phone',
                     'email', 'description', 'owners', 'related', 'users')
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

    # def get_friends(self, obj):
    #     user = self.context.get('user')
    #
    #     friends_wizcards = obj.users_friends(user)
    #     out = dict(
    #         count=len(friends_wizcards),
    #         data=WizcardSerializerL1(friends_wizcards, many=True).data
    #     )
    #     return out

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
                instance.add_subentity(**s)

        location = validated_data.pop('location', None)
        if location:
            instance.create_or_update_location(location['lat'], location['lng'])
        tags = validated_data.pop('tags', None)
        if tags:
            instance.add_tags(tags)

        instance.save()
        return instance


class EventComponentSerializer(serializers.ModelSerializer):
    media = MediaObjectsSerializer(many=True, required=False)
    caption = serializers.CharField(required=False)

    class Meta:
        model = EventComponent
        fields = "__all__"

    def prepare(self, validated_data):
        self.media = validated_data.pop('media', None)

    def post_create(self, component):
        if self.media:
            media_create.send(sender=component, objs=self.media)

        return component

    def update(self, instance, validated_data):
        instance.caption = validated_data.pop('caption', instance.caption)

        # handle related objects. It's a replace
        media = validated_data.pop('media', None)
        if media:
            instance.media.all().delete()
            media_create.send(sender=instance, objs=media)
        instance.save()
        return instance


class SpeakerSerializer(EventComponentSerializer):
    # def __init__(self, *args, **kwargs):
    #     many = kwargs.pop('many', True)
    #     super(SpeakerSerializer, self).__init__(many=many, *args, **kwargs)
    ext_fields = serializers.DictField(required=False)

    class Meta:
        model = Speaker
        fields = "__all__"
        read_only_fields = ('vcard',)

    def create(self, validated_data):
        self.prepare(validated_data)

        s = Speaker.objects.create(**validated_data)
        self.post_create(s)

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
        instance.save()

        instance = super(SpeakerSerializer, self).update(instance, validated_data)
        return instance

class SponsorSerializer(EventComponentSerializer):
    class Meta:
        model = Sponsor
        fields = "__all__"

    def create(self, validated_data):
        self.prepare(validated_data)
        s = Sponsor.objects.create(**validated_data)
        self.post_create(s)
        return s

    def update(self, instance, validated_data):
        instance.name = validated_data.pop("name", instance.name)
        instance.save()
        instance = super(SponsorSerializer, self).update(instance, validated_data)
        return instance


# this is used by portal REST API
class EventSerializer(EntitySerializerL2):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        remove_fields = ['joined', 'engagements']

        super(EventSerializer, self).__init__(*args, **kwargs)

        for field_name in remove_fields:
            self.fields.pop(field_name)

    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    related = RelatedSerializerField(many=True, required=False)
    speakers = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=Speaker.objects.all())
    sponsors = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=Sponsor.objects.all())

    class Meta:
        model = Event
        my_fields = ('start', 'end', 'speakers', 'sponsors')
        fields = EntitySerializerL2.Meta.fields + my_fields

    def create(self, validated_data, **kwargs):
        speakers = validated_data.pop('speakers', [])
        sponsors = validated_data.pop('sponsors', [])
        self.prepare(validated_data)

        event = Event.objects.create(entity_type=BaseEntity.EVENT, **validated_data)
        self.post_create(event)

        for s in speakers:
            event.add_speaker(s)

        for s in sponsors:
            event.add_sponsor(s)

        return event

    def update(self, instance, validated_data):
        instance.start = validated_data.pop("start", instance.start)
        instance.end = validated_data.pop("end", instance.end)
        speakers = validated_data.pop('speakers', [])
        sponsors = validated_data.pop('sponsors', [])

        instance = super(EventSerializer, self).update(instance, validated_data)

        if speakers:
            instance.speakers.clear()
            for s in speakers:
                instance.add_speaker(s)

        if sponsors:
            instance.sponsors.clear()
            for s in sponsors:
                instance.add_sponsor(s)

        return instance


# these are used by App.
class EventSerializerL1(EntitySerializerL1):
    start = serializers.DateTimeField(read_only=True)
    end = serializers.DateTimeField(read_only=True)

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
    speakers = SpeakerSerializer(required=False, many=True)
    sponsors = SponsorSerializer(many=True, required=False)

    class Meta:
        model = Event
        my_fields = ('start', 'end', 'speakers', 'sponsors')
        fields = EntitySerializerL2.Meta.fields + my_fields

    def get_users(self, obj):
        count = 0
        data = []

        out = dict(count=count, data=data)

        user = self.context.get('user')
        ue, is_member = UserEntity.user_member(user, obj)

        if not is_member:
            return out

        users = obj.get_users_after(ue.last_accessed)
        ue.last_accessed_at(timezone.now())

        wizcards = [x.wizcard for x in users if hasattr(x, 'wizcard')]
        count = len(wizcards)

        out['count'] = count
        out['data'] = WizcardSerializerL1(wizcards, many=True, context={'user': user}).data

        return out

# this is used by App
class ProductSerializerL1(EntitySerializerL1):
    class Meta:
        model = Product
        my_fields = ('media', 'name', 'address', 'tags', 'joined', 'like', 'description',)
        # using L0 fields since not all L1 base class fields are needed
        fields = EntitySerializerL0.Meta.fields + my_fields

    def get_media(self, obj):
        return MediaObjectsSerializer(
            obj.media.filter(media_sub_type=MediaObjects.SUB_TYPE_LOGO),
            many=True
        ).data

    def get_users(self, obj):
        count = obj.users.count()

        out = dict(
            count=count,
        )
        return out


# this is used by App
class ProductSerializerL2(EntitySerializerL2):

    class Meta:
        model = Product
        my_fields = ('media', 'name', 'address', 'tags', 'joined', 'like', 'description',)
        fields = EntitySerializerL2.Meta.fields + my_fields


# this is used by portal REST API
class ProductSerializer(EntitySerializerL2):
    def __init__(self, *args, **kwargs):
        remove_fields = ['joined']
        super(ProductSerializer, self).__init__(*args, **kwargs)

        for field_name in remove_fields:
            self.fields.pop(field_name)

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


class TableSerializerL1(EntitySerializerL1):
    time_remaining = serializers.SerializerMethodField(read_only=True)
    creator = WizcardSerializerL1(read_only=True, source='creator.wizcard')
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VirtualTable
        my_fields = ('created', 'timeout', 'time_remaining', 'creator', 'status',)
        fields = EntitySerializerL1.Meta.fields + my_fields

    def get_media(self, obj):
        return MediaObjectsSerializer(
            obj.media.filter(media_sub_type=MediaObjects.SUB_TYPE_THUMBNAIL),
            many=True
        ).data

    def get_time_remaining(self, obj):
        if not obj.expired:
            return obj.location.get().timer.get().time_remaining()
        return 0

    def get_status(self, obj):
        user = self.context.get('user')

        if obj.is_creator(user):
            status = "creator"
        elif obj.is_joined(user):
            status = "joined"
        elif Wizcard.objects.are_wizconnections(user.wizcard, obj.creator.wizcard):
            status = "connected"
        else:
            status = "others"

        return status

class TableSerializerL2(EntitySerializerL2):
    class Meta:
        model = VirtualTable
        fields = EntitySerializerL2.Meta.fields

# this is used by portal REST API
class TableSerializer(EntitySerializerL2):
    def __init__(self, *args, **kwargs):
        remove_fields = ['joined']
        super(TableSerializer, self).__init__(*args, **kwargs)

        for field_name in remove_fields:
            self.fields.pop(field_name)

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
