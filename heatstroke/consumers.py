# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # ประมวลผลการเชื่อมต่อ WebSocket
        self.room_name = "sensor_room"  # หรือชื่อที่เหมาะสมกับการเชื่อมต่อ
        self.room_group_name = f"sensor_{self.room_name}"

        # กำหนดให้เชื่อมต่อ
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # เมื่อเชื่อมต่อถูกยกเลิก
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # รับข้อมูลจาก WebSocket และส่งกลับ
    async def receive(self, text_data):
        data = json.loads(text_data)
        # ส่งข้อมูลไปยัง group
        data_to_send = {
            "type": "sensor_data",
            "heart_rate": data["heart_rate"],
            "skin_temperature": data["skin_temperature"],
            "ambient_temperature": data["ambient_temperature"],
            "humidity": data["humidity"],
            "skin_resistance": data["skin_resistance"],
            "timestamp": data["timestamp"],
        }

        if "ai" in data.keys():
            data_to_send["ai"] = data["ai"]
            
        await self.channel_layer.group_send(self.room_group_name, data_to_send)

    # ส่งข้อมูลไปยัง WebSocket
    async def sensor_data(self, event):
        # รับข้อมูลที่ส่งมาจาก group
        await self.send(text_data=json.dumps(event))


class GroupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope["url_route"]["kwargs"]["group_id"]  # ดึง group_id จาก URL
        self.group_name = f"group_{self.group_id}"  # ตั้งชื่อกลุ่มสำหรับ WebSocket

        # เชื่อมต่อกลุ่ม (join)
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()  # ยอมรับการเชื่อมต่อ WebSocket

    async def disconnect(self, close_code):
        # ออกจากกลุ่มเมื่อปิดการเชื่อมต่อ
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # รับข้อความจาก WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # ส่งข้อความไปยังกลุ่ม
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_message",
                "message": message
            }
        )

    # ส่งข้อความไปยัง WebSocket
    async def send_message(self, event):
        message = event["message"]

        # ส่งข้อความไปยัง WebSocket
        await self.send(text_data=json.dumps({
            "message": message
        }))