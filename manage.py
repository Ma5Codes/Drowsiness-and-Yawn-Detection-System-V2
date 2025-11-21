#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Debug environment variables
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT')
    database_url = os.environ.get('DATABASE_URL')
    port = os.environ.get('PORT')
    
    print(f"🔍 Environment detection:")
    print(f"  RAILWAY_ENVIRONMENT: {railway_env}")
    print(f"  DATABASE_URL present: {bool(database_url)}")
    print(f"  PORT: {port}")
    
    # Automatically use production settings on Railway or when DATABASE_URL is present
    # Also check for PORT (Railway sets this)
    is_production = (
        railway_env is not None or 
        database_url is not None or 
        port is not None
    )
    
    if is_production:
        settings_module = 'drowsiness_project.settings_production'
        print(f"🚀 Using PRODUCTION settings: {settings_module}")
    else:
        settings_module = 'drowsiness_project.settings'
        print(f"🏠 Using DEVELOPMENT settings: {settings_module}")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
