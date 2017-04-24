from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.response import Response
import hashlib
import pdb

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (['id', 'email'])

    def create(self, validated_data):
        email = validated_data.get('email',None)
        if email:
            user, created = User.objects.get_or_create(username=email, email=email)
            if created:
                user.set_password(hashlib.sha1(email).hexdigest())
                user.save()
                user.profile.future_user = True
                user.profile.save()
            return user
        else:
            return Response


