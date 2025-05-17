"""
Django settings initialization.
Loads the appropriate settings module based on DJANGO_ENV.
"""
import os
import importlib

# Determine which settings module to use based on environment
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')

# Map environment names to settings modules
ENV_TO_SETTINGS = {
    'development': 'caf_gpt.settings.dev',
    'production': 'caf_gpt.settings.prod',
}

# Import settings from the appropriate module
settings_module = ENV_TO_SETTINGS.get(DJANGO_ENV, 'caf_gpt.settings.dev')
module = importlib.import_module(settings_module)

# Expose all settings from the loaded module
# Explicitly list the settings to expose
ALLOWED_SETTINGS = [
    'DEBUG',
    'DATABASES',
    'INSTALLED_APPS',
    'MIDDLEWARE',
    'TEMPLATES',
    'STATIC_URL',
    # Add other settings as needed
]

# Update globals with only the allowed settings
globals().update({name: getattr(module, name) for name in ALLOWED_SETTINGS if hasattr(module, name)})
