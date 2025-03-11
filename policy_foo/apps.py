"""
PolicyFoo app configuration.
"""
from django.apps import AppConfig


class PolicyFooConfig(AppConfig):
    """Configuration for the PolicyFoo app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'policy_foo'
    verbose_name = 'Policy Foo' 