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
globals().update({name: getattr(module, name) for name in dir(module) if not name.startswith('_')})
