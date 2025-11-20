"""
User Repository - Data access layer for User and related models
"""
from typing import List, Optional, Dict, Any
from django.db import transaction
from asgiref.sync import sync_to_async

from .base_repository import BaseRepository
from ..models import CustomUser, DriverProfile, UserSettings


class UserRepository(BaseRepository):
    """
    Repository for User model operations
    """
    
    def __init__(self):
        super().__init__(CustomUser)
    
    async def get_by_email(self, email: str) -> Optional[CustomUser]:
        """
        Get user by email address
        Args:
            email: User email address
        Returns: User instance if found, None otherwise
        """
        try:
            return await sync_to_async(
                CustomUser.objects.get
            )(email=email)
        except CustomUser.DoesNotExist:
            return None
    
    async def create_user_with_profile(
        self,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        license_number: str = "",
        phone_number: str = ""
    ) -> Dict[str, Any]:
        """
        Create user with associated profile and settings
        Args:
            email: User email
            password: User password
            first_name: User first name
            last_name: User last name
            license_number: Driver license number
            phone_number: Driver phone number
        Returns: Dictionary with created instances
        """
        async with sync_to_async(transaction.atomic)():
            # Create user
            user = CustomUser(
                email=email,
                username=email,
                first_name=first_name,
                last_name=last_name
            )
            user.set_password(password)
            await sync_to_async(user.save, thread_sensitive=True)()
            
            # Create driver profile
            driver_profile = DriverProfile(
                user=user,
                license_number=license_number or f"TEMP_{user.id}",
                phone_number=phone_number
            )
            await sync_to_async(driver_profile.save, thread_sensitive=True)()
            
            # Create user settings
            user_settings = UserSettings(
                user=user,
                ear_threshold=0.3,
                ear_frames=30,
                yawn_threshold=20,
                alert_frequency='medium'
            )
            await sync_to_async(user_settings.save, thread_sensitive=True)()
            
            return {
                'user': user,
                'driver_profile': driver_profile,
                'user_settings': user_settings
            }
    
    async def email_exists(self, email: str) -> bool:
        """
        Check if email already exists
        Args:
            email: Email to check
        Returns: True if email exists, False otherwise
        """
        return await sync_to_async(
            CustomUser.objects.filter(email=email).exists
        )()


class DriverProfileRepository(BaseRepository):
    """
    Repository for DriverProfile model operations
    """
    
    def __init__(self):
        super().__init__(DriverProfile)
    
    async def get_by_user(self, user: CustomUser) -> Optional[DriverProfile]:
        """
        Get driver profile by user
        Args:
            user: User instance
        Returns: DriverProfile instance if found, None otherwise
        """
        try:
            return await sync_to_async(
                DriverProfile.objects.get
            )(user=user)
        except DriverProfile.DoesNotExist:
            return None
    
    async def get_by_license_number(self, license_number: str) -> Optional[DriverProfile]:
        """
        Get driver profile by license number
        Args:
            license_number: License number to search for
        Returns: DriverProfile instance if found, None otherwise
        """
        try:
            return await sync_to_async(
                DriverProfile.objects.get
            )(license_number=license_number)
        except DriverProfile.DoesNotExist:
            return None
    
    async def license_number_exists(self, license_number: str, exclude_user: CustomUser = None) -> bool:
        """
        Check if license number already exists
        Args:
            license_number: License number to check
            exclude_user: User to exclude from check (for updates)
        Returns: True if license number exists, False otherwise
        """
        queryset = DriverProfile.objects.filter(license_number=license_number)
        
        if exclude_user:
            queryset = queryset.exclude(user=exclude_user)
        
        return await sync_to_async(queryset.exists)()


class UserSettingsRepository(BaseRepository):
    """
    Repository for UserSettings model operations
    """
    
    def __init__(self):
        super().__init__(UserSettings)
    
    async def get_by_user(self, user: CustomUser) -> Optional[UserSettings]:
        """
        Get user settings by user
        Args:
            user: User instance
        Returns: UserSettings instance if found, None otherwise
        """
        try:
            return await sync_to_async(
                UserSettings.objects.get
            )(user=user)
        except UserSettings.DoesNotExist:
            return None
    
    async def get_or_create_by_user(self, user: CustomUser) -> UserSettings:
        """
        Get or create user settings for user
        Args:
            user: User instance
        Returns: UserSettings instance
        """
        settings, created = await sync_to_async(
            UserSettings.objects.get_or_create
        )(
            user=user,
            defaults={
                'ear_threshold': 0.3,
                'ear_frames': 30,
                'yawn_threshold': 20,
                'alert_frequency': 'medium'
            }
        )
        return settings


# Singleton instances
user_repository = UserRepository()
driver_profile_repository = DriverProfileRepository()
user_settings_repository = UserSettingsRepository()