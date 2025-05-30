from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from level.models import CustomUser


def user_login(request):
    if request.user.is_authenticated:
        return redirect("index")  # หากล็อกอินแล้ว ให้ไปหน้า index
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def user_logout(request):
    logout(request)
    return redirect("login")

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        try:
            validate_password(password1)  # ตรวจสอบความแข็งแกร่งของรหัสผ่าน
        except ValidationError as e:
            messages.error(request, e.messages[0])  # แสดงข้อความแจ้งข้อผิดพลาด
            return redirect("register")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        user = CustomUser.objects.create_user(username=username, email=email, password=password1, role=role)
        user.save()
        messages.success(request, "Account created successfully.")
        login(request, user)
        return redirect("index")
    return render(request, "register.html")

# ฟังก์ชันสำหรับหน้า Index (ต้องล็อกอินก่อน)
@login_required
def index(request):
    if request.user.is_authenticated:
        if request.user.is_site_admin():
            return redirect("site_admin_dashboard") #ตรงนี้ต้องแก้
        elif request.user.is_group_admin():
            return redirect("group_admin_dashboard")
        elif request.user.is_member():
            return redirect("member_dashboard")
    return redirect("login")  # หากไม่ผ่านเงื่อนไขใดเลย ให้ไปหน้า login

    
@login_required
def member_dashboard(request):
    return render(request, "receive.html") #ควรเปลี่ยนเป็น receive

def information(request):
    return render(request, "information.html")
        