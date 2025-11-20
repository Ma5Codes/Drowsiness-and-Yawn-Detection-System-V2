"""
Unit tests for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal

from ..models import DriverProfile, Alert, UserSettings, MonitoringSession


User = get_user_model()


class CustomUserModelTests(TestCase):
    """Test cases for CustomUser model"""
    
    def test_create_user_with_email(self):
        """Test creating user with email"""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertEqual(user.username, "test@example.com")  # Should use email as username
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        self.assertEqual(str(user), "test@example.com")
    
    def test_email_unique_constraint(self):
        """Test email uniqueness"""
        User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="test@example.com",
                password="different123"
            )


class DriverProfileModelTests(TestCase):
    """Test cases for DriverProfile model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email="driver@example.com",
            password="testpass123"
        )
    
    def test_create_driver_profile(self):
        """Test creating driver profile"""
        profile = DriverProfile.objects.create(
            user=self.user,
            license_number="ABC123456",
            phone_number="123-456-7890"
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.license_number, "ABC123456")
        self.assertEqual(profile.phone_number, "123-456-7890")
        self.assertFalse(profile.is_verified)  # Default should be False
    
    def test_driver_profile_str_representation(self):
        """Test driver profile string representation"""
        profile = DriverProfile.objects.create(
            user=self.user,
            license_number="ABC123456",
            phone_number="123-456-7890"
        )
        
        expected = f"{self.user.email}'s Profile"
        self.assertEqual(str(profile), expected)
    
    def test_license_number_unique_constraint(self):
        """Test license number uniqueness"""
        DriverProfile.objects.create(
            user=self.user,
            license_number="ABC123456",
            phone_number="123-456-7890"
        )
        
        # Create another user
        user2 = User.objects.create_user(
            email="driver2@example.com",
            password="testpass123"
        )
        
        with self.assertRaises(IntegrityError):
            DriverProfile.objects.create(
                user=user2,
                license_number="ABC123456",  # Same license number
                phone_number="098-765-4321"
            )
    
    def test_license_number_validation(self):
        """Test license number validation"""
        profile = DriverProfile(
            user=self.user,
            license_number="AB",  # Too short
            phone_number="123-456-7890"
        )
        
        with self.assertRaises(ValidationError):
            profile.clean()


