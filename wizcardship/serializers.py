__author__ = 'aammundi'
from rest_framework import serializers
from media_components.serializers import MediaEntitiesSerializer
from wizcardship.models import Wizcard, ContactContainer, DeadCard
import pdb

class ContactContainerSerializerL1(serializers.ModelSerializer):
    class Meta:
        model = ContactContainer
        fields = ('id', 'title', 'company',)


class ContactContainerSerializerL2(ContactContainerSerializerL1):
    media = serializers.SerializerMethodField()

    class Meta:
        model = ContactContainer
        my_fields = ('phone', 'media',)
        fields = ContactContainerSerializerL1.Meta.fields + my_fields

    def get_media(self, obj):
        mobjs = obj.media.all().generic_objects()
        data = MediaEntitiesSerializer(mobjs, many=True).data
        return data


class WizcardSerializerL0(serializers.ModelSerializer):
    wizcard_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    wizuser_id = serializers.PrimaryKeyRelatedField(source='user.pk', read_only=True)
    media = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Wizcard
        fields = ('wizcard_id', 'wizuser_id', 'media', 'status')

    def get_status(self, obj):
        user = self.context.get('user', None)
        status = self.context.get('status', "")

        if user:
            wizcard = user.wizcard
            status = Wizcard.objects.get_connection_status(wizcard, obj)

        return status

    def get_media(self, obj):
        mobjs = obj.media.all().generic_objects()
        data = MediaEntitiesSerializer(mobjs, many=True).data
        return data


class WizcardSerializerL1(WizcardSerializerL0):
    class Meta(WizcardSerializerL0.Meta):
        model = Wizcard
        my_fields = ('first_name', 'last_name', 'contact_container',)
        fields = WizcardSerializerL0.Meta.fields + my_fields

    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    contact_container = ContactContainerSerializerL2(many=True, read_only=True)


class WizcardSerializerL2(WizcardSerializerL1):
    ext_fields = serializers.DictField()
    #video_url = serializers.URLField(read_only=True, source='get_video_url')

    class Meta(WizcardSerializerL1.Meta):
        model = Wizcard
        my_fields = ('phone', 'email', 'ext_fields',
                     'vcard', 'sms_url',)
        fields = WizcardSerializerL1.Meta.fields + my_fields

    contact_container = ContactContainerSerializerL2(many=True, read_only=True)


class DeadCardSerializerL2(WizcardSerializerL2):
    context = serializers.DictField(source='cctx')

    class Meta(WizcardSerializerL2.Meta):
        model = DeadCard
        my_fields = ('invited', 'activated', 'context',)
        fields = WizcardSerializerL2.Meta.fields + my_fields

    def get_status(self, obj):
        return "dead_card"

# not used by App
class WizcardSerializer(WizcardSerializerL2):
    class Meta:
        model = Wizcard
        fields = WizcardSerializerL2.Meta.fields

