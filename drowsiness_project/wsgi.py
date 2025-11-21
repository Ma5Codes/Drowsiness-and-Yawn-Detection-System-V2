"""
WSGI config for drowsiness_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Automatically use production settings on Railway or when DATABASE_URL is present
# Also check for PORT (Railway sets this)
railway_env = os.environ.get('RAILWAY_ENVIRONMENT')
database_url = os.environ.get('DATABASE_URL')
port = os.environ.get('PORT')

is_production = (
    railway_env is not None or 
    database_url is not None or 
    port is not None
)

if is_production:
    settings_module = 'drowsiness_project.settings_production'
    print(f"🚀 WSGI using PRODUCTION settings: {settings_module}")
else:
    settings_module = 'drowsiness_project.settings'
    print(f"🏠 WSGI using DEVELOPMENT settings: {settings_module}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()
