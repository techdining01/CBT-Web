from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("teacher-admin-profile/<int:user_id>/", views.teacheradminprofile, name="teacheradminprofile"),
    path("profile/", views.view_profile, name="view_profile"),
    # path("edit-user/", views.edit_user, name="edit_profile"),
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("broadcast/send/", views.send_broadcast, name="send_broadcast"),
    path("notification/<int:pk>/read/", views.mark_notification_read, name="mark_notification_read"),

    #user management
    path("approvals/", views.user_approval_list, name="user_approval_list"),
    path("approve/<int:user_id>/", views.approve_user, name="approve_user"),
    path("reject/<int:user_id>/", views.reject_user, name="reject_user"),
    path("pending/<int:user_id>/", views.pending_user, name="pending_user"),
    path('create/user', views.create_user, name='create_user'),
    # path("update-status/<int:user_id>/", views.update_user_status, name="update_user_status"),
    path("edit/<int:user_id>/", views.edit_user, name="edit_user"),
    path("manage/", views.manage_users, name="manage_users"),
    path("manage/load/", views.load_users, name="load_users"),  # AJAX
    path("manage/delete/<int:user_id>/", views.delete_user, name="delete_user"),
    
    ]
