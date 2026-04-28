from django.contrib import admin
from .models import Exam, MarksEntry, Result, HallTicket

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'subject', 'date', 'total_marks', 'is_published']
    list_filter = ['exam_type', 'is_published', 'academic_year']

@admin.register(MarksEntry)
class MarksEntryAdmin(admin.ModelAdmin):
    list_display = ['exam', 'student', 'marks_obtained', 'is_absent', 'verified']
    list_filter = ['exam', 'verified']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'semester', 'sgpa', 'cgpa', 'percentage', 'status', 'is_published']
    list_filter = ['semester', 'status', 'is_published']

@admin.register(HallTicket)
class HallTicketAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam_name', 'seat_number', 'generated_at']
