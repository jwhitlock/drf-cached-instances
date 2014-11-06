"""Models for sample poll app.

Based on the "Writing your first Django app" tutorial:
https://docs.djangoproject.com/en/1.7/intro/tutorial01/
"""
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete, post_save, m2m_changed
from django.dispatch import receiver


class Question(models.Model):

    """A poll question."""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(models.Model):

    """An answer to a poll question."""

    question = models.ForeignKey(Question, related_name='choices')
    choice_text = models.CharField(max_length=200)
    voters = models.ManyToManyField(User, related_name='votes')


cached_model_names = ('User', 'Question', 'Choice')


@receiver(
    m2m_changed, sender=Choice.voters.through,
    dispatch_uid='m2m_choice_voters_changed_update_cache')
def choice_voters_changed_update_cache(
        sender, instance, action, reverse, model, pk_set, **kwargs):
    """Update cache when choice.voters changes."""
    if action not in ('post_add', 'post_remove', 'post_clear'):
        # post_clear is not handled, because clear is called in
        # django.db.models.fields.related.ReverseManyRelatedObjects.__set__
        # before setting the new order
        return

    if model == User:
        assert type(instance) == Choice
        choices = [instance]
        if pk_set:
            users = list(User.objects.filter(pk__in=pk_set))
        else:
            users = []
    else:
        if pk_set:
            choices = list(Choice.objects.filter(pk__in=pk_set))
        else:
            choices = []
        users = [instance]

    from .tasks import update_cache_for_instance
    for choice in choices:
        update_cache_for_instance('Choice', choice.pk, choice)
    for user in users:
        update_cache_for_instance('User', user.pk, user)


@receiver(post_delete, dispatch_uid='post_delete_update_cache')
def post_delete_update_cache(sender, instance, **kwargs):
    """Update the cache when an instance is deleted."""
    name = sender.__name__
    if name in cached_model_names:
        from .tasks import update_cache_for_instance
        update_cache_for_instance(name, instance.pk, instance)


@receiver(post_save, dispatch_uid='post_save_update_cache')
def post_save_update_cache(sender, instance, created, raw, **kwargs):
    """Update the cache when an instance is created or modified."""
    if raw:
        return
    name = sender.__name__
    if name in cached_model_names:
        delay_cache = getattr(instance, '_delay_cache', False)
        if not delay_cache:
            from .tasks import update_cache_for_instance
            update_cache_for_instance(name, instance.pk, instance)
