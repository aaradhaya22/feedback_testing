from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator


class FeedbackResponseArchive(models.Model):
    """
    Archived copy of a feedback response.

    This model mirrors the ``feedback_app.Feedback_Response`` table field-for-field
    (including the ``AllocationID`` foreign key) and adds a single ``is_archived``
    flag which is always ``True`` for rows stored here.

    Why copy instead of move?
    -------------------------
    Source rows in ``feedback_response`` are referenced by other tables (e.g.
    ``feedback_submissionlog.ResponseID``) and by live reporting queries. Deleting
    or moving rows would break those references and change existing behaviour.
    Archiving by *copying* keeps the live table intact while preserving a durable,
    immutable snapshot for retention/compliance.

    ``ResponseID`` is reused from the source table and is the primary key here, so
    the archive table itself is the source of truth for what has already been
    archived and duplicates are structurally impossible.
    """

    ResponseID = models.AutoField(primary_key=True)
    AllocationID = models.ForeignKey(
        "feedback_app.Academic_Allocation",
        db_column="AllocationID",
        on_delete=models.PROTECT,
        help_text=(
            "References the live academic allocation. PROTECT (instead of CASCADE) "
            "ensures archived rows can never be silently destroyed when a lookup "
            "allocation is deleted."
        ),
    )
    Q1_Rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    Q2_Rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    Q3_Rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    Q4_Rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    Q5_Rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    Q6_Rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    Q7_Rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    Q8_Rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    Q9_Rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    Q10_Rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    Comments = models.CharField(max_length=500, blank=True, null=True, validators=[MaxLengthValidator(500)])
    is_archived = models.BooleanField(default=False)

    class Meta:
        db_table = "feedback_response_archive"
        verbose_name = "Archived Feedback Response"
        verbose_name_plural = "Archived Feedback Responses"

    def __str__(self):
        return f"ArchivedFeedbackResponse #{self.ResponseID} (archived={self.is_archived})"
