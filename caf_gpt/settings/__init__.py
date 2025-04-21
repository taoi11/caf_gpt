"""
Django settings initialization.
"""
import os
from .base import (
    # Import and explicitly expose settings from base
    BASE_DIR, INSTALLED_APPS as BASE_INSTALLED_APPS, MIDDLEWARE as BASE_MIDDLEWARE, ROOT_URLCONF, TEMPLATES,
    DATABASES, AUTH_PASSWORD_VALIDATORS, LANGUAGE_CODE, TIME_ZONE,
    USE_I18N, USE_TZ, STATIC_URL, MEDIA_URL, MEDIA_ROOT, STATIC_ROOT # Add STATIC_ROOT, removed STATICFILES_DIRS
)

# Start with base lists
INSTALLED_APPS = list(BASE_INSTALLED_APPS)
MIDDLEWARE = list(BASE_MIDDLEWARE)

# Environment-specific settings
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development') # Default to development

if DJANGO_ENV == 'production':
    # Production settings
    DEBUG = False
    SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
    # Split and filter empty strings from ALLOWED_HOSTS
    ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]
    # Ensure admin is not included in production INSTALLED_APPS
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django.contrib.admin']

    # Security settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    # Add other production-specific settings like logging, caching etc.

else:
    # Development settings (or any environment other than 'production')
    DEBUG = True
    SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key') # Provide a default dev key
    # Split and filter empty strings from ALLOWED_HOSTS env var, then add defaults
    env_hosts = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]
    ALLOWED_HOSTS = ['localhost', '127.0.0.1'] + env_hosts

    # Add admin and debug toolbar for development
    if 'django.contrib.admin' not in INSTALLED_APPS:
         INSTALLED_APPS.insert(0, 'django.contrib.admin') # Add admin if not already present
    if 'debug_toolbar' not in INSTALLED_APPS:
        INSTALLED_APPS += ['debug_toolbar']
    if 'debug_toolbar.middleware.DebugToolbarMiddleware' not in MIDDLEWARE:
        # Ensure middleware order is correct: Debug Toolbar typically comes early
        try:
            # Insert after SecurityMiddleware if present
            security_middleware_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
            MIDDLEWARE.insert(security_middleware_index + 1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        except ValueError:
             # Insert at the beginning if SecurityMiddleware is not found
            MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

    INTERNAL_IPS = ['127.0.0.1']
