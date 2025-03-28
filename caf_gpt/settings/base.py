"""
Base settings for caf_gpt project.
Contains common settings for all environments.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
from django.urls import reverse_lazy

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
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
STATICFILES_DIRS = []  # Static files are in app sub directories
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Content Security Policy (CSP) settings
# --------------------------------------------------------------------------
CSP_REPORT_ONLY = True  # Still in report-only mode for testing

CSP_DEFAULT_SRC = ("'self'",)

CSP_SCRIPT_SRC = ("'self'",)

CSP_SCRIPT_SRC_ELEM = ("'self'",)

CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",  # Allow inline styles if needed
)

CSP_STYLE_SRC_ELEM = (
    "'self'",
    "'unsafe-inline'",  # Allow inline styles if needed
)

CSP_IMG_SRC = ("'self'", 'data:')  # Allow self-hosted images and data URIs
CSP_FONT_SRC = ("'self'", "data:")  # Allow local fonts and data URIs
CSP_CONNECT_SRC = ("'self'",)  # Allow fetch/XHR/WebSockets to the same origin
CSP_FRAME_ANCESTORS = ("'none'",)  # Disallow embedding in iframes
CSP_FORM_ACTION = ("'self'",)  # Allow forms to submit to the same origin
CSP_BASE_URI = ("'self'",)
CSP_OBJECT_SRC = ("'none'",)  # Disallow <object>, <embed>, <applet>

# Send violation reports to this endpoint (requires URL configuration)
CSP_REPORT_URI = reverse_lazy('csp_report_view')

# Automatically add nonces to script and style tags for inline code safety
CSP_INCLUDE_NONCE_IN = ['script-src', 'style-src']
# --------------------------------------------------------------------------
