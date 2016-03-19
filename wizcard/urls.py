from django.conf.urls import patterns, include, url
import pdb

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wizcard_schema.views.home', name='home'),
    url(r'^$', include('wizserver.urls')),
    url(r'^healthstatus$', include('healthstatus.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
)
