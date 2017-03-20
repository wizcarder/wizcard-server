__author__ = 'aammundi'

from rest_framework import serializers
from media_mgr.models import MediaObjects

class MediaObjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaObjects
        fields = ('id', 'media_element', 'media_iframe', 'media_type', 'media_sub_type')