"""
PaceNoteFoo app configuration.
"""
from django.apps import AppConfig


class PacenoteFooConfig(AppConfig):  # Renamed from PaceNoteFooConfig
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pacenote_foo'
