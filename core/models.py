"""
Core app models.
"""
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
