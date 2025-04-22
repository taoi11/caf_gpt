"""
Base settings for caf_gpt project.
Contains common settings for all environments.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
from django.urls import reverse_lazy
from django.conf import settings # Import settings

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'core.apps.CoreConfig',
    'pacenote_foo.apps.PacenoteFooConfig',
    'policy_foo.apps.PolicyFooConfig',

    # Third-party apps
    'csp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
]

ROOT_URLCONF = 'caf_gpt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.cost_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'caf_gpt.wsgi.application'

# Database configuration for Neon DB
tmpPostgres = urlparse(os.getenv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/caf_gpt"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': tmpPostgres.path.replace('/', ''),
        'USER': tmpPostgres.username,
        'PASSWORD': tmpPostgres.password,
        'HOST': tmpPostgres.hostname,
        'PORT': 5432,
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Static files settings
STATIC_URL = '/static/'

# Define STATIC_ROOT for collectstatic
# This is where static files will be collected by collectstatic
# Django automatically finds static files within each app's 'static/' directory
# when APP_DIRS is True in TEMPLATES. STATICFILES_DIRS is not needed here.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Use WhiteNoise's storage backend for optimal performance (caching, compression)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Content Security Policy (CSP) settings
# --------------------------------------------------------------------------
CSP_REPORT_ONLY = False

# Most restrictive baseline - only allow resources from same origin
CSP_DEFAULT_SRC = ("'self'",)

# JavaScript restrictions
CSP_SCRIPT_SRC = ("'self'",)
CSP_SCRIPT_SRC_ELEM = ("'self'",)

# If you're using Django's admin or forms, you might need this
# If not, you can remove unsafe-inline completely
CSP_STYLE_SRC = ("'self'",)
CSP_STYLE_SRC_ELEM = ("'self'",)

# Since you said no images, let's restrict this
CSP_IMG_SRC = ("'self'",)

# You probably don't need these if it's just text
CSP_FONT_SRC = ("'none'",)  # Block external fonts

# These are good restrictions to keep
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)  # Prevent framing
CSP_FORM_ACTION = ("'self'",)
CSP_BASE_URI = ("'self'",)
CSP_OBJECT_SRC = ("'none'",)

# Keep your report endpoint
# Note: The URL pattern 'csp-report/' is defined in the root urls.py (caf_gpt/urls.py)
# and its name is 'csp_report_view'.
CSP_REPORT_URI = reverse_lazy('csp_report_view')

# The nonces feature is good if you have any inline scripts or styles
CSP_INCLUDE_NONCE_IN = ['script-src', 'style-src']
# --------------------------------------------------------------------------

# Security settings
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
