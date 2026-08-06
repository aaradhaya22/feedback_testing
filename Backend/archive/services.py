"""Archival service for feedback responses.

Business logic for the archive module lives here. Management commands and any
future callers must go through these functions instead of implementing archival
logic themselves.
"""
import time
from dataclasses import dataclass

from django.db import transaction

from archive.models import FeedbackResponseArchive
from archive.utils import get_archive_cutoff, reset_archive_sequence
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
    Archive every feedback response older than 30 days into the archive table.

    How it works
    ------------
    1. Compute the cutoff (``now - 30 days``).
    2. Find the set of source ``ResponseID`` values that are eligible (their
       submission timestamp predates the cutoff).
    3. Look up which ``ResponseID`` values are already present in the archive
       table and exclude them.
    4. Copy the remaining rows into the archive table with ``is_archived=True``.
    5. Reset the archive primary-key sequence so future auto-generated IDs do not
       collide with the explicitly-inserted ``ResponseID`` values.

    Nothing is ever deleted or modified on ``feedback_response``.

    Duplicate prevention / idempotency
    ----------------------------------
    The archive table reuses the source ``ResponseID`` as its primary key.
    Re-running this function re-selects the same eligible IDs, but every one of
    them is already in the archive, so nothing is re-inserted. The PK uniqueness
    also makes a duplicate structurally impossible at the database level.
    """
    stats = ArchiveStats()
    start = time.perf_counter()
    cutoff = get_archive_cutoff()

    stats.total_scanned = Feedback_Response.objects.count()

    all_logged_ids = set(
        Feedback_SubmissionLog.objects.values_list("ResponseID", flat=True)
    )
    eligible_ids = _eligible_response_ids(cutoff)
    existing_ids = set(
        FeedbackResponseArchive.objects.values_list("ResponseID", flat=True)
    )

    stats.skipped_no_timestamp = stats.total_scanned - len(all_logged_ids)
    stats.skipped_too_recent = len(all_logged_ids - eligible_ids)
    stats.skipped_already_archived = len(eligible_ids & existing_ids)

    to_archive_ids = eligible_ids - existing_ids
    if to_archive_ids:
        with transaction.atomic():
            source_rows = (
                Feedback_Response.objects.filter(ResponseID__in=to_archive_ids)
                .values(
                    "ResponseID",
                    "AllocationID_id",
                    "Q1_Rating",
                    "Q2_Rating",
                    "Q3_Rating",
                    "Q4_Rating",
                    "Q5_Rating",
                    "Q6_Rating",
                    "Q7_Rating",
                    "Q8_Rating",
                    "Q9_Rating",
                    "Q10_Rating",
                    "Comments",
                )
            )
            archived_rows = [
                FeedbackResponseArchive(is_archived=True, **row) for row in source_rows
            ]
            FeedbackResponseArchive.objects.bulk_create(archived_rows)
            reset_archive_sequence()

    stats.newly_archived = len(to_archive_ids)
    stats.skipped = stats.total_scanned - stats.newly_archived
    stats.execution_time_seconds = round(time.perf_counter() - start, 4)
    return stats
