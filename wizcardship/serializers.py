__author__ = 'aammundi'
from rest_framework import serializers
from wizcardship.models import Wizcard
from media_mgr.serializers import MediaObjectsSerializer

class WizcardSerializerThumbnail(serializers.ModelSerializer):
    thumbnail = serializers.URLField(source='get_thumbnail_url')
    wizcard_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)

    class Meta:
        model = Wizcard
        fields = ('wizcard_id', 'thumbnail',)



class WizcardSerializerL1(WizcardSerializerThumbnail):
    media = MediaObjectsSerializer(many=True)
    user_id = serializers.PrimaryKeyRelatedField(read_only=True, source='user')

    class Meta(WizcardSerializerThumbnail.Meta):
        model = Wizcard
        l1_fields = ('first_name', 'last_name', 'phone', 'email', 'media', 'user_id')
        fields = WizcardSerializerThumbnail.Meta.fields + l1_fields


class WizcardSerializer(WizcardSerializerL1):
    extFields = serializers.DictField()

    class Meta:
        model = Wizcard
        l2_fields = ('extFields', 'smsurl', 'vcard')
        fields = WizcardSerializerL1.Meta.fields + l2_fields


