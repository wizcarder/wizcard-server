from rest_framework.response import Response
from base_entity.models import BaseEntityComponent, UserEntity
from entity.models import Event, Campaign, VirtualTable,\
    Speaker, Sponsor, ExhibitorInvitee, AttendeeInvitee, Agenda, AgendaItem, CoOwners
from polls.models import Poll
from entity.serializers import EventSerializer, EventSerializerL0, CampaignSerializer, \
    TableSerializer, AttendeeInviteeSerializer, ExhibitorInviteeSerializer, SponsorSerializer, \
    SpeakerSerializer, AgendaSerializer, AgendaItemSerializer, PollSerializer, CoOwnersSerializer
from media_components.serializers import MediaEntitiesSerializer
from media_components.models import MediaEntities
from notifications.models import AsyncNotification
from notifications.serializers import AsyncNotificationSerializer
from taganomy.models import Taganomy
from entity.serializers import TaganomySerializer
from rest_framework.decorators import detail_route, list_route
from rest_framework import viewsets, status, mixins, views
from base_entity.views import BaseEntityViewSet, BaseEntityComponentViewSet
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from itertools import chain
from scan.models import BadgeTemplate
from scan.serializers import BadgeTemplateSerializer
from wizserver import verbs
from rest_framework.parsers import FileUploadParser, MultiPartParser, JSONParser
from entity.tasks import create_entities



import pdb


# Create your views here.

class ExhibitorEventViewSet(BaseEntityViewSet):
    serializer_class = EventSerializerL0

    def get_serializer_class(self):
        return EventSerializerL0

    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.users_entities(
            user,
            user_filter={'state': UserEntity.JOIN},
            entity_filter={'entity_state': BaseEntityComponent.ENTITY_STATE_PUBLISHED}
        )
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
        exhibitor_invitees = request.data['ids']

        # set related for these exhibitors. We will relate the entity to the ExhibitorInvitee model
        # and check for those events when the exhibitor comes in, treating the exhibitor email as the
        # handle within ExhibitorInvitee. Essentially, Exhibitor/AttendeeInvitee becomes the future user construct

        # exhibitor may already have an account. if so, join them to event
        existing_users, existing_exhibitors = ExhibitorInvitee.objects.check_existing_users_exhibitors(
            exhibitor_invitees
        )
        [inst.user_attach(u, state=UserEntity.JOIN, do_notify=True) for u in existing_users]

        for e in existing_exhibitors:
            e.state = ExhibitorInvitee.ACCEPTED
            e.save()

        new_exhibitors = [x for x in exhibitor_invitees if x not in existing_exhibitors.values_list('id', flat=True)]

        # relate these with Event
        invited_exhibitors = inst.add_subentities(new_exhibitors, BaseEntityComponent.SUB_ENTITY_EXHIBITOR_INVITEE)
        for i in invited_exhibitors:
            i.state = ExhibitorInvitee.INVITED
            i.save()

        result_list = list(chain(existing_exhibitors, invited_exhibitors))
        return Response(ExhibitorInviteeSerializer(result_list, many=True).data)

    @detail_route(methods=['post'])
    def invite_attendees(self, request, pk=None):
        inst = get_object_or_404(Event, pk=pk)
        attendee_invitees = request.data['ids']

        existing_users, existing_attendees = AttendeeInvitee.objects.check_existing_users_attendees(
            attendee_invitees
        )
        [inst.user_attach(u, state=UserEntity.JOIN, do_notify=True) for u in existing_users]

        for e in existing_attendees:
            e.state = AttendeeInvitee.ACCEPTED
            e.save()

        new_attendees = [x for x in attendee_invitees if x not in existing_attendees.values_list('id', flat=True)]

        # relate these with Event
        invited_attendees = inst.add_subentities(new_attendees, BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE)
        for i in invited_attendees:
            i.state = AttendeeInvitee.INVITED
            i.save()

        result_list = list(chain(existing_attendees, invited_attendees))
        return Response(AttendeeInviteeSerializer(result_list, many=True).data)

    @detail_route(methods=['put'])
    def publish_event(self, request, pk=None):
        inst = get_object_or_404(Event, pk=pk)
        inst.set_entity_state(BaseEntityComponent.ENTITY_STATE_PUBLISHED)
        return Response("event id %s published" % pk, status=status.HTTP_200_OK)


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


class SponsorViewSet(BaseEntityViewSet):
    queryset = Sponsor.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Sponsor.objects.owners_entities(user)
        return queryset

    def get_serializer_class(self):
        return SponsorSerializer


