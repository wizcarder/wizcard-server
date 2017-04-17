from django.shortcuts import render
from speaker.serializers import SpeakerSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets
from speaker.models import Speaker
import django_filters
import pdb

class SpeakerViewSet(viewsets.ModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer

