# Windows Setup Script for DrowsiSense
# Run this in PowerShell as Administrator

Write-Host "Setting up DrowsiSense for Windows..." -ForegroundColor Green

# Check Python version
$pythonVersion = python --version
Write-Host "Python version: $pythonVersion" -ForegroundColor Cyan

# Check disk space
$disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
$freeSpaceGB = [math]::Round($disk.FreeSpace / 1GB, 2)
Write-Host "Free disk space: $freeSpaceGB GB" -ForegroundColor Cyan

if ($freeSpaceGB -lt 5) {
    Write-Host "WARNING: Low disk space! Please free up at least 5GB before continuing." -ForegroundColor Red
    Read-Host "Press Enter to continue anyway or Ctrl+C to exit"
}

# Clean pip cache
Write-Host "Cleaning pip cache..." -ForegroundColor Yellow
python -m pip cache purge

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install Visual C++ Build Tools if needed
Write-Host "Note: If installation fails, you may need Visual Studio Build Tools" -ForegroundColor Yellow
Write-Host "Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Yellow

# Install packages step by step
Write-Host "Installing core packages..." -ForegroundColor Green
python -m pip install Django==4.2.9 djangorestframework==3.14.0

Write-Host "Installing computer vision packages..." -ForegroundColor Green
python -m pip install opencv-python==4.8.1.78 mediapipe==0.10.8 Pillow==10.1.0

Write-Host "Installing remaining packages..." -ForegroundColor Green
python -m pip install -r requirements_simplified.txt

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "Run 'python manage.py runserver' to start the application" -ForegroundColor Cyan