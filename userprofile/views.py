# Create your views here.
from userprofile.serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
import django_filters


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


