"""Cache implementation for sample app."""

from django.contrib.auth.models import User, Group

from drf_cached_instances.cache import BaseCache

from .models import Question, Choice


class SampleCache(BaseCache):

    """Cache for the sample poll cache."""

    def user_default_serializer(self, obj):
        """Convert a User to a cached instance representation."""
        if not obj:
            return None

        votes_pks = getattr(obj, '_votes_pks', None)
        if votes_pks is None:
            votes_pks = list(obj.votes.values_list('pk', flat=True))

        return dict((
            ('id', obj.id),
            ('username', obj.username),
            self.field_to_json('DateTime', 'date_joined', obj.date_joined),
            self.field_to_json('PKList', 'votes', model=Choice, pks=votes_pks),
        ))

    def user_default_loader(self, pk):
        """Load a User from the database."""
        try:
            obj = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None
        obj._votes_pks = list(obj.votes.values_list('pk', flat=True))
        return obj

    def user_default_invalidator(self, obj):
        """Invalidate cached items when the User changes."""
        return ['drfc_user_count']

    group_default_serializer = None

    def group_default_loader(self, pk):
        """Load a Group from the database."""
        return Group.objects.get(pk=pk)

    def group_default_invalidator(self, obj):
        """Invalidated cached items when the Group changes."""
        user_pks = User.objects.values_list('pk', flat=True)
        return [('User', pk, False) for pk in user_pks]

    bar_default_serializer = None
    bar_default_loader = None
    bar_default_invalidator = None

    def question_default_serializer(self, obj):
        """Convert a Question to a cached instance representation."""
        if not obj:
            return None
        return dict((
            ('id', obj.id),
            ('question_text', obj.question_text),
            self.field_to_json('DateTime', 'pub_date', obj.pub_date),
        ))

    def question_default_loader(self, pk):
        """Load a Question from the database."""
        return Question.objects.get(pk=pk)

    def question_default_invalidator(self, obj):
        """Invalidated cached items when the Question changes."""
        return []

    def choice_default_serializer(self, obj):
        """Convert a Choice to a cached instance representation."""
        if not obj:
            return None

        voter_pks = getattr(obj, '_voter_pks', None)
        if voter_pks is None:
            voter_pks = list(obj.voters.values_list('pk', flat=True))
        return dict((
            ('id', obj.id),
            ('choice_text', obj.choice_text),
            self.field_to_json(
                'PK', 'question', model=Question, pk=obj.question_id),
            self.field_to_json('PKList', 'voters', model=User, pks=voter_pks)
        ))

    def choice_default_loader(self, pk):
        """Load a Choice from the database."""
        try:
            obj = Choice.objects.get(pk=pk)
        except Choice.DoesNotExist:
            return None
        else:
            obj._voter_pks = obj.voters.values_list('pk', flat=True)
            return obj

    def choice_default_invalidator(self, obj):
        """Invalidated cached items when the Choice changes."""
        invalid = [('Question', obj.question_id, True)]
        for pk in obj.voters.values_list('pk', flat=True):
            invalid.append(('User', pk, False))
        return invalid
