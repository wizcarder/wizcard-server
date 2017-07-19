__author__ = 'aammundi'
from random import sample

from rest_framework import serializers
from rest_framework.validators import ValidationError

from entity.models import Event, Product, Business, VirtualTable
from base_entity.models import UserEntity, BaseEntityComponent, BaseEntity
from base_entity.serializers import EntitySerializerL0, EntitySerializerL1, EntitySerializerL2, \
    BaseEntityComponentSerializer, RelatedSerializerField
#from entity.models import EntityEngagementStats, EntityUserStats

#from entity.serializers import SpeakerSerializerL1, SponsorSerializerL1
from entity.models import Speaker, Sponsor, ExhibitorInvitee, AttendeeInvitee, CoOwners
from wizcardship.serializers import WizcardSerializerL0, WizcardSerializerL1
from wizcardship.models import Wizcard
from entity_components.serializers import MediaEntitiesSerializer
from entity_components.models import MediaEntities
from django.utils import timezone
import pdb

# these shouldn't be directly used.

# this is used by portal REST API
class EventSerializer(EntitySerializerL2):
    def __init__(self, *args, **kwargs):
        kwargs.pop('fields', None)
        remove_fields = ['joined', 'engagements']

        super(EventSerializer, self).__init__(*args, **kwargs)

        for field_name in remove_fields:
            self.fields.pop(field_name)

    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    related = RelatedSerializerField(many=True,required=False, write_only=True)
    products = serializers.SerializerMethodField()
    speakers = serializers.SerializerMethodField()
    sponsors = serializers.SerializerMethodField()
    exhibitors = serializers.SerializerMethodField()


    class Meta:
        model = Event
        my_fields = ('start', 'end', 'speakers', 'sponsors','exhibitors', 'products')
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

    def get_related_out(self, obj):
        valid_sub_entities = [BaseEntity.SUB_ENTITY_SPONSOR, BaseEntity.SUB_ENTITY_SPEAKER, BaseEntity.SUB_ENTITY_MEDIA]
        related_dict = dict()
        for se in valid_sub_entities:

            sobjs = obj.get_sub_entities_of_type(se)
            if sobjs:
                sids = map(lambda x: x.id, sobjs)
                related_dict[se] = sids

        return related_dict

    def get_products(self, obj):
        prods = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_PRODUCT)
        ids = map(lambda x:x.id, prods)
        return ids

    def get_speakers(self, obj):
        spkrs = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_SPEAKER)
        ids = map(lambda x: x.id, spkrs)
        return ids

    def get_sponsors(self, obj):
        spns = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_SPONSOR)
        ids = map(lambda x: x.id, spns)
        return ids

    def get_exhibitors(self, obj):
        exb = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_EXHIBITOR)
        ids = map(lambda x: x.id, exb)
        return ids

    def get_media(self, obj):
        med = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA)
        ids = map(lambda x: x.id, med)
        return ids

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

    class Meta:
        model = Event
        my_fields = ('start', 'end',)
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

    def get_media(self, obj):
        med = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_EXHIBITOR)
        ids = map(lambda x: x.id, med)
        return ids


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
        media = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA)
        ids = map(lambda x: x.id, media)
        return ids

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
        media = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA)
        ids = map(lambda x: x.id, media)
        return ids


class SponsorSerializerL2(SponsorSerializerL1):

    class Meta:
        model = Sponsor
        fields = '__all__'

    def get_media(self, obj):
        media = obj.get_sub_entities_of_type(BaseEntity.SUB_ENTITY_MEDIA)
        s = MediaEntitiesSerializer(media, many=True)
        return s.data



class ExhibitorSerializer(BaseEntityComponentSerializer):
    #def __init__(self, *args, **kwargs):
     #   pdb.set_trace()
      #  many = kwargs.pop('many', True)
       # super(ExhibitorSerializer, self).__init__(many=many, *args, **kwargs)

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
        fields = ['name', 'email']

class CoOwnersSerializer(BaseEntityComponentSerializer):
    pass













