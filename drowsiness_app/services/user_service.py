"""
User Service - Handles user and driver profile related business logic
"""
import logging
from typing import Dict, Any, Optional
from django.contrib.auth import authenticate
from django.db import transaction
from asgiref.sync import sync_to_async

from ..models import CustomUser, DriverProfile, UserSettings
from ..core.exceptions import ValidationError


logger = logging.getLogger(__name__)


class UserService:
    """
    Service class to handle user operations
    """
    
    @staticmethod
    async def create_user_with_profile(
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        license_number: str = "",
        phone_number: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new user with driver profile
        Args:
            email: User email
            password: User password
            first_name: User first name
            last_name: User last name
            license_number: Driver license number
            phone_number: Driver phone number
        Returns: Dictionary with user and profile info
        """
        try:
            async with sync_to_async(transaction.atomic)():
                # Create user
                user = CustomUser(
                    email=email,
                    username=email,  # Use email as username
                    first_name=first_name,
                    last_name=last_name
                )
                user.set_password(password)
                await sync_to_async(user.save)()
                
                # Create driver profile
                driver_profile = DriverProfile(
                    user=user,
                    license_number=license_number or f"TEMP_{user.id}",
                    phone_number=phone_number
                )
                await sync_to_async(driver_profile.save)()
                
                # Create user settings with defaults
                user_settings = UserSettings(
                    user=user,
                    ear_threshold=0.3,
                    ear_frames=30,
                    yawn_threshold=20,
                    alert_frequency='medium'
                )
                await sync_to_async(user_settings.save)()
                
                logger.info(f"User created successfully: {email}")
                
                return {
                    'user': user,
                    'driver_profile': driver_profile,
                    'user_settings': user_settings,
                    'success': True
                }
                
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise ValidationError(f"Failed to create user: {e}")
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[CustomUser]:
        """
        Authenticate user with email and password
        Args:
            email: User email
            password: User password
        Returns: User instance if authenticated, None otherwise
        """
        try:
            user = await sync_to_async(authenticate)(username=email, password=password)
            if user:
                logger.info(f"User authenticated successfully: {email}")
            else:
                logger.warning(f"Authentication failed for: {email}")
            return user
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    @staticmethod
    async def get_driver_profile(user: CustomUser) -> Optional[DriverProfile]:
        """
        Get driver profile for user
        Args:
            user: User instance
        Returns: DriverProfile instance if exists
        """
        try:
            return await sync_to_async(
                lambda: DriverProfile.objects.get(user=user)
            )()
        except DriverProfile.DoesNotExist:
            logger.warning(f"Driver profile not found for user: {user.email}")
            return None
        except Exception as e:
            logger.error(f"Error getting driver profile: {e}")
            return None
    
    @staticmethod
    async def update_driver_profile(
        user: CustomUser,
        license_number: str = None,
        phone_number: str = None
    ) -> bool:
        """
        Update driver profile
        Args:
            user: User instance
            license_number: New license number
            phone_number: New phone number
        Returns: True if updated successfully
        """
        try:
            driver_profile = await UserService.get_driver_profile(user)
            if not driver_profile:
                raise ValidationError("Driver profile not found")
            
            if license_number is not None:
                driver_profile.license_number = license_number
            if phone_number is not None:
                driver_profile.phone_number = phone_number
                
            await sync_to_async(driver_profile.save)()
            logger.info(f"Driver profile updated for: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update driver profile: {e}")
            raise ValidationError(f"Failed to update driver profile: {e}")
    
    @staticmethod
    async def get_or_create_user_settings(user: CustomUser) -> UserSettings:
        """
        Get or create user settings
        Args:
            user: User instance
        Returns: UserSettings instance
        """
        try:
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
            
            if created:
                logger.info(f"User settings created for: {user.email}")
            
            return settings
            
        except Exception as e:
            logger.error(f"Error with user settings: {e}")
            raise ValidationError(f"Error with user settings: {e}")
    
    @staticmethod
    async def update_user_settings(
        user: CustomUser,
        ear_threshold: float = None,
        ear_frames: int = None,
        yawn_threshold: int = None,
        alert_frequency: str = None
    ) -> bool:
        """
        Update user settings
        Args:
            user: User instance
            ear_threshold: New EAR threshold
            ear_frames: New EAR frames count
            yawn_threshold: New yawn threshold
            alert_frequency: New alert frequency
        Returns: True if updated successfully
        """
        try:
            settings = await UserService.get_or_create_user_settings(user)
            
            if ear_threshold is not None:
                settings.ear_threshold = ear_threshold
            if ear_frames is not None:
                settings.ear_frames = ear_frames
            if yawn_threshold is not None:
                settings.yawn_threshold = yawn_threshold
            if alert_frequency is not None:
                settings.alert_frequency = alert_frequency
                
            await sync_to_async(settings.save)()
            logger.info(f"User settings updated for: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user settings: {e}")
            raise ValidationError(f"Failed to update user settings: {e}")


# Singleton instance
user_service = UserService()