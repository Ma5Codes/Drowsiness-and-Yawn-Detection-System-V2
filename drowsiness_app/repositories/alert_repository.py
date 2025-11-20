"""
Alert Repository - Data access layer for Alert model
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from asgiref.sync import sync_to_async

from .base_repository import BaseRepository
from ..models import Alert, DriverProfile


class AlertRepository(BaseRepository):
    """
    Repository for Alert model operations
    """
    
    def __init__(self):
        super().__init__(Alert)
    
    async def get_alerts_by_driver(
        self,
        driver_profile: DriverProfile,
        limit: int = 50,
        alert_type: Optional[str] = None
    ) -> List[Alert]:
        """
        Get alerts for a specific driver
        Args:
            driver_profile: Driver profile instance
            limit: Maximum number of alerts to return
            alert_type: Filter by alert type (optional)
        Returns: List of Alert instances
        """
        queryset = Alert.objects.filter(driver=driver_profile).order_by('-timestamp')
        
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        
        return await sync_to_async(list)(queryset[:limit])
    
    async def get_alerts_by_date_range(
        self,
        driver_profile: DriverProfile,
        start_date: datetime,
        end_date: datetime
    ) -> List[Alert]:
        """
        Get alerts within a date range
        Args:
            driver_profile: Driver profile instance
            start_date: Start date for filtering
            end_date: End date for filtering
        Returns: List of Alert instances
        """
        queryset = Alert.objects.filter(
            driver=driver_profile,
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).order_by('-timestamp')
        
        return await sync_to_async(list)(queryset)
    
    async def get_recent_alerts(
        self,
        driver_profile: DriverProfile,
        hours: int = 24
    ) -> List[Alert]:
        """
        Get recent alerts within specified hours
        Args:
            driver_profile: Driver profile instance
            hours: Number of hours to look back
        Returns: List of recent Alert instances
        """
        cutoff_time = timezone.now() - timedelta(hours=hours)
        queryset = Alert.objects.filter(
            driver=driver_profile,
            timestamp__gte=cutoff_time
        ).order_by('-timestamp')
        
        return await sync_to_async(list)(queryset)
    
    async def get_alert_statistics(
        self,
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
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Get total count
        total_count = await sync_to_async(
            Alert.objects.filter(
                driver=driver_profile,
                timestamp__gte=cutoff_date
            ).count
        )()
        
        # Get count by type
        alert_type_counts = await sync_to_async(
            lambda: dict(
                Alert.objects.filter(
                    driver=driver_profile,
                    timestamp__gte=cutoff_date
                ).values('alert_type').annotate(count=Count('id')).values_list('alert_type', 'count')
            )
        )()
        
        # Get severity distribution if we have severity field
        severity_counts = await sync_to_async(
            lambda: dict(
                Alert.objects.filter(
                    driver=driver_profile,
                    timestamp__gte=cutoff_date
                ).values('severity').annotate(count=Count('id')).values_list('severity', 'count')
            )
        )() if hasattr(Alert, 'severity') else {}
        
        return {
            'total_alerts': total_count,
            'alert_type_counts': alert_type_counts,
            'severity_counts': severity_counts,
            'period_days': days,
            'average_per_day': round(total_count / days, 2) if days > 0 else 0
        }
    
    async def delete_old_alerts(
        self,
        driver_profile: DriverProfile,
        days_to_keep: int = 90
    ) -> int:
        """
        Delete old alerts beyond retention period
        Args:
            driver_profile: Driver profile instance
            days_to_keep: Number of days to keep alerts
        Returns: Number of deleted alerts
        """
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        deleted_count = await sync_to_async(
            lambda: Alert.objects.filter(
                driver=driver_profile,
                timestamp__lt=cutoff_date
            ).delete()[0]
        )()
        
        return deleted_count
    
    async def get_high_frequency_periods(
        self,
        driver_profile: DriverProfile,
        days: int = 7,
        min_alerts_per_hour: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Identify periods with high alert frequency
        Args:
            driver_profile: Driver profile instance
            days: Number of days to analyze
            min_alerts_per_hour: Minimum alerts per hour to consider high frequency
        Returns: List of high frequency periods
        """
        from django.db.models import Count
        from django.db.models.functions import Extract
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Group alerts by hour and count
        hourly_counts = await sync_to_async(
            lambda: list(
                Alert.objects.filter(
                    driver=driver_profile,
                    timestamp__gte=cutoff_date
                ).extra(
                    select={
                        'hour': "DATE_FORMAT(timestamp, '%%Y-%%m-%%d %%H')"
                    }
                ).values('hour').annotate(
                    alert_count=Count('id')
                ).filter(
                    alert_count__gte=min_alerts_per_hour
                ).order_by('-alert_count')
            )
        )()
        
        return hourly_counts


# Singleton instance
alert_repository = AlertRepository()