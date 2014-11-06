"""Tests for drf_cached_instances/mixins.py."""

from datetime import datetime

from django.http import Http404
from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory, APITestCase
from pytz import UTC

from drf_cached_instances.models import CachedModel, CachedQueryset
from sample_poll_app.models import Question
from sample_poll_app.viewsets import QuestionViewSet


class CachedViewMixinTest(APITestCase):

    """Tests for the CachedViewMixin."""

    def test_list_uses_cachedqueryset(self):
        """A GET to the collection (list) uses a CachedQueryset."""
        view = QuestionViewSet()
        view.action = 'list'
        queryset = view.get_queryset()
        self.assertIsInstance(queryset, CachedQueryset)

    def test_update_uses_database(self):
        """A POST to an instance (update) uses the database."""
        view = QuestionViewSet()
        view.action = 'update'
        queryset = view.get_queryset()
        self.assertIsInstance(queryset, type(Question.objects.none()))

    def test_retrieve_object_is_cachedmodel(self):
        """A GET to an instance (retrieve) works with a CachedModel."""
        question = Question.objects.create(
            question_text="What is your quest?",
            pub_date=datetime(2014, 11, 6, 15, 30, 29, 135492, UTC))
        url = reverse('question-detail', kwargs={'pk': question.pk})
        request = APIRequestFactory().get(url)
        view = QuestionViewSet()
        view.action = 'retrieve'
        view.kwargs = {'pk': question.pk}
        view.request = request
        obj = view.get_object()
        self.assertIsInstance(obj, CachedModel)
        self.assertEqual(obj._model, Question)
        expected = {
            'id': question.id,
            'question_text': "What is your quest?",
            'pub_date': question.pub_date,
            'choices': None,
        }
        expected['choices'] = obj._data['choices']
        self.assertEqual(expected, obj._data)

    def test_retrieve_missing_object_is_error(self):
        """A GET to a missing instance is a 404."""
        self.assertFalse(Question.objects.filter(id=666).exists())
        url = reverse('question-detail', kwargs={'pk': 666})
        request = APIRequestFactory().get(url)
        view = QuestionViewSet()
        view.action = 'retrieve'
        view.kwargs = {'pk': 666}
        view.request = request
        self.assertRaises(Http404, view.get_object)

    def test_update_missing_object_is_error(self):
        """A POST to a missing instance is a 404."""
        self.assertFalse(Question.objects.filter(id=666).exists())
        url = reverse('question-detail', kwargs={'pk': 666})
        request = APIRequestFactory().post(
            url, {'question_text': 'What is the capital of Assyria?'})
        view = QuestionViewSet()
        view.action = 'update'
        view.kwargs = {'pk': 666}
        view.request = request
        self.assertRaises(Http404, view.get_object)
