__author__ = 'aammundi'
from random import sample

from rest_framework import serializers
from entity.models import Event, Campaign, VirtualTable
from base_entity.models import UserEntity, BaseEntityComponent, BaseEntity
from base_entity.serializers import EntitySerializerL0, EntitySerializer
from entity.models import Speaker, Sponsor, Agenda, AgendaItem, AttendeeInvitee, ExhibitorInvitee
from wizcardship.serializers import WizcardSerializerL0, WizcardSerializerL1
from wizcardship.models import Wizcard
from media_components.serializers import MediaEntitiesSerializer
from media_components.models import MediaEntities
from base.mixins import MediaMixin
from django.utils import timezone
import pdb


class AgendaItemSerializer(EntitySerializer):
    class Meta:
        model = AgendaItem
        fields = ('id', 'name', 'description', 'start', 'end', 'where', 'related', 'speakers', 'media')

    speakers = serializers.SerializerMethodField()

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.AGENDA_ITEM)

        return super(AgendaItemSerializer, self).create(validated_data)

    def get_speakers(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_SPEAKER)

    def update(self, instance, validated_data):
        instance = super(AgendaItemSerializer, self).update(instance, validated_data)

        return instance


class AgendaItemSerializerL2(EntitySerializer):
    class Meta:
        model = AgendaItem
        fields = ('id', 'name', 'description', 'start', 'end', 'where', 'related', 'speakers', 'media')

    speakers = serializers.SerializerMethodField()

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA),
            many=True,
            context=self.context
        ).data

    def get_speakers(self, obj):
        return SpeakerSerializerL2(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_SPEAKER),
            many=True,
            context=self.context
        ).data


class AgendaSerializer(EntitySerializer):
    class Meta:
        model = Agenda
        fields = ('id', 'entity_type', 'items')

    items = AgendaItemSerializer(many=True)

    def create(self, validated_data, **kwargs):
        items = validated_data.pop('items', [])
        validated_data.update(entity_type=BaseEntityComponent.AGENDA)
        agn = super(AgendaSerializer, self).create(validated_data)

        for item in items:
            item.update(agenda = agn)
            AgendaItemSerializer(context=self.context).create(item)

        return agn


class AgendaSerializerL2(EntitySerializer):

    class Meta:
        model = Agenda
        fields = ('id', 'entity_type', 'items')

    items = AgendaItemSerializerL2(many=True)

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA),
            many=True,
            context=self.context
        ).data

    def get_speakers(self, obj):
        return SpeakerSerializerL2(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_SPEAKER),
            many=True,
            context=self.context
        ).data


# this is used by portal REST API
class EventSerializer(EntitySerializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    speakers = serializers.SerializerMethodField()
    sponsors = serializers.SerializerMethodField()
    campaigns = serializers.SerializerMethodField()
    agenda = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        kwargs.pop('fields', None)
        remove_fields = ['joined', 'engagements', 'users']

        super(EventSerializer, self).__init__(*args, **kwargs)

        for field_name in remove_fields:
            self.fields.pop(field_name)

    class Meta:
        model = Event
        my_fields = ('start', 'end', 'campaigns', 'speakers', 'sponsors', 'agenda')
        fields = EntitySerializer.Meta.fields + my_fields

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.EVENT)

        return super(EventSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        instance.start = validated_data.pop("start", instance.start)
        instance.end = validated_data.pop("end", instance.end)

        instance = super(EventSerializer, self).update(instance, validated_data)

        return instance

    def get_campaigns(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_CAMPAIGN)

    def get_speakers(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_SPEAKER)

    def get_sponsors(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_SPONSOR)

    def get_agenda(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_AGENDA)


# these are used by App.
class EventSerializerL1(EntitySerializer):
    start = serializers.DateTimeField(read_only=True)
    end = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Event

        parent_fields = ('id', 'entity_type', 'num_users', 'name', 'address', 'secure', 'description', 'media',
                         'location', 'users', 'joined', 'friends', 'like', 'tags', 'engagements')
        my_fields = ('start', 'end', )

        fields = parent_fields + my_fields

    def get_friends(self, obj):
        user = self.context.get('user')

        friends_wizcards = obj.users_friends(user, self.MAX_THUMBNAIL_UI_LIMIT)
        out = dict(
            count=len(friends_wizcards),
            data=WizcardSerializerL0(friends_wizcards, many=True).data
        )
        return out

    def get_users(self, obj):
        out = dict(
            count=0,
            data=[]
        )

        qs = obj.users.exclude(wizcard__isnull=True)
        count = qs.count()

        if not count:
            return out

        qs_media = [x.wizcard.media.all().generic_objects() for x in qs if x.wizcard.media.all().exists()]
        qs_thumbnail = [y.get_creator() for x in qs_media for y in x if
                        y.media_sub_type == MediaMixin.SUB_TYPE_THUMBNAIL]

        thumb_count = len(qs_thumbnail)

        if not thumb_count:
            return out

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

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_media_filter(type=MediaEntities.TYPE_IMAGE, sub_type=MediaEntities.SUB_TYPE_BANNER),
            many=True
        ).data

