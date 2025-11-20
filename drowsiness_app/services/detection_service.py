"""
Detection Service - Handles all drowsiness detection business logic
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from django.conf import settings

from ..core.exceptions import DetectionError, CameraError, ModelLoadError
from ..detection_factory import get_detector


logger = logging.getLogger(__name__)


class DetectionService:
    """
    Service class to handle drowsiness detection operations
    """
    
    def __init__(self):
        self.detector = None
        self.is_monitoring = False
        self.current_task = None
    
    async def initialize_detector(self) -> bool:
        """
        Initialize the detection system
        Returns: True if successful, False otherwise
        """
        try:
            self.detector = get_detector()
            if self.detector is None:
                raise ModelLoadError("No detection system available")
            logger.info(f"Detector initialized: {type(self.detector).__name__}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize detector: {e}")
            raise ModelLoadError(f"Failed to initialize detector: {e}")
    
    async def start_monitoring(self, config: Dict[str, Any]) -> bool:
        """
        Start drowsiness monitoring
        Args:
            config: Dictionary containing monitoring configuration
        Returns: True if started successfully
        """
        if self.is_monitoring:
            logger.warning("Monitoring already in progress")
            return False
        
        try:
            if self.detector is None:
                await self.initialize_detector()
            
            self.is_monitoring = True
            logger.info("Monitoring started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            self.is_monitoring = False
            raise DetectionError(f"Failed to start monitoring: {e}")
    
    async def stop_monitoring(self) -> bool:
        """
        Stop drowsiness monitoring
        Returns: True if stopped successfully
        """
        try:
            if self.current_task:
                self.current_task.cancel()
                self.current_task = None
            
            self.is_monitoring = False
            logger.info("Monitoring stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            raise DetectionError(f"Failed to stop monitoring: {e}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get current monitoring status
        Returns: Dictionary with status information
        """
        return {
            'is_monitoring': self.is_monitoring,
            'detector_type': type(self.detector).__name__ if self.detector else None,
            'has_task': self.current_task is not None
        }
    
    async def validate_camera(self, camera_index: int = 0) -> bool:
        """
        Validate camera availability
        Args:
            camera_index: Index of camera to check
        Returns: True if camera is available
        """
        try:
            import cv2
            cap = cv2.VideoCapture(camera_index)
            is_available = cap.isOpened()
            cap.release()
            
            if not is_available:
                raise CameraError(f"Camera {camera_index} is not available")
            
            return True
            
        except Exception as e:
            logger.error(f"Camera validation failed: {e}")
            raise CameraError(f"Camera validation failed: {e}")


# Singleton instance
detection_service = DetectionService()