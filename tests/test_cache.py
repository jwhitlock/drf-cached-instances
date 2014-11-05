"""Tests for drf_cached_instances/cache.py."""

from datetime import datetime, date
import mock

from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.test.utils import override_settings
from pytz import UTC

from drf_cached_instances.cache import BaseCache
from drf_cached_instances.models import PkOnlyModel, PkOnlyValuesList

from .cache import UserCache


class SharedCacheTests(object):

    """Define generic cache tests."""

    def test_get_instances_no_specs(self):
        """An empty spec list returns an empty dictionary."""
        instances = self.cache.get_instances([])
        self.assertEqual({}, instances)

    def test_get_instances_cache_miss_no_obj(self):
        """A instance can be loaded without a Django object."""
        date_joined = datetime(2014, 9, 22, 9, 11, tzinfo=UTC)
        user = User.objects.create(
            username='the_user', date_joined=date_joined)
        with self.assertNumQueries(1):
            instances = self.cache.get_instances([('User', user.pk, None)])
        expected = {
            ('User', user.pk): (
                {
                    'id': user.pk,
                    'username': 'the_user',
                    'date_joined': date_joined,
                },
                'drfc_default_User_1',
                user,
            ),
        }
        self.assertEqual(expected, instances)

    def test_get_instances_cache_miss_with_obj(self):
        """A instance can be loaded with a Django object."""
        date_joined = datetime(2014, 9, 22, 9, 11, tzinfo=UTC)
        user = User.objects.create(
            username='the_user', date_joined=date_joined)
        with self.assertNumQueries(0):
            instances = self.cache.get_instances([('User', user.pk, user)])
        expected = {
            ('User', user.pk): (
                {
                    'id': user.pk,
                    'username': 'the_user',
                    'date_joined': date_joined,
                },
                'drfc_default_User_1',
                user,
            ),
        }
        self.assertEqual(expected, instances)

    def test_get_instances_invalid_pk(self):
        """An invalid PK results in an empty instance return."""
        self.assertFalse(User.objects.filter(pk=666).exists())
        instances = self.cache.get_instances([('User', 666, None)])
        self.assertEqual({}, instances)

    def test_update_instance_invalid_model(self):
        """An error is raised updating a model not defined in the Cache."""
        self.assertRaises(AttributeError, self.cache.update_instance, 'Foo', 1)

    def test_update_instance_unhandled_model(self):
        """An error is raised updating a model defined as None in the Cache."""
        instances = self.cache.update_instance('Bar', 666)
        self.assertEqual([], instances)


@override_settings(USE_DRF_INSTANCE_CACHE=True)
class TestCache(SharedCacheTests, TestCase):

    """Test cache functions when the instance cache is enabled."""

    def setUp(self):
        """Setup environment for an enabled cache."""
        self.cache = UserCache()
        self.cache.cache.clear()
        self.mock_delete = mock.Mock()
        self.cache.cache.delete = self.mock_delete

    def test_update_instance_invalidator_only(self):
        """A model can have no serializer but a defined invalidator."""
        user = User.objects.create(username='A user')
        group = Group.objects.create()
        group.user_set.add(user)
        invalid = self.cache.update_instance('Group', group.pk)
        self.assertEqual([('User', user.pk, 'default')], invalid)

    def test_update_instance_deleted_model(self):
        """A deleted instance can still invalidate related instances."""
        self.assertFalse(User.objects.filter(pk=666).exists())
        invalid = self.cache.update_instance('User', 666)
        self.assertEqual([], invalid)
        self.mock_delete.assertCalledOnce('foo')

    def test_update_instance_cache_string(self):
        """A invalidator can delete cache entries by name."""
        user = User.objects.create(username='username')
        invalid = self.cache.update_instance('User', user.pk)
        self.assertEqual([], invalid)
        self.mock_delete.assertCalledOnce('drfc_user_count')


@override_settings(USE_INSTANCE_CACHE=False)
class TestCacheDisabled(SharedCacheTests, TestCase):

    """Test cache functions when the instance cache is disabled."""

    def setUp(self):
        """Setup environment for a disabled cache."""
        self.cache = UserCache()


class TestFieldConverters(TestCase):

    """Test the built-in field converter methods."""

    def setUp(self):
        """Use a non-customized BaseCache for tests."""
        self.cache = BaseCache()

    def test_date(self):
        """A datetime.date can be stored and retrieved."""
        the_date = date(2014, 9, 22)
        converted = self.cache.field_date_to_json(the_date)
        self.assertEqual(converted, [2014, 9, 22])
        out = self.cache.field_date_from_json(converted)
        self.assertEqual(out, the_date)

    def test_datetime_with_ms(self):
        """A datetime with milliseconds can be stored and retrieved."""
        dt = datetime(2014, 9, 22, 8, 52, 0, 123456, UTC)
        converted = self.cache.field_datetime_to_json(dt)
        self.assertEqual(converted, '1411375920.123456')
        out = self.cache.field_datetime_from_json(converted)
        self.assertEqual(out, dt)

    def test_datetime_without_ms(self):
        """A datetime w/o milliseconds can be stored and retrieved."""
        dt = datetime(2014, 9, 22, 8, 52, 0, 0, UTC)
        converted = self.cache.field_datetime_to_json(dt)
        self.assertEqual(converted, 1411375920)
        out = self.cache.field_datetime_from_json(converted)
        self.assertEqual(out, dt)

    def test_datetime_without_timezone(self):
        """A naive datetime is treated as a UTC datetime."""
        dt = datetime(2014, 9, 22, 8, 52, 0, 123456)
        converted = self.cache.field_datetime_to_json(dt)
        self.assertEqual(converted, '1411375920.123456')
        out = self.cache.field_datetime_from_json(converted)
        self.assertEqual(out, datetime(2014, 9, 22, 8, 52, 0, 123456, UTC))

    def test_pklist(self):
        """A list of primary keys is retrieved as a PkOnlyValuesList."""
        converted = self.cache.field_pklist_to_json(User, (1, 2, 3))
        expected = {
            'app': 'auth',
            'model': 'user',
            'pks': [1, 2, 3],
        }
        self.assertEqual(converted, expected)
        out = self.cache.field_pklist_from_json(converted)
        self.assertIsInstance(out, PkOnlyValuesList)
        self.assertEqual(User, out.model)
        self.assertEqual([1, 2, 3], out.pks)

    def test_pk(self):
        """A primary key is retrieved as a PkOnlyModel."""
        converted = self.cache.field_pk_to_json(User, 1)
        expected = {
            'app': 'auth',
            'model': 'user',
            'pk': 1,
        }
        self.assertEqual(converted, expected)
        out = self.cache.field_pk_from_json(converted)
        self.assertIsInstance(out, PkOnlyModel)
        self.assertEqual(User, out.model)
        self.assertEqual(1, out.pk)
