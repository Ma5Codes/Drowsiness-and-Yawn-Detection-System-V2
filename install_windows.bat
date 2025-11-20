@echo off
echo Setting up DrowsiSense for Windows...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

:: Check available disk space
for /f "tokens=3" %%i in ('dir C:\ ^| findstr "bytes free"') do set freespace=%%i
echo Free disk space: %freespace% bytes

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

:: Clear pip cache to save space
echo Cleaning pip cache...
python -m pip cache purge

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install packages step by step to avoid memory issues
echo Installing core Django packages...
python -m pip install Django==4.2.9 djangorestframework==3.14.0 django-crispy-forms==2.1 django-environ==0.11.2

echo Installing database packages...
python -m pip install dj-database-url==2.1.0

echo Installing async/WebSocket packages...
python -m pip install channels==4.0.0 channels-redis==4.2.0 django-redis==5.4.0

echo Installing computer vision packages...
python -m pip install opencv-python==4.8.1.78 mediapipe==0.10.8 Pillow==10.1.0

echo Installing audio packages...
python -m pip install pygame==2.5.2

echo Installing utility packages...
python -m pip install numpy==1.24.4 requests==2.31.0 python-dotenv==1.0.0

echo Installing text-to-speech (optional)...
python -m pip install pyttsx3

echo Installing production packages...
python -m pip install gunicorn==21.2.0 whitenoise==6.6.0

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Copy .env.example to .env and configure your settings
echo 2. Run: python manage.py migrate
echo 3. Run: python manage.py createsuperuser
echo 4. Run: python manage.py runserver
echo.
pause