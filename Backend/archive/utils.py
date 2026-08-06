"""Helper utilities for the archive module."""
from datetime import datetime, timedelta, timezone

from django.db import connection


ARCHIVE_AGE_DAYS = 30


def get_archive_cutoff():
    """
    Return the timestamp before which a response is considered eligible.

    A response is "older than 30 days" when its submission timestamp is strictly
    before ``now - 30 days``. An aware UTC datetime is returned so comparisons
    against the ``timestamp with time zone`` column in PostgreSQL are exact.
    """
    return datetime.now(timezone.utc) - timedelta(days=ARCHIVE_AGE_DAYS)


def reset_archive_sequence():
    """
    Reset the archive table's primary-key sequence to the highest used value.

    Archived rows are inserted with their original ``ResponseID`` (explicit PK
    values). PostgreSQL's serial sequence does not advance for explicit inserts,
    so without this the next auto-generated ``ResponseID`` could collide with an
    existing archived row. Running it after each batch keeps inserts collision-free.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT pg_get_serial_sequence(%s, %s)",
            ("feedback_response_archive", "ResponseID"),
        )
        seq = cursor.fetchone()
        if seq and seq[0]:
            cursor.execute(
                "SELECT setval(%s, COALESCE((SELECT MAX(\"ResponseID\") FROM feedback_response_archive), 1))",
                (seq[0],),
            )
