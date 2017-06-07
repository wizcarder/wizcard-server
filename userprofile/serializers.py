from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.response import Response
import hashlib
import pdb


class UserSerializerL0(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'email', 'first_name', 'last_name')

    user_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    email = serializers.EmailField(source='wizcard.email', read_only=True)


# used by portal
class UserSerializer(UserSerializerL0):

    class Meta(UserSerializerL0.Meta):
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

    email = serializers.EmailField()


    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')

        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password(hashlib.sha1(email).hexdigest())
            user.save()
        return user


