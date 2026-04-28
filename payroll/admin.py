from django.contrib import admin
from .models import SalaryStructure, Payslip, Allowance, Deduction

@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['designation', 'basic_pay', 'gross_salary', 'total_deductions', 'net_salary']

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ['staff', 'month', 'year', 'net_salary', 'status']
    list_filter = ['status', 'month', 'year']

@admin.register(Allowance)
class AllowanceAdmin(admin.ModelAdmin):
    list_display = ['payslip', 'name', 'amount']

@admin.register(Deduction)
class DeductionAdmin(admin.ModelAdmin):
    list_display = ['payslip', 'name', 'amount']
