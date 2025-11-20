"""
Detection Factory - automatically chooses the best available detection method
Fallback order: dlib -> MediaPipe -> basic OpenCV
"""
import logging

logger = logging.getLogger(__name__)

class DetectionFactory:
    """Factory to create the best available detector"""
    
    @staticmethod
    def create_detector():
        """Create the best available detector"""
        
        # Try dlib first (original implementation)
        try:
            import dlib
            from .original_detection import DlibDrowsinessDetector  # We'll create this
            logger.info("Using dlib-based detection")
            return DlibDrowsinessDetector()
        except ImportError:
            logger.warning("dlib not available, trying MediaPipe")
            
        # Try MediaPipe
        try:
            from .mediapipe_detection import MediaPipeDrowsinessDetector
            logger.info("Using MediaPipe-based detection")
            return MediaPipeDrowsinessDetector()
        except ImportError:
            logger.warning("MediaPipe not available, using basic OpenCV")
            
        # Fallback to basic OpenCV
        try:
            from .basic_detection import BasicOpenCVDetector  # We'll create this
            logger.info("Using basic OpenCV detection")
            return BasicOpenCVDetector()
        except ImportError:
            logger.error("No detection methods available!")
            raise ImportError("No computer vision libraries available for detection")

# Convenience function
def get_detector():
    """Get a detector instance"""
    return DetectionFactory.create_detector()