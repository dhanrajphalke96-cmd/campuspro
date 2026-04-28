from django.contrib import admin
from .models import StudentProfile, ParentDetail, AcademicHistory

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['enrollment_no', 'user', 'department', 'course', 'current_semester', 'division', 'is_active']
    list_filter = ['department', 'course', 'current_semester', 'is_active']
    search_fields = ['enrollment_no', 'user__first_name', 'user__last_name']

@admin.register(ParentDetail)
class ParentDetailAdmin(admin.ModelAdmin):
    list_display = ['student', 'father_name', 'mother_name', 'guardian_phone']

@admin.register(AcademicHistory)
class AcademicHistoryAdmin(admin.ModelAdmin):
    list_display = ['student', 'semester', 'sgpa', 'cgpa', 'status']
    list_filter = ['semester', 'status']
