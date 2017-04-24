__author__ = 'aammundi'

from django.conf.urls import url, include, patterns
from entity.views import BaseEntityViewSet, EventViewSet, ProductViewSet, BusinessViewSet, TableViewSet
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'events', EventViewSet, base_name='events')
router.register(r'products', ProductViewSet, base_name='products')
router.register(r'biz', BusinessViewSet, base_name='biz')
router.register(r'tables', TableViewSet)


urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)
