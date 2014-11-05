"""Django app for drf-cached-instances."""

__author__ = 'John Whitlock'
__email__ = 'john@factorialfive.com'
__version__ = '0.1.0'

"""
Store instances in cache for fast Django REST Framework reads.

There are two read operations when using viewsets in Django REST Framework
(DRF).  The 'list' view displays multiple instances of a resource.  The
'retrieve' view displays a single instance.

The standard Django REST Framework flow is:

- Load object or list of objects (in mixins and viewsets)
- Pass to serializer (serializer.__init__)
- Convert to "native" representation (serializer.data)
- Convert to output format (renderer)

This app uses this flow for read access:

- Get the object's primary key from the request (retrieve action), or load the
  list of primary keys from the database (list action).
- For each object, serialize to a JSON string that includes all the attributes
  and the PKs of related objects.  Store this in the cache, or load from cache
  if done in a previous request.
- Pass de-serialized version of objects (not Django model instances) to
  serializer.
- Convert to "native" representation as before
- Convert to output format as before

With this flow, repeated retrieve actions require no database hits, and
repeared list actions have a single hit to the (hopefully indexed) primary key
column.

There are some additional requirements:
- Resource relations use PrimaryKeyRelatedFields, not
  HyperlinkedRelatedFields.  It may be possible to use HyperlinkedRelatedFields
  with some code changes, but it isn't tested.
- Write operations use Django model instances, and invalidate the cache.  This
  may cascade and invalidate other instances.
- The instance cache needs to be shared between web workers, to see consistant
  data after invalidation.  You'll need a real caching server, not a local
  memory cache, for production.  The cached instances are stored as strings, so
  any cache backend (Memcache, Redis) should work equally well.
- Celery is used for asynchronous cache invalidation, and has many
  requirements.
- Duck-typed objects are used to emulated Django models and querysets.  They
  are not meant to completely replace the originals, or be completely
  compatible, but instead to implement the interface needed by Django REST
  Framework.  If you try to use un-emulated functionality, they will fail.
  Hopefully quickly.
"""
