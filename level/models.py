from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("site_admin", "Site Admin"),     # ผู้ดูแลเว็บไซต์
        ("group_admin", "Group Admin"),  # ผู้ดูแลกลุ่ม
        ("member", "Member"),            # สมาชิกกลุ่ม
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default="member")

    groups = models.ManyToManyField(
        "GroupModel",
        related_name="group_members",  # ✅ เปลี่ยน related_name เพื่อไม่ให้ชนกับ GroupModel
        blank=True
    )
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    age = models.IntegerField(null=True, blank=True)  # อายุ
    height = models.FloatField(null=True, blank=True)  # ส่วนสูง
    weight = models.FloatField(null=True, blank=True)  # น้ำหนัก

    def is_site_admin(self):
        return self.role == "site_admin"

    def is_group_admin(self):
        return self.role == "group_admin"

    def is_member(self):
        return self.role == "member"

    def formatted_id(self):
        """แสดง ID เป็น 3 หลัก เช่น 001, 002, 100"""
        return str(self.id).zfill(3)

    def save(self, *args, **kwargs):
        if self.is_staff and self.role not in ["site_admin"]:
            self.role = "site_admin"
        super().save(*args, **kwargs)

    def __str__(self):
        """แสดง ID เป็น 3 หลักตอนแสดงใน Django Admin หรือ QuerySet"""
        return f"{self.username} (ID: {self.formatted_id()})"


class GroupModel(models.Model):
    name = models.CharField(max_length=100, unique=True)  # ชื่อ Group (ห้ามซ้ำ)
    description = models.TextField(blank=True, null=True)  # คำอธิบาย Group
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_groups"
    )  # ผู้สร้างกลุ่ม

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="user_groups",  #  เปลี่ยน related_name ให้ไม่ชนกัน
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)  # วันที่สร้างอัตโนมัติ

    def __str__(self):
        return self.name
