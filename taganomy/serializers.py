
from rest_framework import serializers
from taganomy.models import Taganomy
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from base_entity.serializers import EntitySerializer
from base_entity.models import BaseEntityComponent
import pdb


class TaganomySerializer(EntitySerializer, TaggitSerializer):
    tags = TagListSerializerField()
    category = serializers.CharField()

    class Meta:
        model = Taganomy
        fields = ('id', 'tags', 'category',)


    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.CATEGORY)

        self.prepare(validated_data)
        obj = super(TaganomySerializer, self).create(validated_data)
        self.post_create(obj)

        return obj

    def update(self, instance, validated_data):
        instance.category = validated_data.pop('category', instance.category)
        tags = validated_data.pop('category', instance.tags)
        instance.tags.set(*tags)

class TaganomySerializerL1(TaggitSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Taganomy
        fields = ('tags', )


