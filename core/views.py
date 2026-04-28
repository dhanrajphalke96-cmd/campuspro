from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from .forms import LoginForm, UserProfileForm
from .models import CustomUser, Department, Course, AcademicYear, Notification


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    user = request.user
    role = user.role if not user.is_superuser else 'admin'
    notifications = Notification.objects.filter(user=user, is_read=False)[:5]

    context = {
        'notifications': notifications,
        'unread_count': notifications.count(),
        'current_year': AcademicYear.objects.filter(is_current=True).first(),
    }

    if role in ['admin', 'principal', 'hr']:
        from hrms.models import LeaveRequest
        context['total_departments'] = Department.objects.filter(is_active=True).count()
        context['pending_leaves'] = LeaveRequest.objects.filter(status='pending').count()
        context['total_courses'] = Course.objects.filter(is_active=True).count()
        context['total_students'] = CustomUser.objects.filter(role='student').count()
        context['total_faculty'] = CustomUser.objects.filter(role='faculty').count()
        context['total_staff'] = CustomUser.objects.exclude(role='student').count()

        dept_data = Department.objects.filter(is_active=True).annotate(
            student_count=Count('courses__studentprofile')
        ).values('name', 'student_count')
        context['dept_labels'] = [d['name'] for d in dept_data]
        context['dept_counts'] = [d['student_count'] for d in dept_data]

    elif role == 'hod':
        hod_dept = Department.objects.filter(hod=user).first()
        if hod_dept:
            context['hod_dept'] = hod_dept
            context['total_students'] = CustomUser.objects.filter(role='student', studentprofile__department=hod_dept).count()
            context['total_faculty'] = CustomUser.objects.filter(role='faculty', staff_profile__department=hod_dept).count()
        else:
            context['total_students'] = 0
            context['total_faculty'] = 0

    elif role == 'faculty':
        assigned_subjects = user.assigned_subjects.filter(is_active=True)
        context['total_subjects'] = assigned_subjects.count()

    elif role == 'student':
        if hasattr(user, 'studentprofile'):
            context['profile'] = user.studentprofile

    elif role == 'accountant':
        from fees.models import FeePayment
        context['total_collected'] = FeePayment.objects.filter(status='paid').aggregate(total=Sum('amount_paid'))['total'] or 0
        context['pending_count'] = FeePayment.objects.filter(status='pending').count()

    elif role == 'librarian':
        from library.models import Book, BookIssue
        context['total_books'] = Book.objects.filter(is_active=True).count()
        context['issued_count'] = BookIssue.objects.filter(status='issued').count()
        context['overdue_count'] = BookIssue.objects.filter(status='overdue').count()

    template_map = {
        'admin': 'core/dashboard/admin.html',
        'principal': 'core/dashboard/principal.html',
        'hod': 'core/dashboard/hod.html',
        'faculty': 'core/dashboard/faculty.html',
        'student': 'core/dashboard/student.html',
        'accountant': 'core/dashboard/accountant.html',
        'hr': 'core/dashboard/hr.html',
        'librarian': 'core/dashboard/librarian.html',
    }
    template = template_map.get(role, 'core/dashboard/admin.html')
    return render(request, template, context)


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'core/profile.html', {'form': form})


@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    return render(request, 'core/notifications.html', {'notifications': notifs})


@login_required
def mark_notification_read(request, pk):
    try:
        notif = Notification.objects.get(pk=pk, user=request.user)
        notif.is_read = True
        notif.save()
    except Notification.DoesNotExist:
        pass
    return JsonResponse({'status': 'ok'})


@login_required
def departments_view(request):
    departments = Department.objects.filter(is_active=True).select_related('hod')
    return render(request, 'core/departments.html', {'departments': departments})


@login_required
def courses_view(request):
    courses = Course.objects.filter(is_active=True).select_related('department')
    return render(request, 'core/courses.html', {'courses': courses})

@login_required
def user_management_view(request):
    if request.user.role not in ['admin', 'principal'] and not request.user.is_superuser:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    users = CustomUser.objects.all().order_by('-date_joined')
    
    role_filter = request.GET.get('role')
    status_filter = request.GET.get('status')
    search_q = request.GET.get('q')
    
    if role_filter:
        users = users.filter(role=role_filter)
    if status_filter:
        is_active = status_filter == 'active'
        users = users.filter(is_active=is_active)
    if search_q:
        users = users.filter(Q(first_name__icontains=search_q) | Q(last_name__icontains=search_q) | Q(username__icontains=search_q))
        
    context = {
        'users': users,
        'total_users': CustomUser.objects.count(),
        'active_users': CustomUser.objects.filter(is_active=True).count(),
        'inactive_users': CustomUser.objects.filter(is_active=False).count(),
        'roles': CustomUser.ROLE_CHOICES,
    }
    return render(request, 'core/user_management.html', context)

@login_required
def assign_role_view(request, pk):
    if request.user.role not in ['admin'] and not request.user.is_superuser:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
        
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=pk)
        new_role = request.POST.get('role')
        if new_role:
            user.role = new_role
            user.save()
            messages.success(request, f"Role updated for {user.username}.")
    return redirect('user_management')

@login_required
def toggle_user_status_view(request, pk):
    if request.user.role not in ['admin'] and not request.user.is_superuser:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
        
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User {user.username} {status}.")
    return redirect('user_management')

