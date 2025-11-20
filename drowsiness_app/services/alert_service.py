"""
Alert Service - Handles all alert-related business logic
"""
import logging
from typing import Dict, Any, List, Optional
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from asgiref.sync import sync_to_async

from ..models import Alert, DriverProfile
from ..core.exceptions import DrowsinessDetectionError


logger = logging.getLogger(__name__)


class AlertService:
    """
    Service class to handle alert operations
    """
    
    @staticmethod
    async def create_alert(
        driver_profile: DriverProfile,
        alert_type: str,
        description: str,
        severity: str = 'medium',
        confidence: float = 1.0
    ) -> Alert:
        """
        Create a new alert
        Args:
            driver_profile: Driver profile instance
            alert_type: Type of alert ('drowsiness', 'yawning')
            description: Alert description
            severity: Alert severity level
            confidence: Detection confidence score
        Returns: Created Alert instance
        """
        try:
            alert = Alert(
                driver=driver_profile,
                alert_type=alert_type,
                description=description,
                severity=severity,
                confidence=confidence,
                timestamp=timezone.now()
            )
            await sync_to_async(alert.save, thread_sensitive=True)()
            logger.info(f"Alert created: {alert_type} for {driver_profile.user.email}")
            return alert
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            raise DrowsinessDetectionError(f"Failed to create alert: {e}")
    
    @staticmethod
    async def send_email_alert(
        alert: Alert,
        recipient_email: str,
        template_name: str = "drowsiness_alert.html"
    ) -> bool:
        """
        Send email alert to recipient
        Args:
            alert: Alert instance
            recipient_email: Email address to send to
            template_name: Email template name
        Returns: True if sent successfully
        """
        try:
            subject_map = {
                'drowsiness': 'Drowsiness Alert - Immediate Attention Required',
                'yawning': 'Fatigue Alert - Driver Monitoring System'
            }
            
            subject = subject_map.get(alert.alert_type, 'Driver Alert')
            
            context = {
                'driver': alert.driver,
                'alert': alert,
                'driver_first_name': alert.driver.user.first_name,
                'severity': alert.severity,
                'confidence': alert.confidence
            }
            
            message = render_to_string(template_name, context)
            email = EmailMessage(subject, message, to=[recipient_email])
            email.content_subtype = "html"
            
            await sync_to_async(email.send)()
            logger.info(f"Email alert sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    @staticmethod
    async def get_driver_alerts(
        driver_profile: DriverProfile,
        limit: int = 50,
        alert_type: Optional[str] = None
    ) -> List[Alert]:
        """
        Get alerts for a driver
        Args:
            driver_profile: Driver profile instance
            limit: Maximum number of alerts to return
            alert_type: Filter by alert type (optional)
        Returns: List of Alert instances
        """
        try:
            queryset = Alert.objects.filter(driver=driver_profile).order_by('-timestamp')
            
            if alert_type:
                queryset = queryset.filter(alert_type=alert_type)
            
            alerts = await sync_to_async(list)(queryset[:limit])
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get driver alerts: {e}")
            raise DrowsinessDetectionError(f"Failed to get driver alerts: {e}")
    
    @staticmethod
    async def get_alert_statistics(
        driver_profile: DriverProfile,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get alert statistics for a driver
        Args:
            driver_profile: Driver profile instance
            days: Number of days to include in statistics
        Returns: Dictionary with statistics
        """
        try:
            from datetime import timedelta
            from django.db.models import Count
            
            cutoff_date = timezone.now() - timedelta(days=days)
            
            alerts = Alert.objects.filter(
                driver=driver_profile,
                timestamp__gte=cutoff_date
            )
            
            total_alerts = await sync_to_async(alerts.count)()
            
            alert_counts = await sync_to_async(
                lambda: dict(alerts.values('alert_type').annotate(count=Count('id')))
            )()
            
            return {
                'total_alerts': total_alerts,
                'alert_counts': alert_counts,
                'period_days': days,
                'average_per_day': round(total_alerts / days, 2) if days > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get alert statistics: {e}")
            raise DrowsinessDetectionError(f"Failed to get alert statistics: {e}")


# Singleton instance
alert_service = AlertService()