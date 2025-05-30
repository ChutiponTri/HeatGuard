from django.contrib import admin
from .models import SensorData

class SensorDataAdmin(admin.ModelAdmin):
    list_display = ["user", "heart_rate", "skin_temperature", "ambient_temperature", "humidity", "skin_resistance", "timestamp"]

admin.site.register(SensorData, SensorDataAdmin)
