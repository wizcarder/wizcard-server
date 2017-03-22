from django.conf.urls import patterns, include, url
import pdb

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from rest_framework.schemas import get_schema_view

schema_view = get_schema_view(title='Entity API')

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wizcard_schema.views.home', name='home'),
    url(r'^$', include('wizserver.urls')),
    url(r'^healthstatus$', include('healthstatus.urls')),
    url(r'^admin/django-ses/', include('django_ses.urls')),
    url(r'^events/', include('entity.urls')),
    url(r'^users/', include('userprofile.urls')),
    url('^schema/$', schema_view),



    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += (url(r'^admin/django-ses/', include('django_ses.urls')),)
