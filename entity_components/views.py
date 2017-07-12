from rest_framework import viewsets
from entity_components.models import Speaker, Sponsor, MediaEntities
from entity_components.serializers import SpeakerSerializerL1, SpeakerSerializerL2, SponsorSerializerL1, SponsorSerializerL2, MediaEntitiesSerializer
import pdb

# Create your views here.

class SpeakerViewSet(viewsets.ModelViewSet):
    queryset = Speaker.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Speaker.objects.users_speakers(user)
        return queryset

    def get_serializer_context(self):
        return {'user' : self.request.user}

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SpeakerSerializerL2
        return SpeakerSerializerL1


class SponsorViewSet(viewsets.ModelViewSet):
    queryset = Sponsor.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Sponsor.objects.users_sponsors(user)
        return queryset

    def get_serializer_context(self):
        return {'user' : self.request.user}

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SponsorSerializerL2
        return SponsorSerializerL1

class MediaEntitiesViewSet(viewsets.ModelViewSet):
    queryset = MediaEntities.objects.all()
    serializer_class = MediaEntitiesSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = MediaEntities.objects.users_media(user)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}

