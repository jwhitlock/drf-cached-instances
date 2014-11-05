"""Tests for drf_cached_instances/models.py. """
from django.contrib.auth.models import User
from django.test import TestCase

from drf_cached_instances.models import CachedModel, CachedQueryset

from .cache import UserCache


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


class TestCachedQueryset(TestCase):

    """Tests for TestCachedQueryset."""

    def setUp(self):
        """Shared objects for testing."""
        self.cache = UserCache()
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
