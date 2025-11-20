"""
Unit tests for service layer
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
import asyncio

from ..services.user_service import user_service
from ..services.alert_service import alert_service
from ..services.detection_service import detection_service
from ..models import DriverProfile, Alert, UserSettings
from ..core.exceptions import ValidationError, CameraError


User = get_user_model()


class UserServiceTests(TestCase):
    """Test cases for UserService"""
    
    def setUp(self):
        """Set up test data"""
        self.test_email = "test@example.com"
        self.test_password = "testpass123"
    
    def test_create_user_with_profile_success(self):
        """Test successful user creation with profile"""
        async def run_test():
            result = await user_service.create_user_with_profile(
                email=self.test_email,
                password=self.test_password,
                first_name="Test",
                last_name="User",
                license_number="TEST123",
                phone_number="123-456-7890"
            )
            
            self.assertTrue(result['success'])
            self.assertIsNotNone(result['user'])
            self.assertIsNotNone(result['driver_profile'])
            self.assertIsNotNone(result['user_settings'])
            self.assertEqual(result['user'].email, self.test_email)
            
        asyncio.run(run_test())
    
    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email fails"""
        async def run_test():
            # Create first user
            await user_service.create_user_with_profile(
                email=self.test_email,
                password=self.test_password
            )
            
            # Try to create another with same email
            with self.assertRaises(ValidationError):
                await user_service.create_user_with_profile(
                    email=self.test_email,
                    password="different_password"
                )
                
        asyncio.run(run_test())
    
    def test_authenticate_user_valid_credentials(self):
        """Test user authentication with valid credentials"""
        async def run_test():
            # Create user first
            await user_service.create_user_with_profile(
                email=self.test_email,
                password=self.test_password
            )
            
            # Test authentication
            user = await user_service.authenticate_user(
                self.test_email, 
                self.test_password
            )
            
            self.assertIsNotNone(user)
            self.assertEqual(user.email, self.test_email)
            
        asyncio.run(run_test())
    
    def test_authenticate_user_invalid_credentials(self):
        """Test user authentication with invalid credentials"""
        async def run_test():
            # Create user first
            await user_service.create_user_with_profile(
                email=self.test_email,
                password=self.test_password
            )
            
            # Test authentication with wrong password
            user = await user_service.authenticate_user(
                self.test_email, 
                "wrong_password"
            )
            
            self.assertIsNone(user)
            
        asyncio.run(run_test())


class AlertServiceTests(TestCase):
    """Test cases for AlertService"""
    
    def setUp(self):
        """Set up test data"""
        async def setup():
            result = await user_service.create_user_with_profile(
                email="alert_test@example.com",
                password="testpass123"
            )
            self.user = result['user']
            self.driver_profile = result['driver_profile']
            
        asyncio.run(setup())
    
    def test_create_alert_success(self):
        """Test successful alert creation"""
        async def run_test():
            alert = await alert_service.create_alert(
                driver_profile=self.driver_profile,
                alert_type='drowsiness',
                description='Test drowsiness alert',
                severity='high',
                confidence=0.9
            )
            
            self.assertIsNotNone(alert)
            self.assertEqual(alert.alert_type, 'drowsiness')
            self.assertEqual(alert.severity, 'high')
            self.assertEqual(alert.confidence, 0.9)
            self.assertEqual(alert.driver, self.driver_profile)
            
        asyncio.run(run_test())
    
    def test_get_driver_alerts(self):
        """Test retrieving alerts for a driver"""
        async def run_test():
            # Create multiple alerts
            for i in range(3):
                await alert_service.create_alert(
                    driver_profile=self.driver_profile,
                    alert_type='drowsiness',
                    description=f'Test alert {i}',
                )
            
            # Retrieve alerts
            alerts = await alert_service.get_driver_alerts(
                self.driver_profile,
                limit=5
            )
            
            self.assertEqual(len(alerts), 3)
            # Should be ordered by timestamp (newest first)
            self.assertTrue(alerts[0].timestamp >= alerts[1].timestamp)
            
        asyncio.run(run_test())
    
    def test_get_alert_statistics(self):
        """Test alert statistics calculation"""
        async def run_test():
            # Create test alerts
            await alert_service.create_alert(
                driver_profile=self.driver_profile,
                alert_type='drowsiness',
                description='Test drowsiness alert',
            )
            await alert_service.create_alert(
                driver_profile=self.driver_profile,
                alert_type='yawning',
                description='Test yawning alert',
            )
            
            # Get statistics
            stats = await alert_service.get_alert_statistics(
                self.driver_profile,
                days=7
            )
            
            self.assertEqual(stats['total_alerts'], 2)
            self.assertIn('drowsiness', stats['alert_counts'])
            self.assertIn('yawning', stats['alert_counts'])
            self.assertGreaterEqual(stats['average_per_day'], 0)
            
        asyncio.run(run_test())


class DetectionServiceTests(TestCase):
    """Test cases for DetectionService"""
    
    @patch('cv2.VideoCapture')
    def test_validate_camera_success(self, mock_video_capture):
        """Test successful camera validation"""
        async def run_test():
            # Mock camera as available
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = True
            mock_video_capture.return_value = mock_cap
            
            # Test validation
            result = await detection_service.validate_camera(0)
            
            self.assertTrue(result)
            mock_video_capture.assert_called_with(0)
            mock_cap.release.assert_called_once()
            
        asyncio.run(run_test())
    
    @patch('cv2.VideoCapture')
    def test_validate_camera_failure(self, mock_video_capture):
        """Test camera validation failure"""
        async def run_test():
            # Mock camera as unavailable
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = False
            mock_video_capture.return_value = mock_cap
            
            # Test validation should raise error
            with self.assertRaises(CameraError):
                await detection_service.validate_camera(0)
                
        asyncio.run(run_test())
    
    def test_get_monitoring_status(self):
        """Test monitoring status retrieval"""
        status = detection_service.get_monitoring_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('is_monitoring', status)
        self.assertIn('detector_type', status)
        self.assertIn('has_task', status)
        self.assertIsInstance(status['is_monitoring'], bool)


if __name__ == '__main__':
    pytest.main([__file__])