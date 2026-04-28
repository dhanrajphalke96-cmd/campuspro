from django.contrib import admin
from .models import StaffProfile, LeaveType, LeaveRequest, StaffAttendance

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'department', 'designation', 'date_of_joining', 'is_active']
    list_filter = ['department', 'designation', 'is_active']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name']

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_days_per_year', 'is_active']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['staff', 'leave_type', 'from_date', 'to_date', 'days', 'status']
    list_filter = ['status', 'leave_type']

@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'date', 'check_in', 'check_out', 'status']
    list_filter = ['status', 'date']
