"""
Custom exceptions for the drowsiness detection system
"""


class DrowsinessDetectionError(Exception):
    """Base exception for all drowsiness detection related errors"""
    pass


class CameraError(DrowsinessDetectionError):
    """Camera related errors"""
    pass


class CameraNotFoundError(CameraError):
    """When camera device is not available"""
    pass


class CameraPermissionError(CameraError):
    """When camera access is denied"""
    pass


class ModelLoadError(DrowsinessDetectionError):
    """When ML models fail to load"""
    pass


class DetectionError(DrowsinessDetectionError):
    """When detection algorithms fail"""
    pass


class AudioError(DrowsinessDetectionError):
    """When audio alerts fail"""
    pass


class ValidationError(DrowsinessDetectionError):
    """When data validation fails"""
    pass