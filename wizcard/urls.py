from django.conf.urls import  include, url
import pdb

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from rest_framework.schemas import get_schema_view
from rest_framework.authtoken import views as rest_framework_views


schema_view = get_schema_view(title='Entity API')

urlpatterns = [
    # Examples:
    # url(r'^$', 'wizcard_schema.views.home', name='home'),
    url(r'^', include('wizserver.urls')),
    url(r'^healthstatus', include('healthstatus.urls')),
    url(r'^admin/django-ses/', include('django_ses.urls')),
    url(r'^entity/', include('entity.urls')),
    url(r'^wizcard/', include('wizcardship.urls')),
    url(r'^users/', include('userprofile.urls')),
    url('^schema/$', schema_view),
    url(r'^get_auth_token/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
    url(r'^admin/django-ses/', include('django_ses.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
]
