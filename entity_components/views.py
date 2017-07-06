from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth.models import User
from entity_components.models import Speaker, Sponsor
from entity_components.serializers import SpeakerSerializer, SponsorSerializer

# Create your views here.

class SpeakerViewSet(viewsets.ModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer

    def get_queryset(self):
        queryset = Speaker.objects.all()
        return super(SpeakerViewSet, self).get_queryset()

    def get_serializer_context(self):
        uid = self.request.query_params.get('user', None)
        if uid is not None:
            user = User.objects.get(id=uid)
            return {'user': user}
        else:
            return {}


class SponsorViewSet(viewsets.ModelViewSet):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer

    def get_queryset(self):
        queryset = Sponsor.objects.all()
        return super(SponsorViewSet, self).get_queryset()

    def get_serializer_context(self):
        uid = self.request.query_params.get('user', None)
        if uid is not None:
            user = User.objects.get(id=uid)
            return {'user': user}
        else:
            return {}