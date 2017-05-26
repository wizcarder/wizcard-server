__author__ = 'aammundi'
from rest_framework import serializers
from wizcardship.models import Wizcard, ContactContainer
from media_mgr.serializers import MediaObjectsSerializer


class ContactContainerSerializerL0(serializers.ModelSerializer):
    f_card_url = serializers.URLField(source='get_fbizcard_url')

    class Meta:
        model = ContactContainer
        fields = ('id', 'title', 'company', 'f_card_url')


class ContactContainerSerializerL1(ContactContainerSerializerL0):
    pass


class WizcardSerializerThumbnail(serializers.ModelSerializer):
    wizcard_id = serializers.IntegerField(source='id')

    class Meta:
        model = Wizcard
        fields = ('wizcard_id', 'thumbnail_url',)

    thumbnail_url = serializers.URLField(source='get_thumbnail_url')


class WizcardSerializerL1(WizcardSerializerThumbnail):
    # AA: couldn't find a prescribed way to do this
    user_id = serializers.PrimaryKeyRelatedField(read_only=True, source='user.id')
    contact_container = ContactContainerSerializerL0(many=True, read_only=True)
    media = MediaObjectsSerializer(many=True)

    class Meta(WizcardSerializerThumbnail.Meta):
        model = Wizcard
        l1_fields = ('first_name', 'last_name', 'phone', 'email', 'user_id', 'contact_container')
        fields = WizcardSerializerThumbnail.Meta.fields + l1_fields


class WizcardSerializerL2(WizcardSerializerL1):
    pass

# not used by App
class WizcardSerializer(WizcardSerializerL1):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    extFields = serializers.DictField()

    class Meta:
        model = Wizcard
        l2_fields = ('extFields', 'smsurl', 'vcard')
        fields = WizcardSerializerL1.Meta.fields + l2_fields


