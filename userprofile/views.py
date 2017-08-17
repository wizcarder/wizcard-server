# Create your views here.
from userprofile.serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
import django_filters
import pdb

class UserQueryFilter(django_filters.rest_framework.FilterSet):
    email = django_filters.CharFilter(name="email")
    username = django_filters.CharFilter(name="username")

    class Meta:
        model = User
        fields = ['id','email', 'username']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_class = UserQueryFilter


class ProfileView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):

        try:
            response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
            token = Token.objects.get(key=response.data['token'])
            user = User.objects.get(id=token.user_id)
            data = UserSerializer(user).data
            return Response({'token': token.key, 'user': data})
        except:
            return Response({'error': "Could not login with credentials"}, status=status.HTTP_403_FORBIDDEN)


