"""
WebSocket consumers for real-time updates
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Alert


class MonitoringConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time monitoring updates
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            # Join user-specific monitoring group
            self.room_group_name = f"monitoring_{self.user.id}"
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            print(f"✅ WebSocket connected for user {self.user.email}")
            
            # Send initial status
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Connected to monitoring system'
            }))
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"👋 WebSocket disconnected for user {self.user.email}")
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'get_alerts':
                # Send recent alerts
                alerts = await self.get_recent_alerts()
                await self.send(text_data=json.dumps({
                    'type': 'alerts_update',
                    'alerts': alerts
                }))
            elif message_type == 'ping':
                # Respond to ping
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': text_data_json.get('timestamp')
                }))
        except json.JSONDecodeError:
            pass
    
    async def alert_notification(self, event):
        """Send alert notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'new_alert',
            'alert': event['alert'],
            'message': event['message']
        }))
    
    async def monitoring_status(self, event):
        """Send monitoring status update"""
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': event['status']
        }))
    
    @database_sync_to_async
    def get_recent_alerts(self):
        """Get recent alerts for the user"""
        try:
            driver_profile = self.user.driver_profile
            alerts = Alert.objects.filter(driver=driver_profile).order_by('-timestamp')[:10]
            
            return [{
                'id': alert.id,
                'alert_type': alert.alert_type,
                'description': alert.description,
                'severity': alert.severity,
                'timestamp': alert.timestamp.isoformat(),
                'status': alert.status
            } for alert in alerts]
        except Exception as e:
            print(f"Error getting alerts: {e}")
            return []


class AlertConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for alert-specific updates
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            # Join alerts group
            self.room_group_name = f"alerts_{self.user.id}"
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def new_alert(self, event):
        """Send new alert to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'data': event['data']
        }))