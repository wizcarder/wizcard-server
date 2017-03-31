__author__ = 'aammundi'

from django.conf.urls import url, include, patterns
from wizcardship.views import WizcardViewSet
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'wizcard', WizcardViewSet, base_name='wizcard')

urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),

)


# event_list = EventViewSet.as_view(
#     {
#         'get': 'list',
#         'post': 'create'
#     }
# )
# event_detail = EventViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })
#
# media_list = MediaObjectsViewSet.as_view(
#     {
#         'get': 'list',
#         'post': 'create'
#     }
# )
#
# media_detail = MediaObjectsViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })
#
#
# urlpatterns = [
#     url(r'^', include(router.urls)),
#     url(r'^events/$', event_list, name='event-list'),
#     url(r'^events/(?P<event_pk>[0-9]+)/$', event_detail, name='event-detail'),
#     url(r'^events/(?P<event_pk>[0-9]+)/media/$', media_list, name='media-list'),
#     url(r'^events/(?P<event_pk>[0-9]+)/media/(?P<media_pk>[0-9]+)/$', media_detail, {'cls': Event}, name='media-detail'),
#
# ]
