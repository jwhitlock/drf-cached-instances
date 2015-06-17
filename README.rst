==========================================
Cached Instances for Django REST Framework
==========================================

.. image:: https://travis-ci.org/jwhitlock/drf-cached-instances.png?branch=master
    :height: 22px
    :alt: The status of Travis continuous integration tests
    :target: https://travis-ci.org/jwhitlock/drf-cached-instances

.. image:: https://coveralls.io/repos/jwhitlock/drf-cached-instances/badge.png
    :target: https://coveralls.io/r/jwhitlock/drf-cached-instances
    :height: 22px
    :alt: The code coverage

.. image:: https://badge.fury.io/py/drf-cached-instances.png
    :height: 22px
    :alt: The PyPI package
    :target: http://badge.fury.io/py/drf-cached-instances

.. image:: https://pypip.in/download/drf-cached-instances/badge.png
    :height: 22px
    :alt: PyPI download statistics
    :target: https://pypi.python.org/pypi/drf-cached-instances

.. image:: https://www.herokucdn.com/deploy/button.png
    :height: 35px
    :alt: Deploy to Heroku
    :target: https://heroku.com/deploy?template=https://github.com/jwhitlock/drf-cached-instances

.. Omit badges from docs

Speed up `Django REST Framework`_ (DRF) reads by storing instance data in cache.

This code was split from web-platform-compat_.  You may be interested in
viewing the web-platform-compat source code for a full example implementation.

* Code: https://github.com/jwhitlock/drf-cached-instances
* Free software: `Mozilla Public License Version 2.0`_
* Documentation: https://drf-cached-instances.readthedocs.org

How it works
------------
In a normal DRF view, a Django queryset is used to load an object or list of
objects.  A serializer is used to convert the objects into the "native"
representation, and then a renderer works on this native representation.  If
the serializer includes data from related models, then multiple database
queries may be required to generate a native representation.  Some database
efficiency can be gained by using ``select_related``, but a minimum of one query
is needed, which is unfortunate for an API with heavy read usage.

This project replaces the Django queryset with a cache-aware proxy class,
making it possible to serve a read request with zero database requests (to
retrieve an instance) or one request (to get the primary keys for a list view).
It is suitable for APIs with heavy read operations and lots of linking between
related instances.

When using the cache, Django objects are serialized to JSON.  Only the
attributes needed for the DRF native representation are stored in the cache.
This include the JSON representation of fields such as foreign keys, reverse
relations, and dates and times.  These serialized objects are stored by primary
key in the cache.  When an instance is found in the cache, no database reads
are needed to render the DRF representation.  If the instance is not in the
cache, it is serialized and stored, so that future reads will be faster.

The API implementor writes methods to handle JSON serialization, loading from
the database, and identifying invalid cache entries on changes.  There are a
few integration points, including a mixin for views to load data from the cache.
With only a few changes to existing code, your read views could be a lot faster.

Project status
--------------
This code is used for the web-platform-compat_ project, which is in development
as of June 2015.  The code may change in response to the needs of the
web-platform-compat project.  It is expected to stabilize by early 2016.  And,
like all open source projects, more documentation is needed.

.. _`Django REST Framework`: http://www.django-rest-framework.org
.. _`web-platform-compat`: https://github.com/mozilla/web-platform-compat
.. _`Mozilla Public License Version 2.0`: https://www.mozilla.org/MPL/2.0/
