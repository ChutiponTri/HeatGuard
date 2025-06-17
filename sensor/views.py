from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import SensorData
from django.contrib.auth.decorators import login_required
from .forms import SensorDataForm  # import SensorDataForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from datetime import timedelta

@csrf_exempt
#@login_required
def receive_sensor_data(request):
    print("🚨 ฟังก์ชันถูกเรียกแล้ว")
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            user_id = data.get("user_id")
            heart_rate = data.get("heart_rate")
            skin_temperature = data.get("skin_temperature")
            ambient_temperature = data.get("ambient_temperature")
            humidity = data.get("humidity")
            skin_resistance = data.get("skin_resistance")
            risk = data.get("risk", "normal")

            User = get_user_model()
            user = User.objects.get(id=user_id)

            sensor_data = SensorData.objects.create(
                user=user,
                heart_rate=heart_rate,
                skin_temperature=skin_temperature,
                ambient_temperature=ambient_temperature,
                humidity=humidity,
                skin_resistance=skin_resistance,
                risk=risk,
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
            
            print("✅ ส่งข้อมูลเข้าสู่ WebSocket แล้ว:", sensor_data.heart_rate)
            return JsonResponse({"status": "success"})

        except Exception as e:
            import traceback
            traceback.print_exc()  # 👈 แสดง traceback ใน log
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)




#@login_required
#def receive_sensor_data(request):
#    if request.method == "POST":
#        form = SensorDataForm(request.POST)
#        if form.is_valid():
#            # ตั้งค่า user เป็นผู้ใช้ที่ล็อกอินอยู่
#            sensor_data = form.save(commit=False)
#            sensor_data.user = request.user  # ตั้งค่า user เป็นผู้ใช้ที่ล็อกอิน
#            sensor_data.save()  # บันทึกข้อมูล
#            return redirect("index")  # เปลี่ยนไปที่หน้ารายการข้อมูล
#    else:
#        form = SensorDataForm()
#
#    return render(request, 'sensor_data_form.html', {'form': form})
#

@login_required
def display_data(request):
    User = get_user_model()
    user_id = request.GET.get("user_id")

    # ถ้ามี user_id ที่ส่งมา → ใช้ข้อมูลของ user นั้น
    if user_id:
        target_user = get_object_or_404(User, id=user_id)
    else:
        target_user = request.user

    seven_days_ago = timezone.now() - timedelta(days=7)
    sensor_data = SensorData.objects.filter(
        user=target_user,
        timestamp__gte=seven_days_ago
    ).order_by("-timestamp")

    # เตรียมข้อมูลสำหรับกราฟ
    timestamps = [data.timestamp.strftime("%Y-%m-%d %H:%M") for data in sensor_data]
    heart_rates = [data.heart_rate for data in sensor_data]
    temperatures = [data.ambient_temperature for data in sensor_data]
    body_temps = [data.skin_temperature for data in sensor_data]
    humidity_values = [data.humidity for data in sensor_data]
    skin_resistances = [data.skin_resistance for data in sensor_data]
    risks = [map_risk_to_score(data.risk) for data in sensor_data]

    context = {
        "sensor_data": sensor_data,
        "target_user": target_user,
        "timestamps": json.dumps(timestamps),
        "heart_rates": json.dumps(heart_rates),
        "temperatures": json.dumps(temperatures),
        "body_temps": json.dumps(body_temps),
        "humidity_values": json.dumps(humidity_values),
        "risks": json.dumps(risks),
    }

    return render(request, "sensor/display_data.html", context)


def map_risk_to_score(risk):
    if not risk:
        return 0
    risk = risk.lower()
    if risk in ["ปกติ", "normal"]:
        return 0
    elif risk in ["ต่ำ", "low"]:
        return 1
    elif risk in ["กลาง", "medium"]:
        return 2
    elif risk in ["สูง", "high"]:
        return 3
    return 0
