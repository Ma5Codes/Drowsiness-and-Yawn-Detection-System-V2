"""
Refactored Views - Clean, service-oriented architecture
"""
import logging
import asyncio
from typing import Dict, Any

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_http_methods
from asgiref.sync import async_to_sync

from .forms import CustomUserCreationForm
from .services.user_service import user_service
from .services.detection_service import detection_service
from .services.alert_service import alert_service
from .core.detection_engine import create_detection_engine
from .core.exceptions import ValidationError, DetectionError, CameraError


logger = logging.getLogger(__name__)


def home(request):
    """Home page view"""
    context = {
        "app_name": "DrowsiSense",
        "year": 2025,
        "version": "2.0",
    }
    return render(request, "index_modern.html", context)


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('driver_dashboard')

    if request.method == 'POST':
        email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            return render(request, 'login.html')
        
        try:
            # Use service for authentication
            user = async_to_sync(user_service.authenticate_user)(email, password)
            
            if user:
                login(request, user)
                messages.success(request, 'Login successful!')
                logger.info(f"User logged in successfully: {email}")
                return redirect('driver_dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
                logger.warning(f"Failed login attempt for: {email}")
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            messages.error(request, 'An error occurred during login. Please try again.')

    return render(request, 'login_modern.html')


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('driver_dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            try:
                # Extract form data
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password1')
                first_name = form.cleaned_data.get('first_name', '')
                last_name = form.cleaned_data.get('last_name', '')
                
                # Use service to create user with profile
                result = async_to_sync(user_service.create_user_with_profile)(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    license_number="",  # Will be set to default
                    phone_number=""
                )
                
                if result.get('success'):
                    # Authenticate and login the new user
                    user = async_to_sync(user_service.authenticate_user)(email, password)
                    if user:
                        login(request, user)
                        messages.success(request, 'Registration successful! Please update your profile.')
                        logger.info(f"New user registered: {email}")
                        return redirect('driver_dashboard')
                
            except ValidationError as e:
                messages.error(request, f'Registration failed: {str(e)}')
                logger.error(f"Registration validation error: {e}")
            except Exception as e:
                messages.error(request, 'Registration failed. Please try again.')
                logger.error(f"Registration error: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register_modern.html', {'form': form})


@login_required
def driver_dashboard(request):
    """Driver dashboard view"""
    try:
        # Get driver profile using service
        driver_profile = async_to_sync(user_service.get_driver_profile)(request.user)
        if not driver_profile:
            messages.error(request, 'Driver profile not found. Please contact support.')
            return redirect('home')
        
        # Get user settings
        user_settings = async_to_sync(user_service.get_or_create_user_settings)(request.user)
        
        # Get recent alerts
        alerts = async_to_sync(alert_service.get_driver_alerts)(driver_profile, limit=10)
        
        # Get alert statistics
        alert_stats = async_to_sync(alert_service.get_alert_statistics)(driver_profile, days=7)
        
        # Get monitoring status
        monitoring_status = detection_service.get_monitoring_status()
        
        context = {
            "driver_profile": driver_profile,
            "user_settings": user_settings,
            "alerts": alerts,
            "alert_stats": alert_stats,
            "monitoring_status": monitoring_status,
        }
        
        logger.info(f"Dashboard accessed by: {request.user.email}")
        return render(request, "driver_dashboard_modern.html", context)
        
    except Exception as e:
        logger.error(f"Dashboard error for {request.user.email}: {e}")
        messages.error(request, 'Error loading dashboard. Please try again.')
        return render(request, "driver_dashboard.html", {"alerts": []})


@login_required
@csrf_protect
@require_http_methods(["POST"])
def update_settings(request):
    """Update user settings"""
    try:
        # Extract and validate settings
        ear_threshold = float(request.POST.get("ear_threshold", 0.3))
        ear_frames = int(request.POST.get("ear_frames", 30))
        yawn_threshold = int(request.POST.get("yawn_threshold", 20))
        alert_frequency = request.POST.get("alert_frequency", "medium")
        
        # Validate ranges
        if not (0.1 <= ear_threshold <= 0.8):
            messages.error(request, 'EAR threshold must be between 0.1 and 0.8')
            return redirect("driver_dashboard")
        
        if not (5 <= ear_frames <= 100):
            messages.error(request, 'EAR frames must be between 5 and 100')
            return redirect("driver_dashboard")
        
        if not (5 <= yawn_threshold <= 50):
            messages.error(request, 'Yawn threshold must be between 5 and 50')
            return redirect("driver_dashboard")
        
        # Update settings using service
        success = async_to_sync(user_service.update_user_settings)(
            user=request.user,
            ear_threshold=ear_threshold,
            ear_frames=ear_frames,
            yawn_threshold=yawn_threshold,
            alert_frequency=alert_frequency
        )
        
        if success:
            messages.success(request, 'Settings updated successfully!')
            logger.info(f"Settings updated for: {request.user.email}")
        else:
            messages.error(request, 'Failed to update settings.')
            
    except (ValueError, TypeError) as e:
        messages.error(request, 'Invalid input values. Please check your settings.')
        logger.error(f"Settings validation error: {e}")
    except ValidationError as e:
        messages.error(request, f'Validation error: {str(e)}')
    except Exception as e:
        messages.error(request, 'An error occurred while updating settings.')
        logger.error(f"Settings update error: {e}")

    return redirect("driver_dashboard")


@login_required
@csrf_protect
@require_http_methods(["POST"])
def update_profile(request):
    """Update driver profile"""
    try:
        license_number = request.POST.get("license_number", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        
        # Basic validation
        if license_number and len(license_number) < 3:
            messages.error(request, 'License number must be at least 3 characters long.')
            return redirect("driver_dashboard")
        
        # Update profile using service
        success = async_to_sync(user_service.update_driver_profile)(
            user=request.user,
            license_number=license_number,
            phone_number=phone_number
        )
        
        if success:
            messages.success(request, 'Profile updated successfully!')
            logger.info(f"Profile updated for: {request.user.email}")
        else:
            messages.error(request, 'Failed to update profile.')
            
    except ValidationError as e:
        messages.error(request, f'Validation error: {str(e)}')
    except Exception as e:
        messages.error(request, 'An error occurred while updating profile.')
        logger.error(f"Profile update error: {e}")

    return redirect("driver_dashboard")


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def toggle_monitoring(request):
    """Toggle drowsiness monitoring"""
    try:
        action = request.POST.get("action", "").lower()
        
        if action == "start":
            return async_to_sync(_start_monitoring)(request)
        elif action == "stop":
            return async_to_sync(_stop_monitoring)(request)
        else:
            return JsonResponse({
                "success": False,
                "message": "Invalid action. Use 'start' or 'stop'."
            }, status=400)
            
    except Exception as e:
        logger.error(f"Monitoring toggle error: {e}")
        return JsonResponse({
            "success": False,
            "message": "An error occurred while toggling monitoring."
        }, status=500)


async def _start_monitoring(request):
    """Start monitoring process"""
    try:
        # Get user data
        driver_profile = await user_service.get_driver_profile(request.user)
        if not driver_profile:
            return JsonResponse({
                "success": False,
                "message": "Driver profile not found."
            }, status=400)
        
        user_settings = await user_service.get_or_create_user_settings(request.user)
        
        # Validate camera availability
        try:
            await detection_service.validate_camera(user_settings.camera_index)
        except CameraError as e:
            return JsonResponse({
                "success": False,
                "message": f"Camera error: {str(e)}"
            }, status=400)
        
        # Prepare configuration
        config = {
            'camera_index': user_settings.camera_index,
            'ear_threshold': user_settings.ear_threshold,
            'ear_frames': user_settings.ear_frames,
            'yawn_threshold': user_settings.yawn_threshold,
            'driver_profile': driver_profile,
            'user_settings': user_settings.get_detection_config()
        }
        
        # Start monitoring
        success = await detection_service.start_monitoring(config)
        
        if success:
            # Create and start detection engine in background
            detection_engine = create_detection_engine()
            await detection_engine.initialize(config)
            
            # Store task reference in session
            task = asyncio.create_task(detection_engine.start_monitoring(
                driver_profile, 
                user_settings.get_detection_config()
            ))
            request.session['monitoring_task_id'] = id(task)
            
            logger.info(f"Monitoring started for: {request.user.email}")
            
            return JsonResponse({
                "success": True,
                "action": "start",
                "message": "Monitoring started successfully."
            })
        else:
            return JsonResponse({
                "success": False,
                "message": "Failed to start monitoring."
            }, status=500)
            
    except DetectionError as e:
        return JsonResponse({
            "success": False,
            "message": f"Detection error: {str(e)}"
        }, status=500)
    except Exception as e:
        logger.error(f"Start monitoring error: {e}")
        return JsonResponse({
            "success": False,
            "message": "Failed to start monitoring."
        }, status=500)


async def _stop_monitoring(request):
    """Stop monitoring process"""
    try:
        success = await detection_service.stop_monitoring()
        
        # Clear session task reference
        if 'monitoring_task_id' in request.session:
            del request.session['monitoring_task_id']
        
        if success:
            logger.info(f"Monitoring stopped for: {request.user.email}")
            return JsonResponse({
                "success": True,
                "action": "stop",
                "message": "Monitoring stopped successfully."
            })
        else:
            return JsonResponse({
                "success": False,
                "message": "Failed to stop monitoring."
            }, status=500)
            
    except Exception as e:
        logger.error(f"Stop monitoring error: {e}")
        return JsonResponse({
            "success": False,
            "message": "Failed to stop monitoring."
        }, status=500)


@login_required
def get_monitoring_status(request):
    """Get current monitoring status"""
    try:
        status = detection_service.get_monitoring_status()
        return JsonResponse({
            "success": True,
            "status": status
        })
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return JsonResponse({
            "success": False,
            "message": "Failed to get monitoring status."
        }, status=500)


def logout_view(request):
    """User logout view"""
    email = request.user.email if request.user.is_authenticated else "Unknown"
    logout(request)
    messages.success(request, "Logout successful!")
    logger.info(f"User logged out: {email}")
    return redirect("home")