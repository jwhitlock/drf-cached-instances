"""DRF serializers for sample app."""

from django.contrib.auth.models import User
from rest_framework.serializers import (
    DateField, ModelSerializer)

from .models import Question, Choice


class UserSerializer(ModelSerializer):
    """DRF serializer for Users."""

    created = DateField(source='date_joined', read_only=True)

    class Meta:
        """Configuration for UserSerializer."""

        model = User
        fields = ('id', 'username', 'created')


class QuestionSerializer(ModelSerializer):
    """DRF serializer for Questions."""

    class Meta:
        """Configuration for QuestionSerializer."""

        model = Question


class ChoiceSerializer(ModelSerializer):
    """DRF serializer for Choices."""

    class Meta:
        """Configuration for ChoiceSerializer."""

        model = Choice
