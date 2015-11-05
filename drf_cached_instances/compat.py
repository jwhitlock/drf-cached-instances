"""Backports and compatible methods."""

# get_model(app_name, model_name)
# Retrieves Django model class given the app and model name
try:
    # Django 1.8 and later
    from django.apps import apps
    get_model = apps.get_model
except ImportError:  # pragma: nocover
    from django.db.models.loading import get_model
assert get_model

# parse_duration(string)
# Parses a Django or ISO 8601 string into a datetime.timedelta
try:
    # Django 1.8 and later
    from django.utils.dateparse import parse_duration
except:  # pragma: nocover
    from datetime import timedelta
    import re
    from django.utils import six

    standard_duration_re = re.compile(
        r'^'
        r'(?:(?P<days>-?\d+) (days?, )?)?'
        r'((?:(?P<hours>\d+):)(?=\d+:\d+))?'
        r'(?:(?P<minutes>\d+):)?'
        r'(?P<seconds>\d+)'
        r'(?:\.(?P<microseconds>\d{1,6})\d{0,6})?'
        r'$'
    )

    # Support the sections of ISO 8601 date representation that are accepted by
    # timedelta
    iso8601_duration_re = re.compile(
        r'^P'
        r'(?:(?P<days>\d+(.\d+)?)D)?'
        r'(?:T'
        r'(?:(?P<hours>\d+(.\d+)?)H)?'
        r'(?:(?P<minutes>\d+(.\d+)?)M)?'
        r'(?:(?P<seconds>\d+(.\d+)?)S)?'
        r')?'
        r'$'
    )

    def parse_duration(value):
        """Parse a duration string and returns a datetime.timedelta.

        The preferred format for durations in Django is '%d %H:%M:%S.%f'.

        Also supports ISO 8601 representation.
        """
        match = standard_duration_re.match(value)
        if not match:
            match = iso8601_duration_re.match(value)
        if match:
            kw = match.groupdict()
            if kw.get('microseconds'):
                kw['microseconds'] = kw['microseconds'].ljust(6, '0')
            kw = dict([
                (k, float(v)) for k, v in six.iteritems(kw)
                if v is not None])
            return timedelta(**kw)
