"""
Configuration Management - Centralized configuration handling
"""
import os
from typing import Dict, Any


class Config:
    """
    Centralized configuration management
    """
    
    # Detection Engine Configuration
    DETECTION_CONFIG = {
        'default_detector': 'auto',  # auto, mediapipe, dlib, basic
        'fallback_detectors': ['mediapipe', 'basic'],
        'frame_width': 640,
        'frame_height': 480,
        'target_fps': 30,
        'max_detection_retries': 3,
        'detection_timeout': 30,  # seconds
    }
    
    # Camera Configuration
    CAMERA_CONFIG = {
        'default_index': 0,
        'initialization_timeout': 5,  # seconds
        'frame_buffer_size': 1,
        'auto_exposure': True,
        'brightness': 0.5,
        'contrast': 0.5,
    }
    
    # Audio Configuration
    AUDIO_CONFIG = {
        'enable_audio_alerts': True,
        'enable_tts': True,
        'audio_file_path': 'static/music.wav',
        'volume': 0.8,
        'tts_voice_rate': 200,  # words per minute
    }
    
    # Alert Configuration
    ALERT_CONFIG = {
        'default_severity': 'medium',
        'email_retry_attempts': 3,
        'email_retry_delay': 2,  # seconds
        'alert_cooldown': 5,  # seconds between same type alerts
        'max_alerts_per_session': 100,
    }
    
    # Performance Configuration
    PERFORMANCE_CONFIG = {
        'enable_performance_monitoring': True,
        'max_memory_usage': 512,  # MB
        'frame_skip_threshold': 0.1,  # seconds
        'detection_thread_pool_size': 2,
    }
    
    # Security Configuration
    SECURITY_CONFIG = {
        'enable_rate_limiting': True,
        'max_login_attempts': 5,
        'lockout_duration': 300,  # seconds
        'session_timeout': 3600,  # seconds
        'require_https': False,  # Set to True in production
    }
    
    # Database Configuration
    DATABASE_CONFIG = {
        'connection_timeout': 30,
        'query_timeout': 30,
        'max_connections': 20,
        'connection_retry_attempts': 3,
    }
    
    @classmethod
    def get_detection_config(cls) -> Dict[str, Any]:
        """Get detection configuration with environment overrides"""
        config = cls.DETECTION_CONFIG.copy()
        
        # Environment variable overrides
        if os.getenv('DETECTION_METHOD'):
            config['default_detector'] = os.getenv('DETECTION_METHOD')
        
        if os.getenv('FRAME_WIDTH'):
            config['frame_width'] = int(os.getenv('FRAME_WIDTH'))
            
        if os.getenv('FRAME_HEIGHT'):
            config['frame_height'] = int(os.getenv('FRAME_HEIGHT'))
            
        if os.getenv('TARGET_FPS'):
            config['target_fps'] = int(os.getenv('TARGET_FPS'))
        
        return config
    
    @classmethod
    def get_camera_config(cls) -> Dict[str, Any]:
        """Get camera configuration with environment overrides"""
        config = cls.CAMERA_CONFIG.copy()
        
        if os.getenv('DEFAULT_CAMERA_INDEX'):
            config['default_index'] = int(os.getenv('DEFAULT_CAMERA_INDEX'))
        
        return config
    
    @classmethod
    def get_audio_config(cls) -> Dict[str, Any]:
        """Get audio configuration with environment overrides"""
        config = cls.AUDIO_CONFIG.copy()
        
        if os.getenv('ENABLE_AUDIO_ALERTS'):
            config['enable_audio_alerts'] = os.getenv('ENABLE_AUDIO_ALERTS').lower() == 'true'
            
        if os.getenv('ENABLE_TTS'):
            config['enable_tts'] = os.getenv('ENABLE_TTS').lower() == 'true'
            
        if os.getenv('AUDIO_VOLUME'):
            config['volume'] = float(os.getenv('AUDIO_VOLUME'))
        
        return config
    
    @classmethod
    def get_alert_config(cls) -> Dict[str, Any]:
        """Get alert configuration with environment overrides"""
        config = cls.ALERT_CONFIG.copy()
        
        if os.getenv('DEFAULT_ALERT_SEVERITY'):
            config['default_severity'] = os.getenv('DEFAULT_ALERT_SEVERITY')
        
        return config
    
    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """Get all configuration sections"""
        return {
            'detection': cls.get_detection_config(),
            'camera': cls.get_camera_config(),
            'audio': cls.get_audio_config(),
            'alert': cls.get_alert_config(),
            'performance': cls.PERFORMANCE_CONFIG,
            'security': cls.SECURITY_CONFIG,
            'database': cls.DATABASE_CONFIG,
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return validation results"""
        issues = []
        
        # Validate detection config
        detection_config = cls.get_detection_config()
        if detection_config['frame_width'] < 320:
            issues.append("Frame width should be at least 320px")
        if detection_config['target_fps'] < 10:
            issues.append("Target FPS should be at least 10")
        
        # Validate audio config
        audio_config = cls.get_audio_config()
        if not (0.0 <= audio_config['volume'] <= 1.0):
            issues.append("Audio volume should be between 0.0 and 1.0")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }


# Singleton configuration instance
config = Config()