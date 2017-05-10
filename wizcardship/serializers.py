__author__ = 'aammundi'
from rest_framework import serializers
from wizcardship.models import Wizcard
from media_mgr.serializers import MediaObjectsSerializer

class WizcardSerializerThumbnail(serializers.ModelSerializer):
    class Meta:
        model = Wizcard
        fields = ('id', 'thumbnail',)

    thumbnail = serializers.URLField(source='get_thumbnail_url')


class WizcardSerializerL1(WizcardSerializerThumbnail):
    media = MediaObjectsSerializer(many=True)

    class Meta(WizcardSerializerThumbnail.Meta):
        model = Wizcard
        l1_fields = ('first_name', 'last_name', 'phone', 'email', 'media', 'user')
        fields = WizcardSerializerThumbnail.Meta.fields + l1_fields


class WizcardSerializer(WizcardSerializerL1):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    extFields = serializers.DictField()

    class Meta:
        model = Wizcard
        l2_fields = ('extFields', 'smsurl', 'vcard')
        fields = WizcardSerializerL1.Meta.fields + l2_fields


