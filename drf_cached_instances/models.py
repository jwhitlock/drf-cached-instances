# -*- coding: utf-8 -*-
"""Model-like classes that work with the instance cache.

These classes are look-alike replacements for django.db.model.Model and
Queryset.  The full interface is not implemented, only enough to use then
in common Django REST Framework use cases.
"""


class PkOnlyModel(object):

    """Emulate a Django model with only the primary key (pk) set.

    This is used to represent related objects.
    """

    def __init__(self, cache, model, pk):
        """Initialize a PkOnlyModel."""
        self.cache = cache
        self.model = model
        self.pk = pk


class PkOnlyQueryset(object):

    """Emulate a Django queryset with only the primary keys (pks) available.

    This is used to represent a group of related objects, which can be
    accessed by iteration (returning PkOnlyModels) or by values_list
    (returning the list of primary keys).
    """

    def __init__(self, cache, model, pks):
        """Initialize PkOnlyQueryset."""
        self.cache = cache
        self.model = model
        self.pks = pks

    def __iter__(self):
        """Return PkOnlyModels for each pk."""
        for pk in self.pks:
            yield PkOnlyModel(self.cache, self.model, pk)

    def all(self):
        """Handle asking for an unfiltered queryset."""
        return self

    def values_list(self, *args, **kwargs):
        """Return the primary keys as a list.

        The only valid call is values_list('pk', flat=True)
        """
        flat = kwargs.pop('flat', False)
        assert flat is True
        assert len(args) == 1
        assert args[0] == self.model._meta.pk.name
        return self.pks


class CachedModel(object):

    """Emulate a Django model, but with data loaded from the cache."""

    def __init__(self, model, data):
        """Initialize a CachedModel."""
        self._model = model
        self._data = data

    def __getattr__(self, name):
        """Return an attribute from the cached data."""
        if name in self._data:
            return self._data[name]
        elif name == 'pk':
            return self._data.get(self._model._meta.pk.attname)
        else:
            raise AttributeError(
                "%r object has no attribute %r" %
                (self.__class__, name))


class CachedQueryset(object):

    """Emulate a Djange queryset, but with data loaded from the cache.

    A real queryset is used to get filtered lists of primary keys, but the
    cache is used instead of the database to get the instance data.
    """

    def __init__(self, cache, queryset, primary_keys=None):
        """Initialize a CachedQueryset."""
        self.cache = cache
        assert queryset is not None
        self.queryset = queryset
        self.model = queryset.model
        self.filter_kwargs = {}
        self._primary_keys = primary_keys

    @property
    def pks(self):
        """Lazy-load the primary keys."""
        if self._primary_keys is None:
            self._primary_keys = list(
                self.queryset.values_list('pk', flat=True))
        return self._primary_keys

    def __iter__(self):
        """Return the cached data as a list."""
        model_name = self.model.__name__
        object_specs = [(model_name, pk, None) for pk in self.pks]
        instances = self.cache.get_instances(object_specs)
        for pk in self.pks:
            model_data = instances.get((model_name, pk), {})[0]
            yield CachedModel(self.model, model_data)

    def all(self):
        """Handle asking for an unfiltered queryset."""
        return self

    def none(self):
        """Handle asking for an empty queryset."""
        return CachedQueryset(self.cache, self.queryset.none(), [])

    def count(self):
        """Return a count of instances."""
        if self._primary_keys is None:
            return self.queryset.count()
        else:
            return len(self.pks)

    def filter(self, **kwargs):
        """Filter the base queryset."""
        assert not self._primary_keys
        self.queryset = self.queryset.filter(**kwargs)
        return self

    def get(self, *args, **kwargs):
        """Return the single item from the filtered queryset."""
        assert not args
        assert list(kwargs.keys()) == ['pk']
        pk = kwargs['pk']
        model_name = self.model.__name__
        object_spec = (model_name, pk, None)
        instances = self.cache.get_instances((object_spec,))
        try:
            model_data = instances[(model_name, pk)][0]
        except KeyError:
            raise self.model.DoesNotExist(
                "No match for %r with args %r, kwargs %r" %
                (self.model, args, kwargs))
        else:
            return CachedModel(self.model, model_data)

    def __getitem__(self, key):
        """Access the queryset by index or range."""
        if self._primary_keys is None:
            pks = self.queryset.values_list('pk', flat=True)[key]
        else:
            pks = self.pks[key]
        return CachedQueryset(self.cache, self.queryset, pks)
