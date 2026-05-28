from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models, transaction
from django.core.exceptions import ValidationError
from core.decorators import role_required
from core.models import CustomUser, Department
from attendance.models import Subject
from .models import StaffProfile, LeaveRequest, LeaveType, StaffAttendance
from .forms import StaffUserForm, StaffProfileForm, LeaveTypeForm

@login_required
@role_required('admin', 'principal', 'hr')
def hrms_dashboard(request):
    today = timezone.now().date()
    staff = StaffProfile.objects.select_related('user', 'department')
    active_staff = staff.filter(is_active=True)
    
    # Advanced Stats
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    approved_today = LeaveRequest.objects.filter(status='approved', updated_at__date=today).count()
    on_leave_today = LeaveRequest.objects.filter(status='approved', from_date__lte=today, to_date__gte=today).count()
    added_this_month = StaffProfile.objects.filter(created_at__month=today.month, created_at__year=today.year).count()
    
    # Pending list inline
    recent_pending = LeaveRequest.objects.filter(status='pending').select_related('staff__user', 'leave_type').order_by('-applied_at')[:5]
    
    # Chart Data
    departments = active_staff.values('department__name').annotate(count=models.Count('id'))
    dept_labels = [d['department__name'] or 'Unassigned' for d in departments]
    dept_counts = [d['count'] for d in departments]

    return render(request, 'hrms/dashboard.html', {
        'staff_list': staff,
        'total_staff': active_staff.count(),
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
@role_required('admin', 'principal', 'hr')
def staff_create(request):
    if request.method == 'POST':
        user_form = StaffUserForm(request.POST)
        profile_form = StaffProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    # Create and configure user
                    user = user_form.save(commit=False)
                    password = user_form.cleaned_data.get('password')
                    user.set_password(password)
                    user.save()
                    
                    # Create and link staff profile
                    profile = profile_form.save(commit=False)
                    profile.user = user
                    profile.save()
                    
                    messages.success(request, f"Staff account for {user.get_full_name() or user.username} created successfully.")
                    return redirect('hrms_dashboard')
            except Exception as e:
                messages.error(request, f"An error occurred during creation: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = StaffUserForm()
        profile_form = StaffProfileForm()
        
    return render(request, 'hrms/staff_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Add New Staff Member'
    })


@login_required
@role_required('admin', 'principal', 'hr')
def staff_edit(request, pk):
    profile = get_object_or_404(StaffProfile, pk=pk)
    user = profile.user
    
    if request.method == 'POST':
        user_form = StaffUserForm(request.POST, instance=user)
        profile_form = StaffProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save(commit=False)
                    password = user_form.cleaned_data.get('password')
                    if password:
                        user.set_password(password)
                    user.save()
                    
                    profile_form.save()
                    
                    messages.success(request, f"Staff profile for {user.get_full_name()} updated successfully.")
                    return redirect('staff_detail', pk=profile.pk)
            except Exception as e:
                messages.error(request, f"An error occurred during update: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = StaffUserForm(instance=user)
        profile_form = StaffProfileForm(instance=profile)
        
    return render(request, 'hrms/staff_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': f"Edit Staff: {user.get_full_name()}"
    })


@login_required
@role_required('admin', 'principal', 'hr')
def staff_toggle_status(request, pk):
    profile = get_object_or_404(StaffProfile, pk=pk)
    user = profile.user
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, "You cannot deactivate your own account.")
        else:
            profile.is_active = not profile.is_active
            user.is_active = not user.is_active
            profile.save()
            user.save()
            status = "activated" if profile.is_active else "deactivated"
            messages.success(request, f"Staff profile for {user.get_full_name()} has been {status}.")
    return redirect('staff_detail', pk=pk)


@login_required
@role_required('admin', 'principal', 'hr', 'hod', 'faculty', 'accountant', 'librarian')
def leave_list(request):
    leaves = LeaveRequest.objects.select_related('staff__user', 'leave_type', 'approved_by')
    # Full access for Admin/Principal/HR and superusers
    if request.user.role in ['admin', 'principal', 'hr'] or request.user.is_superuser:
        pass
    # HOD: access to leaves for staff in their department
    elif request.user.role == 'hod':
        hod_dept = Department.objects.filter(hod=request.user).first()
        if hod_dept:
            leaves = leaves.filter(staff__department=hod_dept)
        else:
            leaves = leaves.none()
    # Other roles: only see their own leave requests
    else:
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
@role_required('admin', 'principal', 'hr', 'hod')
def leave_action(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        # Authorization: HOD can approve/reject only for staff in their department
        if request.user.role == 'hod':
            hod_dept = Department.objects.filter(hod=request.user).first()
            if not hod_dept or leave.staff.department != hod_dept:
                messages.error(request, 'You are not authorized to act on this leave request.')
                return redirect('hrms_leave_list')

        action = request.POST.get('action')
        if action in ['approved', 'rejected']:
            leave.status = action
            leave.approved_by = request.user
            leave.save()
            messages.success(request, f'Leave {action}.')
    return redirect('hrms_leave_list')


@login_required
@role_required('admin', 'principal', 'hr')
def attendance_record(request):
    selected_date_str = request.GET.get('date') or request.POST.get('date')
    if selected_date_str:
        try:
            selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
        
    active_staff = StaffProfile.objects.filter(is_active=True).select_related('user', 'department')
    
    # Fetch existing attendance for this date
    existing_attendance = StaffAttendance.objects.filter(date=selected_date)
    attendance_map = {att.staff_id: att.status for att in existing_attendance}
    
    # Fetch approved leaves for this date to display in UI or validate
    active_leaves = LeaveRequest.objects.filter(
        status='approved',
        from_date__lte=selected_date,
        to_date__gte=selected_date
    ).select_related('staff')
    on_leave_staff_ids = set(lv.staff_id for lv in active_leaves)
    
    if request.method == 'POST':
        saved_count = 0
        errors = []
        for staff in active_staff:
            status = request.POST.get(f'attendance_{staff.id}')
            if status:
                # Overwrite with 'on_leave' if staff has an approved leave
                if staff.id in on_leave_staff_ids:
                    status = 'on_leave'
                
                try:
                    attendance, created = StaffAttendance.objects.get_or_create(
                        staff=staff,
                        date=selected_date,
                        defaults={'status': status}
                    )
                    if not created:
                        attendance.status = status
                        attendance.save()
                    saved_count += 1
                except ValidationError as e:
                    errors.append(f"{staff.user.get_full_name()}: {', '.join(e.messages)}")
                except Exception as e:
                    errors.append(f"{staff.user.get_full_name()}: {str(e)}")
                    
        if errors:
            for err in errors:
                messages.error(request, err)
        if saved_count > 0:
            messages.success(request, f"Attendance successfully saved for {saved_count} staff members on {selected_date}.")
        return redirect(f"{request.path}?date={selected_date}")
        
    # Bundle staff with their attendance statuses and leave flags
    staff_data = []
    for staff in active_staff:
        status = attendance_map.get(staff.id, 'present')  # Default status to present
        on_leave = staff.id in on_leave_staff_ids
        staff_data.append({
            'profile': staff,
            'status': 'on_leave' if on_leave else status,
            'on_leave': on_leave
        })

    return render(request, 'hrms/attendance_record.html', {
        'staff_data': staff_data,
        'selected_date': selected_date,
    })


@login_required
@role_required('admin', 'principal', 'hr')
def attendance_report(request):
    attendance_list = StaffAttendance.objects.select_related('staff__user', 'staff__department').order_by('-date')
    
    # Filters
    date_str = request.GET.get('date')
    if date_str:
        try:
            attendance_list = attendance_list.filter(date=date_str)
        except ValueError:
            pass
            
    department_id = request.GET.get('department')
    if department_id:
        attendance_list = attendance_list.filter(staff__department_id=department_id)
        
    staff_id = request.GET.get('staff')
    if staff_id:
        attendance_list = attendance_list.filter(staff_id=staff_id)
        
    departments = Department.objects.filter(is_active=True)
    staff_members = StaffProfile.objects.filter(is_active=True).select_related('user')
    
    return render(request, 'hrms/attendance_report.html', {
        'attendance_list': attendance_list[:100],  # limit to 100 entries for performance
        'departments': departments,
        'staff_members': staff_members,
        'selected_date': date_str,
        'selected_department': int(department_id) if department_id and department_id.isdigit() else None,
        'selected_staff': int(staff_id) if staff_id and staff_id.isdigit() else None,
    })


@login_required
@role_required('admin', 'principal', 'hr')
def leave_type_list(request):
    leave_types = LeaveType.objects.all()
    return render(request, 'hrms/leave_type_list.html', {'leave_types': leave_types})


@login_required
@role_required('admin', 'principal', 'hr')
def leave_type_create(request):
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Leave type created successfully.")
            return redirect('leave_type_list')
    else:
        form = LeaveTypeForm()
    return render(request, 'hrms/leave_type_form.html', {'form': form, 'title': 'Create Leave Type'})


@login_required
@role_required('admin', 'principal', 'hr')
def leave_type_edit(request, pk):
    leave_type = get_object_or_404(LeaveType, pk=pk)
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=leave_type)
        if form.is_valid():
            form.save()
            messages.success(request, "Leave type updated successfully.")
            return redirect('leave_type_list')
    else:
        form = LeaveTypeForm(instance=leave_type)
    return render(request, 'hrms/leave_type_form.html', {'form': form, 'title': 'Edit Leave Type'})


@login_required
@role_required('hod', 'admin', 'principal')
def assign_subjects(request):
    # HOD can assign subjects to faculty within their department
    if request.user.role == 'hod':
        dept = Department.objects.filter(hod=request.user).first()
    else:
        # Admin/Principal may optionally pass ?department=<id>
        dept_id = request.GET.get('department')
        dept = Department.objects.filter(pk=dept_id).first() if dept_id else None

    if not dept:
        messages.error(request, 'No department found to manage assignments.')
        return redirect('hrms_dashboard')

    subjects = Subject.objects.filter(department=dept, is_active=True)
    staff_members = StaffProfile.objects.filter(department=dept, is_active=True).select_related('user')

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        staff_id = request.POST.get('staff')
        if not subject_id or not staff_id:
            messages.error(request, 'Please select both subject and staff member.')
        else:
            subject = Subject.objects.filter(pk=subject_id, department=dept).first()
            staff = StaffProfile.objects.filter(pk=staff_id, department=dept).first()
            if not subject or not staff:
                messages.error(request, 'Invalid selection or not in your department.')
            else:
                subject.assigned_faculty.add(staff.user)
                messages.success(request, f"{staff.user.get_full_name()} assigned to {subject.name}.")
                return redirect('assign_subjects')

    return render(request, 'hrms/assign_subjects.html', {
        'subjects': subjects,
        'staff_members': staff_members,
        'department': dept,
    })
