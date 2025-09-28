"""
Core app models.
"""
import uuid
from django.db import models


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    created and modified fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CostTracker(models.Model):
    """
    Model for tracking API usage costs.
    Stores a single record with the total accumulated cost.
    """
    id = models.IntegerField(primary_key=True, default=1)
    total_usage = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cost_tracker'
        verbose_name = 'Cost Tracker'
        verbose_name_plural = 'Cost Tracker'

    def __str__(self):
        return f"Total Usage: ${self.total_usage:.6f}"

    @classmethod
    def get_or_create_singleton(cls):
        """
        Gets or creates the singleton cost tracker record.
        """
        obj, created = cls.objects.get_or_create(
            id=1,
            defaults={'total_usage': 0.0}
        )
        return obj


# Database models for shared SvelteKit database integration
class DoadDocument(models.Model):
    """
    Model for DOAD (Defence Operations and Activities Directive) documents.

    Maps to the 'doad' table in the shared database.
    Each record represents a chunk of a DOAD document with metadata.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text_chunk = models.TextField(help_text="Content chunk of the DOAD document")
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Document metadata including title, section, etc."
    )
    created_at = models.DateTimeField(help_text="When this chunk was created")
    doad_number = models.TextField(
        null=True,
        blank=True,
        help_text="DOAD number identifier (e.g., '1000-1')"
    )

    class Meta:
        managed = False  # Don't let Django manage this table
        db_table = 'doad'
        ordering = ['created_at']
        verbose_name = 'DOAD Document'
        verbose_name_plural = 'DOAD Documents'

    def __str__(self):
        return f"DOAD {self.doad_number or 'Unknown'} - Chunk {self.id}"

    @classmethod
    def get_by_doad_number(cls, doad_number: str):
        """Get all chunks for a specific DOAD number, ordered by creation time."""
        return cls.objects.filter(doad_number=doad_number).order_by('created_at')

    @classmethod
    def get_available_doad_numbers(cls):
        """Get list of all available DOAD numbers."""
        return cls.objects.filter(
            doad_number__isnull=False
        ).values_list('doad_number', flat=True).distinct().order_by('doad_number')


class LeaveDocument(models.Model):
    """
    Model for Leave policy documents.

    Maps to the 'leave_2025' table in the shared database.
    Each record represents a chunk of leave policy documentation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text_chunk = models.TextField(help_text="Content chunk of the leave document")
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Document metadata including chapter info, etc."
    )
    created_at = models.DateTimeField(help_text="When this chunk was created")
    chapter = models.TextField(help_text="Chapter identifier for the leave document")

    class Meta:
        managed = False  # Don't let Django manage this table
        db_table = 'leave_2025'
        ordering = ['created_at']
        verbose_name = 'Leave Document'
        verbose_name_plural = 'Leave Documents'

    def __str__(self):
        return f"Leave Chapter {self.chapter} - Chunk {self.id}"

    @classmethod
    def get_by_chapter(cls, chapter: str):
        """Get all chunks for a specific chapter, ordered by creation time."""
        return cls.objects.filter(chapter=chapter).order_by('created_at')

    @classmethod
    def get_available_chapters(cls):
        """Get list of all available chapters."""
        return cls.objects.values_list('chapter', flat=True).distinct().order_by('chapter')
