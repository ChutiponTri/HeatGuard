import paho.mqtt.client as mqtt
import os
import sys
import json
import ssl

sys.path.append("/app")
from sensor.models import SensorData
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

MQTT_BROKER = "vad77f40.ala.asia-southeast1.emqxsl.com"
MQTT_PORT = 8883
MQTT_KEEPALIVE = 60
MQTT_USER = "Heatstroke_all"
MQTT_PASSWORD = "6310611097@Heat"
MQTT_TOPIC = "data"
USER_ID = 10

def on_connect(client, userdata, connect_flags, reason_code, properties):
    if reason_code == 0:
        print("Connected successfully")
        print("MQTT User ID:", USER_ID)
        client.subscribe(MQTT_TOPIC)
    else:
        print("Bad connection. Code:", reason_code)

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print("Disconnected with Reason", reason_code)
    client.reconnect()

def on_message(client, userdata, message: mqtt.MQTTMessage):
    try:
        payload = message.payload.decode()
        print(f"Received message on topic: {message.topic} with payload: {payload}")
        data = json.loads(payload)

        user_id = USER_ID or data.get("user")       # Switch Priority to get Real ID
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
    except Exception as e:
        print("Error", e)
        
class Command(BaseCommand):
    help = "MQTT start listening!!!"

    def handle(self, *args, **options):
        print("MQTT command running...")
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        client.tls_set(ca_certs="/app/emqxsl-ca.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
        #client.tls_insecure_set(True)
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.loop_forever()
