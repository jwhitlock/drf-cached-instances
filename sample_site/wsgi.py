"""
WSGI config for wpcsite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sample_site.settings")

from django.core.wsgi import get_wsgi_application  # flake8: noqa
from dj_static import Cling  # flake8: noqa
application = Cling(get_wsgi_application())
