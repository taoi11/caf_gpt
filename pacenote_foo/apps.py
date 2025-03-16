"""
PaceNoteFoo app configuration.
"""
from django.apps import AppConfig


class PacenoteFooConfig(AppConfig):
    """Configuration for the PaceNoteFoo app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pacenote_foo'
    verbose_name = 'PaceNote Foo'
