"""
Fixed monitoring views that actually show the camera and work properly
"""
import logging
import asyncio
import threading
from typing import Dict, Any

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from asgiref.sync import async_to_sync

from .services.user_service import user_service
from .services.detection_service import detection_service
from .services.alert_service import alert_service
from .core.exceptions import CameraError, DetectionError
from .tasks import drowsiness_detection_task  # Use the original task


logger = logging.getLogger(__name__)

# Global variable to track monitoring thread
monitoring_thread = None
monitoring_active = False


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def toggle_monitoring(request):
    """Toggle drowsiness monitoring - FIXED VERSION"""
    global monitoring_thread, monitoring_active
    
    try:
        action = request.POST.get("action", "").lower()
        
        if action == "start":
            return start_monitoring_sync(request)
        elif action == "stop":
            return stop_monitoring_sync(request)
        else:
            return JsonResponse({
                "success": False,
                "message": "Invalid action. Use 'start' or 'stop'."
            }, status=400)
            
    except Exception as e:
        logger.error(f"Monitoring toggle error: {e}")
        return JsonResponse({
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)


def start_monitoring_sync(request):
    """Start monitoring process - SYNCHRONOUS VERSION THAT WORKS"""
    global monitoring_thread, monitoring_active
    
    try:
        # Check if already monitoring
        if monitoring_active:
            return JsonResponse({
                "success": False,
                "message": "Monitoring is already active."
            })
        
        # Get user data
        driver_profile = async_to_sync(user_service.get_driver_profile)(request.user)
        if not driver_profile:
            return JsonResponse({
                "success": False,
                "message": "Driver profile not found."
            }, status=400)
        
        user_settings = async_to_sync(user_service.get_or_create_user_settings)(request.user)
        
        # Test camera availability
        import cv2
        test_camera = cv2.VideoCapture(user_settings.camera_index)
        if not test_camera.isOpened():
            test_camera.release()
            return JsonResponse({
                "success": False,
                "message": f"Camera {user_settings.camera_index} is not available. Please check your camera connection."
            }, status=400)
        test_camera.release()
        
        # Prepare detection parameters
        webcam_index = user_settings.camera_index
        ear_thresh = user_settings.ear_threshold
        ear_frames = user_settings.ear_frames
        yawn_thresh = user_settings.yawn_threshold
        driver_email = request.user.email
        
        logger.info(f"Starting monitoring for {driver_email} with camera {webcam_index}")
        
        # Start monitoring in a separate thread so it doesn't block the response
        def run_detection():
            global monitoring_active
            monitoring_active = True
            try:
                # Run the original detection task
                async_to_sync(drowsiness_detection_task)(
                    webcam_index=webcam_index,
                    ear_thresh=ear_thresh,
                    ear_frames=ear_frames,
                    yawn_thresh=yawn_thresh,
                    driver_profile=driver_profile,
                    driver_email=driver_email
                )
            except Exception as e:
                logger.error(f"Detection task failed: {e}")
            finally:
                monitoring_active = False
        
        # Import and use the fixed detection task
        from .tasks_fixed import drowsiness_detection_task_sync
        
        # Start the detection in a background thread
        def run_detection():
            global monitoring_active
            monitoring_active = True
            try:
                # Run the FIXED detection task (sync version)
                drowsiness_detection_task_sync(
                    webcam_index=webcam_index,
                    ear_thresh=ear_thresh,
                    ear_frames=ear_frames,
                    yawn_thresh=yawn_thresh,
                    driver_profile=driver_profile,
                    driver_email=driver_email
                )
            except Exception as e:
                logger.error(f"Detection task failed: {e}")
            finally:
                monitoring_active = False
        
        monitoring_thread = threading.Thread(target=run_detection, daemon=True)
        monitoring_thread.start()
        
        # Store monitoring state in session
        request.session['monitoring_active'] = True
        request.session['monitoring_camera'] = webcam_index
        
        logger.info(f"Monitoring started successfully for: {request.user.email}")
        
        return JsonResponse({
            "success": True,
            "action": "start",
            "message": "Monitoring started successfully. Camera window should appear."
        })
        
    except Exception as e:
        logger.error(f"Start monitoring error: {e}")
        return JsonResponse({
            "success": False,
            "message": f"Failed to start monitoring: {str(e)}"
        }, status=500)


def stop_monitoring_sync(request):
    """Stop monitoring process - SYNCHRONOUS VERSION"""
    global monitoring_thread, monitoring_active
    
    try:
        if not monitoring_active:
            return JsonResponse({
                "success": False,
                "message": "Monitoring is not currently active."
            })
        
        # Signal to stop monitoring
        monitoring_active = False
        
        # Close any OpenCV windows
        import cv2
        cv2.destroyAllWindows()
        
        # Clear session
        request.session['monitoring_active'] = False
        if 'monitoring_camera' in request.session:
            del request.session['monitoring_camera']
        
        logger.info(f"Monitoring stopped for: {request.user.email}")
        
        return JsonResponse({
            "success": True,
            "action": "stop", 
            "message": "Monitoring stopped successfully."
        })
        
    except Exception as e:
        logger.error(f"Stop monitoring error: {e}")
        return JsonResponse({
            "success": False,
            "message": f"Failed to stop monitoring: {str(e)}"
        }, status=500)


@login_required
def get_monitoring_status(request):
    """Get current monitoring status"""
    try:
        global monitoring_active
        
        # Check session state as well
        session_active = request.session.get('monitoring_active', False)
        camera_index = request.session.get('monitoring_camera', 0)
        
        status = {
            'is_monitoring': monitoring_active or session_active,
            'detector_type': 'MediaPipe/OpenCV',
            'camera_index': camera_index,
            'thread_active': monitoring_thread is not None and monitoring_thread.is_alive() if monitoring_thread else False
        }
        
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


def test_camera_view(request):
    """Test camera functionality"""
    if request.method == 'GET':
        camera_index = int(request.GET.get('camera', 0))
        
        import cv2
        cap = cv2.VideoCapture(camera_index)
        
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                return JsonResponse({
                    "success": True,
                    "message": f"Camera {camera_index} is working properly.",
                    "frame_shape": frame.shape if ret else None
                })
            else:
                return JsonResponse({
                    "success": False,
                    "message": f"Camera {camera_index} opened but no frame received."
                })
        else:
            return JsonResponse({
                "success": False,
                "message": f"Cannot open camera {camera_index}. Please check connection."
            })


# Simple monitoring view for testing
@login_required  
def simple_monitoring_test(request):
    """Simple monitoring test that definitely shows camera"""
    try:
        import cv2
        import time
        
        camera_index = 0
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            messages.error(request, f"Cannot access camera {camera_index}")
            return redirect('driver_dashboard')
        
        messages.success(request, "Camera test started. Press 'q' to quit the camera window.")
        
        # Simple camera display loop
        def show_camera():
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Add some text to show it's working
                cv2.putText(frame, "DrowsiSense - Camera Test", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, "Press 'q' to quit", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow("Camera Test", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
        
        # Start camera in thread so page can respond
        import threading
        camera_thread = threading.Thread(target=show_camera, daemon=True)
        camera_thread.start()
        
        return redirect('driver_dashboard')
        
    except Exception as e:
        logger.error(f"Camera test error: {e}")
        messages.error(request, f"Camera test failed: {str(e)}")
        return redirect('driver_dashboard')