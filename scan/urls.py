__author__ = 'aammundi'

from django.conf.urls import url, include 
from rest_framework.routers import SimpleRouter
from scan.views import ScannedEntityViewSet, BadgeTemplateViewSet

scan_router = SimpleRouter()
scan_router.register(r'scans', ScannedEntityViewSet, base_name='scans')
badge_router = SimpleRouter()
badge_router.register(r'badges', BadgeTemplateViewSet, base_name='badges')

urlpatterns = [
    url(r'^', include(scan_router.urls)),
    url(r'^', include(badge_router.urls)),
]
