from django.conf.urls import patterns, url

urlpatterns = patterns(
    'healthstatus.views',
    url(r'^$', 'healthstatus_handler'),
)
