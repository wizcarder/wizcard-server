__author__ = 'aammundi'
from random import sample

from rest_framework import serializers
from entity.models import Event, Product, Business, VirtualTable
from base_entity.models import UserEntity, BaseEntityComponent, BaseEntity
from base_entity.serializers import EntitySerializerL0, EntitySerializerL1, EntitySerializerL2, \
    BaseEntityComponentSerializer, RelatedSerializerField
from entity.models import Speaker, Sponsor, ExhibitorInvitee, AttendeeInvitee, CoOwners
from wizcardship.serializers import WizcardSerializerL0, WizcardSerializerL1
from wizcardship.models import Wizcard
from media_components.serializers import MediaEntitiesSerializer
from media_components.models import MediaEntities
from django.utils import timezone
import pdb


# this is used by portal REST API
class EventSerializer(EntitySerializerL2):
    def __init__(self, *args, **kwargs):
        kwargs.pop('fields', None)
        remove_fields = ['joined', 'engagements', 'users']

        super(EventSerializer, self).__init__(*args, **kwargs)

        for field_name in remove_fields:
            self.fields.pop(field_name)

    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    products = serializers.SerializerMethodField()
    speakers = serializers.SerializerMethodField()
    sponsors = serializers.SerializerMethodField()
    exhibitors = serializers.SerializerMethodField()
    attendees = serializers.SerializerMethodField()

    class Meta:
        model = Event
        my_fields = ('start', 'end', 'speakers', 'sponsors', 'exhibitors', 'products')
        fields = EntitySerializerL2.Meta.fields + my_fields

    def create(self, validated_data, **kwargs):
        self.prepare(validated_data)
        event = Event.objects.create(entity_type=BaseEntity.EVENT, **validated_data)
        self.post_create(event)

        return event

    def update(self, instance, validated_data):
        instance.start = validated_data.pop("start", instance.start)
        instance.end = validated_data.pop("end", instance.end)

        instance = super(EventSerializer, self).update(instance, validated_data)

        return instance

    def get_products(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_PRODUCT)

    def get_speakers(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_SPEAKER)

    def get_sponsors(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_SPONSOR)

    def get_exhibitors(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_EXHIBITOR)

    def get_media(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_MEDIA)

    def get_attendees(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_ATTENDEE)


# these are used by App.
class EventSerializerL1(EntitySerializerL1):
    start = serializers.DateTimeField(read_only=True)
    end = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Event
        my_fields = ('start', 'end',)
        fields = EntitySerializerL1.Meta.fields + my_fields

    def get_media(self, obj):
        return MediaEntitiesSerializer(
            obj.get_media_filter(type = MediaEntities.TYPE_IMAGE, sub_type=MediaEntities.SUB_TYPE_BANNER),
            many=True
        ).data

# these are used by App.
class EventSerializerL2(EventSerializerL1, EntitySerializerL2):

    products = serializers.SerializerMethodField()
    speakers = serializers.SerializerMethodField()
    sponsors = serializers.SerializerMethodField()


    class Meta:
        model = Event
        my_fields = ('start', 'end', 'speakers', 'sponsors', 'products')
        fields = EntitySerializerL2.Meta.fields + my_fields

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
        spkrs = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_SPEAKER)
        s = SpeakerSerializerL2(spkrs, many=True)
        return s.data

    def get_sponsors(self, obj):
        spns = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_SPONSOR)
        s = SponsorSerializerL2(spns, many=True)
        return s.data

    def get_products(self, obj):
        prods = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_PRODUCT)
        s = ProductSerializerL2(prods, many=True, context=self.context)
        return s.data


# this is used by App
class ProductSerializerL1(EntitySerializerL1):

    class Meta:
        model = Product
        my_fields = ('name', 'address', 'tags', 'joined', 'like', 'description',)
        # using L0 fields since not all L1 base class fields are needed
        fields = EntitySerializerL0.Meta.fields + my_fields

    def get_media(self, obj):
        return ""

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
        my_fields = ('name', 'address', 'tags', 'joined', 'like', 'description',)
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

    related = RelatedSerializerField(many=True, required=False, write_only=True)

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
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VirtualTable
        my_fields = ('created', 'timeout', 'time_remaining', 'status',)
        fields = EntitySerializerL1.Meta.fields + my_fields

    def get_media(self, obj):
        return ""

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


class SpeakerSerializerL1(BaseEntityComponentSerializer):
    media = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = Speaker
        fields = '__all__'
        read_only_fields = ('vcard',)

    def create(self, validated_data, **kwargs):
        self.prepare(validated_data)
        spkr = BaseEntityComponent.create(Speaker, owner=self.context.get('user'), is_creator=True, entity_type='SPK', **validated_data)
        self.post_create(spkr)
        return spkr

    def update(self, instance, validated_data):
        instance.vcard = validated_data.pop('vcard', instance.vcard)
        instance.company = validated_data.pop('company', instance.company)
        instance.title = validated_data.pop('title', instance.title)
        instance.name = validated_data.pop('name', instance.name)
        instance.email = validated_data.pop('email', instance.email)
        instance.website = validated_data.pop('website', instance.website)
        instance.description = validated_data.pop('description', instance.description)

        instance = super(SpeakerSerializerL1, self).update(instance, validated_data)

        return instance

    def get_media(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_MEDIA)

class SpeakerSerializerL2(SpeakerSerializerL1):

    class Meta:
        model = Speaker
        fields = '__all__'

    def get_media(self, obj):
        media = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA)
        s = MediaEntitiesSerializer(media, many=True)
        return s.data


class SponsorSerializerL1(BaseEntityComponentSerializer):

    media = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = Sponsor
        fields = "__all__"

    def create(self, validated_data):
        self.prepare(validated_data)
        spn = BaseEntityComponent.create(Sponsor, owner=self.context.get('user'), is_creator=True, entity_type='SPN',**validated_data)
        self.post_create(spn)
        return spn

    def get_media(self, obj):
        return obj.get_sub_entities_id_of_type(BaseEntity.SUB_ENTITY_MEDIA)


class SponsorSerializerL2(SponsorSerializerL1):

    class Meta:
        model = Sponsor
        fields = '__all__'

    def get_media(self, obj):
        media = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA)
        s = MediaEntitiesSerializer(media, many=True)
        return s.data



class ExhibitorSerializer(BaseEntityComponentSerializer):

    class Meta:
        model = ExhibitorInvitee
        fields = ('id', 'name', 'email')

    def create(self, validated_data):
        user = self.context.get('user')
        mobj = BaseEntityComponent.create(ExhibitorInvitee, owner=user, is_creator=True, entity_type='EXB', **validated_data)
        return mobj

class AttendeeSerializer(ExhibitorSerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(AttendeeSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = AttendeeInvitee
        fields = ['id', 'name', 'email']

    def create(self, validated_data):
        user = self.context.get('user')
        mobj = BaseEntityComponent.create(AttendeeInvitee, owner=user, is_creator=True, entity_type='ATT', **validated_data)
        return mobj

class CoOwnersSerializer(BaseEntityComponentSerializer):
    pass
