__author__ = 'aammundi'
from rest_framework import serializers
from wizcardship.models import Wizcard


class WizcardSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    extFields = serializers.SerializerMethodField()

    def get_extFields(self, obj):
        return obj.get_extFields

    class Meta:
        model = Wizcard
        fields = ('pk','user', 'first_name', 'last_name', 'phone', 'email', 'thumbnailImage', 'videoUrl', 'videoThumbnailUrl', 'extFields',
                  'smsurl', 'vcard')

