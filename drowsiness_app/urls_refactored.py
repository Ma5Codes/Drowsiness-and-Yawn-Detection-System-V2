"""
Refactored URLs with better naming and organization
"""
from django.urls import path
from . import views_refactored as views

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
    
    # Monitoring
    path('toggle-monitoring/', views.toggle_monitoring, name='toggle_monitoring'),
    path('monitoring-status/', views.get_monitoring_status, name='monitoring_status'),
]