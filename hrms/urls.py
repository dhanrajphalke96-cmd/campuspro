from django.urls import path
from . import views

urlpatterns = [
    path('', views.hrms_dashboard, name='hrms_dashboard'),
    path('staff/<int:pk>/', views.staff_detail, name='staff_detail'),
    path('leaves/', views.leave_list, name='hrms_leave_list'),
    path('leaves/apply/', views.leave_apply, name='leave_apply'),
    path('leaves/<int:pk>/action/', views.leave_action, name='leave_action'),
]
