from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from sensor.models import SensorData
import paho.mqtt.client as mqtt
import requests
import json
import sys
import ssl
import os
from sensor.management.commands.gemini import Gemini

sys.path.append("/app")

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
USER_ID = int(os.getenv("USER_ID"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
GEMINI = Gemini()

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
        if risk_int == 0:
            risk = "normal"
        elif risk_int == 1:
            risk = "low"
        elif risk_int == 2:
            risk = "medium"
        elif risk_int == 3:
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

        json_data = {
            "user_id": user.id,
            "username": user.username,
            "timestamp": str(sensor_data.timestamp),
            "heart_rate": sensor_data.heart_rate,
            "skin_temperature": sensor_data.skin_temperature,
            "ambient_temperature": sensor_data.ambient_temperature,
            "humidity": sensor_data.humidity,
            "skin_resistance": sensor_data.skin_resistance,
            "risk": sensor_data.risk,
        }

        output = GEMINI.prompt("Please verify if the user is in risk of Heat Stroke", json_data)
        json_data["ai"] = output.content
        print(output.content)

        # ✅ Broadcast ข้อมูลไปยัง WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "sensor_group", {
                "type": "send_sensor_data",
                "data": json_data,
            }
        )

        if risk_int >= 2:
            risk = risk.replace("high", "emergency")
            message = f"Status of {user.username.capitalize()}\nRisk Level: {risk_int}\n{risk.capitalize()} Condition"
            Telegram.telegram(message)

        print("✅ ส่งข้อมูลเข้าสู่ WebSocket แล้ว:")

    except Exception as e:
        print("Error", e)

class Telegram():
    @staticmethod
    def get_updates():
        url = f"{TELEGRAM_BASE_URL}/getUpdates"
        response = requests.get(url)
        return response.json()
    
    @staticmethod
    def send_message(chat_id, text):
        url = f"{TELEGRAM_BASE_URL}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        response = requests.post(url, data=data)
        return response.json()
    
    @staticmethod
    def telegram(message: str):
        updates = Telegram.get_updates()
        if updates["result"]:
            chat_id = updates["result"][-1]["message"]["chat"]["id"]
            Telegram.send_message(chat_id, message)
 
class Command(BaseCommand):
    help = "MQTT start listening!!!"

    def handle(self, *args, **options):
        print("MQTT command running...")
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        client.tls_set(ca_certs="/app/cert/emqxsl-ca.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
        #client.tls_insecure_set(True)
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.loop_forever()
