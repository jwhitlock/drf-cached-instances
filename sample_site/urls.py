# -*- coding: utf-8 -*-
"""URL routing patterns for drf-cached-instances."""

from django.conf.urls import include, url
from django.contrib import admin

from sample_poll_app.urls import urlpatterns as sample_urlpatterns

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include(sample_urlpatterns)),
]
