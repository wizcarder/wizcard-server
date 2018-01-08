__author__ = 'aammundi'

from django.conf.urls import url, include, patterns
from entity.views import EventViewSet, CampaignViewSet, TableViewSet
from entity.views import SpeakerViewSet, SponsorViewSet, ExhibitorViewSet, AttendeeViewSet, \
    CoOwnersViewSet, AgendaViewSet, AgendaItemViewSet, EventAgendaViewSet, ExhibitorEventViewSet
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
events_router.register(r'agenda', EventAgendaViewSet, base_name='event-agenda')
router.register(r'campaigns', CampaignViewSet, base_name='campaigns')
router.register(r'tables', TableViewSet)
router.register(r'speakers', SpeakerViewSet, base_name='speakers')
router.register(r'sponsors', SponsorViewSet, base_name='sponsors')
router.register(r'media', MediaEntitiesViewSet, base_name='media')
router.register(r'exhibitors', ExhibitorViewSet, base_name='exhibitors')
router.register(r'attendees', AttendeeViewSet, base_name='attendees')
router.register(r'owners', CoOwnersViewSet, base_name='owners')
router.register(r'tags', TaganomyViewSet, base_name='tags')
router.register(r'agenda', AgendaViewSet, base_name='agenda')
agenda_item_router = routers.NestedSimpleRouter(router, r'agenda', lookup='agenda')
agenda_item_router.register(r'agenda_item', AgendaItemViewSet, base_name='agenda-item')



urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
    url(r'^', include(events_router.urls)),
    url(r'^', include(agenda_item_router.urls)),
)

urlpatterns += poll_urlpatterns
urlpatterns += scan_urlpatterns
urlpatterns += notification_urlpatterns
urlpatterns += taganomy_urlpatterns
