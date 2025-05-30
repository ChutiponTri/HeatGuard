# sensor/routing.py
from django.urls import re_path
from . import consumers  # เปลี่ยนเป็นการนำเข้า consumers

websocket_urlpatterns = [
    re_path(r'ws/sensor/', consumers.SensorConsumer.as_asgi()),  # ใช้ consumer สำหรับรับข้อมูล
]
