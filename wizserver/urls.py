from django.conf.urls import patterns, url


urlpatterns = patterns(
    'wizserver.views',
    url(r'^$', 'wizrequest_handler')
)
