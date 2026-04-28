from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department, Course, AcademicYear, Semester, Notification


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('ERP Info', {'fields': ('role', 'phone', 'profile_photo', 'date_of_birth', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('ERP Info', {'fields': ('role', 'phone')}),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'hod', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'course_type', 'duration_years', 'total_seats']
    list_filter = ['course_type', 'department', 'is_active']
    search_fields = ['name', 'code']


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['label', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['number', 'academic_year', 'is_current']
    list_filter = ['academic_year', 'is_current']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['title', 'message']
