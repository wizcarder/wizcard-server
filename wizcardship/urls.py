__author__ = 'aammundi'

from django.conf.urls import url, include
from wizcardship.views import WizcardViewSet
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'wizcard', WizcardViewSet, base_name='wizcard')

urlpatterns = [
    url(r'^', include(router.urls)),

]
