__author__ = 'aammundi'
from rest_framework import serializers
from wizcardship.models import Wizcard
from media_mgr.serializers import MediaObjectsSerializer


class WizcardSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    extFields = serializers.SerializerMethodField()
    media = MediaObjectsSerializer(many=True)

    def get_extFields(self, obj):
        return obj.get_extFields

    class Meta:
        model = Wizcard
        fields = ('pk', 'user', 'first_name', 'last_name', 'phone', 'email', 'extFields', 'media', 'smsurl', 'vcard')

class WizcardSerializerSummary(serializers.ModelSerializer):
    media = MediaObjectsSerializer(many=True)

    class Meta:
        model = Wizcard
        fields = ('pk', 'first_name', 'last_name', 'phone', 'email', 'media',)

