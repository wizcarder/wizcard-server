__author__ = 'aammundi'
from random import sample

from rest_framework import serializers
from entity.models import Event, Campaign, VirtualTable
from base_entity.models import UserEntity, BaseEntityComponent, BaseEntity
from base_entity.serializers import EntitySerializerL0, EntitySerializer
from scan.serializers import ScannedEntitySerializer, BadgeTemplateSerializer
from entity.models import Speaker, Sponsor, Agenda, AgendaItem, AttendeeInvitee, ExhibitorInvitee, CoOwners
from wizcardship.serializers import WizcardSerializerL0, WizcardSerializerL1
from media_components.serializers import MediaEntitiesSerializer
from media_components.models import MediaEntities
from base.mixins import MediaMixin
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from polls.models import Poll, Question
from polls.serializers import QuestionResponseSerializer, QuestionSerializer, QuestionSerializerL1
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from taganomy.serializers import TaganomySerializerField
from taganomy.models import Taganomy
from lib.wizlib import get_dates_between
from time import strftime
import pdb


class TaganomySerializer(TaggitSerializer, EntitySerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Taganomy
        fields = ('id', 'tags', 'name')

    def create(self, validated_data, **kwargs):

        # prepare for this is not required. it messes with the tags by
        # popping them out.
        validated_data.update(entity_type=BaseEntityComponent.CATEGORY)
        obj = super(TaganomySerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj

    def update(self, instance, validated_data):
        obj = super(TaganomySerializer, self).update(instance, validated_data)
        self.post_create_update(instance, update=True)

        return obj


class TaganomySerializerL2(TaganomySerializer):
    class Meta:
        model = Taganomy

        my_fields = ('tags_exhibitor', 'venue_exhibitor',)
        fields = TaganomySerializer.Meta.fields + my_fields

    tags_exhibitor = serializers.SerializerMethodField()
    venue_exhibitor = serializers.SerializerMethodField()

    def get_tags_exhibitor(self, obj):
        return obj.get_sub_entities_by_tags(BaseEntityComponent.SUB_ENTITY_CAMPAIGN)

    def get_venue_exhibitor(self, obj):
        return obj.get_sub_entities_by_venue(BaseEntityComponent.SUB_ENTITY_CAMPAIGN)


class AgendaItemSerializer(EntitySerializer):
    class Meta:
        model = AgendaItem
        fields = ('id', 'name', 'description', 'start', 'end', 'venue', 'related', 'speakers',
                  'media', 'agenda', 'num_users')

    agenda = serializers.PrimaryKeyRelatedField(
        queryset=Agenda.objects.all(),
        required=False,
        source='agenda_key'
    )
    speakers = serializers.SerializerMethodField()

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.AGENDA_ITEM)

        self.prepare(validated_data)
        obj = super(AgendaItemSerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj

    def update(self, instance, validated_data):
        self.prepare(validated_data)
        obj = super(AgendaItemSerializer, self).update(instance, validated_data)
        self.post_create_update(instance, update=True)

        return obj

    def get_speakers(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_SPEAKER)


class AgendaItemSerializerL2(EntitySerializer):
    class Meta:
        model = AgendaItem
        fields = ('id', 'name', 'description', 'start', 'end', 'venue', 'related', 'speakers', 'media',  'users',
                  'poll')

    speakers = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    poll = serializers.SerializerMethodField()

    def get_speakers(self, obj):
        return SpeakerSerializerL2(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_SPEAKER),
            many=True,
            context=self.context
        ).data

    def get_users(self, obj):
        qs = obj.users.exclude(wizcard__isnull=True)
        count = qs.count()
        return count

    def get_poll(self, obj):
        poll = obj.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_POLL)
        return poll[0].id if poll else None


