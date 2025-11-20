# Windows Installation Troubleshooting Guide

## Common Installation Issues

### 1. "No space left on device" Error

**Problem:** Disk space issue when installing large packages like dlib or face-recognition.

**Solutions:**
```bash
# Clean up system
# 1. Run Disk Cleanup
cleanmgr

# 2. Clear pip cache
pip cache purge

# 3. Clear temp files
del /q /f %TEMP%\*

# 4. Use simplified requirements
pip install -r requirements_simplified.txt
```

### 2. "Cannot import 'setuptools.build_meta'" Error

**Problem:** Missing or corrupt build tools.

**Solutions:**
```bash
# Update setuptools
pip install --upgrade setuptools wheel pip

# Or reinstall
pip uninstall setuptools
pip install setuptools

# Install Visual C++ Build Tools if needed
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### 3. dlib Installation Fails

**Problem:** dlib requires C++ compilation which often fails on Windows.

**Solution:** Use MediaPipe instead (already implemented in the code):
```bash
# Skip dlib entirely
pip install mediapipe opencv-python
```

### 4. Camera Permission Issues

**Problem:** Webcam access denied or not working.

**Solutions:**
1. **Check Windows Privacy Settings:**
   - Go to Settings → Privacy → Camera
   - Enable "Allow apps to access your camera"

2. **Check Antivirus:**
   - Temporarily disable antivirus camera protection
   - Add Python to antivirus exceptions

3. **Test Camera:**
   ```python
   import cv2
   cap = cv2.VideoCapture(0)
   print(f"Camera opened: {cap.isOpened()}")
   cap.release()
   ```

### 5. Audio/TTS Issues

**Problem:** pygame or pyttsx3 not working.

**Solutions:**
```bash
# For Windows TTS
pip install pyttsx3

# Test audio
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Test'); engine.runAndWait()"
```

## Step-by-Step Windows Setup

### Method 1: Automated Script (Recommended)
```bash
# Run as Administrator
install_windows.bat
```

### Method 2: Manual Installation
```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install simplified requirements
pip install -r requirements_simplified.txt

# 3. Setup database (SQLite by default)
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Run server
python manage.py runserver
```

## Environment Configuration

Create `.env` file:
```env
# Basic configuration for development
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True

# Use SQLite for development (no PostgreSQL needed)
DATABASE_URL=sqlite:///db.sqlite3

# Email settings (optional for development)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Performance Optimization

### For Low-End Systems:
```python
# In settings.py, reduce video quality
CAMERA_SETTINGS = {
    'width': 480,
    'height': 360,
    'fps': 15
}
```

### For Better Performance:
1. Close unnecessary applications
2. Use wired internet connection
3. Ensure good lighting for camera
4. Use external USB camera if laptop camera is poor

## Alternative Detection Methods

### If dlib fails:
The code automatically falls back to:
1. **MediaPipe** (recommended for Windows)
2. **Basic OpenCV** (minimal features)

### Manual selection:
```python
# In detection_factory.py, force a specific detector
def get_detector():
    from .mediapipe_detection import MediaPipeDrowsinessDetector
    return MediaPipeDrowsinessDetector()
```

## Testing the Installation

### Quick Test Script:
```python
# test_installation.py
import cv2
import numpy as np

try:
    import mediapipe
    print("✓ MediaPipe available")
except ImportError:
    print("✗ MediaPipe not available")

try:
    import pygame
    print("✓ Pygame available")
except ImportError:
    print("✗ Pygame not available")

# Test camera
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("✓ Camera accessible")
    cap.release()
else:
    print("✗ Camera not accessible")

print("Installation test complete!")
```

## Common Runtime Issues

### 1. "Module not found" errors
```bash
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall missing packages
pip install package_name
```

### 2. Camera not detected
```bash
# List available cameras
python -c "import cv2; print([cv2.VideoCapture(i).isOpened() for i in range(5)])"
```

### 3. Permission errors
```bash
# Run as Administrator if needed
# Or check file permissions in project directory
```

## Getting Help

1. **Check logs:** Look for error messages in terminal
2. **Test components:** Use the test script above
3. **Simplified mode:** Use basic_detection.py if advanced features fail
4. **Community:** Check Django and OpenCV documentation

## Hardware Requirements

**Minimum:**
- 4GB RAM
- 2GB free disk space
- Webcam
- Windows 10 or later

**Recommended:**
- 8GB RAM
- 5GB free disk space
- USB webcam with good resolution
- Good lighting conditions