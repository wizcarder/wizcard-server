from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.response import Response
import hashlib
import pdb

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')

        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password(hashlib.sha1(email).hexdigest())
            user.save()
        return user


