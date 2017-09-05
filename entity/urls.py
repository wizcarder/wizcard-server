__author__ = 'aammundi'

from django.conf.urls import url, include, patterns
from entity.views import EventViewSet, ProductViewSet, BusinessViewSet, TableViewSet
from entity.views import  SpeakerViewSet, SponsorViewSet, ExhibitorViewSet, AttendeeViewSet, OwnersViewSet, AgendaViewSet
from media_components.views import  MediaEntitiesViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'events', EventViewSet, base_name='events')
router.register(r'products', ProductViewSet, base_name='products')
router.register(r'biz', BusinessViewSet, base_name='biz')
router.register(r'tables', TableViewSet)
router.register(r'speakers', SpeakerViewSet, base_name='speaker')
router.register(r'agenda', AgendaViewSet, base_name='agenda')
router.register(r'sponsors', SponsorViewSet, base_name='sponsors')
router.register(r'media', MediaEntitiesViewSet, base_name='media')
router.register(r'exhibitors', ExhibitorViewSet, base_name='exhibitors')
router.register(r'attendees', AttendeeViewSet, base_name='attendees')
router.register(r'owners', OwnersViewSet, base_name='owners')



urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)
