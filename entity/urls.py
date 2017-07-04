__author__ = 'aammundi'

from django.conf.urls import url, include, patterns
from entity.views import EventViewSet, ProductViewSet, BusinessViewSet, TableViewSet, SpeakerViewSet, SponsorViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'events', EventViewSet, base_name='events')
router.register(r'products', ProductViewSet, base_name='products')
router.register(r'biz', BusinessViewSet, base_name='biz')
router.register(r'tables', TableViewSet)
router.register(r'speakers', SpeakerViewSet, base_name='speaker')
router.register(r'sponsors', SponsorViewSet, base_name='sponsors')



urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)
