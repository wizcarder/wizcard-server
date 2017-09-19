from rest_framework.response import Response
from base_entity.models import BaseEntityComponent
from entity.models import Event, Campaign, VirtualTable,\
    Speaker, Sponsor, ExhibitorInvitee, AttendeeInvitee
from entity.serializers import EventSerializer, CampaignSerializer, \
    TableSerializer, AttendeeInviteeSerializer, ExhibitorInviteeSerializer, SponsorSerializer, \
    SpeakerSerializer
from django.http import Http404
from rest_framework.decorators import detail_route
from email_and_push_infra.models import EmailEvent
from email_and_push_infra.signals import email_trigger
from rest_framework import status
from base_entity.views import BaseEntityViewSet, BaseEntityComponentViewSet
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
        queryset = Event.objects.owners_entities(user)
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

     # AR: Need to the nested thingy but given Raghu's time adding this hack.
    @detail_route(methods=['post'])
    def invite_attendees(self, request, pk=None):
        inst = self.get_object_or_404(pk)

        attendees = request.data
        passed_emails, failed_str = AttendeeInvitee.validate(attendees['ids'])

        for recp in passed_emails:
            email_trigger.send(inst, source=inst, trigger=EmailEvent.INVITE_ATTENDEE, to_email=recp)

        return Response("Attendees invited %s Failed ids: %s" % (len(passed_emails), failed_str),
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def publish_event(self, request, pk=None):
        inst = self.get_object_or_404(pk)
        inst.make_live()

        return Response("event id %s activated" % pk, status=status.HTTP_200_OK)


class CampaignViewSet(BaseEntityViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Campaign.objects.owners_entities(user)
        return queryset

class TableViewSet(BaseEntityViewSet):
    queryset = VirtualTable.objects.all()
    serializer_class = TableSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = VirtualTable.objects.owners_entities(user)
        return queryset

class SpeakerViewSet(BaseEntityComponentViewSet):
    queryset = Speaker.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Speaker.objects.owners_entities(user)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_serializer_class(self):
        return SpeakerSerializer


class SponsorViewSet(BaseEntityComponentViewSet):
    queryset = Sponsor.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Sponsor.objects.users_sponsors(user)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_serializer_class(self):
        return SponsorSerializer


class ExhibitorViewSet(BaseEntityComponentViewSet):
    queryset = ExhibitorInvitee.objects.all()
    serializer_class = ExhibitorInviteeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = BaseEntityComponent.objects.users_components(user, ExhibitorInvitee)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}

class AttendeeViewSet(BaseEntityComponentViewSet):
    queryset = AttendeeInvitee.objects.all()
    serializer_class = AttendeeInviteeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = BaseEntityComponent.objects.users_components(user, AttendeeInvitee)
        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}


class OwnersViewSet(BaseEntityComponentViewSet):
    pass



