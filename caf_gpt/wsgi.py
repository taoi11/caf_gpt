"""
WSGI config for caf_gpt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise  # Add this import

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'caf_gpt.settings')

application = get_wsgi_application()
application = WhiteNoise(application)  # Wrap the application
