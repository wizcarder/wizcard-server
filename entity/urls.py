__author__ = 'aammundi'

from django.conf.urls import url, include
from entity.views import EventViewSet, CampaignViewSet, TableViewSet, SpeakerViewSet, SponsorViewSet, \
    ExhibitorViewSet, AttendeeViewSet, CoOwnerViewSet, AgendaViewSet, AgendaItemViewSet, ExhibitorEventViewSet
from entity.views import EventExhibitorViewSet, EventCampaignViewSet, EventSpeakerViewSet, EventSponsorViewSet, \
    EventMediaViewSet, EventAttendeeViewSet, EventCoOwnerViewSet,\
    EventAgendaViewSet, EventPollViewSet, EventTaganomyViewSet, EventNotificationViewSet, \
    EventBadgeViewSet, CampaignMediaViewSet, CampaignCoOwnerViewSet
from media_components.views import MediaEntitiesViewSet
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers
from polls.urls import urlpatterns as poll_urlpatterns
from taganomy.views import TaganomyViewSet
from notifications.urls import urlpatterns as notification_urlpatterns
from scan.urls import urlpatterns as scan_urlpatterns
from taganomy.urls import urlpatterns as taganomy_urlpatterns
from entity.views import FileUploader, FileDownloader

router = SimpleRouter()

# Organizer end-points
router.register(r'events', EventViewSet, base_name='events')
router.register(r'tables', TableViewSet, base_name='tables')
router.register(r'speakers', SpeakerViewSet, base_name='speakers')
router.register(r'sponsors', SponsorViewSet, base_name='sponsors')
router.register(r'media', MediaEntitiesViewSet, base_name='media')
router.register(r'exhibitors', ExhibitorViewSet, base_name='exhibitors')
router.register(r'attendees', AttendeeViewSet, base_name='attendees')
router.register(r'taganomy', TaganomyViewSet, base_name='taganomy')
router.register(r'agenda', AgendaViewSet, base_name='agenda')
agenda_item_router = routers.NestedSimpleRouter(router, r'agenda', lookup='agenda')
agenda_item_router.register(r'agenda_item', AgendaItemViewSet, base_name='agenda-item')

# Exhibitor End-points
router.register(r'exhibitor_events', ExhibitorEventViewSet, base_name='exhibitor_events')
router.register(r'coowners', CoOwnerViewSet, base_name='owners')
router.register(r'campaigns', CampaignViewSet, base_name='campaigns')
campaigns_router = routers.NestedSimpleRouter(router, r'campaigns', lookup='campaigns')
campaigns_router.register(r'media', CampaignMediaViewSet, base_name='campaign-media')

# nested end-points for all applicable sub-entities

# organizer nested
events_router = routers.NestedSimpleRouter(router, r'events', lookup='event')
events_router.register(r'exhibitors', EventExhibitorViewSet, base_name='event-exhibitors')
events_router.register(r'speakers', EventSpeakerViewSet, base_name='event-speaker')
events_router.register(r'sponsors', EventSponsorViewSet, base_name='event-sponsor')
events_router.register(r'media', EventMediaViewSet, base_name='event-media')
events_router.register(r'attendees', EventAttendeeViewSet, base_name='event-attendees')
events_router.register(r'agenda', EventAgendaViewSet, base_name='event-agenda')
events_router.register(r'poll', EventPollViewSet, base_name='event-poll')
events_router.register(r'notification', EventNotificationViewSet, base_name='event-notification')
events_router.register(r'taganomy', EventTaganomyViewSet, base_name='event-tagonomy')
events_router.register(r'badge', EventBadgeViewSet, base_name='event-badge')


# Exhibitor Nested
events_router.register(r'campaigns', EventCampaignViewSet, base_name='event-campaigns')

campaigns_router = routers.NestedSimpleRouter(router, r'campaigns', lookup='campaigns')
campaigns_router.register(r'media', CampaignMediaViewSet, base_name='campaign-media')
campaigns_router.register(r'coowners', CampaignCoOwnerViewSet, base_name='campaign-coowner')


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(events_router.urls)),
    url(r'^', include(agenda_item_router.urls)),
    url(r'^', include(campaigns_router.urls)),
    url(r'^upload/(?P<filename>[^/]+)$', FileUploader.as_view()),
    url(r'^download$', FileDownloader.as_view())
]

urlpatterns += poll_urlpatterns
urlpatterns += scan_urlpatterns
urlpatterns += notification_urlpatterns
urlpatterns += taganomy_urlpatterns