class ExhibitorInviteeViewSet(BaseEntityComponentViewSet):
    queryset = ExhibitorInvitee.objects.all()
    serializer_class = ExhibitorInviteeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = ExhibitorInvitee.objects.owners_entities(user)
        return queryset


class AgendaViewSet(BaseEntityComponentViewSet):
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Agenda.objects.owners_entities(user)
        return queryset

    def get_serializer_class(self):
        return AgendaSerializer


class AgendaItemViewSet(BaseEntityComponentViewSet):
    queryset = AgendaItem.objects.all()
    serializer_class = AgendaItemSerializer

    def list(self, request, agenda_pk=None):
        agn = Agenda.objects.get(id=agenda_pk)
        return Response(AgendaItemSerializer(agn.items.all(), many=True).data)

    def retrieve(self, request, pk=None, agenda_pk=None):
        try:
            agn = Agenda.objects.get(id=agenda_pk)
            agi = AgendaItem.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if agi not in agn.items.all():
            return Response("agenda item id %s not associated with Agenda %s " % (pk, agenda_pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(AgendaItemSerializer(agi).data)

    def create(self, request, agenda_pk=None):
        try:
            agn = Agenda.objects.get(id=agenda_pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        request.data.update(agenda=agn.pk)
        serializer = AgendaItemSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, agenda_pk=None):
        try:
            agn = Agenda.objects.get(id=agenda_pk)
            agi = AgendaItem.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if agi not in agn.items.all():
            return Response("agenda item id %s not associated with Agenda %s " % (pk, agenda_pk),
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = AgendaItemSerializer(agi, data=request.data)
        if serializer.is_valid():
            inst = serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None, agenda_pk=None):
        try:
            agn = Agenda.objects.get(id=agenda_pk)
            agi = AgendaItem.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if agi not in agn.items.all():
            return Response("agenda item id %s not associated with Agenda %s " % (pk, agenda_pk),
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = AgendaItemSerializer(agi, data=request.data, partial=True)
        if serializer.is_valid():
            inst = serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, agenda_pk=None):
        try:
            agn = Agenda.objects.get(id=agenda_pk)
            agi = AgendaItem.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if agi not in agn.items.all():
            return Response("agenda item id %s not associated with Agenda %s " % (pk, agenda_pk),
                            status=status.HTTP_400_BAD_REQUEST)

        agi.delete()

        return Response(status=status.HTTP_200_OK)


class AttendeeViewSet(BaseEntityComponentViewSet):
    queryset = AttendeeInvitee.objects.all()
    serializer_class = AttendeeInviteeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = AttendeeInvitee.objects.owners_entities(user)
        return queryset


class CoOwnerViewSet(BaseEntityComponentViewSet):
    queryset = CoOwners.objects.all()
    serializer_class = CoOwnersSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = CoOwners.objects.owners_entities(user)
        return queryset


"""
All the nested end-points for linking entity to sub-entity
"""


class EventCampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        cpg = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CAMPAIGN)
        return Response(CampaignSerializer(cpg, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            cpg = Campaign.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if cpg not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CAMPAIGN):
            return Response("event id %s not associated with Campaign %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(CampaignSerializer(cpg).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CampaignSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_CAMPAIGN)
            inst.set_entity_state(BaseEntityComponent.ENTITY_STATE_PUBLISHED)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            cpg = Campaign.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if cpg in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CAMPAIGN):
            return Response("event %s already  associated with Campaign %s " % (event_pk, pk),
                            status=status.HTTP_200_OK)

        event.add_subentity_obj(cpg, BaseEntityComponent.SUB_ENTITY_CAMPAIGN)
        cpg.set_entity_state(BaseEntityComponent.ENTITY_STATE_PUBLISHED)

        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            cpg = Campaign.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if cpg not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CAMPAIGN):
            return Response("event id %s not associated with Campaign %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        event.remove_sub_entity_obj(cpg, BaseEntityComponent.SUB_ENTITY_CAMPAIGN)
        cpg.set_entity_state(BaseEntityComponent.ENTITY_STATE_CREATED)

        return Response(status=status.HTTP_200_OK)


class EventSpeakerViewSet(viewsets.ModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        spk = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_SPEAKER)
        return Response(SpeakerSerializer(spk, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            spk = Speaker.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if spk not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_SPEAKER):
            return Response("event id %s not associated with Speaker %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(SpeakerSerializer(spk).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = SpeakerSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_SPEAKER)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            spk = Speaker.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if spk in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_SPEAKER):
            return Response("event %s already  associated with Speaker %s " % (event_pk, pk),
                            status=status.HTTP_200_OK)

        event.add_subentity_obj(spk, BaseEntityComponent.SUB_ENTITY_SPEAKER)
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            spk = Speaker.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if spk not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_SPEAKER):
            return Response("event id %s not associated with Speaker %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        event.remove_sub_entity_obj(spk, BaseEntityComponent.SUB_ENTITY_SPEAKER)

        return Response(status=status.HTTP_200_OK)


class EventSponsorViewSet(viewsets.ModelViewSet):
    queryset = Sponsor.objects.all()
    serializer_class = SpeakerSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        spn = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_SPONSOR)
        return Response(SpeakerSerializer(spn, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            spn = Sponsor.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if spn not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_SPONSOR):
            return Response("event id %s not associated with Sponsor %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(SponsorSerializer(spn).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = SponsorSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_SPONSOR)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            spn = Sponsor.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if spn in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_SPONSOR):
            return Response("event %s already  associated with Sponsor %s " % (event_pk, pk),
                            status=status.HTTP_200_OK)

        event.add_subentity_obj(spn, BaseEntityComponent.SUB_ENTITY_SPONSOR)
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            spn = Sponsor.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if spn not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_SPONSOR):
            return Response("event id %s not associated with Sponsor %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        event.remove_sub_entity_obj(spn, BaseEntityComponent.SUB_ENTITY_SPONSOR)

        return Response(status=status.HTTP_200_OK)


class EventMediaViewSet(viewsets.ModelViewSet):
    queryset = MediaEntities.objects.all()
    serializer_class = MediaEntitiesSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        med = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_MEDIA)
        return Response(MediaEntitiesSerializer(med, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            med = MediaEntities.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if med not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_MEDIA):
            return Response("event id %s not associated with Media %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(SponsorSerializer(med).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = MediaEntitiesSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_MEDIA)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            med = MediaEntities.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if med in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_MEDIA):
            return Response("event %s already  associated with Media %s " % (event_pk, pk),
                            status=status.HTTP_200_OK)

        event.add_subentity_obj(med, BaseEntityComponent.SUB_ENTITY_MEDIA)
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            med = MediaEntities.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if med not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_MEDIA):
            return Response("event id %s not associated with Media %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        event.remove_sub_entity_obj(med, BaseEntityComponent.SUB_ENTITY_MEDIA)

        return Response(status=status.HTTP_200_OK)


class EventAttendeeViewSet(viewsets.ModelViewSet):
    queryset = AttendeeInvitee.objects.all()
    serializer_class = AttendeeInviteeSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        ati = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE)
        return Response(AttendeeInviteeSerializer(ati, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            ati = AttendeeInvitee.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if ati not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE):
            return Response("event id %s not associated with invitee %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(AttendeeInviteeSerializer(ati).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AttendeeInviteeSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            ati = AttendeeInvitee.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if ati in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE):
            return Response("event %s already  associated with attendee invitee %s " % (event_pk, pk),
                            status=status.HTTP_200_OK)

        event.add_subentity_obj(ati, BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE)
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            ati = AttendeeInvitee.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if ati not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE):
            return Response("event id %s not associated with Attendee Invitee %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        event.remove_sub_entity_obj(ati, BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE)

        return Response(status=status.HTTP_200_OK)


class EventExhibitorViewSet(viewsets.ModelViewSet):
    queryset = ExhibitorInvitee.objects.all()
    serializer_class = ExhibitorInviteeSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        exi = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_EXHIBITOR_INVITEE)
        return Response(ExhibitorInviteeSerializer(exi, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            exi = ExhibitorInvitee.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if exi not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_EXHIBITOR_INVITEE):
            return Response("event id %s not associated with invitee %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(ExhibitorInviteeSerializer(exi).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ExhibitorInviteeSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_EXHIBITOR_INVITEE)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            exi = ExhibitorInvitee.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if exi in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_EXHIBITOR_INVITEE):
            return Response("event %s already  associated with exhibitor invitee %s " % (event_pk, pk),
                            status=status.HTTP_200_OK)

        event.add_subentity_obj(exi, BaseEntityComponent.SUB_ENTITY_EXHIBITOR_INVITEE)
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            exi = ExhibitorInvitee.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if exi not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_EXHIBITOR_INVITEE):
            return Response("event id %s not associated with Exhibitor Invitee %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        event.remove_sub_entity_obj(exi, BaseEntityComponent.SUB_ENTITY_EXHIBITOR_INVITEE)

        return Response(status=status.HTTP_200_OK)


class EventCoOwnerViewSet(viewsets.ModelViewSet):
    queryset = CoOwners.objects.all()
    serializer_class = CoOwnersSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        ati = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_COOWNER)
        return Response(CoOwnersSerializer(ati, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            coo = CoOwners.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if coo not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_COOWNER):
            return Response("event id %s not associated with co-owner %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(CoOwnersSerializer(coo).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CoOwnersSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_COOWNER)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            coo = CoOwners.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if coo in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_COOWNER):
            return Response("event %s already  associated with CoOwner %s " % (event_pk, pk),
                            status=status.HTTP_200_OK)

        event.add_subentity_obj(coo, BaseEntityComponent.SUB_ENTITY_COOWNER)
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            coo = CoOwners.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if coo not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_COOWNER):
            return Response("event id %s not associated with CoOwner %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        event.remove_sub_entity_obj(coo, BaseEntityComponent.SUB_ENTITY_COOWNER)

        return Response(status=status.HTTP_200_OK)


class EventAgendaViewSet(viewsets.ModelViewSet):
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
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if agn not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_AGENDA):
            return Response("event id %s not associated with Agenda %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(AgendaSerializer(agn).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AgendaSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_AGENDA)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            agn = Agenda.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if agn in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_AGENDA):
            return Response("event id %s already associated with agenda %s " % (event_pk, pk),
                            status=status.HTTP_200_OK)

        parents = agn.get_parent_entities()
        if parents:
            return Response("Operation Failed - Detach Agenda %s from  Event - %s and Retry" % (agn.name, event.name),
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        event.add_subentity_obj(agn, BaseEntityComponent.SUB_ENTITY_AGENDA)
        agn.set_entity_state(BaseEntityComponent.ENTITY_STATE_PUBLISHED)

        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            agn = Agenda.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if agn not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_AGENDA):
            return Response("event id %s not associated with Agenda %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        event.remove_sub_entity_obj(agn, BaseEntityComponent.SUB_ENTITY_AGENDA)
        return Response(status=status.HTTP_200_OK)


class EventPollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        pol = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_POLL)
        return Response(PollSerializer(pol, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            pol = Poll.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if pol not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_POLL):
            return Response("event id %s not associated with Poll %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(PollSerializer(pol).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PollSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_POLL)
            inst.set_entity_state(BaseEntityComponent.ENTITY_STATE_PUBLISHED)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            pol = Poll.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if pol in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_POLL):
            return Response("event id %s already associated with poll %s " % (event_pk, pk),
                            status=status.HTTP_200_OK)

        parents = pol.get_parent_entities()
        if parents:
            return Response("Operation Failed - Detach Poll - %s from  Event - %s and Retry" % (pol.name, event.name),
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        event.add_subentity_obj(pol, BaseEntityComponent.SUB_ENTITY_POLL)
        pol.set_entity_state(BaseEntityComponent.ENTITY_STATE_PUBLISHED)

        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            pol = Poll.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if pol not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_POLL):
            return Response("event id %s not associated with Poll %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        event.remove_sub_entity_obj(pol, BaseEntityComponent.SUB_ENTITY_POLL)
        pol.set_entity_state(BaseEntityComponent.ENTITY_STATE_CREATED)

        return Response(status=status.HTTP_200_OK)


class EventNotificationViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = AsyncNotification.objects.all()
    serializer_class = AsyncNotificationSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        ntf = AsyncNotification.objects.event_notifications(event)

        return Response(AsyncNotificationSerializer(ntf, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            ntf = AsyncNotification.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(AsyncNotificationSerializer(ntf).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AsyncNotificationSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventTaganomyViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Taganomy.objects.all()
    serializer_class = TaganomySerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        cat = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CATEGORY)
        return Response(TaganomySerializer(cat, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            cat = Taganomy.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if cat not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CATEGORY):
            return Response("event id %s not associated with category %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(TaganomySerializer(cat).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TaganomySerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_CATEGORY)
            inst.set_entity_state(BaseEntityComponent.ENTITY_STATE_PUBLISHED)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            taganomy = Taganomy.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if taganomy in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_POLL):
            return Response("event id %s already associated with taganomy %s " % (event_pk, pk),
                            status=status.HTTP_200_OK)

        parents = taganomy.get_parent_entities()
        if parents:
            return Response("Operation Failed - Detach Taganomy - %s from  Event - %s and Retry" % (taganomy.name, event.name),
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        event.add_subentity_obj(taganomy, BaseEntityComponent.SUB_ENTITY_CATEGORY)
        taganomy.set_entity_state(BaseEntityComponent.ENTITY_STATE_PUBLISHED)

        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            tgn = Taganomy.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if tgn not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CATEGORY):
            return Response("event id %s not associated with Taganomy %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        event.remove_sub_entity_obj(tgn, BaseEntityComponent.SUB_ENTITY_CATEGORY)
        tgn.set_entity_state(BaseEntityComponent.ENTITY_STATE_CREATED)

        return Response(status=status.HTTP_200_OK)


class EventBadgeViewSet(viewsets.ModelViewSet):
    queryset = BadgeTemplate.objects.all()
    serializer_class = BadgeTemplateSerializer

    def list(self, request, event_pk=None):
        event = Event.objects.get(id=event_pk)
        badge = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_BADGE_TEMPLATE)
        return Response(BadgeTemplateSerializer(badge, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            badge = BadgeTemplate.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if badge not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_BADGE_TEMPLATE):
            return Response("event id %s not associated with BadgeTemplate %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(BadgeTemplateSerializer(badge).data)

    def create(self, request, event_pk=None):
        try:
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BadgeTemplateSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_BADGE_TEMPLATE)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            badge = BadgeTemplate.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        parents = badge.get_parent_entities()
        if parents:
            return Response("Operation Failed - Detach Badge - %s from  Event - %s and Retry" % (badge.name, event.name),
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        if badge in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_BADGE_TEMPLATE):
            return Response("event id %s already associated with badge %s " % (event_pk, pk),
                            status=status.HTTP_200_OK)

        event.add_subentity_obj(badge, BaseEntityComponent.SUB_ENTITY_BADGE_TEMPLATE)
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            badge = BadgeTemplate.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if badge not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_BADGE_TEMPLATE):
            return Response("event id %s not associated with Badge %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        event.remove_sub_entity_obj(badge, BaseEntityComponent.SUB_ENTITY_BADGE_TEMPLATE)
        return Response(status=status.HTTP_200_OK)


class CampaignMediaViewSet(viewsets.ModelViewSet):
    queryset = MediaEntities.objects.all()
    serializer_class = MediaEntitiesSerializer

    def list(self, request, campaigns_pk=None):
        campaign = Campaign.objects.get(id=campaigns_pk)
        med = campaign.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_MEDIA)
        return Response(MediaEntitiesSerializer(med, many=True).data)

    def retrieve(self, request, pk=None, campaigns_pk=None):
        try:
            med = MediaEntities.objects.get(id=pk)
            campaign = Campaign.objects.get(id=campaigns_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if med not in campaign.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_MEDIA):
            return Response("campaign id %s not associated with Media %s " % (campaigns_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(SponsorSerializer(med).data)

    def create(self, request, campaigns_pk=None):
        try:
            campaign = Campaign.objects.get(id=campaigns_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = MediaEntitiesSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            campaign.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_MEDIA)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, campaigns_pk=None, pk=None):
        try:
            campaign = Campaign.objects.get(id=campaigns_pk)
            med = MediaEntities.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if med in campaign.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_MEDIA):
            return Response("campaign %s already  associated with Media %s " % (campaigns_pk, pk),
                            status=status.HTTP_200_OK)

        campaign.add_subentity_obj(med, BaseEntityComponent.SUB_ENTITY_MEDIA)
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, campaigns_pk=None, pk=None):
        try:
            campaign = Campaign.objects.get(id=campaigns_pk)
            med = MediaEntities.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if med not in campaign.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_MEDIA):
            return Response("campaign id %s not associated with Media %s " % (campaigns_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        campaign.remove_sub_entity_obj(med, BaseEntityComponent.SUB_ENTITY_MEDIA)

        return Response(status=status.HTTP_200_OK)


class FileUploader(views.APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, filename, format=None):
        file_obj = request.data['file']
        type = request.data['data_type']
        user = request.user
        result = create_entities(file_obj, type, user)
        returnmesg = "All records uploaded successfully" if not result[1] \
            else "%s Succeeded, Check Lines %s that Failed" % (str(result[0]), result[1])
        return Response(returnmesg, status=201)



