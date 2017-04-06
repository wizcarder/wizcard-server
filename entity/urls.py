__author__ = 'aammundi'

from django.conf.urls import url, include, patterns
from entity.views import BaseEntityViewSet, EventViewSet, ProductViewSet, BusinessViewSet
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'events', EventViewSet, base_name='events')
router.register(r'products', ProductViewSet, base_name='products')
router.register(r'biz', BusinessViewSet, base_name='biz')



#events_router = routers.NestedSimpleRouter(router, r'events', lookup='event')
#events_router.register(r'media', MediaObjectsViewSet, base_name='event-media')
#events_router.register(r'owners', EventOwnersViewSet, base_name='event-owners')
#events_router.register(r'subentity', EventSubEntityViewSet, base_name='event-subentity')


urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
    #url(r'^', include(events_router.urls)),
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
