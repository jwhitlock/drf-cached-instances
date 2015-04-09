"""Tests for drf_cached_instances/cache.py."""

from datetime import datetime, date
from json import dumps
import mock

from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.test.utils import override_settings
from pytz import UTC

from drf_cached_instances.cache import BaseCache
from drf_cached_instances.models import PkOnlyModel, PkOnlyQueryset

from sample_poll_app.cache import SampleCache
from sample_poll_app.models import Question, Choice


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
        self.cache.cache and self.cache.cache.clear()
        with self.assertNumQueries(2):
            instances = self.cache.get_instances([('User', user.pk, None)])
        expected = {
            ('User', user.pk): (
                {
                    'id': user.pk,
                    'username': 'the_user',
                    'date_joined': date_joined,
                    'votes': [],
                },
                'drfc_default_User_1',
                user,
            ),
        }
        expected[('User', user.pk)][0]['votes'] = (
            instances[('User', user.pk)][0]['votes'])
        self.assertEqual(expected, instances)

    def test_get_instances_cache_miss_with_obj(self):
        """A instance can be loaded with a Django object."""
        date_joined = datetime(2014, 9, 22, 9, 11, tzinfo=UTC)
        user_pk = User.objects.create(
            username='the_user', date_joined=date_joined).pk
        user = self.cache.user_default_loader(user_pk)
        with self.assertNumQueries(0):
            instances = self.cache.get_instances([('User', user_pk, user)])
        expected = {
            ('User', user_pk): (
                {
                    'id': user_pk,
                    'username': 'the_user',
                    'date_joined': date_joined,
                    'votes': [],
                },
                'drfc_default_User_1',
                user,
            ),
        }
        expected[('User', user_pk)][0]['votes'] = (
            instances[('User', user_pk)][0]['votes'])
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
        self.cache = SampleCache()
        self.cache.cache.clear()
        self.mock_delete = mock.Mock()
        self.cache.cache.delete = self.mock_delete

    def test_cache_is_available(self):
        """When USE_DRF_INSTANCE_CACHE is True, cache is available."""
        self.assertTrue(self.cache.cache)

    def test_get_instance_cache_hit(self):
        """When instance is cached, the database is not queried."""
        key = self.cache.key_for('default', 'User', 123)
        self.assertEqual('drfc_default_User_123', key)
        data = {'id': 123, 'foo': 'bar'}
        self.cache.cache.set(key, dumps(data))
        with self.assertNumQueries(0):
            instances = self.cache.get_instances([('User', 123, None)])
        expected = {('User', 123): (data, key, None)}
        self.assertEqual(expected, instances)

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
        self.mock_delete.assert_called_once_with('drfc_default_User_666')

    def test_update_instance_cache_string(self):
        """A invalidator can delete cache entries by name."""
        user = User.objects.create(username='username')
        invalid = self.cache.update_instance('User', user.pk)
        self.assertEqual([], invalid)
        self.mock_delete.assert_called_once_with('drfc_user_count')

    def test_update_instance_no_changes(self):
        """When the representation is unchanged, updates do not cascade."""
        user = User.objects.create(
            username='username',
            date_joined=datetime(2014, 11, 5, 22, 2, 16, 735772, UTC))
        key = self.cache.key_for('default', 'User', user.pk)
        representation = {
            'id': user.id,
            'username': 'username',
            'date_joined:DateTime': '1415224936.735772',
            'votes:PKList': {
                'app': 'sample_poll_app',
                'model': 'choice',
                'pks': [],
            },
        }
        self.cache.cache.set(key, dumps(representation))
        self.mock_delete.side_effect = Exception('Not Called')
        invalid = self.cache.update_instance('User', user.pk, user)
        self.assertEqual([], invalid)

    def test_update_instance_with_raw_instance(self):
        """An invalidator loads related PKs with a raw instance."""
        # Create user, then delete auto-created cache
        User.objects.create(username='username')
        self.cache.cache.clear()
        self.mock_delete.reset_mock()
        user = User.objects.get(username='username')

        with self.assertNumQueries(1):
            invalid = self.cache.update_instance('User', user.pk, user)
        self.assertEqual([], invalid)
        self.mock_delete.assert_called_once_with('drfc_user_count')

    def test_update_instance_with_loaded_instance(self):
        """An invalidator skips the database with a loaded instance."""
        # Create user, then delete auto-created cache
        user_pk = User.objects.create(username='username').pk
        user = self.cache.user_default_loader(user_pk)
        self.cache.cache.clear()
        self.mock_delete.reset_mock()

        with self.assertNumQueries(0):
            invalid = self.cache.update_instance('User', user_pk, user)
        self.assertEqual([], invalid)
        self.mock_delete.assert_called_once_with('drfc_user_count')

    def test_delete_called_on_immediate_invalidate(self):
        """An invalidator can ask for immediate invalidation."""
        user = User.objects.create(username='voter')
        question = Question.objects.create(
            question_text='What is your favorite color?',
            pub_date=datetime(2014, 11, 6, 8, 45, 49, 538232, UTC))
        choice = Choice.objects.create(
            question=question, choice_text="Blue. No, Green!")
        choice.voters.add(user)
        invalid = self.cache.choice_default_invalidator(choice)
        expected = [
            ('Question', question.pk, True),
            ('User', user.pk, False),
        ]
        self.assertEqual(expected, invalid)
        to_update = self.cache.update_instance('Choice', choice.pk)
        expected_update = [
            ('Question', question.pk, 'default'),
            ('User', user.pk, 'default'),
        ]
        self.assertEqual(expected_update, to_update)
        self.mock_delete.assertEqual('drf_default_question_%s' % question.pk)

    def test_update_instance_cache_miss_update_only(self):
        """With update_only, cache misses don't update or cascade."""
        user = User.objects.create(username='voter')
        question = Question.objects.create(
            question_text='What is your favorite color?',
            pub_date=datetime(2014, 11, 6, 8, 45, 49, 538232, UTC))
        choice = Choice.objects.create(
            question=question, choice_text="Blue. No, Green!")
        choice.voters.add(user)
        self.cache.cache.clear()
        to_update = self.cache.update_instance(
            'Choice', choice.pk, update_only=True)
        self.assertEqual([], to_update)
        self.mock_delete.assertEqual('drf_default_question_%s' % question.pk)

    def test_delete_all_versions_one_version(self):
        """Delete all cached instances for a model and ID."""
        self.cache.delete_all_versions("Model", 86)
        self.mock_delete.assert_called_once_with("drfc_default_Model_86")


