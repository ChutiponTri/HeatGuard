from django.urls import path
from .views import receive_sensor_data, display_data

app_name = "sensor"  # ใช้ namespace

urlpatterns = [
    path("receive/", receive_sensor_data, name="receive_sensor_data"),  # รับข้อมูลจากเซ็นเซอร์
    path("display_data/", display_data, name="display_data"),  # แสดงข้อมูลเซ็นเซอร์
]
