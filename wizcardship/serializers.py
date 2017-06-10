__author__ = 'aammundi'
from rest_framework import serializers
from media_mgr.serializers import MediaObjectsSerializer
from wizcardship.models import Wizcard, ContactContainer

class ContactContainerSerializerL0(serializers.ModelSerializer):
    class Meta:
        model = ContactContainer
        fields = ('id', 'title', 'company',)


class ContactContainerSerializerL1(ContactContainerSerializerL0):
    f_card_url = serializers.URLField(source='get_fbizcard_url')

    class Meta:
        model = ContactContainer
        my_fields = ('phone', 'f_card_url',)
        fields = ContactContainerSerializerL0.Meta.fields + my_fields


class WizcardSerializerL0(serializers.ModelSerializer):
    wizcard_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(source='user.pk', read_only=True)
    thumbnail_url = serializers.URLField(source='get_thumbnail_url')
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Wizcard
        fields = ('wizcard_id', 'user_id', 'thumbnail_url', 'status')

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

    contact_container = ContactContainerSerializerL0(many=True, read_only=True)


class WizcardSerializerL2(WizcardSerializerL1):
    media = MediaObjectsSerializer(many=True)
    ext_fields = serializers.DictField()
    video_url = serializers.URLField(read_only=True, source='get_video_url')

    class Meta(WizcardSerializerL1.Meta):
        model = Wizcard
        my_fields = ('phone', 'email', 'media', 'ext_fields', 'video_url',
                     'video_thumbnail_url', 'vcard', 'sms_url',)
        fields = WizcardSerializerL1.Meta.fields + my_fields


# not used by App
class WizcardSerializer(WizcardSerializerL2):
    class Meta:
        model = Wizcard
        fields = WizcardSerializerL2.Meta.fields