class AgendaSerializer(EntitySerializer):
    event = serializers.SerializerMethodField()

    class Meta:
        model = Agenda
        fields = ('id', 'name', 'description', 'entity_type', 'items', 'media', 'event', 'entity_state', 'agenda_items')

    items = AgendaItemSerializer(many=True, write_only=True)
    agenda_items = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data, **kwargs):
        items = validated_data.pop('items', [])
        validated_data.update(entity_type=BaseEntityComponent.AGENDA)

        self.prepare(validated_data)
        agn = super(AgendaSerializer, self).create(validated_data)
        self.post_create_update(agn)

        for item in items:
            item.update(agenda_key=agn)
            AgendaItemSerializer(context=self.context).create(item)

        return agn

    def update(self, instance, validated_data):
        self.prepare(validated_data)
        obj = super(AgendaSerializer, self).update(instance, validated_data)
        self.post_create_update(instance, update=True)

        return obj

    def get_event(self, obj):
        event = obj.get_parent_entities_by_contenttype_id(ContentType.objects.get(model="event"))
        return EventSerializerL0(event, many=True).data

    def get_agenda_items(self, obj):
        event = obj.get_parent_entities_by_contenttype_id(ContentType.objects.get(model="event"))[0]
        event_start = event.start
        event_end = event.end
        date_dict = dict()
        for dt in get_dates_between(event_start, event_end):
            str_dt = strftime("%Y-%m-%dT%H:%M%Z")
            date_dict[str_dt] = AgendaItemSerializer(obj.items.filter(start__year=dt.year, start__month=dt.month, start__day=dt.day), many=True).data
        return date_dict


class AgendaSerializerL1(EntitySerializer):

    class Meta:
        model=Agenda
        fields = ('id', 'entity_type', 'items', 'media')

    items = AgendaItemSerializer(many=True)

class AgendaSerializerL2(EntitySerializer):

    class Meta:
        model = Agenda
        fields = ('id', 'entity_type', 'items', 'media')

    items = AgendaItemSerializerL2(many=True)


# this is used by portal REST API
class EventSerializer(EntitySerializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    speakers = serializers.SerializerMethodField()
    sponsors = serializers.SerializerMethodField()
    agenda = serializers.SerializerMethodField()
    polls = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()
    taganomy = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        kwargs.pop('fields', None)
        remove_fields = ['user_state', 'engagements', 'users', ]

        super(EventSerializer, self).__init__(*args, **kwargs)

        for field_name in remove_fields:
            self.fields.pop(field_name)

    class Meta:
        model = Event
        my_fields = ('start', 'end', 'speakers', 'sponsors', 'agenda', 'polls', 'badges', 'taganomy',)
        fields = EntitySerializer.Meta.fields + my_fields

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.EVENT)

        self.prepare(validated_data)
        obj = super(EventSerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj

    def update(self, instance, validated_data):
        self.prepare(validated_data)
        obj = super(EventSerializer, self).update(instance, validated_data)
        self.post_create_update(instance, update=True)

        return obj

    def get_speakers(self, obj):
        return SpeakerSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_SPEAKER),
            many=True,
            context=self.context
        ).data

    def get_sponsors(self, obj):
        return SponsorSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_SPONSOR),
            many=True,
            context=self.context
        ).data

    def get_agenda(self, obj):
        return AgendaSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_AGENDA),
            many=True,
            context=self.context
        ).data

    def get_polls(self, obj):
        return PollSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_POLL),
            many=True,
            context=self.context
        ).data

    def get_taganomy(self, obj):
        return TaganomySerializer(
            obj.get_sub_entities_of_type(entity_type=BaseEntityComponent.SUB_ENTITY_CATEGORY),
            many=True
        ).data

    def get_badges(self, obj):
        return BadgeTemplateSerializer(
            obj.get_sub_entities_of_type(entity_type=BaseEntityComponent.SUB_ENTITY_BADGE_TEMPLATE),
            many=True
        ).data


# presently used by portal to show mini-event summary in sub-entity views
class EventSerializerL0(EntitySerializer):
    class Meta:
        model = Event
        fields = ('id', 'name', 'media', 'start', 'end',)

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_media_filter(
                type=MediaEntities.TYPE_IMAGE,
                sub_type=[MediaEntities.SUB_TYPE_BANNER, MediaEntities.SUB_TYPE_LOGO]
            ),
            many=True
        ).data


