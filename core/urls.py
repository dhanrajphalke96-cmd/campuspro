from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('departments/', views.departments_view, name='departments'),
    
    # User Management
    path('users/', views.user_management_view, name='user_management'),
    path('users/<int:pk>/assign-role/', views.assign_role_view, name='assign_role'),
    path('users/<int:pk>/toggle-status/', views.toggle_user_status_view, name='toggle_user_status'),
]
