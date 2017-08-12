from rest_framework import viewsets
from rest_framework.response import Response
from base_entity.models import BaseEntity
from entity.models import Event, Product, Business, VirtualTable,\
    Speaker, Sponsor, ExhibitorInvitee, AttendeeInvitee, CoOwners
from entity.serializers import  EventSerializer, EventSerializerL2 ,ProductSerializer, \
    BusinessSerializer, TableSerializer, ExhibitorSerializer, AttendeeSerializer, SpeakerSerializerL1, \
    SponsorSerializerL1, SponsorSerializerL2, CoOwnersSerializer
from django.http import Http404
from rest_framework.decorators import detail_route
from email_and_push_infra.models import EmailEvent
from email_and_push_infra.signals import email_trigger
from rest_framework import status
from base_entity.views import BaseEntityViewSet, BaseEntityComponentViewSet
from base_entity.models import BaseEntityComponent
import pdb


# Create your views here.

class EventViewSet(BaseEntityViewSet):
    serializer_class = EventSerializer

    def get_serializer_class(self):
        user = self.request.user
        #if self.request.method == 'GET' and user is not None:
         #   return EventSerializerL2
        return EventSerializer

    def get_object_or_404(self, pk):
        try:
            return Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404

    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.users_entities(user)
        return queryset

    def update(self, request, pk=None, partial=True):
        inst = self.get_object_or_404(pk)
        serializer = EventSerializer(inst, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
        else:
            raise Http404
        return Response(serializer.data)

    @detail_route(methods=['post'])
    def invite_exhibitors(self, request, pk=None):
        inst = self.get_object_or_404(pk)

        exhibitors = request.data
        passed_emails, failed_str = ExhibitorInvitee.validate(exhibitors['ids'])

        for recp in passed_emails:
            email_trigger.send(inst, source=inst, trigger=EmailEvent.INVITE_EXHIBITOR, to_email=recp)

        return Response("Exhibitors invited %s Failed ids: %s" % (len(passed_emails), failed_str) , status=status.HTTP_200_OK)


class ProductViewSet(BaseEntityViewSet, BaseEntityComponentViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.users_entities(user)
        return queryset


class BusinessViewSet(BaseEntityViewSet, BaseEntityComponentViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Business.objects.users_entities(user)
        return queryset


class TableViewSet(BaseEntityViewSet, BaseEntityComponentViewSet):
    queryset = VirtualTable.objects.all()
    serializer_class = TableSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = VirtualTable.objects.users_entities(user)
        return queryset

class SpeakerViewSet(BaseEntityComponentViewSet):
    queryset = Speaker.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Speaker.objects.users_speakers(user)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_serializer_class(self):
        return SpeakerSerializerL1


class SponsorViewSet(BaseEntityComponentViewSet):
    queryset = Sponsor.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Sponsor.objects.users_sponsors(user)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_serializer_class(self):
        return SponsorSerializerL1


class ExhibitorViewSet(BaseEntityComponentViewSet):
    queryset = ExhibitorInvitee.objects.all()
    serializer_class = ExhibitorSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = BaseEntityComponent.objects.users_components(user, ExhibitorInvitee)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}

class AttendeeViewSet(BaseEntityComponentViewSet):
    queryset = AttendeeInvitee.objects.all()
    serializer_class = AttendeeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = BaseEntityComponent.objects.users_components(user, AttendeeInvitee)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}


class OwnersViewSet(BaseEntityComponentViewSet):
    pass




