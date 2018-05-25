from rest_framework.response import Response
from base_entity.models import BaseEntityComponent, BaseEntity, UserEntity
from entity.models import Event, Campaign, VirtualTable,\
    Speaker, Sponsor, ExhibitorInvitee, AttendeeInvitee, Agenda, AgendaItem, CoOwners
from polls.models import Poll
from entity.serializers import EventSerializer, EventSerializerL0, VanillaCampaignSerializer, CampaignSerializer, \
    TableSerializer, AttendeeInviteeSerializer, ExhibitorInviteeSerializer, SponsorSerializer, \
    SpeakerSerializer, AgendaSerializer, AgendaItemSerializer, PollSerializer, CoOwnersSerializer
from base.mixins import InviteStateMixin
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
from scan.models import ScannedEntity, BadgeTemplate
from scan.serializers import BadgeTemplateSerializer, ScannedEntitySerializer
from wizserver import verbs
from rest_framework.parsers import FileUploadParser, MultiPartParser, JSONParser
from entity.tasks import create_entities
from time import strftime
from wsgiref.util import FileWrapper
from django.utils import timezone
from django.http import HttpResponse
from wizcardship.models import Wizcard
from userprofile.models import WebExhibitorUser
from notifications.serializers import notify
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import pdb
import codecs


# Create your views here.

# Exhibitor Viewsets

class ExhibitorEventViewSet(BaseEntityViewSet):
    serializer_class = EventSerializerL0

    def get_serializer_class(self):
        return EventSerializerL0

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.users_entities(
            user,
            user_filter={'state': UserEntity.JOIN},
            entity_filter={
                'entity_state': [BaseEntityComponent.ENTITY_STATE_PUBLISHED, BaseEntityComponent.ENTITY_STATE_CREATED]
            }
        )
        return queryset


class CoOwnerViewSet(BaseEntityComponentViewSet):
    queryset = CoOwners.objects.all()
    serializer_class = CoOwnersSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = CoOwners.objects.owners_entities(user)
        return queryset


