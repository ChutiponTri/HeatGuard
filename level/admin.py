from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("role",)}),
    )
    list_display = ["formatted_id", "username", "email", "role", "is_staff", "is_active"]  # เปลี่ยนจาก id เป็น formatted_id
    list_filter = ["role", "is_staff", "is_active"]

    def formatted_id(self, obj):
        """ แสดง ID เป็น 3 หลัก เช่น 001, 002, 100 """
        return str(obj.id).zfill(3)

    formatted_id.admin_order_field = "id"  # เรียงลำดับตาม id ได้
    formatted_id.short_description = "User ID"  # เปลี่ยนชื่อคอลัมน์ใน Admin เป็น "User ID"

admin.site.register(CustomUser, CustomUserAdmin)
