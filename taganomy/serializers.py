
from rest_framework import serializers
from taganomy.models import Taganomy
from django.contrib.auth.models import User
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)


class TaganomySerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    #editor = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Taganomy
        fields = '__all__'