class CampaignViewSet(BaseEntityViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Campaign.objects.owners_entities(user)
        return queryset


class CampaignMediaViewSet(viewsets.ModelViewSet):
    queryset = MediaEntities.objects.all()
    serializer_class = MediaEntitiesSerializer

    def list(self, request, **kwargs):
        campaign = Campaign.objects.get(id=kwargs.get('campaigns_pk'))
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

    def create(self, request, **kwargs):
        try:
            campaign = Campaign.objects.get(id=kwargs.get('campaigns_pk'))
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

        campaign.remove_sub_entity_obj(med, BaseEntityComponent.SUB_ENTITY_MEDIA, send_notif=True)

        return Response(status=status.HTTP_200_OK)


# Organizer Viewsets
class EventViewSet(BaseEntityViewSet):
    serializer_class = EventSerializer

    def get_serializer_class(self):
        return EventSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.owners_entities(user)
        return queryset

    def perform_destroy(self, instance):
        instance.delete()
        return Response(status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def invite_exhibitor(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)

        # this is the id of the vanilla Campaign object created by Organizer, which is being
        # invited to form a sponsored campaign
        exhibitor_id = request.data['id']
        exhibitor = get_object_or_404(Campaign, pk=exhibitor_id)

        # Portal UI to also have a field for email when sending invite. Trying to get this automatically
        # will rarely work in practise since it'll almost never be the same as the Exhibitor (org) email
        exhibitor_email = request.data['email']

        try:
            existing_exhibitor_user = WebExhibitorUser.objects.get(profile__user__email=exhibitor_email)
            state = ExhibitorInvitee.ACCEPTED
        except ObjectDoesNotExist:
            existing_exhibitor_user = None
            state = ExhibitorInvitee.INVITED

        # create an exhibitor_invitee object which will serve as future user construct and/or org dashboard
        # display purposes.
        # Link event for this exhibitor and check for those emails.event when the exhibitor comes in, treating
        # the exhibitor email as the handle within ExhibitorInvitee. Essentially, Exhibitor/AttendeeInvitee
        # becomes the future user construct This also serves as the glue between
        # event<->exhibitor(vanilla campaign object)<->sponsored campaign
        exi_inv, created = ExhibitorInvitee.objects.get_or_create(
            entity_type=BaseEntityComponent.EXHIBITOR_INVITEE,
            exhibitor=exhibitor,
            email=exhibitor_email,
            event=event,
            defaults={
                'invite_state': state
            }
        )

        if not created:
            return Response("Exhibitor has already been invited", status=status.HTTP_200_OK)
        else:
            notify.send(
                request.user,
                recipient=exi_inv,
                notif_tuple=verbs.WIZCARD_INVITE_EXHIBITOR,
                target=event,
                action_object=event,
                do_push=False,
                force_sync=False
            )

        if existing_exhibitor_user:
            # join this guy to the Event. We need to be aware now that Event joinees are not only wizcard users
            # and need to handle that in other queries across the code-base
            event.user_attach(existing_exhibitor_user.profile.user, state=UserEntity.JOIN, do_notify=False)

        return Response(ExhibitorInviteeSerializer(exi_inv).data)

    # @detail_route(methods=['post'])
    # def invite_attendees(self, request, pk=None):
    #     inst = get_object_or_404(Event, pk=pk)
    #     attendee_invitees = request.data['ids']
    #
    #     existing_users, existing_attendees = AttendeeInvitee.objects.check_existing_users_attendees(
    #         attendee_invitees
    #     )
    #     [inst.user_attach(u, state=UserEntity.JOIN) for u in existing_users]
    #
    #     for e in existing_attendees:
    #         e.state = AttendeeInvitee.ACCEPTED
    #         e.save()
    #
    #     new_attendees = [x for x in attendee_invitees if x not in existing_attendees.values_list('id', flat=True)]
    #
    #     # relate these with Event
    #     invited_attendees = inst.add_subentities(
    #         new_attendees,
    #         BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE
    #     )
    #     for i in invited_attendees:
    #         i.state = AttendeeInvitee.INVITED
    #         i.save()
    #
    #     result_list = list(chain(existing_attendees, invited_attendees))
    #     return Response(AttendeeInviteeSerializer(result_list, many=True).data)

    @detail_route(methods=['put'])
    def publish_event(self, request, pk=None):
        inst = get_object_or_404(Event, pk=pk)
        inst.set_entity_state(BaseEntityComponent.ENTITY_STATE_PUBLISHED)
        return Response("event id %s published" % pk, status=status.HTTP_200_OK)


class ExhibitorViewSet(BaseEntityViewSet):
    serializer_class = VanillaCampaignSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Campaign.objects.owners_entities(user)
        return queryset

    @list_route()
    def download_exhibitors(self, request, pk=None):
        queryset = self.get_queryset()
        fname = timezone.now().strftime("/tmp/%Y%b%d%H%m%s.tsv")
        header = "#id\tname\tdescription\taddress\tphone\twebsite\ttags\tvenue\temail\n"

        f = open(fname, "w")
        f.write(header)
        for q in queryset:
            record = '\t'.join([q.name, q.description, q.address, q.phone, q.website, "", "", q.email])
            record = record + "\n"
            f.write(record)

        f.close()
        f = open(fname, "rb")

        response = HttpResponse(f, content_type='text/tab-separated-values')
        response['Content-Disposition'] = 'attachment; filename="exhibitors.tsv"'
        return response


class TableViewSet(BaseEntityViewSet):
    serializer_class = TableSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = VirtualTable.objects.owners_entities(user)
        return queryset


class SpeakerViewSet(BaseEntityComponentViewSet):

    def get_queryset(self):
        user = self.request.user
        queryset = Speaker.objects.owners_entities(user)
        return queryset

    def get_serializer_class(self):
        return SpeakerSerializer


class SponsorViewSet(BaseEntityViewSet):

    def get_queryset(self):
        user = self.request.user
        queryset = Sponsor.objects.owners_entities(user)
        return queryset

    def get_serializer_class(self):
        return SponsorSerializer

#
# class ExhibitorInviteeViewSet(BaseEntityComponentViewSet):
#     queryset = ExhibitorInvitee.objects.all()
#     serializer_class = ExhibitorInviteeSerializer
#
#     def get_queryset(self):
#         user = self.request.user
#         queryset = ExhibitorInvitee.objects.owners_entities(user)
#         return queryset


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

    def list(self, request, **kwargs):
        agn = Agenda.objects.get(id=kwargs.get('agenda_pk'))
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

    def create(self, request, **kwargs):
        try:
            agn = Agenda.objects.get(id=kwargs.get('agenda_pk'))
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

        agi.delete(type=BaseEntityComponent.ENTITY_STATE_DESTROY)

        return Response(status=status.HTTP_200_OK)


class AttendeeViewSet(BaseEntityComponentViewSet):
    queryset = AttendeeInvitee.objects.all()
    serializer_class = AttendeeInviteeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = AttendeeInvitee.objects.owners_entities(user)
        return queryset


"""
All the nested end-points for linking entity to sub-entity
"""


# Exhibitor Viewsets
class EventCampaignViewSet(viewsets.ModelViewSet):
    # queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Campaign.objects.owners_entities(user)
        return queryset

    def list(self, request, **kwargs):
        event = Event.objects.get(id=kwargs.get('event_pk'))
        evt_cpgs = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CAMPAIGN)
        my_cpgs = self.get_queryset()

        cpgs = set(set(evt_cpgs) & set(my_cpgs))
        return Response(
            CampaignSerializer(
                cpgs,
                many=True,
                context={
                    'parent': event
                }
            ).data
        )

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            cpg = Campaign.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if cpg not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CAMPAIGN):
            return Response("event id %s not associated with Campaign %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(
            CampaignSerializer(
                cpg,
                context={
                    'parent': event
                }
            ).data
        )

    def create(self, request, **kwargs):
        try:
            event = Event.objects.get(id=kwargs.get('event_pk'))
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        context = {
            'user': request.user,
            'parent': event
        }

        serializer = CampaignSerializer(data=request.data, context=context)

        if serializer.is_valid():
            inst = serializer.save()

            # link the exhibitor to campaign.

            # 1. find the Invite for this Event sent to request.user.email
            invite_obj = event.get_event_invite(request.user.email)
            if not invite_obj:
                return Response(
                    "You don't have access to create campaigns for this Event",
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # 2. Get the referenced exhibitor
            exhibitor = invite_obj.exhibitor

            # 3. relate this campaign to exhibitor. This doesn't trigger notif since campaign (=inst)
            # only sends notif if parent (=exhibitor) is an Event type. So we'll trigger manually
            exhibitor.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_CAMPAIGN)

            # have to trigger notif for exhibitor so app can create link exhibitor->inst
            if event.is_active():
                notify.send(
                    exhibitor.get_creator(),
                    # recipient is dummy
                    recipient=exhibitor.get_creator(),
                    notif_tuple=verbs.WIZCARD_ENTITY_UPDATE,
                    target=event,
                    action_object=exhibitor,
                    notif_operation=verbs.NOTIF_OPERATION_CREATE
                )

            # link campaign to event
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

        context = {
            'user': request.user,
            'parent': event
        }

        # link the exhibitor to campaign.

        # 1. find the Invite for this Event sent to request.user.email
        invite_obj = event.get_event_invite(request.user.email)
        if not invite_obj:
            return Response(
                "You don't have access to create campaigns for this Event",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 2. Get the referenced exhibitor
        exhibitor = invite_obj.exhibitor

        # 3. relate this campaign to exhibitor. This doesn't trigger notif since campaign (=inst)
        # only sends notif if parent (=exhibitor) is an Event type. So we'll trigger manually
        exhibitor.add_subentity_obj(cpg, BaseEntityComponent.SUB_ENTITY_CAMPAIGN)

        # have to trigger notif for exhibitor so app can create link exhibitor->inst
        if event.is_active():
            notify.send(
                exhibitor.get_creator(),
                # recipient is dummy
                recipient=exhibitor.get_creator(),
                notif_tuple=verbs.WIZCARD_ENTITY_UPDATE,
                target=event,
                action_object=exhibitor,
                notif_operation=verbs.NOTIF_OPERATION_CREATE
            )

        #TODO : AR Ideally we should have got the previous value of join_fields and used it here.
        join_fields = request.data.pop('join_fields') if 'join_fields' in request.data else {}
        taganomy = request.data.get('taganomy', {})
        if taganomy:
            serializer = CampaignSerializer(cpg, data=request.data, context=context, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        event.add_subentity_obj(cpg, BaseEntityComponent.SUB_ENTITY_CAMPAIGN, join_fields=join_fields)
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

        return Response(status=status.HTTP_200_OK)


# Organizer Viewsets

class EventExhibitorViewSet(viewsets.ModelViewSet):
    serializer_class = VanillaCampaignSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Campaign.objects.owners_entities(user)
        return queryset

    def list(self, request, **kwargs):
        event = Event.objects.get(id=kwargs.get('event_pk'))
        cpg = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CAMPAIGN)
        return Response(
            VanillaCampaignSerializer(
                cpg,
                many=True,
                context={
                    'parent': event
                }
            ).data
        )

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            cpg = Campaign.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if cpg not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CAMPAIGN):
            return Response("event id %s not associated with Campaign %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(
            VanillaCampaignSerializer(
                cpg,
                context={
                    'parent': event
                }
            ).data
        )

    def create(self, request, **kwargs):
        try:
            event = Event.objects.get(id=kwargs.get('event_pk'))
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        join_fields = request.data.pop('join_fields', {})

        context = {
            'user': request.user,
            'parent': event
        }

        serializer = VanillaCampaignSerializer(data=request.data, context=context)

        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_CAMPAIGN, join_fields=join_fields)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            cpg = Campaign.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        context = {
            'user': request.user,
            'parent': event
        }

        join_fields = request.data.pop('join_fields') if 'join_fields' in request.data else {}

        tags = request.data.pop('tags') if 'tags' in request.data else {}

        # This seems like a less restrictive approach to tags than going via taganomy, this will faciliate the organizer to add
        # tags to the exhibitor and create a tag cloud implicitly.

        if tags:
            taganomy = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CATEGORY)
            if taganomy:
                taganomy_inst = taganomy[0]
                taganomy_inst.tags.add(*tags)
                taganomy_inst.register_object(cpg)
            else:
                ser = TaganomySerializer(
                    data={"name": event.name + "_Tags", "tags": tags},
                    context={'user': request.user}
                )
                if ser.is_valid():
                    taganomy_inst = ser.save()
                    event.add_subentity_obj(taganomy_inst, BaseEntityComponent.SUB_ENTITY_CATEGORY)
                    taganomy_inst.register_object(cpg)
                else:
                    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = VanillaCampaignSerializer(cpg, data=request.data, context=context, partial=True)
        if serializer.is_valid():
            inst = serializer.save()
            if tags:
                inst.tags.add(*tags)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # serializer above will send notif. Don't send notif for this one
        event.add_subentity_obj(
            cpg,
            BaseEntityComponent.SUB_ENTITY_CAMPAIGN,
            join_fields=join_fields,
            send_notif=False
        )
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

        return Response(status=status.HTTP_200_OK)

    @list_route()
    def download_exhibitors(self, request, **kwargs):
        try:
            event = Event.objects.get(id=kwargs.get('event_pk'))
            queryset = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CAMPAIGN)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        fname = timezone.now().strftime("/tmp/%Y%b%d%H%m%s.tsv")
        header = "#name\tdescription\taddress\tphone\twebsite\ttags\tvenue\temail\n"

        f = open(fname, "w")
        f.write(header)

        for q in queryset:
            join_row = event.get_join_table_row(q)
            join_field = join_row.join_fields
            venue = join_field['venue'] if 'venue' in join_field else ""

            tags = ",".join(list(q.tags.names()))
            record = '\t'.join([q.name, q.description, q.address, q.phone, q.website, tags, venue, q.email])
            record += "\n"
            f.write(record)

        f.close()
        f = open(fname, "rb")

        response = HttpResponse(f, content_type='text/tab-separated-values')
        response['Content-Disposition'] = 'attachment; filename="exhibitors.tsv"'
        return response


