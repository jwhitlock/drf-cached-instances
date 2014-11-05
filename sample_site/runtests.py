#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run tests for drf-cached-instances.

This is for running tests from `setup.py test`.  Most users should use
`manage.py test` instead.
"""

import os
import sys

# Setup path to Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'sample_site.settings'

# Add project folder to sys.path
full_path = os.path.abspath(__file__)
my_dir = os.path.dirname(full_path)
proj_dir = os.path.dirname(my_dir)
sys.path.insert(0, proj_dir)

try:
    from django import setup
except ImportError:
    # Django 1.6 and below does not require setup
    setup = lambda: None
else:
    assert setup

from django.test.utils import get_runner
from django.conf import settings


def runtests():
    """Find and run tests for drf-cached-instances."""
    setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True)
    failures = test_runner.run_tests([])
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
