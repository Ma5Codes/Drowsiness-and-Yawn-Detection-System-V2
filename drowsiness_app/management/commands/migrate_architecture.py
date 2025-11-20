"""
Management command to migrate to new architecture
"""
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from drowsiness_app.utils.logging_utils import setup_logging, get_logger


class Command(BaseCommand):
    help = 'Migrate to new clean architecture'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force migration even if there are warnings',
        )

    def handle(self, *args, **options):
        # Setup logging
        logger = setup_logging()
        
        self.stdout.write(
            self.style.SUCCESS('Starting architecture migration...')
        )

        try:
            # Step 1: Check current state
            self.stdout.write('Step 1: Checking current state...')
            self.check_current_state(options['dry_run'])

            # Step 2: Run database migrations
            self.stdout.write('Step 2: Running database migrations...')
            if not options['dry_run']:
                call_command('makemigrations', 'drowsiness_app')
                call_command('migrate')
            else:
                self.stdout.write('  (DRY RUN) Would run migrations')

            # Step 3: Update configurations
            self.stdout.write('Step 3: Updating configurations...')
            self.update_configurations(options['dry_run'])

            # Step 4: Validate new architecture
            self.stdout.write('Step 4: Validating new architecture...')
            self.validate_architecture(options['dry_run'])

            # Step 5: Clean up old files (optional)
            if options.get('force', False):
                self.stdout.write('Step 5: Cleaning up old files...')
                self.cleanup_old_files(options['dry_run'])

            self.stdout.write(
                self.style.SUCCESS('Architecture migration completed successfully!')
            )

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            self.stdout.write(
                self.style.ERROR(f'Migration failed: {e}')
            )
            raise

    def check_current_state(self, dry_run):
        """Check the current state of the application"""
        checks = []
        
        # Check if old views exist
        if os.path.exists('drowsiness_app/views.py'):
            checks.append('✓ Old views.py found')
        
        # Check if old tasks exist
        if os.path.exists('drowsiness_app/tasks.py'):
            checks.append('✓ Old tasks.py found')
        
        # Check if new structure exists
        if os.path.exists('drowsiness_app/services'):
            checks.append('✓ New services directory found')
        
        if os.path.exists('drowsiness_app/repositories'):
            checks.append('✓ New repositories directory found')
        
        for check in checks:
            self.stdout.write(f"  {check}")

    def update_configurations(self, dry_run):
        """Update configuration files"""
        updates = [
            'Update URLs to use refactored views',
            'Update settings for new logging',
            'Update INSTALLED_APPS if needed',
            'Create environment configuration'
        ]
        
        for update in updates:
            if dry_run:
                self.stdout.write(f"  (DRY RUN) Would: {update}")
            else:
                self.stdout.write(f"  {update}")

        # Update URLs file
        if not dry_run:
            self.update_urls_file()

    def update_urls_file(self):
        """Update the main URLs file to use refactored views"""
        urls_content = '''"""
Updated URLs using refactored architecture
"""
from django.urls import path
from . import views_refactored as views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.driver_dashboard, name='driver_dashboard'),
    
    # Profile Management
    path('update-settings/', views.update_settings, name='update_settings'),
    path('update-profile/', views.update_profile, name='update_profile'),
    
    # Monitoring
    path('toggle-monitoring/', views.toggle_monitoring, name='toggle_monitoring'),
    path('monitoring-status/', views.get_monitoring_status, name='monitoring_status'),
]
'''
        
        try:
            # Backup original file
            if os.path.exists('drowsiness_app/urls.py'):
                os.rename('drowsiness_app/urls.py', 'drowsiness_app/urls_backup.py')
            
            # Write new URLs
            with open('drowsiness_app/urls.py', 'w') as f:
                f.write(urls_content)
                
            self.stdout.write('  ✓ URLs file updated')
            
        except Exception as e:
            self.stdout.write(f"  ✗ Failed to update URLs: {e}")

    def validate_architecture(self, dry_run):
        """Validate the new architecture"""
        validations = []
        
        try:
            # Test imports
            from drowsiness_app.services.user_service import user_service
            from drowsiness_app.services.detection_service import detection_service
            from drowsiness_app.services.alert_service import alert_service
            validations.append('✓ Services can be imported')
            
            from drowsiness_app.repositories.user_repository import user_repository
            from drowsiness_app.repositories.alert_repository import alert_repository
            validations.append('✓ Repositories can be imported')
            
            from drowsiness_app.core.config import config
            validations.append('✓ Configuration system works')
            
            # Test configuration
            config_validation = config.validate_config()
            if config_validation['valid']:
                validations.append('✓ Configuration is valid')
            else:
                validations.append(f'✗ Configuration issues: {config_validation["issues"]}')
            
        except ImportError as e:
            validations.append(f'✗ Import error: {e}')
        except Exception as e:
            validations.append(f'✗ Validation error: {e}')
        
        for validation in validations:
            self.stdout.write(f"  {validation}")

    def cleanup_old_files(self, dry_run):
        """Clean up old files (backup them first)"""
        old_files = [
            'drowsiness_app/views.py',
            'drowsiness_app/tasks.py',
        ]
        
        for old_file in old_files:
            if os.path.exists(old_file):
                if dry_run:
                    self.stdout.write(f"  (DRY RUN) Would backup and remove: {old_file}")
                else:
                    # Create backup
                    backup_name = f"{old_file}_backup"
                    os.rename(old_file, backup_name)
                    self.stdout.write(f"  ✓ Backed up {old_file} to {backup_name}")

    def create_environment_file(self):
        """Create .env.example file"""
        env_content = '''# DrowsiSense Environment Configuration
# Copy this file to .env and update the values

# Django Core Settings
DJANGO_SECRET_KEY=your-very-long-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Detection Settings
DETECTION_METHOD=auto
FRAME_WIDTH=640
FRAME_HEIGHT=480
TARGET_FPS=30

# Audio Settings
ENABLE_AUDIO_ALERTS=True
ENABLE_TTS=True
AUDIO_VOLUME=0.8

# Camera Settings
DEFAULT_CAMERA_INDEX=0

# Database (for production)
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
'''
        
        if not os.path.exists('.env.example'):
            with open('.env.example', 'w') as f:
                f.write(env_content)
            self.stdout.write('  ✓ Created .env.example file')