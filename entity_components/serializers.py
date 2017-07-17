__author__ = 'aammundi'

from rest_framework import serializers
from entity.models import BaseEntityComponent
from entity_components.models import MediaEntities

#from entity.serializers import RelatedSerializerField, RelatedSerializerFieldL2
import pdb

class MediaEntitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaEntities
        fields = ('id', 'entity_type', 'media_type', 'media_element', 'media_iframe', 'media_sub_type')

    def create(self, validated_data):
        user = self.context.get('user')
        mobj = BaseEntityComponent.create(MediaEntities, owner=user, is_creator=True, entity_type='MED', **validated_data)
        return mobj