# these are used by App.
class EventSerializerL2(EntitySerializer):
    start = serializers.DateTimeField(read_only=True)
    end = serializers.DateTimeField(read_only=True)
    speakers = serializers.SerializerMethodField()
    sponsors = serializers.SerializerMethodField()
    campaigns = serializers.SerializerMethodField()
    agenda = serializers.SerializerMethodField()

    class Meta:
        model = Event

        parent_fields = EntitySerializer.Meta.fields
        my_fields = ('start', 'end', 'speakers', 'sponsors', 'campaigns', 'agenda')

        fields = parent_fields + my_fields

    def get_users(self, obj):
        out = dict(
            count=0,
            data=[]
        )

        user = self.context.get('user')
        ue, is_member = UserEntity.user_member(user, obj)

        if not is_member:
            return out

        users = obj.get_users_after(ue.last_accessed)
        ue.last_accessed_at(timezone.now())

        wizcards = [x.wizcard for x in users if hasattr(x, 'wizcard')]
        count = len(wizcards)

        if not count:
            return out

        out['count'] = count
        out['data'] = WizcardSerializerL1(wizcards, many=True, context={'user': user}).data

        return out

    def get_speakers(self, obj):
        return SpeakerSerializerL2(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_SPEAKER),
            many=True,
            context=self.context
        ).data

    def get_sponsors(self, obj):
        return SponsorSerializerL2(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_SPONSOR),
            many=True,
            context=self.context
        ).data

    def get_campaigns(self, obj):
        return CampaignSerializerL2(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_CAMPAIGN),
            many=True,
            context=self.context
        ).data

    def get_agenda(self, obj):
        return AgendaSerializerL2(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_AGENDA),
            many=True,
            context=self.context
        ).data

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA),
            many=True
        ).data


# this is used by App
class CampaignSerializerL1(EntitySerializer):

    class Meta:
        model = Campaign

        # using L0 fields since not all L1 base class fields are needed
        parent_fields = EntitySerializerL0.Meta.fields
        my_fields = ('name', 'address', 'tags', 'joined', 'like', 'description',)

        fields = parent_fields + my_fields

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_media_filter(type=MediaEntities.TYPE_IMAGE, sub_type=MediaEntities.SUB_TYPE_BANNER),
            many=True
        ).data

    def get_users(self, obj):
        count = obj.users.count()

        out = dict(
            count=count,
        )
        return out


# this is used by App
class CampaignSerializerL2(EntitySerializer):
    class Meta:
        model = Campaign
        my_fields = ('tags', 'joined', 'like',)
        fields = EntitySerializer.Meta.fields + my_fields

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA),
            many=True
        ).data

# this is used by portal REST API
class CampaignSerializer(EntitySerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = ['joined']
        super(CampaignSerializer, self).__init__(*args, **kwargs)

        for field_name in remove_fields:
            self.fields.pop(field_name)

    class Meta:
        model = Campaign
        fields = EntitySerializer.Meta.fields

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.CAMPAIGN)

        return super(CampaignSerializer, self).create(validated_data)


