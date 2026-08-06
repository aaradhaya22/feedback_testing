"""Django management command to archive old feedback responses.

Usage
-----
    python manage.py archive_feedback

The command scans ``feedback_response``, copies every record whose submission
timestamp is older than 30 days into the archive table
(``feedback_response_archive``), and prints a summary. It is safe to run
repeatedly: already-archived records are skipped and no duplicates are ever
created. No source data is deleted or modified.
"""
from django.core.management.base import BaseCommand

from archive.services import archive_feedback


class Command(BaseCommand):
    help = (
        "Copy feedback responses older than 30 days into the archive table. "
        "Idempotent: already-archived records are skipped. Source data is never "
        "modified or deleted."
    )

    def handle(self, *args, **options):
        stats = archive_feedback()

        self.stdout.write("=" * 52)
        self.stdout.write("Feedback archival completed")
        self.stdout.write("=" * 52)
        self.stdout.write(f"Total records scanned    : {stats.total_scanned}")
        self.stdout.write(f"Newly archived records   : {stats.newly_archived}")
        self.stdout.write(f"Skipped records          : {stats.skipped}")
        self.stdout.write("  - already archived     : "
                          f"{stats.skipped_already_archived}")
        self.stdout.write("  - too recent (< 30 days): "
                          f"{stats.skipped_too_recent}")
        self.stdout.write("  - no submission timestamp: "
                          f"{stats.skipped_no_timestamp}")
        self.stdout.write(f"Execution time           : "
                          f"{stats.execution_time_seconds}s")
        self.stdout.write("=" * 52)
