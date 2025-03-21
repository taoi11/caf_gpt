"""
Django settings initialization.
"""
import os
from .base import (
    # Import and explicitly expose settings from base
    BASE_DIR, INSTALLED_APPS, MIDDLEWARE, ROOT_URLCONF, TEMPLATES,
    DATABASES, AUTH_PASSWORD_VALIDATORS, LANGUAGE_CODE, TIME_ZONE,
    USE_I18N, USE_TZ, STATIC_URL, STATICFILES_DIRS, MEDIA_URL, MEDIA_ROOT
)

# Make all variables available at the module level
__all__ = [
    'BASE_DIR', 'INSTALLED_APPS', 'MIDDLEWARE', 'ROOT_URLCONF', 'TEMPLATES',
    'DATABASES', 'AUTH_PASSWORD_VALIDATORS', 'LANGUAGE_CODE', 'TIME_ZONE',
    'USE_I18N', 'USE_TZ', 'STATIC_URL', 'STATICFILES_DIRS', 'MEDIA_URL', 'MEDIA_ROOT',
    'DEBUG', 'SECRET_KEY', 'ALLOWED_HOSTS'
]

# Environment-specific settings
if os.getenv('DJANGO_ENV') == 'production':
    # Production settings
    DEBUG = False
    SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

    # Security settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
else:
    # Development settings
    DEBUG = True
    SECRET_KEY = 'django-insecure-+dvyb7^bme)edn!i%4-zyq&ov2+s6vrf()s6-ar9^ab6)&m@&6'
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

    # Debug toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    INTERNAL_IPS = ['127.0.0.1']