class ExhibitorEventSerializer(EventSerializerL0):
    class Meta:
        model = Event
        my_fields = ('taganomy',)
        fields = EventSerializerL0.Meta.fields + my_fields

    taganomy = serializers.SerializerMethodField()

    def get_taganomy(self, obj):
        return TaganomySerializer(
            obj.get_sub_entities_of_type(entity_type=BaseEntityComponent.SUB_ENTITY_CATEGORY),
            many=True
        ).data


# these are used by App.
class EventSerializerL1(EventSerializerL0):
    start = serializers.DateTimeField(read_only=True)
    end = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Event

        parent_fields = ('id', 'entity_type', 'num_users', 'name', 'address', 'secure', 'description', 'media',
                         'location', 'users', 'friends', 'like',  'engagements', 'user_state')
        my_fields = ('start', 'end',)

        fields = parent_fields + my_fields

    def get_friends(self, obj):
        user = self.context.get('user')

        friends_wizcards = obj.users_friends(user, self.MAX_THUMBNAIL_UI_LIMIT)
        out = dict(
            count=len(friends_wizcards),
            data=WizcardSerializerL0(friends_wizcards, many=True, context=self.context).data
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
            data=WizcardSerializerL0(wizcards, many=True, context={'user': self.context.get('user')}).data
        )
        return out


# these are used by App.
class EventSerializerL2(EntitySerializer):
    start = serializers.DateTimeField(read_only=True)
    end = serializers.DateTimeField(read_only=True)
    speakers = serializers.SerializerMethodField()
    sponsors = serializers.SerializerMethodField()
    campaigns = serializers.SerializerMethodField()
    agenda = serializers.SerializerMethodField()
    polls = serializers.SerializerMethodField()
    taganomy = serializers.SerializerMethodField()

    class Meta:
        model = Event

        parent_fields = EntitySerializer.Meta.fields
        my_fields = ('start', 'end', 'speakers', 'sponsors', 'campaigns', 'agenda',
                     'polls', 'taganomy',)

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

    def get_polls(self, obj):
        return PollSerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_POLL),
            many=True,
            context=self.context
        ).data

    def get_taganomy(self, obj):
        return TaganomySerializerL2(
            obj.get_sub_entities_of_type(entity_type=BaseEntityComponent.SUB_ENTITY_CATEGORY),
            many=True
        ).data


# this is used by App
class CampaignSerializerL1(EntitySerializer):

    class Meta:
        model = Campaign

        # using L0 fields since not all L1 base class fields are needed
        parent_fields = EntitySerializerL0.Meta.fields
        my_fields = ('name', 'address', 'like', 'description')

        fields = parent_fields + my_fields

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_media_filter(type=MediaEntities.TYPE_IMAGE, sub_type=[MediaEntities.SUB_TYPE_BANNER, MediaEntities.SUB_TYPE_LOGO]),
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
        my_fields = ('tags', 'like', 'is_sponsored')
        fields = EntitySerializer.Meta.fields + my_fields

    tags = TagListSerializerField(required=False)


