from django.urls import path
from . import views

urlpatterns = [
    path('', views.hrms_dashboard, name='hrms_dashboard'),
    path('staff/create/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/', views.staff_detail, name='staff_detail'),
    path('staff/<int:pk>/edit/', views.staff_edit, name='staff_edit'),
    path('staff/<int:pk>/toggle-status/', views.staff_toggle_status, name='staff_toggle_status'),
    path('leaves/', views.leave_list, name='hrms_leave_list'),
    path('leaves/apply/', views.leave_apply, name='leave_apply'),
    path('leaves/<int:pk>/action/', views.leave_action, name='leave_action'),
    path('attendance/record/', views.attendance_record, name='attendance_record'),
    path('attendance/report/', views.attendance_report, name='attendance_report'),
    path('leave-types/', views.leave_type_list, name='leave_type_list'),
    path('leave-types/create/', views.leave_type_create, name='leave_type_create'),
    path('leave-types/<int:pk>/edit/', views.leave_type_edit, name='leave_type_edit'),
    path('assign-subjects/', views.assign_subjects, name='assign_subjects'),
]
