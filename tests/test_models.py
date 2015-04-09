"""Tests for drf_cached_instances/models.py."""
from django.contrib.auth.models import User
from django.test import TestCase

from drf_cached_instances.models import (
    CachedModel, CachedQueryset, PkOnlyModel, PkOnlyQueryset)

from sample_poll_app.cache import SampleCache


class TestCachedModel(TestCase):

    """Tests for CachedModel."""

    def test_has_data(self):
        """Data can be accessed by attribute."""
        cm = CachedModel(User, {'username': 'frank'})
        self.assertEqual('frank', cm.username)

    def test_does_not_have_data(self):
        """Accessing missing attributes is AttributeError, not KeyError."""
        cm = CachedModel(User, {'username': 'frank'})
        self.assertRaises(AttributeError, getattr, cm, 'email')

    def test_pk_alias(self):
        """Accessing .pk returns the ID.

        DRF 3 uses pk to determine if a model has been created.
        """
        cm = CachedModel(User, {'id': 7, 'username': 'frank'})
        self.assertEqual(7, cm.pk)


class TestCachedQueryset(TestCase):

    """Tests for TestCachedQueryset."""

    def setUp(self):
        """Shared objects for testing."""
        self.cache = SampleCache()
        self.cache.cache.clear()

    def create_users(self, number):
        """Create a set of test users."""
        for x in range(number):
            User.objects.create(username='user%d' % x)

    def test_get_existing_instance(self):
        """A cached instance can be retrieved by get(pk)."""
        user = User.objects.create(username='frank')
        cq = CachedQueryset(self.cache, User.objects.all())
        cached_user = cq.get(pk=user.pk)
        self.assertEqual('frank', cached_user.username)

    def test_get_nonexisting_instance(self):
        """Attempting to get a missing instance raises DoesNotExist."""
        self.assertFalse(User.objects.filter(pk=666).exists())
        cq = CachedQueryset(self.cache, User.objects.all())
        self.assertRaises(User.DoesNotExist, cq.get, pk=666)

    def test_all(self):
        """Filtering by all() returns the CachedQueryset."""
        cq = CachedQueryset(self.cache, User.objects.all())
        self.assertEqual(cq, cq.all())

    def test_none(self):
        """An empty queryset has no items."""
        cq = CachedQueryset(self.cache, User.objects.all())
        cq_none = cq.none()
        self.assertEqual([], cq_none.pks)

    def test_pks_by_queryset(self):
        """Acessing primary keys populates the pk cache from the database."""
        self.create_users(10)
        cq = CachedQueryset(self.cache, User.objects.all())
        with self.assertNumQueries(1):
            pks = cq.pks
        self.assertEqual(10, len(pks))

    def test_pks_by_pks(self):
        """Accessing cached primary keys does not query the database."""
        self.create_users(10)
        cq = CachedQueryset(self.cache, User.objects.all(), [1, 2, 3])
        with self.assertNumQueries(0):
            pks = cq.pks
        self.assertEqual(3, len(pks))
        self.assertEqual([1, 2, 3], pks)

    def test_iteration_of_populated_queryset(self):
        """Iterating through a queryset returns CachedModels."""
        self.create_users(10)
        user_pks = list(User.objects.values_list('pk', flat=True))
        cq = CachedQueryset(self.cache, User.objects.order_by('pk'))
        for pk, cm in zip(user_pks, cq):
            self.assertIsInstance(cm, CachedModel)
            self.assertEqual(pk, cm.id)

    def test_iteration_of_empty_queryset(self):
        """Iterating through a queryset returns CachedModels."""
        cq = CachedQueryset(self.cache, User.objects.order_by('pk'))
        self.assertFalse(list(cq))

    def test_count_by_queryset(self):
        """Getting the count with an empty cache is a database operation."""
        self.create_users(10)
        cq = CachedQueryset(self.cache, User.objects.all())
        with self.assertNumQueries(1):
            self.assertEqual(10, cq.count())
        self.assertIsNone(cq._primary_keys)

    def test_count_by_pks(self):
        """Getting the count with a full cache does not query the database."""
        self.create_users(10)
        cq = CachedQueryset(self.cache, User.objects.all(), range(5))
        with self.assertNumQueries(0):
            self.assertEqual(5, cq.count())

    def test_filter(self):
        """A queryset without pks retrived can be filtered by pk."""
        self.create_users(5)
        user = User.objects.latest('id')
        cq = CachedQueryset(self.cache, User.objects.all())
        users = list(cq.filter(id=user.id))
        self.assertEqual(1, len(users))
        self.assertEqual(user.id, users[0].id)

    def test_get_slice_by_queryset(self):
        """A queryset slice of postpones database access until usage."""
        self.create_users(10)
        cq = CachedQueryset(self.cache, User.objects.all())
        with self.assertNumQueries(0):
            users = cq[0:5]
        with self.assertNumQueries(1):
            self.assertEqual(5, users.count())

    def test_get_slice_by_pks(self):
        """A queryset slice with a full cache does not query the database."""
        self.create_users(10)
        cq = CachedQueryset(self.cache, User.objects.all(), range(5))
        with self.assertNumQueries(0):
            users = cq[0:5]
        with self.assertNumQueries(0):
            self.assertEqual(5, users.count())


class TestPkOnlvQueryset(TestCase):

    """Tests for PkOnlyQueryset."""

    def setUp(self):
        """Shared objects for testing."""
        self.cache = SampleCache()
        self.cache.cache.clear()

    def test_iter(self):
        """Iterating a PkOnlyQueryset returns PkOnlyModels."""
        pks = [1, 2, 3]
        pkvl = PkOnlyQueryset(self.cache, User, pks)
        for pk, pm in zip(pks, pkvl):
            self.assertIsInstance(pm, PkOnlyModel)
            self.assertEqual(pm.pk, pk)

    def test_iter_empty_list(self):
        """Iterating an PkOnlyQueryset returns an empty list."""
        pkvl = PkOnlyQueryset(self.cache, User, [])
        self.assertFalse(list(pkvl))

    def test_filter_all(self):
        """Filtering with .all() returns the PkOnlyQueryset."""
        pkvl = PkOnlyQueryset(self.cache, User, range(5))
        pkall = pkvl.all()
        self.assertEqual(pkvl, pkall)

    def test_values_list(self):
        """A limited version of values_list returns pks."""
        pkvl = PkOnlyQueryset(self.cache, User, range(5))
        values_list = pkvl.values_list('id', flat=True)
        self.assertEqual(range(5), values_list)
