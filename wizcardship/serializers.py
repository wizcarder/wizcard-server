__author__ = 'aammundi'
from rest_framework import serializers
from wizcardship.models import Wizcard, ContactContainer
from media_mgr.serializers import MediaObjectsSerializer
from wizserver import verbs


class ContactContainerSerializerL0(serializers.ModelSerializer):
    f_card_url = serializers.URLField(source='get_fbizcard_url')

    class Meta:
        model = ContactContainer
        fields = ('id', 'title', 'company', 'f_card_url')


class ContactContainerSerializerL1(ContactContainerSerializerL0):
    pass


class WizcardSerializerThumbnail(serializers.ModelSerializer):
    thumbnail_url = serializers.URLField(source='get_thumbnail_url')
    wizcard_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)

    class Meta:
        model = Wizcard
        fields = ('wizcard_id', 'thumbnail_url',)


class WizcardSerializerL1(WizcardSerializerThumbnail):
    # AA: couldn't find a prescribed way to do this
    user_id = serializers.PrimaryKeyRelatedField(read_only=True, source='user.id')
    contact_container = ContactContainerSerializerL0(many=True, read_only=True)
    media = MediaObjectsSerializer(many=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta(WizcardSerializerThumbnail.Meta):
        model = Wizcard
        l1_fields = ('first_name', 'last_name', 'phone', 'email', 'user_id', 'contact_container', 'status', 'media')
        fields = WizcardSerializerThumbnail.Meta.fields + l1_fields

    def get_status(self, obj):
        user = self.context.get('user', None)
        status = ''
        if user:
            wizcard = user.wizcard
            status = Wizcard.objects.get_connection_status(wizcard, obj)
        return status


class WizcardSerializerL2(WizcardSerializerL1):
    ext_fields = serializers.DictField()
    video_url = serializers.URLField(read_only=True, source='get_video_url')
    video_thumbnail_url = serializers.URLField(read_only=True)

    class Meta(WizcardSerializerL1.Meta):
        model = Wizcard
        l2_fields = ('ext_fields', 'video_url', 'video_thumbnail_url', 'vcard', 'sms_url')
        fields = WizcardSerializerL1.Meta.fields + l2_fields
    

# not used by App
class WizcardSerializer(WizcardSerializerL1):
    ext_fields = serializers.DictField()

    class Meta:
        model = Wizcard
        l2_fields = ('ext_fields', 'sms_url', 'vcard')
        fields = WizcardSerializerL1.Meta.fields + l2_fields


