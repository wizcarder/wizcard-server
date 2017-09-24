__author__ = 'aammundi'

from django.conf.urls import url, include, patterns
from entity.views import EventViewSet, CampaignViewSet, TableViewSet
from entity.views import SpeakerViewSet, SponsorViewSet, ExhibitorViewSet, AttendeeViewSet, CoOwnersViewSet, AgendaViewSet
from media_components.views import MediaEntitiesViewSet
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers


router = SimpleRouter()
router.register(r'events', EventViewSet, base_name='events')
events_router = routers.NestedSimpleRouter(router, r'events', lookup='event')
events_router.register(r'agenda', AgendaViewSet, base_name='event-agenda')
router.register(r'campaigns', CampaignViewSet, base_name='campaigns')
router.register(r'tables', TableViewSet)
router.register(r'speakers', SpeakerViewSet, base_name='speakers')
router.register(r'sponsors', SponsorViewSet, base_name='sponsors')
router.register(r'media', MediaEntitiesViewSet, base_name='media')
router.register(r'exhibitors', ExhibitorViewSet, base_name='exhibitors')
router.register(r'attendees', AttendeeViewSet, base_name='attendees')
router.register(r'owners', CoOwnersViewSet, base_name='owners')



urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
    url(r'^', include(events_router.urls)),
)