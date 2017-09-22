__author__ = 'aammundi'

from django.conf.urls import url, include, patterns
from entity.views import EventViewSet, CampaignViewSet, TableViewSet
from entity.views import SpeakerViewSet, SponsorViewSet, ExhibitorViewSet, AttendeeViewSet, CoOwnersViewSet, AgendaViewSet
from media_components.views import MediaEntitiesViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_extensions.routers import ExtendedSimpleRouter


router = ExtendedSimpleRouter()
router.register(r'events', EventViewSet, base_name='events').register(
    r'agenda', AgendaViewSet, base_name='agenda', parents_query_lookups=['events_related']
)
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
)