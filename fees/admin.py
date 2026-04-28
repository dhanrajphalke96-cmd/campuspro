from django.contrib import admin
from .models import FeeStructure, FeePayment, Scholarship, FeeReminder

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['course', 'semester', 'academic_year', 'total_fee', 'is_active']
    list_filter = ['course', 'academic_year', 'is_active']

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'student', 'amount_paid', 'payment_mode', 'status', 'paid_at']
    list_filter = ['status', 'payment_mode']
    search_fields = ['receipt_number', 'student__enrollment_no']

@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ['name', 'student', 'amount', 'status']
    list_filter = ['status']

@admin.register(FeeReminder)
class FeeReminderAdmin(admin.ModelAdmin):
    list_display = ['student', 'sent_date', 'is_sent']