@override_settings(USE_DRF_INSTANCE_CACHE=True)
class TestVersionsCache(SharedCacheTests, TestCase):

    """Test cache functions when multiple versions are defined."""

    def setUp(self):
        """Setup environment for an enabled cache."""
        self.cache = SampleCache()
        self.cache.versions = ['default', 'v2']
        self.cache.cache.clear()
        self.mock_delete = mock.Mock()
        self.cache.cache.delete = self.mock_delete

    def test_update_instance_unhandled_model(self):
        """An error is raised update a model defined as None in the Cache."""
        self.cache.bar_v2_serializer = None
        self.cache.bar_v2_loader = None
        self.cache.bar_v2_invalidator = None
        super(TestVersionsCache, self).test_update_instance_unhandled_model()

    def test_delete_all_versions_two_versions(self):
        """Delete all cached instances with multiple versions."""
        self.cache.delete_all_versions("Model", 86)
        self.mock_delete.assert_has_calls([
            mock.call("drfc_default_Model_86"),
            mock.call("drfc_v2_Model_86")])


@override_settings(USE_DRF_INSTANCE_CACHE=False)
class TestCacheDisabled(SharedCacheTests, TestCase):

    """Test cache functions when the instance cache is disabled."""

    def setUp(self):
        """Setup environment for a disabled cache."""
        self.cache = SampleCache()

    def test_cache_is_none(self):
        """When USE_DRF_INSTANCE_CACHE is False, cache is None."""
        self.assertIsNone(self.cache.cache)

    def test_invalidate_returns_none(self):
        """When cache is disabled, updating is skipped."""
        with self.assertNumQueries(0):
            invalid = self.cache.update_instance('User', 123)
        self.assertEqual([], invalid)

    def test_delete_all_versions(self):
        """No error when requesting to delete all cached instances."""
        self.cache.delete_all_versions("Model", 86)


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
        """A list of primary keys is retrieved as a PkOnlyQueryset."""
        converted = self.cache.field_pklist_to_json(User, (1, 2, 3))
        expected = {
            'app': 'auth',
            'model': 'user',
            'pks': [1, 2, 3],
        }
        self.assertEqual(converted, expected)
        out = self.cache.field_pklist_from_json(converted)
        self.assertIsInstance(out, PkOnlyQueryset)
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
