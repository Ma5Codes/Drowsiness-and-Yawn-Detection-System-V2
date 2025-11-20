"""
Updated models.py - Direct replacement for the original models.py
This avoids migration issues by updating the existing models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    """Enhanced Custom User Model"""
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    # Enhanced fields
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this user belongs to.",
        related_name="custom_user_set",
        related_query_name="user",
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="custom_user_set",
        related_query_name="user",
    )

    def __str__(self):
        return self.email


class DriverProfile(models.Model):
    """Enhanced Driver Profile Model"""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="driver_profile",
    )
    license_number = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=20)
    
    # Enhanced fields (with defaults for existing data)
    date_of_birth = models.DateField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True, default="")
    vehicle_info = models.CharField(max_length=100, blank=True, default="")
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"

    def clean(self):
        """Custom validation"""
        if self.license_number and len(self.license_number.strip()) < 3:
            raise ValidationError("License number must be at least 3 characters long")


class Alert(models.Model):
    """Enhanced Alert Model"""
    
    ALERT_TYPES = [
        ('drowsiness', 'Drowsiness'),
        ('yawning', 'Excessive Yawning'),
        ('distraction', 'Driver Distraction'),
        ('fatigue', 'Driver Fatigue'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    ]
    
    driver = models.ForeignKey(
        DriverProfile, 
        on_delete=models.CASCADE, 
        related_name="alerts"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    alert_type = models.CharField(
        max_length=50,
        choices=ALERT_TYPES,
        default='drowsiness'
    )
    description = models.TextField(blank=True, null=True)
    
    # Enhanced fields (with defaults for existing data)
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        default='medium'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    confidence = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Detection confidence score (0.0 to 1.0)"
    )
    device_info = models.JSONField(default=dict, blank=True)
    location_data = models.JSONField(default=dict, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    response_time = models.DurationField(null=True, blank=True)
    action_taken = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.alert_type} - {self.driver.user.email} ({self.timestamp})"
    
    def acknowledge(self, user=None):
        """Mark alert as acknowledged"""
        self.status = 'acknowledged'
        self.acknowledged_at = timezone.now()
        self.save()
    
    def resolve(self, action_taken="", user=None):
        """Mark alert as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.action_taken = action_taken
        self.save()


class UserSettings(models.Model):
    """Enhanced User Settings Model"""
    
    ALERT_FREQUENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('custom', 'Custom'),
    ]
    
    DETECTION_MODE_CHOICES = [
        ('strict', 'Strict'),
        ('balanced', 'Balanced'),
        ('lenient', 'Lenient'),
        ('custom', 'Custom'),
    ]
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_settings",
    )
    
    # Enhanced detection thresholds
    ear_threshold = models.FloatField(
        default=0.3,
        validators=[MinValueValidator(0.1), MaxValueValidator(0.8)],
        help_text="Eye Aspect Ratio threshold for drowsiness detection"
    )
    ear_frames = models.IntegerField(
        default=30,
        validators=[MinValueValidator(5), MaxValueValidator(100)],
        help_text="Consecutive frames for drowsiness confirmation"
    )
    yawn_threshold = models.IntegerField(
        default=20,
        validators=[MinValueValidator(5), MaxValueValidator(50)],
        help_text="Mouth opening threshold for yawn detection"
    )
    alert_frequency = models.CharField(
        max_length=10,
        choices=ALERT_FREQUENCY_CHOICES,
        default="medium",
    )
    
    # Enhanced settings (with defaults for existing data)
    detection_mode = models.CharField(
        max_length=10,
        choices=DETECTION_MODE_CHOICES,
        default='balanced',
    )
    email_alerts = models.BooleanField(default=True)
    audio_alerts = models.BooleanField(default=True)
    vibration_alerts = models.BooleanField(default=False)
    camera_index = models.IntegerField(default=0)
    video_quality = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )
    data_retention_days = models.IntegerField(default=30)
    share_analytics = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email}'s Settings"
    
    def get_detection_config(self):
        """Get detection configuration as dictionary"""
        return {
            'ear_threshold': self.ear_threshold,
            'ear_frames': self.ear_frames,
            'yawn_threshold': self.yawn_threshold,
            'camera_index': self.camera_index,
            'detection_mode': self.detection_mode,
            'email_alerts': self.email_alerts,
            'audio_alerts': self.audio_alerts,
        }


class MonitoringSession(models.Model):
    """New Model - Track monitoring sessions"""
    
    SESSION_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('interrupted', 'Interrupted'),
        ('failed', 'Failed'),
    ]
    
    driver = models.ForeignKey(
        DriverProfile,
        on_delete=models.CASCADE,
        related_name='monitoring_sessions'
    )
    
    # Session details
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=SESSION_STATUS,
        default='active'
    )
    
    # Session metadata
    device_info = models.JSONField(default=dict)
    settings_snapshot = models.JSONField(default=dict)
    
    # Performance metrics
    frames_processed = models.IntegerField(default=0)
    alerts_generated = models.IntegerField(default=0)
    average_confidence = models.FloatField(null=True, blank=True)
    
    # Quality metrics
    detection_accuracy = models.FloatField(null=True, blank=True)
    false_positive_rate = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"Session {self.id} - {self.driver.user.email} ({self.start_time})"
    
    def end_session(self):
        """End the monitoring session"""
        if self.status == 'active':
            self.end_time = timezone.now()
            if self.start_time:
                self.duration = self.end_time - self.start_time
            self.status = 'completed'
            self.save()