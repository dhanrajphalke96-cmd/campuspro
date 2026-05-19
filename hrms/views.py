from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from core.decorators import role_required
from .models import StaffProfile, LeaveRequest, LeaveType, StaffAttendance
from django.db import models


@login_required
@role_required('admin', 'principal', 'hr')
def hrms_dashboard(request):
    today = timezone.now().date()
    staff = StaffProfile.objects.filter(is_active=True).select_related('user', 'department')
    
    # Advanced Stats
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    approved_today = LeaveRequest.objects.filter(status='approved', updated_at__date=today).count()
    on_leave_today = LeaveRequest.objects.filter(status='approved', from_date__lte=today, to_date__gte=today).count()
    added_this_month = StaffProfile.objects.filter(created_at__month=today.month, created_at__year=today.year).count()
    
    # Pending list inline
    recent_pending = LeaveRequest.objects.filter(status='pending').select_related('staff__user', 'leave_type').order_by('-applied_at')[:5]
    
    # Chart Data
    departments = staff.values('department__name').annotate(count=models.Count('id'))
    dept_labels = [d['department__name'] or 'Unassigned' for d in departments]
    dept_counts = [d['count'] for d in departments]

    return render(request, 'hrms/dashboard.html', {
        'staff_list': staff,
        'total_staff': staff.count(),
        'pending_leaves': pending_leaves,
        'approved_today': approved_today,
        'on_leave_today': on_leave_today,
        'added_this_month': added_this_month,
        'recent_pending': recent_pending,
        'dept_labels': dept_labels,
        'dept_counts': dept_counts,
    })


@login_required
@role_required('admin', 'principal', 'hr')
def staff_detail(request, pk):
    staff = get_object_or_404(StaffProfile.objects.select_related('user', 'department'), pk=pk)
    leaves = LeaveRequest.objects.filter(staff=staff).order_by('-applied_at')[:10]
    return render(request, 'hrms/staff_detail.html', {'staff': staff, 'leaves': leaves})


@login_required
@role_required('admin', 'principal', 'hr', 'hod', 'faculty', 'accountant', 'librarian')
def leave_list(request):
    leaves = LeaveRequest.objects.select_related('staff__user', 'leave_type', 'approved_by')
    if request.user.role not in ['admin', 'principal', 'hr'] and not request.user.is_superuser:
        if hasattr(request.user, 'staff_profile'):
            leaves = leaves.filter(staff=request.user.staff_profile)
        else:
            leaves = leaves.none()
            
    status = request.GET.get('status')
    if status:
        leaves = leaves.filter(status=status)
    return render(request, 'hrms/leave_list.html', {'leaves': leaves})


@login_required
@role_required('admin', 'principal', 'hr', 'hod', 'faculty', 'accountant', 'librarian')
def leave_apply(request):
    # Ensure user has a StaffProfile
    staff = StaffProfile.objects.filter(user=request.user).first()
    if not staff:
        messages.error(request, 'You do not have a Staff Profile set up yet. Please contact your administrator to create one before applying for leave.')
        return redirect('hrms_leave_list')

    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        leave_type_id = request.POST.get('leave_type')
        reason = request.POST.get('reason')

        if not all([from_date, to_date, leave_type_id, reason]):
            messages.error(request, 'All fields are required.')
        else:
            LeaveRequest.objects.create(
                staff=staff,
                leave_type_id=leave_type_id,
                from_date=from_date,
                to_date=to_date,
                reason=reason,
            )
            messages.success(request, 'Leave request submitted successfully.')
            return redirect('hrms_leave_list')

    leave_types = LeaveType.objects.filter(is_active=True)
    return render(request, 'hrms/leave_apply.html', {'leave_types': leave_types, 'staff': staff})


@login_required
@role_required('admin', 'principal', 'hr')
def leave_action(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['approved', 'rejected']:
            leave.status = action
            leave.approved_by = request.user
            leave.save()
            messages.success(request, f'Leave {action}.')
    return redirect('hrms_leave_list')
