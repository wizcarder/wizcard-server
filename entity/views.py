from rest_framework.response import Response
from base_entity.models import BaseEntityComponent
from entity.models import Event, Campaign, VirtualTable,\
    Speaker, Sponsor, ExhibitorInvitee, AttendeeInvitee, Agenda, CoOwners
from entity.serializers import EventSerializer, CampaignSerializer, \
    TableSerializer, AttendeeInviteeSerializer, ExhibitorInviteeSerializer, SponsorSerializer, \
    SpeakerSerializer, AgendaSerializer, CoOwnersSerializer
from rest_framework.decorators import detail_route
from rest_framework import status
from base_entity.views import BaseEntityViewSet, BaseEntityComponentViewSet
from django.shortcuts import get_object_or_404
from itertools import chain


import pdb


# Create your views here.

class ExhibitorEventViewSet(BaseEntityViewSet):
    serializer_class = EventSerializer

    def get_serializer_class(self):
        return EventSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.users_entities(user)
        return queryset


class EventViewSet(BaseEntityViewSet):
    serializer_class = EventSerializer

    def get_serializer_class(self):
        return EventSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.owners_entities(user)
        return queryset

    @detail_route(methods=['post'])
    def invite_exhibitors(self, request, pk=None):
        inst = get_object_or_404(Event, pk=pk)

        exhibitor_invitees = request.data

        # set related for these exhibitors. We will relate the entity to the ExhibitorInvitee model
        # and check for those events when the exhibitor comes in, treating the exhibitor email as the
        # handle within ExhibitorInvitee. Essentially, Exhibitor/AttendeeInvitee becomes the future user construct

        # exhibitor may already have an account. if so, join them to event
        existing_users, existing_exhibitors = ExhibitorInvitee.objects.check_existing_users_exhibitors(
            exhibitor_invitees
        )
        [inst.join(u, notify=False) for u in existing_users]
        existing_exhibitors.update(state=ExhibitorInvitee.ACCEPTED)

        new_exhibitors = [x for x in exhibitor_invitees if x not in existing_exhibitors.values_list('id', flat=True)]

        # @AR: the complicated c-type logic is not required. add_subentities already validates with a much more
        # concise & pythonic query

        # relate these with Event
        invited_exhibitors = inst.add_subentities(new_exhibitors, BaseEntityComponent.SUB_ENTITY_EXHIBITOR_INVITEE)
        invited_exhibitors.update(state=ExhibitorInvitee.INVITED)

        result_list = list(chain(existing_exhibitors, invited_exhibitors))
        return Response(ExhibitorInviteeSerializer(result_list, many=True).data)

    @detail_route(methods=['post'])
    def invite_attendees(self, request, pk=None):
        inst = get_object_or_404(Event, pk=pk)

        attendees = request.data

        valid_candidates = inst.add_subentities(attendees, BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE)

        return Response(AttendeeInviteeSerializer(valid_candidates, many=True)).data

    @detail_route(methods=['get'])
    def publish_event(self, request, pk=None):
        inst = get_object_or_404(Event, pk=pk)
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
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer

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



