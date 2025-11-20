"""
Integration tests for views
"""
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, AsyncMock

from ..models import DriverProfile, UserSettings, Alert


User = get_user_model()


class AuthenticationViewTests(TestCase):
    """Test cases for authentication views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.test_email = "test@example.com"
        self.test_password = "testpass123"
        
        # Create test user
        self.user = User.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            first_name="Test",
            last_name="User"
        )
        
        # Create driver profile
        self.driver_profile = DriverProfile.objects.create(
            user=self.user,
            license_number="TEST123",
            phone_number="123-456-7890"
        )
        
        # Create user settings
        self.user_settings = UserSettings.objects.create(
            user=self.user
        )
    
    def test_home_page_loads(self):
        """Test home page loads correctly"""
        response = self.client.get(reverse('home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DrowsiSense")
    
    def test_login_page_loads(self):
        """Test login page loads correctly"""
        response = self.client.get(reverse('login'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")
    
    def test_register_page_loads(self):
        """Test register page loads correctly"""
        response = self.client.get(reverse('register'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register")
    
    def test_successful_login(self):
        """Test successful user login"""
        response = self.client.post(reverse('login'), {
            'username': self.test_email,
            'password': self.test_password
        })
        
        # Should redirect to dashboard after successful login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('driver_dashboard'))
        
        # Check user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
    
    def test_failed_login(self):
        """Test failed user login"""
        response = self.client.post(reverse('login'), {
            'username': self.test_email,
            'password': 'wrong_password'
        })
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password")
        
        # Check user is not logged in
        self.assertFalse('_auth_user_id' in self.client.session)
    
    def test_logout(self):
        """Test user logout"""
        # Login first
        self.client.login(username=self.test_email, password=self.test_password)
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Logout
        response = self.client.get(reverse('logout'))
        
        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # Check user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)


class DashboardViewTests(TestCase):
    """Test cases for dashboard views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.test_email = "dashboard@example.com"
        self.test_password = "testpass123"
        
        # Create test user with profile
        self.user = User.objects.create_user(
            email=self.test_email,
            password=self.test_password
        )
        
        self.driver_profile = DriverProfile.objects.create(
            user=self.user,
            license_number="DASH123",
            phone_number="123-456-7890"
        )
        
        self.user_settings = UserSettings.objects.create(
            user=self.user,
            ear_threshold=0.3,
            ear_frames=30,
            yawn_threshold=20
        )
        
        # Create some test alerts
        Alert.objects.create(
            driver=self.driver_profile,
            alert_type='drowsiness',
            description='Test drowsiness alert'
        )
        Alert.objects.create(
            driver=self.driver_profile,
            alert_type='yawning',
            description='Test yawning alert'
        )
    
    def test_dashboard_requires_login(self):
        """Test dashboard redirects to login if not authenticated"""
        response = self.client.get(reverse('driver_dashboard'))
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))
    
    def test_dashboard_loads_for_authenticated_user(self):
        """Test dashboard loads correctly for authenticated user"""
        self.client.login(username=self.test_email, password=self.test_password)
        
        response = self.client.get(reverse('driver_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")
        self.assertContains(response, self.driver_profile.license_number)
        
        # Check that alerts are displayed
        self.assertContains(response, "drowsiness")
        self.assertContains(response, "yawning")
    
    def test_update_settings(self):
        """Test updating user settings"""
        self.client.login(username=self.test_email, password=self.test_password)
        
        new_settings = {
            'ear_threshold': 0.25,
            'ear_frames': 25,
            'yawn_threshold': 15,
            'alert_frequency': 'high'
        }
        
        response = self.client.post(reverse('update_settings'), new_settings)
        
        # Should redirect back to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('driver_dashboard'))
        
        # Check settings were updated
        updated_settings = UserSettings.objects.get(user=self.user)
        self.assertEqual(updated_settings.ear_threshold, 0.25)
        self.assertEqual(updated_settings.ear_frames, 25)
        self.assertEqual(updated_settings.yawn_threshold, 15)
        self.assertEqual(updated_settings.alert_frequency, 'high')
    
    def test_update_settings_invalid_data(self):
        """Test updating settings with invalid data"""
        self.client.login(username=self.test_email, password=self.test_password)
        
        invalid_settings = {
            'ear_threshold': 1.5,  # Invalid: > 0.8
            'ear_frames': 200,     # Invalid: > 100
            'yawn_threshold': -5,  # Invalid: < 5
        }
        
        response = self.client.post(reverse('update_settings'), invalid_settings)
        
        # Should redirect back with error message
        self.assertEqual(response.status_code, 302)
        
        # Settings should not be updated
        settings = UserSettings.objects.get(user=self.user)
        self.assertNotEqual(settings.ear_threshold, 1.5)
    
    def test_update_profile(self):
        """Test updating driver profile"""
        self.client.login(username=self.test_email, password=self.test_password)
        
        new_profile_data = {
            'license_number': 'NEW123456',
            'phone_number': '098-765-4321'
        }
        
        response = self.client.post(reverse('update_profile'), new_profile_data)
        
        # Should redirect back to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('driver_dashboard'))
        
        # Check profile was updated
        updated_profile = DriverProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.license_number, 'NEW123456')
        self.assertEqual(updated_profile.phone_number, '098-765-4321')


class MonitoringViewTests(TestCase):
    """Test cases for monitoring views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.test_email = "monitor@example.com"
        self.test_password = "testpass123"
        
        # Create test user with profile
        self.user = User.objects.create_user(
            email=self.test_email,
            password=self.test_password
        )
        
        self.driver_profile = DriverProfile.objects.create(
            user=self.user,
            license_number="MON123",
            phone_number="123-456-7890"
        )
        
        self.user_settings = UserSettings.objects.create(
            user=self.user,
            camera_index=0
        )
    
    def test_monitoring_status_requires_login(self):
        """Test monitoring status requires authentication"""
        response = self.client.get(reverse('monitoring_status'))
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))
    
    def test_get_monitoring_status(self):
        """Test getting monitoring status"""
        self.client.login(username=self.test_email, password=self.test_password)
        
        response = self.client.get(reverse('monitoring_status'))
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('status', data)
        self.assertIn('is_monitoring', data['status'])
    
    @patch('drowsiness_app.services.detection_service.detection_service.validate_camera')
    @patch('drowsiness_app.services.detection_service.detection_service.start_monitoring')
    def test_start_monitoring_success(self, mock_start_monitoring, mock_validate_camera):
        """Test successful monitoring start"""
        self.client.login(username=self.test_email, password=self.test_password)
        
        # Mock successful operations
        mock_validate_camera.return_value = AsyncMock(return_value=True)
        mock_start_monitoring.return_value = AsyncMock(return_value=True)
        
        response = self.client.post(reverse('toggle_monitoring'), {
            'action': 'start'
        })
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['action'], 'start')
    
    @patch('drowsiness_app.services.detection_service.detection_service.stop_monitoring')
    def test_stop_monitoring_success(self, mock_stop_monitoring):
        """Test successful monitoring stop"""
        self.client.login(username=self.test_email, password=self.test_password)
        
        # Mock successful operation
        mock_stop_monitoring.return_value = AsyncMock(return_value=True)
        
        response = self.client.post(reverse('toggle_monitoring'), {
            'action': 'stop'
        })
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['action'], 'stop')
    
    def test_toggle_monitoring_invalid_action(self):
        """Test monitoring toggle with invalid action"""
        self.client.login(username=self.test_email, password=self.test_password)
        
        response = self.client.post(reverse('toggle_monitoring'), {
            'action': 'invalid_action'
        })
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Invalid action', data['message'])