class TableSerializerL1(EntitySerializer):
    time_remaining = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VirtualTable
        my_fields = ('created', 'timeout', 'time_remaining', 'status',)
        fields = EntitySerializer.Meta.fields + my_fields

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_media_filter(type=MediaEntities.TYPE_IMAGE, sub_type=MediaEntities.SUB_TYPE_BANNER),
            many=True
        ).data

    def get_time_remaining(self, obj):
        if not obj.expired:
            return obj.location.get().timer.get().time_remaining()
        return 0

    def get_creator(self, obj):
        return WizcardSerializerL1(obj.get_creator().wizcard).data

    def get_status(self, obj):
        user = self.context.get('user')

        if obj.is_creator(user):
            status = "creator"
        elif obj.is_joined(user):
            status = "joined"
        elif Wizcard.objects.are_wizconnections(user.wizcard, obj.get_creator().wizcard):
            status = "connected"
        else:
            status = "others"

        return status

class TableSerializerL2(EntitySerializer):
    class Meta:
        model = VirtualTable
        fields = EntitySerializer.Meta.fields

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA),
            many=True
        ).data


# this is used by portal REST API
class TableSerializer(EntitySerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = ['joined']
        super(TableSerializer, self).__init__(*args, **kwargs)

        for field_name in remove_fields:
            self.fields.pop(field_name)

    class Meta:
        model = VirtualTable
        fields = EntitySerializer.Meta.fields

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.TABLE)

        return super(TableSerializer, self).create(validated_data)

"""
used by portal
"""
class SpeakerSerializer(EntitySerializer):
    class Meta:
        model = Speaker
        fields = ('id', 'name', 'email', 'entity_type', 'website', 'vcard',
                  'description', 'ext_fields', 'company', 'title', 'media', 'related')
        read_only_fields = ('vcard',)

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.SPEAKER)

        return super(SpeakerSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.pop('name', instance.name)
        instance.email = validated_data.pop('email', instance.email)
        instance.website = validated_data.pop('website', instance.website)
        instance.vcard = validated_data.pop('vcard', instance.vcard)
        instance.description = validated_data.pop('description', instance.description)
        instance.ext_fields = validated_data.pop('ext_fields', instance.ext_fields)
        instance.company = validated_data.pop('company', instance.company)
        instance.title = validated_data.pop('title', instance.title)

        instance = super(SpeakerSerializer, self).update(instance, validated_data)

        return instance

"""
used by App
"""
class SpeakerSerializerL2(EntitySerializer):

    class Meta:
        model = Speaker
        fields = ('id', 'name', 'email', 'entity_type', 'website', 'vcard',
                  'description', 'ext_fields', 'company', 'title', 'media')

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA),
            many=True
        ).data


class SponsorSerializer(EntitySerializer):

    class Meta:
        model = Sponsor
        fields = ('id', 'name', 'email', 'entity_type', 'website', 'caption', 'media', 'related')

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.SPONSOR)

        return super(SponsorSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.pop('name', instance.name)
        instance.email = validated_data.pop('email', instance.email)
        instance.website = validated_data.pop('website', instance.website)
        instance.caption = validated_data.pop('caption', instance.caption)
        instance.description = validated_data.pop('description', instance.description)

        instance = super(SponsorSerializer, self).update(instance, validated_data)

        return instance


class SponsorSerializerL2(EntitySerializer):

    class Meta:
        model = Sponsor
        fields = ('id', 'name', 'email', 'entity_type', 'website', 'vcard',
                  'description', 'phone', 'caption', 'ext_fields', 'media')

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA),
            many=True
        ).data


class ExhibitorInviteeSerializer(EntitySerializer):

    class Meta:
        model = ExhibitorInvitee
        fields = ('id', 'name', 'email')

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.EXHIBITOR_INVITEE)

        return super(ExhibitorInviteeSerializer, self).create(validated_data)


class AttendeeInviteeSerializer(EntitySerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(AttendeeInviteeSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = AttendeeInvitee
        fields = ['id', 'name', 'email']

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.ATTENDEE_INVITEE)

        return super(AttendeeInviteeSerializer, self).create(validated_data)


class CoOwnersSerializer(EntitySerializer):
    class Meta:
        model = AttendeeInvitee
        fields = ['id', 'name', 'email']

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.COOWNER)

        return super(CoOwnersSerializer, self).create(validated_data)

