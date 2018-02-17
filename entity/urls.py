__author__ = 'aammundi'

from django.conf.urls import url, include
from entity.views import EventViewSet, CampaignViewSet, TableViewSet
from entity.views import SpeakerViewSet, SponsorViewSet, ExhibitorInviteeViewSet, AttendeeViewSet, \
    CoOwnerViewSet, AgendaViewSet, AgendaItemViewSet, ExhibitorEventViewSet
from entity.views import EventCampaignViewSet, EventSpeakerViewSet, EventSponsorViewSet, \
    EventMediaViewSet, EventAttendeeViewSet, EventExhibitorViewSet, EventCoOwnerViewSet,\
    EventAgendaViewSet, EventPollViewSet, EventTaganomyViewSet, EventNotificationViewSet, \
    EventBadgeViewSet, CampaignMediaViewSet
from media_components.views import MediaEntitiesViewSet
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers
from polls.urls import urlpatterns as poll_urlpatterns
from taganomy.views import TaganomyViewSet
from notifications.urls import urlpatterns as notification_urlpatterns
from scan.urls import urlpatterns as scan_urlpatterns
from taganomy.urls import urlpatterns as taganomy_urlpatterns

router = SimpleRouter()
router.register(r'events', EventViewSet, base_name='events')
router.register(r'exhibitor_events', ExhibitorEventViewSet, base_name='exhibitor_events')
events_router = routers.NestedSimpleRouter(router, r'events', lookup='event')
router.register(r'campaigns', CampaignViewSet, base_name='campaigns')
router.register(r'tables', TableViewSet)
router.register(r'speakers', SpeakerViewSet, base_name='speakers')
router.register(r'sponsors', SponsorViewSet, base_name='sponsors')
router.register(r'media', MediaEntitiesViewSet, base_name='media')
router.register(r'exhibitors', ExhibitorInviteeViewSet, base_name='exhibitors')
router.register(r'attendees', AttendeeViewSet, base_name='attendees')
router.register(r'owners', CoOwnerViewSet, base_name='owners')
router.register(r'taganomy', TaganomyViewSet, base_name='taganomy')
router.register(r'agenda', AgendaViewSet, base_name='agenda')
agenda_item_router = routers.NestedSimpleRouter(router, r'agenda', lookup='agenda')
agenda_item_router.register(r'agenda_item', AgendaItemViewSet, base_name='agenda-item')

# nested end-points for all applicable sub-entities
events_router.register(r'campaign', EventCampaignViewSet, base_name='event-campaign')
events_router.register(r'speaker', EventSpeakerViewSet, base_name='event-speaker')
events_router.register(r'sponsor', EventSponsorViewSet, base_name='event-sponsor')
events_router.register(r'media', EventMediaViewSet, base_name='event-media')
events_router.register(r'attendee', EventAttendeeViewSet, base_name='event-attendees')
events_router.register(r'exhibitor', EventExhibitorViewSet, base_name='event-exhibitors')
events_router.register(r'coowner', EventCoOwnerViewSet, base_name='event-coowners')
events_router.register(r'agenda', EventAgendaViewSet, base_name='event-agenda')
events_router.register(r'poll', EventPollViewSet, base_name='event-poll')
events_router.register(r'notification', EventNotificationViewSet, base_name='event-notification')
events_router.register(r'taganomy', EventTaganomyViewSet, base_name='event-tagonomy')
events_router.register(r'badge', EventBadgeViewSet, base_name='event-badge')

campaigns_router = routers.NestedSimpleRouter(router, r'campaigns', lookup='campaigns')
campaigns_router.register(r'media', CampaignMediaViewSet, base_name='campaign-media')


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(events_router.urls)),
    url(r'^', include(agenda_item_router.urls)),
    url(r'^', include(campaigns_router.urls)),
]

urlpatterns += poll_urlpatterns
urlpatterns += scan_urlpatterns
urlpatterns += notification_urlpatterns
urlpatterns += taganomy_urlpatterns
