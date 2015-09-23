==========================================
Cached Instances for Django REST Framework
==========================================

.. image:: http://img.shields.io/travis/jwhitlock/drf-cached-instances/master.svg
    :alt: The status of Travis continuous integration tests
    :target: https://travis-ci.org/jwhitlock/drf-cached-instances

.. image:: https://img.shields.io/coveralls/jwhitlock/drf-cached-instances/master.svg
    :target: https://coveralls.io/r/jwhitlock/drf-cached-instances
    :alt: The code coverage

.. image:: https://img.shields.io/pypi/v/drf-cached-instances.svg
    :alt: The PyPI package
    :target: https://pypi.python.org/pypi/drf-cached-instances

.. image:: https://img.shields.io/pypi/dm/drf-cached-instances.svg
    :alt: PyPI download statistics
    :target: https://pypi.python.org/pypi/drf-cached-instances

.. image:: https://www.herokucdn.com/deploy/button.png
    :alt: Deploy to Heroku
    :target: https://heroku.com/deploy?template=https://github.com/jwhitlock/drf-cached-instances

.. Omit badges from docs

Speed up `Django REST Framework`_ (DRF) reads by storing instance data in cache.

This code was split from browsercompat_.  You may be interested in
viewing the browsercompat source code for a full example implementation.

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
This code is used for the browsercompat_ project, which is in development
as of September 2015.  The code may change in response to the needs of the
browsercompat project.  It is expected to stabilize by early 2016.  And,
like all open source projects, more documentation is needed.

.. _`Django REST Framework`: http://www.django-rest-framework.org
.. _`browsercompat`: https://github.com/mdn/browsercompat
.. _`Mozilla Public License Version 2.0`: https://www.mozilla.org/MPL/2.0/
