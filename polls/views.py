from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets, status
from base_entity.views import BaseEntityComponentViewSet
from polls.serializers import PollSerializer
from polls.models import Poll

# Create your views here.

class PollViewSet(BaseEntityComponentViewSet):

    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Poll.objects.owners_entities(user)
        return queryset