"""Models for sample poll app.

Based on the "Writing your first Django app" tutorial:
https://docs.djangoproject.com/en/1.7/intro/tutorial01/
"""
from django.contrib.auth.models import User
from django.db import models


class Question(models.Model):

    """A poll question."""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(models.Model):

    """An answer to a poll question."""

    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    voters = models.ManyToManyField(User, related_name='votes')
