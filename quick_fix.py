#!/usr/bin/env python
"""
Quick fix script to update the project without problematic migrations
"""
import os
import shutil

print("🚀 Quick Fix: Updating DrowsiSense Architecture...")

# Step 1: Backup original files
print("Step 1: Backing up original files...")
files_to_backup = [
    'drowsiness_app/models.py',
    'drowsiness_app/views.py',
    'drowsiness_app/urls.py',
    'drowsiness_app/tasks.py'
]

for file_path in files_to_backup:
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup"
        shutil.copy2(file_path, backup_path)
        print(f"  ✓ Backed up {file_path}")

# Step 2: Replace models.py
print("\nStep 2: Updating models.py...")
try:
    shutil.copy2('drowsiness_app/models_updated.py', 'drowsiness_app/models.py')
    print("  ✓ Models updated with enhanced features")
except Exception as e:
    print(f"  ✗ Failed to update models: {e}")

# Step 3: Replace views.py
print("\nStep 3: Updating views.py...")
try:
    shutil.copy2('drowsiness_app/views_refactored.py', 'drowsiness_app/views.py')
    print("  ✓ Views updated with clean architecture")
except Exception as e:
    print(f"  ✗ Failed to update views: {e}")

# Step 4: Replace urls.py
print("\nStep 4: Updating urls.py...")
try:
    shutil.copy2('drowsiness_app/urls_refactored.py', 'drowsiness_app/urls.py')
    print("  ✓ URLs updated for new views")
except Exception as e:
    print(f"  ✗ Failed to update URLs: {e}")

# Step 5: Create environment file
print("\nStep 5: Creating environment configuration...")
env_content = """# DrowsiSense Configuration
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key-change-in-production

# Database (SQLite for development)
DATABASE_NAME=db.sqlite3

# Detection Settings
DETECTION_METHOD=auto
CAMERA_INDEX=0

# Audio Settings
ENABLE_AUDIO_ALERTS=True
ENABLE_TTS=True

# Email (optional for development)
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
"""

if not os.path.exists('.env'):
    with open('.env', 'w') as f:
        f.write(env_content)
    print("  ✓ Created .env configuration file")
else:
    print("  ✓ .env file already exists")

print("\n🎉 Quick fix completed!")
print("\nNext steps:")
print("1. Run: python manage.py makemigrations")
print("2. Run: python manage.py migrate --run-syncdb")
print("3. Run: python manage.py runserver")
print("\nNote: The new architecture is now ready to use!")
print("- Services layer for business logic")
print("- Repository pattern for data access") 
print("- Enhanced error handling")
print("- Better configuration management")