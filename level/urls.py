from django.urls import path
from .views import create_group, group_admin_dashboard, view_group, add_member, update_profile, user_profile, delete_member, manage_group

urlpatterns = [
    path("create-group/", create_group, name="create_group"),  # URL สำหรับสร้าง Group
    path("group-admin-dashboard/", group_admin_dashboard, name="group_admin_dashboard"),
    path("group/<int:group_id>/", view_group, name="view_group"),
    path("group/<int:group_id>/add-member/", add_member, name="add_member"),
    path("profile/<int:user_id>/", user_profile, name="user_profile"),
    path("profile/<int:user_id>/update/", update_profile, name="update_profile"),
    path("group/<int:group_id>/manage/", manage_group, name="manage_group"),
    path("group/<int:group_id>/delete_member/<int:member_id>/", delete_member, name="delete_member"),
]
