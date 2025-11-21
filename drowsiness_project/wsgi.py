"""
WSGI config for drowsiness_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Automatically use production settings on Railway or when DATABASE_URL is present
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('DATABASE_URL'):
    settings_module = 'drowsiness_project.settings_production'
else:
    settings_module = 'drowsiness_project.settings'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()
