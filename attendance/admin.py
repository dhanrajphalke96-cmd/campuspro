from django.contrib import admin
from .models import Subject, AttendanceSession, Attendance, AttendanceAlert

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'semester', 'credits', 'is_active']
    list_filter = ['department', 'semester', 'is_active']
    search_fields = ['code', 'name']

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'faculty', 'date', 'period', 'division']
    list_filter = ['date', 'subject']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['session', 'student', 'status', 'marked_at']
    list_filter = ['status']

@admin.register(AttendanceAlert)
class AttendanceAlertAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'percentage', 'alert_sent']
