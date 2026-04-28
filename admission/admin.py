from django.contrib import admin
from .models import AdmissionApplication, AdmissionDocument, MeritList, AdmissionFeePayment

@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ['application_id', 'first_name', 'last_name', 'course', 'category', 'status', 'applied_at']
    list_filter = ['status', 'category', 'course', 'academic_year']
    search_fields = ['application_id', 'first_name', 'last_name', 'email']

@admin.register(AdmissionDocument)
class AdmissionDocumentAdmin(admin.ModelAdmin):
    list_display = ['application', 'document_type', 'uploaded_at']

@admin.register(MeritList)
class MeritListAdmin(admin.ModelAdmin):
    list_display = ['course', 'academic_year', 'cutoff_marks', 'is_published']

@admin.register(AdmissionFeePayment)
class AdmissionFeePaymentAdmin(admin.ModelAdmin):
    list_display = ['application', 'amount', 'payment_mode', 'status', 'paid_at']
