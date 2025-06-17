from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth.decorators import login_required
from .models import GroupModel
from .forms import UserProfileForm
from django.views.decorators.csrf import csrf_exempt
from sensor.models import SensorData
from django.contrib.auth import get_user_model

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role")  # รับ Role จากฟอร์ม

        # ตรวจสอบข้อมูล
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        # สร้างผู้ใช้ใหม่
        user = CustomUser.objects.create_user(
            username=username, email=email, password=password1, role=role
        )
        user.save()

        messages.success(request, "Account created successfully.")
        login(request, user)
        return redirect("login")
    return render(request, "register.html")

@login_required
def create_group(request):
    if not request.user.is_group_admin():
        messages.error(request, "Only Group Admins can create groups.")
        return redirect("index")

    if request.method == "POST":
        group_name = request.POST.get("group_name")
        description = request.POST.get("description")

        if GroupModel.objects.filter(name=group_name).exists():
            messages.error(request, "This group name is already taken.")
        else:
            group = GroupModel.objects.create(name=group_name, description=description, created_by=request.user)
            messages.success(request, f"Group '{group.name}' created successfully!")
            return redirect("group_admin_dashboard")

    return render(request, "create_group.html")

@csrf_exempt
@login_required
def group_admin_dashboard(request):
    user_groups = GroupModel.objects.filter(created_by=request.user)  #  ดึงเฉพาะ Group ที่ User สร้าง
    return render(request, "group_admin_dashboard.html", {"user_groups": user_groups})

@csrf_exempt
@login_required
def view_group(request, group_id):
    # ดึงกลุ่มจากฐานข้อมูล
    group = get_object_or_404(GroupModel, id=group_id)

    # สมาชิกทั้งหมดในกลุ่มนี้
    members = group.members.all()

    # สร้าง dict เก็บข้อมูล sensor ล่าสุดของแต่ละสมาชิก
    sensor_data_dict = {}

    for member in members:
        latest_data = SensorData.objects.filter(user=member).order_by("-timestamp").first()
        member.latest_sensor = latest_data
        if latest_data:
            sensor_data_dict[member.id] = latest_data

    # ส่ง group, members และข้อมูล sensor แต่ละคนไปให้ template
    return render(request, "view_group.html", {
        "group": group,
        "members": members,
        "sensor_data_dict": sensor_data_dict,
    })

@csrf_exempt
@login_required
def add_member(request, group_id):
    group = get_object_or_404(GroupModel, id=group_id)

    # ✅ ตรวจสอบว่าเฉพาะ Group Admin เท่านั้นที่สามารถเพิ่มสมาชิกได้
    if request.user != group.created_by:
        messages.error(request, "Only the Group Admin can add members.")
        return redirect("view_group", group_id=group.id)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        try:
            user = CustomUser.objects.get(id=user_id)
            if user in group.members.all():
                messages.error(request, f"User ID {user_id} is already a member of this group.")
            else:
                group.members.add(user)  # ✅ เพิ่มผู้ใช้เข้ากลุ่ม
                messages.success(request, f"User ID {user_id} has been added to the group!")
        except CustomUser.DoesNotExist:
            messages.error(request, "User ID not found.")

    return render(request, "add_member.html", {"group": group})
    
@csrf_exempt
@login_required
def update_profile(request, user_id):
    # ดึงข้อมูลผู้ใช้จากฐานข้อมูลโดยใช้ user_id
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("user_profile", user_id=user.id)  # ส่ง user_id ไปใน redirect
    else:
        form = UserProfileForm(instance=user)

    return render(request, "update_profile.html", {"form": form})

@csrf_exempt
@login_required
def user_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    group = None
    if request.user.role == 'group_admin':
        group = GroupModel.objects.filter(created_by=request.user).first()  # หรือ logic ที่เหมาะสมกับโมเดลของคุณ

    return render(request, "user_profile.html", {"user": user, "group": group})

@csrf_exempt
@login_required
def manage_group(request, group_id):
    User = get_user_model()
    group = get_object_or_404(GroupModel, id=group_id, created_by=request.user)
    members = group.members.all()
    return render(request, 'manage_group.html', {
        'group': group,
        'members': members
    })

@csrf_exempt
@login_required
def delete_member(request, group_id, member_id):
    User = get_user_model()
    group = get_object_or_404(GroupModel, id=group_id, created_by=request.user)
    member = get_object_or_404(User, id=member_id)

    if request.method == "POST":
        group.members.remove(member)
        return redirect('manage_group', group_id=group.id)

