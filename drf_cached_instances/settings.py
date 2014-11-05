"""Settings for drf_cached_instances."""

from django.conf import settings
USE_DRF_INSTANCE_CACHE = getattr(
    settings, 'USE_DRF_INSTANCE_CACHE', True)
