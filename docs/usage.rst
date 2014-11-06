=====
Usage
=====

drf-cached-instances is designed to work with `Django REST Framework`_ (DRF)
2.x, using a cache for read-only operations such as getting an instance or list
of instances.  You may also want Celery_ for asynchronously updating the
cache.

There are a few steps needed to integrate drf-cached-instances into your
project.  See the sample app sample_poll_app for a small example, or
`web-platform-compat`_ for a fuller example.

Create an app-specific cache strategy
-------------------------------------
drf-cached-instances requires that you specify how a model is cached, by
adding methods to the Cache class.  Each model requires three functions:

1. A serializer, which turns a Django instance into a JSON-serializable
   dictionary,
2. A loader, which loads a Django instance and related objects
   from the database, and
3. An invalidator, which specifies which instance caches are possibly invalid
   when an instance is updated.

The naming convention for these functions are ``{model}_{version}_{function}``.
For example, the serializer for the User model for the 'v1' API would be
``user_v1_serializer``.  API/cache versioning is option, and the default
version name is 'default'.

Here's an example of a customized Cache::

    from django.contrib.auth.models import User
    from drf_cached_instances.cache import BaseCache

    class MyCache(BaseCache):

        """Cache for my application."""

        def user_default_serializer(self, obj):
            """Convert a User to a cached instance representation."""
            if not obj:
                return None
            self.user_default_add_related_pks(obj)
            return dict((
                ('id', obj.id),
                ('username', obj.username),
                self.field_to_json('DateTime', 'date_joined', obj.date_joined),
            ))

        def user_default_loader(self, pk):
            """Load a User from the database."""
            try:
                obj = User.objects.get(pk=pk)
            except User.DoesNotExist:
                return None
            else:
                self.user_default_add_related_pks(obj)
                return obj

        def user_default_add_related_pks(self, obj):
            """Add related primary keys to a User instance."""
            if not hasattr(obj, '_votes_pks'):
                obj._votes_pks = list(obj.votes.values_list('pk', flat=True))

        def user_default_invalidator(self, obj):
            """Invalidate cached items when the User changes."""
            return []

Use the cache in views
----------------------

If you are using viewsets, add the `CachedViewMixin` to your viewset
declarations::

    from django.contrib.auth.models import User
    from drf_cached_instances.mixins import CachedViewMixin
    from rest_framework.viewsets import ModelViewSet
    from rest_framework.serializers import DateField, ModelSerializer

    class UserSerializer(ModelSerializer):

        """DRF serializer for Users."""

        created = DateField(source='date_joined', read_only=True)

        class Meta:
            model = User
            fields = ('id', 'username', 'created')

    class UserViewSet(CachedViewMixin, ModelViewSet):

        """API endpoint that allows users to be viewed or edited."""

        queryset = User.objects.all()
        serializer_class = UserSerializer


Add signal hooks to update the cache
------------------------------------

When an instance is updated, the cache is invalid and needs to be updated.
This can be done by adding signal hooks for model modifications in models.py::

    from django.contrib.auth.models import User
    from django.db.models.signals import post_delete, post_save, m2m_changed
    from django.dispatch import receiver
    from .cache import MyCache

    def update_cache_for_instance(model_name, instance_pk, instance):
        cache = MyCache()
        version = cache.default_version
        to_update = cache.update_instance(
            model_name, instance_pk, instance, version)
        for related_name, related_pk, related_version in to_update:
            update_cache_for_instance(
                related_name, related_pk, version=related_version)

    @receiver(post_delete, sender=User, dispatch_uid='post_delete_update_cache')
    def post_delete_user_update_cache(sender, instance, **kwargs):
        update_cache_for_instance('User', instance.pk, instance)

    @receiver(post_save, sender=User, dispatch_uid='post_save_update_cache')
    def post_save_user_update_cache(sender, instance, created, raw, **kwargs):
        if raw:
            return
        update_cache_for_instance('User', instance.pk, instance)

This will follow the invalidation logic in the Cache class, to ensure that the
cache is consistant across related instances.

.. _`Django REST Framework`: http://www.django-rest-framework.org
.. _Celery: http://www.celeryproject.org
.. _`web-platform-compat`: https://github.com/mozilla/web-platform-compat