# this is used by portal REST API
class CampaignSerializer(EntitySerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = ['user_state', ]
        super(CampaignSerializer, self).__init__(*args, **kwargs)

        for field_name in remove_fields:
            self.fields.pop(field_name)

    class Meta:
        model = Campaign
        my_fields = ('scans', 'is_sponsored', 'events', 'tags', 'taganomy')
        fields = EntitySerializer.Meta.fields + my_fields

    scans = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()
    # this is write tags
    taganomy = TaganomySerializerField(required=False, write_only=True)
    # this is to read tags
    tags = TagListSerializerField(required=False)

    def get_scans(self, obj):
        return ScannedEntitySerializer(
            obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_SCANNED_USER),
            many=True
        ).data

    def get_events(self, obj):
        parents = obj.get_parent_entities_by_contenttype_id(ContentType.objects.get(model="event"))
        return ExhibitorEventSerializer(parents, many=True).data

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.CAMPAIGN)

        self.prepare(validated_data)
        obj = super(CampaignSerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj

    def update(self, instance, validated_data):
        self.prepare(validated_data)
        obj = super(CampaignSerializer, self).update(instance, validated_data)
        self.post_create_update(instance, update=True)

        return obj


class TableSerializerL1(EntitySerializer):
    time_remaining = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VirtualTable
        my_fields = ('created', 'timeout', 'time_remaining',)
        fields = EntitySerializer.Meta.fields + my_fields

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_media_filter(type=MediaEntities.TYPE_IMAGE, sub_type=MediaEntities.SUB_TYPE_BANNER),
            many=True
        ).data

    def get_time_remaining(self, obj):
        if not obj.is_expired():
            return obj.location.get().timer.get().time_remaining()
        return 0

    def get_creator(self, obj):
        return WizcardSerializerL1(obj.get_creator().wizcard).data


class TableSerializerL2(TableSerializerL1):
    class Meta:
        model = VirtualTable
        fields = EntitySerializer.Meta.fields


