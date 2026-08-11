"""Tests for the archive module."""
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone as django_timezone

from archive.services import archive_feedback
from archive.utils import get_archive_cutoff
from feedback_app.models import Academic_Allocation, Academic_Subject, Faculty_Teacher, Feedback_Response, Feedback_SubmissionLog


class ArchiveFeedbackTestCase(TestCase):
    """Test the archive_feedback management command / service."""

    def setUp(self):
        """Create test data."""
        # Create required related objects with unique codes to avoid conflicts
        import uuid
        unique_code = f"CS{uuid.uuid4().hex[:6].upper()}"
        unique_teacher = f"T{uuid.uuid4().hex[:6].upper()}"
        
        self.subject = Academic_Subject.objects.create(
            SubjectCode=unique_code,
            SubjectName="Computer Science 101",
            Semester=1,
            Branch="CSE",
        )
        self.teacher = Faculty_Teacher.objects.create(
            TeacherID=unique_teacher,
            FullName="Dr. Test Teacher",
            Designation="Professor",
        )
        self.allocation = Academic_Allocation.objects.create(
            TargetBranch="CSE",
            Target_Year=1,
            Target_Semester=1,
            Target_Section=1,
            SubjectCode=self.subject,
            TeacherID=self.teacher,
        )

    def create_response_with_log(self, timestamp, is_archived=False):
        """Helper to create a response with a submission log at the given timestamp."""
        response = Feedback_Response.objects.create(
            AllocationID=self.allocation,
            Q1_Rating=4,
            Q2_Rating=4,
            Q3_Rating=4,
            Q4_Rating=4,
            Q5_Rating=4,
            Q6_Rating=4,
            Q7_Rating=4,
            Q8_Rating=4,
            Q9_Rating=4,
            Q10_Rating=4,
            Comments="Test comment",
            is_archived=is_archived,
        )
        # Create the log first (auto_now_add sets current time), then update timestamp
        # directly in DB to bypass auto_now_add
        log = Feedback_SubmissionLog.objects.create(
            AllocationID=self.allocation,
            ResponseID=response,
            EnrollmentNo="E12345",
        )
        Feedback_SubmissionLog.objects.filter(LogID=log.LogID).update(Timestamp=timestamp)
        return response

    def test_old_responses_become_archived(self):
        """Responses older than 30 days should be marked as archived."""
        cutoff = get_archive_cutoff()
        old_timestamp = cutoff - timedelta(days=1)
        old_response = self.create_response_with_log(timestamp=old_timestamp)

        stats = archive_feedback()

        old_response.refresh_from_db()
        self.assertTrue(old_response.is_archived)
        self.assertEqual(stats.newly_archived, 1)

    def test_new_responses_remain_unarchived(self):
        """Responses newer than 30 days should remain unarchived."""
        cutoff = get_archive_cutoff()
        recent_timestamp = cutoff + timedelta(days=15)
        recent_response = self.create_response_with_log(timestamp=recent_timestamp)

        stats = archive_feedback()

        recent_response.refresh_from_db()
        self.assertFalse(recent_response.is_archived)
        self.assertEqual(stats.newly_archived, 0)
        # Only the response we created should be scanned in this isolated test
        self.assertEqual(stats.skipped_too_recent, 1)

    def test_already_archived_responses_handled_correctly(self):
        """Already archived responses should be skipped, not re-archived."""
        cutoff = get_archive_cutoff()
        old_timestamp = cutoff - timedelta(days=1)
        old_response = self.create_response_with_log(timestamp=old_timestamp, is_archived=True)

        stats = archive_feedback()

        old_response.refresh_from_db()
        self.assertTrue(old_response.is_archived)
        self.assertEqual(stats.newly_archived, 0)
        self.assertEqual(stats.skipped_already_archived, 1)

    def test_running_multiple_times_is_safe(self):
        """Running the command multiple times should be idempotent."""
        cutoff = get_archive_cutoff()
        old_timestamp = cutoff - timedelta(days=1)
        old_response = self.create_response_with_log(timestamp=old_timestamp)

        # Run archival first time
        stats1 = archive_feedback()
        self.assertEqual(stats1.newly_archived, 1)

        # Run archival second time
        stats2 = archive_feedback()
        self.assertEqual(stats2.newly_archived, 0)
        self.assertEqual(stats2.skipped_already_archived, 1)

        # Verify response is still archived
        old_response.refresh_from_db()
        self.assertTrue(old_response.is_archived)

    def test_existing_records_not_deleted(self):
        """Archival should never delete any feedback_response records."""
        cutoff = get_archive_cutoff()
        old_response = self.create_response_with_log(timestamp=cutoff - timedelta(days=1))
        recent_response = self.create_response_with_log(timestamp=cutoff + timedelta(days=15))

        initial_count = Feedback_Response.objects.count()

        archive_feedback()

        final_count = Feedback_Response.objects.count()
        self.assertEqual(initial_count, final_count)

        old_response.refresh_from_db()
        recent_response.refresh_from_db()
        self.assertTrue(old_response.is_archived)
        self.assertFalse(recent_response.is_archived)

    def test_response_without_submission_log_skipped(self):
        """Responses without a submission log should be skipped."""
        response = Feedback_Response.objects.create(
            AllocationID=self.allocation,
            Q1_Rating=3,
            Q2_Rating=3,
            Q3_Rating=3,
            Q4_Rating=3,
            Q5_Rating=3,
            Q6_Rating=3,
            Q7_Rating=3,
            Q8_Rating=3,
            Q9_Rating=3,
            Q10_Rating=3,
            Comments="No log",
        )

        stats = archive_feedback()

        response.refresh_from_db()
        self.assertFalse(response.is_archived)
        self.assertEqual(stats.skipped_no_timestamp, 1)

    @patch("archive.services.get_archive_cutoff")
    @patch("archive.utils.get_archive_cutoff")
    def test_cutoff_is_exactly_30_days(self, mock_utils_cutoff, mock_services_cutoff):
        """The cutoff should be exactly 30 days (older than 30 days = archived)."""
        # Use a fixed cutoff for deterministic testing
        fixed_cutoff = django_timezone.now()
        mock_utils_cutoff.return_value = fixed_cutoff
        mock_services_cutoff.return_value = fixed_cutoff
        
        # Create a response at exactly the cutoff (should NOT be archived - strictly less than)
        exactly_30_days = self.create_response_with_log(timestamp=fixed_cutoff)
        
        # Create a response 1 second before cutoff (should be archived)
        thirty_days_one_sec = self.create_response_with_log(timestamp=fixed_cutoff - timedelta(seconds=1))

        stats = archive_feedback()

        exactly_30_days.refresh_from_db()
        thirty_days_one_sec.refresh_from_db()

        # Exactly at cutoff should NOT be archived (cutoff is strictly less than)
        self.assertFalse(exactly_30_days.is_archived)
        # 1 second before cutoff should be archived
        self.assertTrue(thirty_days_one_sec.is_archived)

        self.assertEqual(stats.newly_archived, 1)
        self.assertEqual(stats.skipped_too_recent, 1)


class ArchiveManagementCommandTestCase(TestCase):
    """Test the management command directly."""

    def test_command_runs_without_error(self):
        """The management command should execute without errors."""
        from django.core.management import call_command
        from io import StringIO

        out = StringIO()
        call_command("archive_feedback", stdout=out)
        output = out.getvalue()

        self.assertIn("Feedback archival completed", output)
        self.assertIn("Total records scanned", output)
        self.assertIn("Newly archived records", output)
        self.assertIn("Skipped records", output)
        self.assertIn("Execution time", output)