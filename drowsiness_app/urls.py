"""
Refactored URLs with better naming and organization
"""
from django.urls import path
from . import views_refactored as views
from . import views_monitoring_fixed as monitoring_views

# Use the refactored views
urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.driver_dashboard, name='driver_dashboard'),
    
    # Profile Management
    path('update-settings/', views.update_settings, name='update_settings'),
    path('update-profile/', views.update_profile, name='update_profile'),
    
    # Monitoring - FIXED VERSIONS
    path('toggle-monitoring/', monitoring_views.toggle_monitoring, name='toggle_monitoring'),
    path('monitoring-status/', monitoring_views.get_monitoring_status, name='monitoring_status'),
    
    # Additional monitoring endpoints
    path('test-camera/', monitoring_views.test_camera_view, name='test_camera'),
    path('camera-test/', monitoring_views.simple_monitoring_test, name='camera_test'),
]