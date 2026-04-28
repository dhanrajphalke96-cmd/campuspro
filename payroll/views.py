from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from core.decorators import role_required
from .models import SalaryStructure, Payslip


@login_required
@role_required('admin', 'principal', 'accountant', 'hr')
def payroll_dashboard(request):
    structures = SalaryStructure.objects.all()
    recent_payslips = Payslip.objects.select_related('staff__user').order_by('-year', '-month')[:20]
    total_paid = Payslip.objects.filter(status='paid').aggregate(t=Sum('net_salary'))['t'] or 0
    return render(request, 'payroll/dashboard.html', {
        'structures': structures, 'recent_payslips': recent_payslips,
        'total_paid': total_paid,
    })


@login_required
@role_required('admin', 'principal', 'accountant', 'hr', 'hod', 'faculty', 'librarian')
def payslip_list(request):
    payslips = Payslip.objects.select_related('staff__user', 'salary_structure').order_by('-year', '-month')
    if request.user.role not in ['admin', 'principal', 'accountant', 'hr']:
        if hasattr(request.user, 'staff_profile'):
            payslips = payslips.filter(staff=request.user.staff_profile)
        else:
            payslips = payslips.none()
    return render(request, 'payroll/payslip_list.html', {'payslips': payslips})
