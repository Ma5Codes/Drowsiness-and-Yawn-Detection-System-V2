from django.urls import re_path
from .consumers import MonitoringConsumer, AlertConsumer

websocket_urlpatterns = [
    re_path(r'ws/monitoring/$', MonitoringConsumer.as_asgi()),
    re_path(r'ws/alerts/$', AlertConsumer.as_asgi()),
]
