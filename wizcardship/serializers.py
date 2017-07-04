__author__ = 'aammundi'
from rest_framework import serializers
from media_mgr.serializers import MediaObjectsSerializer
from wizcardship.models import Wizcard, ContactContainer

class ContactContainerSerializerL1(serializers.ModelSerializer):
    class Meta:
        model = ContactContainer
        fields = ('id', 'title', 'company',)


class ContactContainerSerializerL2(ContactContainerSerializerL1):
    media = MediaObjectsSerializer(many=True)

    class Meta:
        model = ContactContainer
        my_fields = ('phone', 'media',)
        fields = ContactContainerSerializerL1.Meta.fields + my_fields


class WizcardSerializerL0(serializers.ModelSerializer):
    wizcard_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    wizuser_id = serializers.PrimaryKeyRelatedField(source='user.pk', read_only=True)
    media = MediaObjectsSerializer(many=True)
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


class WizcardSerializerL1(WizcardSerializerL0):
    class Meta(WizcardSerializerL0.Meta):
        model = Wizcard
        my_fields = ('first_name', 'last_name', 'contact_container',)
        fields = WizcardSerializerL0.Meta.fields + my_fields

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



# not used by App
class WizcardSerializer(WizcardSerializerL2):
    class Meta:
        model = Wizcard
        fields = WizcardSerializerL2.Meta.fields

