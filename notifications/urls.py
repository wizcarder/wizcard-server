# -*- coding: utf-8 -*-

from django.conf.urls import *


from django.conf.urls import url, include, patterns
from rest_framework.routers import SimpleRouter
from notifications.views import NotificationViewSet

notification_router = SimpleRouter()
notification_router.register(r'notifications', NotificationViewSet, base_name='notifications')

urlpatterns = patterns(
    '',
    url(r'^', include(notification_router.urls)),
)