class AlertModelTests(TestCase):
    """Test cases for Alert model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email="alert@example.com",
            password="testpass123"
        )
        self.driver_profile = DriverProfile.objects.create(
            user=self.user,
            license_number="ALERT123",
            phone_number="123-456-7890"
        )
    
    def test_create_alert(self):
        """Test creating an alert"""
        alert = Alert.objects.create(
            driver=self.driver_profile,
            alert_type='drowsiness',
            description='Test drowsiness alert',
            severity='high',
            confidence=0.9
        )
        
        self.assertEqual(alert.driver, self.driver_profile)
        self.assertEqual(alert.alert_type, 'drowsiness')
        self.assertEqual(alert.severity, 'high')
        self.assertEqual(alert.confidence, 0.9)
        self.assertEqual(alert.status, 'active')  # Default status
    
    def test_alert_str_representation(self):
        """Test alert string representation"""
        alert = Alert.objects.create(
            driver=self.driver_profile,
            alert_type='yawning',
            description='Test yawning alert'
        )
        
        expected = f"yawning - {self.user.email} ({alert.timestamp})"
        self.assertEqual(str(alert), expected)
    
    def test_acknowledge_alert(self):
        """Test acknowledging an alert"""
        alert = Alert.objects.create(
            driver=self.driver_profile,
            alert_type='drowsiness',
            description='Test alert'
        )
        
        # Initially should be active
        self.assertEqual(alert.status, 'active')
        self.assertIsNone(alert.acknowledged_at)
        
        # Acknowledge the alert
        alert.acknowledge()
        
        self.assertEqual(alert.status, 'acknowledged')
        self.assertIsNotNone(alert.acknowledged_at)
    
    def test_resolve_alert(self):
        """Test resolving an alert"""
        alert = Alert.objects.create(
            driver=self.driver_profile,
            alert_type='drowsiness',
            description='Test alert'
        )
        
        # Initially should be active
        self.assertEqual(alert.status, 'active')
        self.assertIsNone(alert.resolved_at)
        
        # Resolve the alert
        action_taken = "Driver took break"
        alert.resolve(action_taken=action_taken)
        
        self.assertEqual(alert.status, 'resolved')
        self.assertEqual(alert.action_taken, action_taken)
        self.assertIsNotNone(alert.resolved_at)
    
    def test_confidence_validation(self):
        """Test confidence score validation"""
        # Should accept valid confidence scores
        alert1 = Alert.objects.create(
            driver=self.driver_profile,
            alert_type='drowsiness',
            confidence=0.0
        )
        self.assertEqual(alert1.confidence, 0.0)
        
        alert2 = Alert.objects.create(
            driver=self.driver_profile,
            alert_type='drowsiness',
            confidence=1.0
        )
        self.assertEqual(alert2.confidence, 1.0)
        
        # Should reject invalid confidence scores
        with self.assertRaises(ValidationError):
            alert_invalid = Alert(
                driver=self.driver_profile,
                alert_type='drowsiness',
                confidence=1.5  # > 1.0
            )
            alert_invalid.full_clean()


class UserSettingsModelTests(TestCase):
    """Test cases for UserSettings model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email="settings@example.com",
            password="testpass123"
        )
    
    def test_create_user_settings(self):
        """Test creating user settings"""
        settings = UserSettings.objects.create(
            user=self.user,
            ear_threshold=0.25,
            ear_frames=25,
            yawn_threshold=15
        )
        
        self.assertEqual(settings.user, self.user)
        self.assertEqual(settings.ear_threshold, 0.25)
        self.assertEqual(settings.ear_frames, 25)
        self.assertEqual(settings.yawn_threshold, 15)
        self.assertEqual(settings.alert_frequency, 'medium')  # Default
    
    def test_user_settings_str_representation(self):
        """Test user settings string representation"""
        settings = UserSettings.objects.create(user=self.user)
        
        expected = f"{self.user.email}'s Settings"
        self.assertEqual(str(settings), expected)
    
    def test_get_detection_config(self):
        """Test getting detection configuration"""
        settings = UserSettings.objects.create(
            user=self.user,
            ear_threshold=0.25,
            ear_frames=25,
            yawn_threshold=15,
            camera_index=1
        )
        
        config = settings.get_detection_config()
        
        self.assertEqual(config['ear_threshold'], 0.25)
        self.assertEqual(config['ear_frames'], 25)
        self.assertEqual(config['yawn_threshold'], 15)
        self.assertEqual(config['camera_index'], 1)
        self.assertIn('detection_mode', config)
        self.assertIn('email_alerts', config)
        self.assertIn('audio_alerts', config)
    
    def test_threshold_validation(self):
        """Test threshold validation ranges"""
        # Valid thresholds should work
        settings = UserSettings(
            user=self.user,
            ear_threshold=0.5,
            ear_frames=50,
            yawn_threshold=25
        )
        settings.full_clean()  # Should not raise
        
        # Invalid thresholds should fail
        with self.assertRaises(ValidationError):
            invalid_settings = UserSettings(
                user=self.user,
                ear_threshold=1.5,  # > 0.8
                ear_frames=5,
                yawn_threshold=25
            )
            invalid_settings.full_clean()


class MonitoringSessionModelTests(TestCase):
    """Test cases for MonitoringSession model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email="monitor@example.com",
            password="testpass123"
        )
        self.driver_profile = DriverProfile.objects.create(
            user=self.user,
            license_number="MONITOR123",
            phone_number="123-456-7890"
        )
    
    def test_create_monitoring_session(self):
        """Test creating a monitoring session"""
        session = MonitoringSession.objects.create(
            driver=self.driver_profile,
            device_info={'camera': 'USB Camera'},
            settings_snapshot={'ear_threshold': 0.3}
        )
        
        self.assertEqual(session.driver, self.driver_profile)
        self.assertEqual(session.status, 'active')  # Default status
        self.assertEqual(session.frames_processed, 0)  # Default
        self.assertEqual(session.alerts_generated, 0)  # Default
        self.assertIsNotNone(session.start_time)
        self.assertIsNone(session.end_time)
    
    def test_monitoring_session_str_representation(self):
        """Test monitoring session string representation"""
        session = MonitoringSession.objects.create(
            driver=self.driver_profile
        )
        
        expected = f"Session {session.id} - {self.user.email} ({session.start_time})"
        self.assertEqual(str(session), expected)
    
    def test_end_session(self):
        """Test ending a monitoring session"""
        session = MonitoringSession.objects.create(
            driver=self.driver_profile
        )
        
        # Initially should be active
        self.assertEqual(session.status, 'active')
        self.assertIsNone(session.end_time)
        self.assertIsNone(session.duration)
        
        # End the session
        session.end_session()
        
        self.assertEqual(session.status, 'completed')
        self.assertIsNotNone(session.end_time)
        self.assertIsNotNone(session.duration)
        self.assertGreater(session.end_time, session.start_time)