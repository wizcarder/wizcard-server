from rest_framework.response import Response
from base_entity.models import BaseEntityComponent
from entity.models import Event, Campaign, VirtualTable,\
    Speaker, Sponsor, ExhibitorInvitee, AttendeeInvitee, Agenda, CoOwners
from entity.serializers import EventSerializer, CampaignSerializer, \
    TableSerializer, AttendeeInviteeSerializer, ExhibitorInviteeSerializer, SponsorSerializer, \
    SpeakerSerializer, AgendaSerializer, CoOwnersSerializer
from django.http import Http404
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from email_and_push_infra.models import EmailEvent
from email_and_push_infra.signals import email_trigger
from rest_framework import status
from base_entity.views import BaseEntityViewSet, BaseEntityComponentViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

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
            inst.notify_update()
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

    def perform_destroy(self, instance):
        parents = instance.get_parent_entities()
        if parents:
            return Response(data="Instance is being used", status=status.HTTP_403_FORBIDDEN)
        else:
            instance.related.all().delete()
            instance.mark_deleted()
            instance.notify_delete()
            return Response(status=status.HTTP_200_OK)





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

    def get_serializer_class(self):
        return SpeakerSerializer


class SponsorViewSet(BaseEntityComponentViewSet):
    queryset = Sponsor.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Sponsor.objects.owners_entities(user)
        return queryset

    def get_serializer_class(self):
        return SponsorSerializer


class ExhibitorViewSet(BaseEntityComponentViewSet):
    queryset = ExhibitorInvitee.objects.all()
    serializer_class = ExhibitorInviteeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = ExhibitorInvitee.objects.owners_entities(user)
        return queryset


class AttendeeViewSet(BaseEntityComponentViewSet):
    queryset = AttendeeInvitee.objects.all()
    serializer_class = AttendeeInviteeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = AttendeeInvitee.objects.owners_entities(user)
        return queryset


class CoOwnersViewSet(BaseEntityComponentViewSet):
    queryset = CoOwners.objects.all()
    serializer_class = CoOwnersSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = CoOwners.objects.owners_entities(user)
        return queryset


class AgendaViewSet(BaseEntityComponentViewSet):
    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        agn = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_AGENDA)
        return Response(AgendaSerializer(agn, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            agn = Agenda.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if agn not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_AGENDA):
            return Response("event id %s not associated with Agenda %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(AgendaSerializer(agn).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AgendaSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_AGENDA)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None, event_pk=None):
        try:
            agn = Agenda.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if agn not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_AGENDA):
            return Response("event id %s not associated with Agenda %s " % (pk, event_pk),
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = AgendaSerializer(agn, data=request.data)
        if serializer.is_valid():
            inst = serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, pk=None, event_pk=None):
        try:
            agn = Agenda.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if agn not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_AGENDA):
            return Response("event id %s not associated with Agenda %s " % (pk, event_pk),
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = AgendaSerializer(agn, data=request.data)
        if serializer.is_valid():
            inst = serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None, event_pk=None):
        try:
            agn = Agenda.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if agn not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_AGENDA):
            return Response("event id %s not associated with Agenda %s " % (pk, event_pk),
                            status=status.HTTP_400_BAD_REQUEST)

        event.remove_sub_entity_of_type(agn.pk, BaseEntityComponent.AGENDA)
        agn.delete()

        return Response(status=status.HTTP_200_OK)