class EventSpeakerViewSet(viewsets.ModelViewSet):
    serializer_class = SpeakerSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Speaker.objects.owners_entities(user)
        return queryset

    def list(self, request, **kwargs):
        event = Event.objects.get(id=kwargs.get('event_pk'))
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

    def create(self, request, **kwargs):
        try:
            event = Event.objects.get(id=kwargs.get('event_pk'))
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
    serializer_class = SpeakerSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Sponsor.objects.owners_entities(user)
        return queryset

    def list(self, request, **kwargs):
        event = Event.objects.get(id=kwargs.get('event_pk'))
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

    def create(self, request, **kwargs):
        try:
            event = Event.objects.get(id=kwargs.get('event_pk'))
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

    def list(self, request, **kwargs):
        event = Event.objects.get(id=kwargs.get('event_pk'))
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

    def create(self, request, **kwargs):
        try:
            event = Event.objects.get(id=kwargs.get('event_pk'))
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

        event.remove_sub_entity_obj(med, BaseEntityComponent.SUB_ENTITY_MEDIA, send_notif=True)

        return Response(status=status.HTTP_200_OK)


class EventAttendeeViewSet(viewsets.ModelViewSet):
    serializer_class = AttendeeInviteeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = AttendeeInvitee.objects.owners_entities(user)
        return queryset

    def list(self, request, **kwargs):
        event = Event.objects.get(id=kwargs.get('event_pk'))
        ati = event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE)
        return Response(AttendeeInviteeSerializer(ati, context={'parent': event}, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            ati = AttendeeInvitee.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if ati not in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE):
            return Response("event id %s not associated with invitee %s " % (event_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(AttendeeInviteeSerializer(ati, context={'parent': event}).data)

    def create(self, request, **kwargs):
        try:
            event = Event.objects.get(id=kwargs.get('event_pk'))
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if event.is_expired():
            return Response("Expired events cannot be updated",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        elif not event.is_active():
            return Response("Please publish Event before inviting attendees",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        serializer = AttendeeInviteeSerializer(data=request.data, context={'user': request.user, 'parent': event})
        if serializer.is_valid():
            inst = serializer.save()
            join_fields = {'invite_state': InviteStateMixin.INVITED}

            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE, join_fields=join_fields)

            # hook-up the app side flow if app user for this attendee exists

            # 1: Check if any app_users exists. Ideally should only be one. But who knows...deal with
            # all of the matches.
            # note to self: If multiple app_users show up (hopefully unlikely) as matches for an attendeeinvitee,
            # then it should/must also be the case that each of those app-users should result in this invitee with
            # the converse search.
            exists, app_users = inst.check_existing_app_users()

            # attach each of them to the event.
            if exists:
                for au in app_users:
                    u = au.profile.user
                    event.user_attach(u, UserEntity.JOIN, do_notify=True)

                    # push notif,
                    # Send an implicit event join notif
                    notify.send(
                        event.get_creator(),
                        recipient=u,
                        target=event,
                        notif_tuple=verbs.WIZCARD_ENTITY_IMPLICIT_ATTACH,
                        action_object=u,
                        do_push=False,
                    )

                    # in-app notif
                    notify.send(
                        event.get_creator(),
                        recipient=u,
                        notif_tuple=verbs.WIZCARD_INFO,
                        target=event,
                        action_object=u,
                        do_push=True,
                        notification_text=verbs.INFO_NOTIFICATION_TEXT[verbs.EVENT_ACCESS_GRANTED],
                        force_sync=True
                    )
                    # send email
                    notify.send(
                        event.get_creator(),
                        recipient=au,
                        notif_tuple=verbs.WIZCARD_INVITE_ATTENDEE,
                        target=event,
                        action_object=event,
                        do_push=False,
                        force_sync=False
                    )
            else:
               # send email
               notify.send(
                   event.get_creator(),
                   recipient=inst,
                   notif_tuple=verbs.WIZCARD_INVITE_ATTENDEE,
                   target=event,
                   action_object=event,
                   do_push=False,
                   force_sync=False
               )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            ati = AttendeeInvitee.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if event.is_expired():
            return Response("Expired events cannot be updated",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        elif not event.is_active():
            return Response("Please publish Event before inviting attendees",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        join_row = event.get_join_table_row(ati)
        if join_row:
            # this was an app user who requested access. Now organizer is granting access.
            # set state=APP_ACCEPTED so that going forward we're able to distinguish between
            # wizcard's contribution to organizer attendee list
            join_fields = join_row.join_fields
            assert (join_fields['invite_state'] == InviteStateMixin.REQUESTED), "Invalid Join row state"
            join_fields.update(invite_state=InviteStateMixin.APP_ACCEPTED)
        else:
            join_fields = {'invite_state': InviteStateMixin.INVITED}
            event.add_subentity_obj(ati, BaseEntityComponent.SUB_ENTITY_ATTENDEE_INVITEE, join_fields=join_fields)

        # hook-up the app side flow if app user for this attendee exists

        # 1: Check if any app_users exists. Ideally should only be one. But who knows...deal with
        # all of the matches.
        # note to self: If multiple app_users show up (hopefully unlikely) as matches for an attendeeinvitee,
        # then it should/must also be the case that each of those app-users should result in this invitee with
        # the converse search.
        exists, app_users = ati.check_existing_app_users()

        # attach each of them to the event.
        if exists:
            for au in app_users:
                u = au.profile.user
                event.user_attach(u, UserEntity.JOIN, do_notify=True)

                # Send an implicit event join notif
                notify.send(
                    event.get_creator(),
                    recipient=u,
                    notif_tuple=verbs.WIZCARD_ENTITY_IMPLICIT_ATTACH,
                    target=event,
                    action_object=u,
                    do_push=False,
                )
                # in-app notif
                notify.send(
                    event.get_creator(),
                    recipient=au,
                    notif_tuple=verbs.WIZCARD_INFO,
                    target=event,
                    action_object=u,
                    do_push=True,
                    notification_text=verbs.INFO_NOTIFICATION_TEXT[verbs.EVENT_ACCESS_GRANTED],
                    force_sync=True
                )

            # send email
        else:
            # send email
            pass

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

        # AA: TODO: We probably need to eject the user out of the event as well ?

        return Response(status=status.HTTP_200_OK)


# class EventExhibitorInviteeViewSet(viewsets.ModelViewSet):
#     queryset = ExhibitorInvitee.objects.all()
#     serializer_class = ExhibitorInviteeSerializer
#
#     def list(self, request, **kwargs):
#         event = Event.objects.get(id=kwargs.get('event_pk'))
#         exi = event.exhibitor_invitees.all()
#         return Response(ExhibitorInviteeSerializer(exi, many=True).data)
#
#     def retrieve(self, request, pk=None, event_pk=None):
#         try:
#             exi = ExhibitorInvitee.objects.get(id=pk)
#             event = Event.objects.get(id=event_pk)
#         except ObjectDoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#
#         if exi.event != event:
#             return Response("event id %s not associated with invitee %s " % (event_pk, pk),
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         return Response(ExhibitorInviteeSerializer(exi).data)
#
#     def create(self, request, **kwargs):
#         try:
#             event = Event.objects.get(id=kwargs.get('event_pk'))
#         except ObjectDoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#
#         request.data.update(event=event)
#         serializer = ExhibitorInviteeSerializer(data=request.data, context={'user': request.user})
#         if serializer.is_valid():
#             inst = serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def destroy(self, request, event_pk=None, pk=None):
#         try:
#             event = Event.objects.get(id=event_pk)
#             exi = ExhibitorInvitee.objects.get(id=pk)
#         except ObjectDoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#
#         if exi.event != event:
#             return Response("event id %s not associated with invitee %s " % (event_pk, pk),
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         exi.delete()
#
#         return Response(status=status.HTTP_200_OK)


class EventCoOwnerViewSet(viewsets.ModelViewSet):
    serializer_class = CoOwnersSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = CoOwners.objects.owners_entities(user)
        return queryset

    def list(self, request, **kwargs):
        event = Event.objects.get(id=kwargs.get('event_pk'))
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

    def create(self, request, **kwargs):
        try:
            event = Event.objects.get(id=kwargs.get('event_pk'))
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
    serializer_class = AgendaSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Agenda.objects.owners_entities(user)
        return queryset

    def list(self, request, **kwargs):
        event = Event.objects.get(id=kwargs.get('event_pk'))
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

    def create(self, request, **kwargs):
        try:
            event = Event.objects.get(id=kwargs.get('event_pk'))
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
    serializer_class = PollSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Poll.objects.owners_entities(user)
        return queryset

    def list(self, request, **kwargs):
        event = Event.objects.get(id=kwargs.get('event_pk'))
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

    def create(self, request, **kwargs):
        try:
            event = Event.objects.get(id=kwargs.get('event_pk'))
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PollSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_POLL)
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

        return Response(status=status.HTTP_200_OK)


class EventNotificationViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = AsyncNotification.objects.all()
    serializer_class = AsyncNotificationSerializer

    def list(self, request, **kwargs):
        event = Event.objects.get(id=kwargs.get('event_pk'))
        ntf = AsyncNotification.objects.event_notifications(event)

        return Response(AsyncNotificationSerializer(ntf, many=True).data)

    def retrieve(self, request, pk=None, event_pk=None):
        try:
            ntf = AsyncNotification.objects.get(id=pk)
            event = Event.objects.get(id=event_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(AsyncNotificationSerializer(ntf).data)

    def create(self, request, **kwargs):
        try:
            event = Event.objects.get(id=kwargs.get('event_pk'))
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AsyncNotificationSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventTaganomyViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = TaganomySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Taganomy.objects.owners_entities(user)
        return queryset

    def list(self, request, **kwargs):
        event = Event.objects.get(id=kwargs.get('event_pk'))
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

    def create(self, request, **kwargs):
        try:
            event = Event.objects.get(id=kwargs.get('event_pk'))
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TaganomySerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            event.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_CATEGORY)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_pk=None, pk=None):
        try:
            event = Event.objects.get(id=event_pk)
            taganomy = Taganomy.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if taganomy in event.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_CATEGORY):
            return Response("event id %s already associated with taganomy %s " % (event_pk, pk),
                            status=status.HTTP_200_OK)

        parents = taganomy.get_parent_entities()
        if parents:
            parent = parents[0]
            return Response(
                "Operation Failed - Detach Taganomy - %s from  Event - %s and Retry" % (taganomy.name, parent.name),
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        event.add_subentity_obj(taganomy, BaseEntityComponent.SUB_ENTITY_CATEGORY)

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

        return Response(status=status.HTTP_200_OK)


class EventBadgeViewSet(viewsets.ModelViewSet):
    queryset = BadgeTemplate.objects.all()
    serializer_class = BadgeTemplateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = BadgeTemplate.objects.owners_entities(user)
        return queryset

    def list(self, request, **kwargs):
        event = Event.objects.get(id=kwargs.get('event_pk'))
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

    def create(self, request, **kwargs):
        try:
            event = Event.objects.get(id=kwargs.get('event_pk'))
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

    def list(self, request, **kwargs):
        campaign = Campaign.objects.get(id=kwargs.get('campaigns_pk'))
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

    def create(self, request, **kwargs):
        try:
            campaign = Campaign.objects.get(id=kwargs.get('campaigns_pk'))
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

        campaign.remove_sub_entity_obj(med, BaseEntityComponent.SUB_ENTITY_MEDIA, send_notif=True)

        return Response(status=status.HTTP_200_OK)


class CampaignCoOwnerViewSet(viewsets.ModelViewSet):
    serializer_class = CoOwnersSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = CoOwners.objects.owners_entities(user)
        return queryset

    def list(self, request, **kwargs):
        cmp = Campaign.objects.get(id=kwargs.get('campaigns_pk'))
        coo = cmp.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_COOWNER)
        return Response(CoOwnersSerializer(coo, many=True).data)

    def retrieve(self, request, pk=None, campaigns_pk=None):
        try:
            coo = CoOwners.objects.get(id=pk)
            cmp = Campaign.objects.get(id=campaigns_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if coo not in cmp.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_COOWNER):
            return Response("Campaign id %s not associated with co-owner %s " % (campaigns_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(CoOwnersSerializer(coo).data)

    def create(self, request, **kwargs):
        try:
            cmp = Campaign.objects.get(id=kwargs.get('campaigns_pk'))
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CoOwnersSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            inst = serializer.save()
            cmp.add_subentity_obj(inst, BaseEntityComponent.SUB_ENTITY_COOWNER)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, campaigns_pk=None, pk=None):
        try:
            cmp = Campaign.objects.get(id=campaigns_pk)
            coo = CoOwners.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if coo in cmp.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_COOWNER):
            return Response("campaign %s already  associated with CoOwner %s " % (campaigns_pk, pk),
                            status=status.HTTP_200_OK)

        cmp.add_subentity_obj(coo, BaseEntityComponent.SUB_ENTITY_COOWNER)
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, campaigns_pk=None, pk=None):
        try:
            cmp = Campaign.objects.get(id=campaigns_pk)
            coo = CoOwners.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if coo not in cmp.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_COOWNER):
            return Response("campaign id %s not associated with CoOwner %s " % (campaigns_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        cmp.remove_sub_entity_obj(coo, BaseEntityComponent.SUB_ENTITY_COOWNER)

        return Response(status=status.HTTP_200_OK)


class CampaignScansViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScannedEntitySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = ScannedEntity.objects.owners_entities(user)
        return queryset

    def list(self, request, **kwargs):
        cpg = get_object_or_404(Campaign, pk=kwargs.get('campaigns_pk'))
        scans = cpg.get_sub_entities_of_type(BaseEntityComponent.SUB_ENTITY_SCANNED_USER)

        return Response(ScannedEntitySerializer(scans, many=True).data)

    def retrieve(self, request, pk=None, campaigns_pk=None):
        try:
            scn = ScannedEntity.objects.get(id=pk)
            cpg = Campaign.objects.get(id=campaigns_pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if cpg not in scn.get_parent_entities():
            return Response("Campaign id %s not associated with Scanned User %s " % (campaigns_pk, pk),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(ScannedEntitySerializer(scn).data)


class FileUploader(views.APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, filename, format=None):
        myargs = {}
        file_obj = request.data['file']
        utf_file = codecs.EncodedFile(file_obj, "utf-8")
        owner = request.user
        myargs['type'] = request.data.get('data_type', BaseEntityComponent.CAMPAIGN)
        myargs['event'] = request.data.get('event', None)

        result = create_entities(utf_file, owner, **myargs)

        returnmesg = "All records uploaded successfully" if not result[1] \
            else "%s Succeeded, Check Lines %s that Failed" % (str(result[0]), result[1])
        return Response(returnmesg, status=201)


class FileDownloader(views.APIView):

    parser_classes = (MultiPartParser,)

    def get(self, request, format=None):

        template_dir = settings.TEMPLATES[0]['DIRS'][0]
        fname = template_dir + "/" + settings.EXHIBITOR_TEMPLATE

        f = open(fname, "rb")
        response = HttpResponse(f, content_type='text/tab-separated-values')
        response['Content-Disposition'] = 'attachment; filename="%s"' % fname
        return response





