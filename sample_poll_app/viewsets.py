"""Django REST Framework viewsets for sample app."""
from django.contrib.auth.models import User
from drf_cached_instances.mixins import CachedViewMixin
from rest_framework.viewsets import ModelViewSet as BaseModelViewSet

from .cache import SampleCache
from .models import Choice, Question
from .serializers import ChoiceSerializer, QuestionSerializer, UserSerializer


class ModelViewSet(CachedViewMixin, BaseModelViewSet):

    """ModelViewSet that uses CachedViewMixin."""

    cache_class = SampleCache


class UserViewSet(ModelViewSet):

    """API endpoint that allows users to be viewed or edited."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class QuestionViewSet(ModelViewSet):

    """API endpoint that allows questions to be viewed or edited."""

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class ChoiceViewSet(ModelViewSet):

    """API endpoint that allows choices to be viewed or edited."""

    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
