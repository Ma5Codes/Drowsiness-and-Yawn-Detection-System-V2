"""
Fixed WebSocket routing configuration
"""
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from drowsiness_app.consumers import MonitoringConsumer, AlertConsumer


websocket_urlpatterns = [
    re_path(r'ws/monitoring/$', MonitoringConsumer.as_asgi()),
    re_path(r'ws/alerts/$', AlertConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})