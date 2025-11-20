"""
Real-time update utilities for dashboard
"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


def send_alert_to_user(user_id, alert_data):
    """
    Send real-time alert update to user's dashboard
    """
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            room_group_name = f"monitoring_{user_id}"
            
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'alert_notification',
                    'alert': alert_data,
                    'message': f"New {alert_data.get('alert_type', 'alert')} detected!"
                }
            )
            print(f"📡 Real-time alert sent to user {user_id}")
        else:
            print("⚠️ Channel layer not available for real-time updates")
    except Exception as e:
        print(f"❌ Failed to send real-time alert: {e}")


def send_monitoring_status(user_id, status):
    """
    Send monitoring status update to user's dashboard
    """
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            room_group_name = f"monitoring_{user_id}"
            
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'monitoring_status',
                    'status': status
                }
            )
            print(f"📡 Status update sent to user {user_id}")
    except Exception as e:
        print(f"❌ Failed to send status update: {e}")


def broadcast_system_message(message):
    """
    Broadcast system message to all connected users
    """
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                "system_updates",
                {
                    'type': 'system_message',
                    'message': message
                }
            )
            print(f"📡 System message broadcasted: {message}")
    except Exception as e:
        print(f"❌ Failed to broadcast system message: {e}")