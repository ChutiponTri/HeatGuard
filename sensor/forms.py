from django import forms
from .models import SensorData  # นำเข้ารูปแบบโมเดล SensorData

class SensorDataForm(forms.ModelForm):
    class Meta:
        model = SensorData  # ระบุว่าใช้โมเดล SensorData
        fields = ['heart_rate', 'skin_temperature', 'ambient_temperature', 'humidity', 'skin_resistance']
