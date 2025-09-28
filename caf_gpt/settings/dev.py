"""
Development settings for caf_gpt project.
These settings extend and override base.py for the development environment.
"""
import os
from .base import (
    DEBUG,
    ALLOWED_HOSTS,
    INSTALLED_APPS,
    MIDDLEWARE,
    ROOT_URLCONF,
    TEMPLATES,
    WSGI_APPLICATION,
    DATABASES,
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key')

# Split and filter empty strings from ALLOWED_HOSTS env var, then add defaults
env_hosts = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]
ALLOWED_HOSTS = ['localhost', '127.0.0.1'] + env_hosts

# Django Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE.insert(1, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # After SecurityMiddleware
INTERNAL_IPS = ['127.0.0.1']

# Add Admin for development
if 'django.contrib.admin' not in INSTALLED_APPS:
    INSTALLED_APPS.insert(0, 'django.contrib.admin')

# Additional development-specific settings
# For example, you could disable certain security settings during development
CSP_REPORT_ONLY = True  # Report CSP violations but don't enforce in development

# Email backend for development (outputs to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
