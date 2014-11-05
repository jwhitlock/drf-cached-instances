# -*- coding: utf-8 -*-
"""URL routing patterns for drf-cached-instances."""

from django.conf.urls import patterns, include, url
from django.contrib import admin

from drf_cached_instances.urls import (
    urlpatterns as drf_cached_instances_urlpatterns)

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include(drf_cached_instances_urlpatterns)),
)
