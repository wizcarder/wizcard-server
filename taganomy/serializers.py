
from taganomy.models import Taganomy
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from base_entity.serializers import EntitySerializer
from base_entity.models import BaseEntityComponent


class TaganomySerializer(EntitySerializer, TaggitSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Taganomy
        fields = ('id', 'tags', 'name')

    def create(self, validated_data, **kwargs):
        validated_data.update(entity_type=BaseEntityComponent.CATEGORY)
        self.prepare(validated_data)
        obj = super(TaganomySerializer, self).create(validated_data)
        self.post_create_update(obj)

        return obj

    def update(self, instance, validated_data):
        obj = super(TaganomySerializer, self).update(validated_data)
        self.post_create_update(instance, update=True)


class TaganomySerializerL1(TaggitSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Taganomy
        fields = ('tags', )