# this is used by portal REST API
class TableSerializer(EntitySerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = ['user_state']
        super(TableSerializer, self).__init__(*args, **kwargs)

        for field_name in remove_fields:
            self.fields.pop(field_name)

    class Meta:
        model = VirtualTable
        fields = EntitySerializer.Meta.fields

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.TABLE)

        self.prepare(validated_data)
        obj = super(TableSerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj

    def update(self, instance, validated_data):
        self.prepare(validated_data)
        obj = super(TableSerializer, self).update(instance, validated_data)
        self.post_create_update(instance, update=True)

        return obj


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

        self.prepare(validated_data)
        obj = super(SpeakerSerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj

    def update(self, instance, validated_data):
        self.prepare(validated_data)
        obj = super(SpeakerSerializer, self).update(instance, validated_data)
        self.post_create_update(obj, update=True)

        return obj


"""
used by App
"""


class SpeakerSerializerL2(EntitySerializer):

    class Meta:
        model = Speaker
        fields = ('id', 'name', 'email', 'entity_type', 'website', 'vcard',
                  'description', 'ext_fields', 'company', 'title', 'media')


class SponsorSerializer(EntitySerializer):

    class Meta:
        model = Sponsor
        fields = ('id', 'name', 'email', 'entity_type', 'website', 'caption', 'media', 'related')

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.SPONSOR)

        self.prepare(validated_data)
        obj = super(SponsorSerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj

    def update(self, instance, validated_data):
        self.prepare(validated_data)
        obj = super(SponsorSerializer, self).update(instance, validated_data)
        self.post_create_update(obj, update=True)

        return obj


class SponsorSerializerL1(EntitySerializer):

    class Meta:
        model = Sponsor

        # using L0 fields since not all L1 base class fields are needed
        parent_fields = EntitySerializerL0.Meta.fields
        my_fields = ('id', 'name', 'email', 'entity_type', 'website', 'caption', 'media', 'related', 'like')

        fields = parent_fields + my_fields

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_media_filter(type=MediaEntities.TYPE_IMAGE, sub_type=MediaEntities.SUB_TYPE_SPONSORS_LOGO),
            many=True
        ).data

    def get_users(self, obj):
        count = obj.users.count()

        out = dict(
            count=count,
        )
        return out


class SponsorSerializerL2(EntitySerializer):

    class Meta:
        model = Sponsor
        fields = ('id', 'name', 'email', 'entity_type', 'website', 'vcard',
                  'description', 'phone', 'caption', 'ext_fields', 'media',
                  'like', 'user_state')


class ExhibitorInviteeSerializer(EntitySerializer):

    class Meta:
        model = ExhibitorInvitee
        fields = ('id', 'name', 'email', 'state',)

    state = serializers.ChoiceField(
        choices=ExhibitorInvitee.INVITE_CHOICES,
        required=False,
        read_only=True,
    )

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.EXHIBITOR_INVITEE)

        self.prepare(validated_data)
        obj = super(ExhibitorInviteeSerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj


class AttendeeInviteeSerializer(EntitySerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(AttendeeInviteeSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = AttendeeInvitee
        fields = ('id', 'name', 'email', 'state',)

    state = serializers.ChoiceField(
        choices=AttendeeInvitee.INVITE_CHOICES,
        required=False,
        read_only=True,
    )

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.ATTENDEE_INVITEE)

        self.prepare(validated_data)
        obj = super(AttendeeInviteeSerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj


class CoOwnersSerializer(EntitySerializer):
    class Meta:
        model = CoOwners
        fields = ('id', 'user', 'name', 'email', 'phone',)

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    name = serializers.SerializerMethodField(read_only=True)
    email = serializers.EmailField(read_only=True, source='user.email')
    phone = serializers.SerializerMethodField()

    def get_phone(self, obj):
        if hasattr(obj.user, 'wizcard'):
            return obj.user.wizcard.phone

        return ""

    def get_name(self, obj):
        return obj.user.first_name + "" + obj.user.last_name

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.COOWNER)
        self.prepare(validated_data)
        obj = super(CoOwnersSerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj


class PollSerializerL1(EntitySerializer):
    class Meta:
        model = Poll
        fields = ('id', 'questions', 'num_responders', )
        read_only_fields = ('num_responders',)

    questions = QuestionSerializerL1(many=True)


# this is used to create a poll. This is also used to send serialized Poll to App

class PollSerializer(EntitySerializer):
    class Meta:
        model = Poll
        fields = ('id', 'description', 'questions', 'user_state', 'num_responders', 'created', 'event')
        read_only_fields = ('entity_state', 'num_responders', 'created', 'event',)

    event = serializers.SerializerMethodField()
    questions = QuestionSerializer(many=True)

    def get_user_state(self, obj):
        return ""

    def prepare(self, validated_data):
        self.questions = validated_data.pop('questions', None)
        super(PollSerializer, self).prepare(validated_data)

    def post_create_update(self, obj, update=False):
        for q in self.questions:
            choices = q.pop('choices', [])
            q_inst = Question.objects.create(poll=obj, **q)

            cls = Question.objects.get_choice_cls_from_type(q['question_type'])

            if choices:
                [cls.objects.create(question=q_inst, **c) for c in choices]
            else:
                cls.objects.create(question=q_inst)

        super(PollSerializer, self).post_create_update(obj, update=update)

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.POLL)

        self.prepare(validated_data)
        obj = super(PollSerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj

    def update(self, instance, validated_data):
        self.prepare(validated_data)
        super(PollSerializer, self).update(instance, validated_data)

        # clear all questions first. For some reason bulk delete is not working
        for q in instance.questions.all():
            q.delete()

        # create the questions and choices
        self.post_create_update(instance, update=True)

        return instance

    def get_event(self, obj):
        event = obj.get_parent_entities_by_contenttype_id(ContentType.objects.get(model="event"))
        return EventSerializerL0(event, many=True).data


class PollResponseSerializer(EntitySerializer):
    class Meta:
        model = Poll
        fields = ('id', 'event', 'num_responders', 'description', 'questions', 'entity_state')
        read_only_fields = ('entity_state', 'num_responders',)

    questions = QuestionResponseSerializer(many=True)
    event = serializers.SerializerMethodField(read_only=True)

    def get_event(self, obj):
        # typically expecting one parent only...the Poll UI allows associating with one event only. No issues
        # if extended to multiple events both in the related_to plumbing and here as well. Here, since we're
        # passing the whole list, the only difference is that even for a single case, there will be {[]] instead
        # of {}, in the response
        event = obj.get_parent_entities_by_contenttype_id(ContentType.objects.get(model="event"))
        return EventSerializerL0(event, many=True).data

