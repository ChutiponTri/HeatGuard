"""
URL configuration for heatstroke project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from . import consumers  # สำหรับนำ WebSocket consumer เข้ามา


urlpatterns = [
    path('admin/', admin.site.urls),
    path('sensor/', include('sensor.urls')),
    path("", views.index, name="index"),
    path("information", views.information, name="information"),
    path("login/", views.user_login, name="login"),
    path('logout/', views.user_logout, name='logout'),
    path("register/", views.register, name="register"),
    path("member_dashboard/", views.member_dashboard, name="member_dashboard"),
    path("", include("level.urls")),
]

# URL patterns สำหรับ WebSocket
websocket_urlpatterns = [
    path('ws/sensor/', consumers.SensorConsumer.as_asgi(), name='sensor_data'),  # URL สำหรับ WebSocket
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)