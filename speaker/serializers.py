from rest_framework import serializers
from rest_framework.validators import ValidationError
from speaker.models import Speaker
from userprofile.serializers import UserSerializer
import pdb




class SpeakerSerializer(serializers.ModelSerializer):

    user = UserSerializer(required=False)

    class Meta:
        model = Speaker
        fields = "__all__"