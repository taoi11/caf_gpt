"""
PaceNoteFoo app models.
"""
from django.db import models
from core.models import TimeStampedModel


class PaceNote(TimeStampedModel):
    """
    Model to store generated pace notes.

    Note: This model is not currently used in the implementation,
    but is provided as a placeholder for future enhancements
    such as storing generated pace notes for reference or analytics.
    """
    user_input = models.TextField()
    rank = models.CharField(max_length=50)
    generated_note = models.TextField()

    def __str__(self):
        return f"PaceNote for {self.rank} - {self.created[:10]}"
