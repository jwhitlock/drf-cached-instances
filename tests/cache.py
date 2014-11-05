"""Cache implementation for tests.

This uses the standard django.contrib.auth.models.User.
"""

from django.contrib.auth.models import User, Group

from drf_cached_instances.cache import BaseCache


class UserCache(BaseCache):

    """Test cache that cached User instances."""

    def user_default_serializer(self, obj):
        """Convert a User to a cached instance representation."""
        if not obj:
            return None
        return dict((
            ('id', obj.id),
            ('username', obj.username),
            self.field_to_json('DateTime', 'date_joined', obj.date_joined),
        ))

    def user_default_loader(self, pk):
        """Load a User from the database."""
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def user_default_invalidator(self, obj):
        """Invalidate cached items when the User changes."""
        return ['drfc_user_count']

    group_default_serializer = None

    def group_default_loader(self, pk):
        """Convert a Group to a cached instance representation."""
        return Group.objects.get(pk=pk)

    def group_default_invalidator(self, obj):
        """Invalidated cached items when the Group changes."""
        user_pks = User.objects.values_list('pk', flat=True)
        return [('User', pk, False) for pk in user_pks]

    bar_default_serializer = None
    bar_default_loader = None
    bar_default_invalidator = None
