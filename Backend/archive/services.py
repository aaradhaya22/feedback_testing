"""Archival service for feedback responses.

Business logic for the archive module lives here. Management commands and any
future callers must go through these functions instead of implementing archival
logic themselves.
"""
import time
from dataclasses import dataclass

from django.db import transaction

from archive.utils import get_archive_cutoff
from feedback_app.models import Feedback_Response, Feedback_SubmissionLog


@dataclass
class ArchiveStats:
    """Summary produced by a single archival run."""

    total_scanned: int = 0
    newly_archived: int = 0
    skipped: int = 0
    skipped_already_archived: int = 0
    skipped_too_recent: int = 0
    skipped_no_timestamp: int = 0
    execution_time_seconds: float = 0.0


def _eligible_response_ids(cutoff):
    """
    Return the set of ``ResponseID`` values whose submission is older than cutoff.

    ``feedback_response`` has no timestamp column; the session timestamp lives on
    ``feedback_submissionlog.Timestamp`` (one log row per response, created
    atomically with the response). A response is eligible if any of its submission
    logs predates the cutoff.
    """
    return set(
        Feedback_SubmissionLog.objects.filter(Timestamp__lt=cutoff)
        .values_list("ResponseID", flat=True)
    )


def archive_feedback():
    """
    Mark feedback responses older than 30 days as archived.

    How it works
    ------------
    1. Compute the cutoff (``now - 30 days``).
    2. Find the set of source ``ResponseID`` values that are eligible (their
       submission timestamp predates the cutoff).
    3. Look up which ``ResponseID`` values are already marked as archived
       and exclude them.
    4. Update the remaining rows with ``is_archived=True``.

    Nothing is ever deleted. Responses are updated in-place.

    Duplicate prevention / idempotency
    ----------------------------------
    Re-running this function re-selects the same eligible IDs, but every one of
    them is already archived, so nothing is re-updated. The operation is safe to
    run multiple times.
    """
    stats = ArchiveStats()
    start = time.perf_counter()
    cutoff = get_archive_cutoff()

    stats.total_scanned = Feedback_Response.objects.count()

    all_logged_ids = set(
        Feedback_SubmissionLog.objects.values_list("ResponseID", flat=True)
    )
    eligible_ids = _eligible_response_ids(cutoff)
    already_archived_ids = set(
        Feedback_Response.objects.filter(is_archived=True).values_list("ResponseID", flat=True)
    )

    stats.skipped_no_timestamp = stats.total_scanned - len(all_logged_ids)
    stats.skipped_too_recent = len(all_logged_ids - eligible_ids)
    stats.skipped_already_archived = len(eligible_ids & already_archived_ids)

    to_archive_ids = eligible_ids - already_archived_ids
    if to_archive_ids:
        with transaction.atomic():
            updated = Feedback_Response.objects.filter(ResponseID__in=to_archive_ids).update(is_archived=True)
            stats.newly_archived = updated
    else:
        stats.newly_archived = 0

    stats.skipped = stats.total_scanned - stats.newly_archived
    stats.execution_time_seconds = round(time.perf_counter() - start, 4)
    return stats
