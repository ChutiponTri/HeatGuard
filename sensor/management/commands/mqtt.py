import paho.mqtt.client as mqtt
import os
import sys
import json
import ssl

sys.path.append('/app')
from sensor.models import SensorData
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

MQTT_SERVER = 'vad77f40.ala.asia-southeast1.emqxsl.com'
MQTT_PORT = 8883
MQTT_KEEPALIVE = 60
MQTT_USER = 'Heatstroke_all'
MQTT_PASSWORD = '6310611097@Heat'

def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe("data")
    else:
        print('Bad connection. Code:', rc)


def on_message(mqtt_client, userdata, msg):
    payload = msg.payload.decode()
    print(f'Received message on topic: {msg.topic} with payload: {payload}')
    data = json.loads(payload)

    user_id = data.get("user")
    User = get_user_model()
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = User.objects.get_or_create(username="anonymous")[0]
    else:
        user = User.objects.get_or_create(username="anonymous")[0]

    risk_int  = data.get("risk")
    if(risk_int == 0):
        risk = "normal"
    elif(risk_int == 1):
        risk = "low"
    elif(risk_int == 2):
        risk = "medium"
    elif(risk_int == 3):
        risk = "high"
    else:
        risk = "🤔?"
    
    sensor_data = SensorData.objects.create(
        user = user,
        heart_rate = data.get("heart_rate"),
        skin_temperature = data.get("skin_temperature"),
        ambient_temperature = data.get("ambient_temperature"),
        humidity = data.get("humidity"),
        skin_resistance = data.get("skin_resistance"),
        risk  = risk
    )

    # ✅ Broadcast ข้อมูลไปยัง WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "sensor_group",
        {
            "type": "send_sensor_data",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "timestamp": str(sensor_data.timestamp),
                "heart_rate": sensor_data.heart_rate,
                "skin_temperature": sensor_data.skin_temperature,
                "ambient_temperature": sensor_data.ambient_temperature,
                "humidity": sensor_data.humidity,
                "skin_resistance": sensor_data.skin_resistance,
                "risk": sensor_data.risk,
            },
        }
    )
            
    print("✅ ส่งข้อมูลเข้าสู่ WebSocket แล้ว:")


class Command(BaseCommand):
    help = "MQTT start listening!!!"

    def handle(self, *args, **options):
        client = mqtt.Client()
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        client.tls_set(ca_certs="/app/emqxsl-ca.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
        #client.tls_insecure_set(True)
        client.connect(
            host=MQTT_SERVER,
            port=MQTT_PORT,
            keepalive=MQTT_KEEPALIVE
        )
        client.on_connect = on_connect
        client.on_message = on_message
        client.loop_forever()