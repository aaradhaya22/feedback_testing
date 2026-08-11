"""Helper utilities for the archive module."""
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone


ARCHIVE_AGE_DAYS = 30


def get_archive_cutoff():
    """
    Return the timestamp before which a response is considered eligible.

    A response is "older than 30 days" when its submission timestamp is strictly
    before ``now - 30 days``.

    When USE_TZ=True, returns an aware UTC datetime for comparison against
    timezone-aware database columns. When USE_TZ=False, returns a naive datetime
    in the project's TIME_ZONE for comparison against naive database columns.
    """
    if settings.USE_TZ:
        return timezone.now() - timedelta(days=ARCHIVE_AGE_DAYS)
    else:
        # Return naive datetime in project's TIME_ZONE
        return datetime.now() - timedelta(days=ARCHIVE_AGE_DAYS)
