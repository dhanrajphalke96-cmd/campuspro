"""
core/views.py
─────────────
Central view logic for CampusPro:
  - Authentication (login / logout)
  - Role-based dashboard dispatch
  - User profile management
  - Notifications
  - Academic administration (departments, courses)
  - Admin: User management (list, assign role, toggle active)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Sum, Q

from .forms import LoginForm, UserProfileForm
from .models import CustomUser, Department, Course, AcademicYear, Notification, ENGINEERING_DEPARTMENT_CODES


# ─────────────────────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────────────────────

def login_view(request):
    """Authenticate user and redirect to role-based dashboard."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            # Honour ?next= redirect but only to safe internal URLs
            next_url = request.GET.get('next', '')
            if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {'form': form})


@require_POST          # Logout MUST be a POST — prevents CSRF logout attacks
@login_required
def logout_view(request):
    """Log the user out and redirect to login page."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


# ─────────────────────────────────────────────────────────────
# DASHBOARD  (role-based dispatch)
# ─────────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    """Render the appropriate dashboard template for the user's role."""
    from hrms.models import LeaveRequest
    from fees.models import FeePayment
    from library.models import Book, BookIssue

    user = request.user
    role = 'admin' if user.is_superuser else user.role

    notifications = Notification.objects.filter(user=user, is_read=False)[:5]
    context = {
        'notifications': notifications,
        'unread_count': notifications.count(),
        'current_year': AcademicYear.objects.filter(is_current=True).first(),
    }

    if role in ('admin', 'principal', 'hr'):
        context.update({
            'total_departments': Department.objects.filter(is_active=True, code__in=ENGINEERING_DEPARTMENT_CODES).count(),
            'pending_leaves': LeaveRequest.objects.filter(status='pending').count(),
            'total_students': CustomUser.objects.filter(role='student').count(),
            'total_faculty': CustomUser.objects.filter(role='faculty').count(),
            'total_staff': CustomUser.objects.exclude(role='student').count(),
        })
        dept_data = Department.objects.filter(is_active=True, code__in=ENGINEERING_DEPARTMENT_CODES).annotate(
            student_count=Count('courses__studentprofile')
        ).values('name', 'student_count')
        context['dept_labels'] = [d['name'] for d in dept_data]
        context['dept_counts'] = [d['student_count'] for d in dept_data]

    elif role == 'hod':
        hod_dept = Department.objects.filter(hod=user).first()
        context['hod_dept'] = hod_dept
        if hod_dept:
            context['total_students'] = CustomUser.objects.filter(
                role='student', student_profile__department=hod_dept
            ).count()
            context['total_faculty'] = CustomUser.objects.filter(
                role='faculty', staff_profile__department=hod_dept
            ).count()
        else:
            context['total_students'] = 0
            context['total_faculty'] = 0

    elif role == 'faculty':
        context['total_subjects'] = user.assigned_subjects.filter(is_active=True).count()

    elif role == 'student':
        context['profile'] = getattr(user, 'student_profile', None)

    elif role == 'accountant':
        context['total_collected'] = (
            FeePayment.objects.filter(status='paid')
            .aggregate(total=Sum('amount_paid'))['total'] or 0
        )
        context['pending_count'] = FeePayment.objects.filter(status='pending').count()

    elif role == 'librarian':
        context['total_books'] = Book.objects.filter(is_active=True).count()
        context['issued_count'] = BookIssue.objects.filter(status='issued').count()
        context['overdue_count'] = BookIssue.objects.filter(status='overdue').count()

    template_map = {
        'admin':      'core/dashboard/admin.html',
        'principal':  'core/dashboard/principal.html',
        'hod':        'core/dashboard/hod.html',
        'faculty':    'core/dashboard/faculty.html',
        'student':    'core/dashboard/student.html',
        'accountant': 'core/dashboard/accountant.html',
        'hr':         'core/dashboard/hr.html',
        'librarian':  'core/dashboard/librarian.html',
    }
    template = template_map.get(role, 'core/dashboard/admin.html')
    return render(request, template, context)


# ─────────────────────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    """View and edit own profile."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'core/profile.html', {'form': form})


# ─────────────────────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────────────────────

@login_required
def notifications_view(request):
    """List the user's last 50 notifications."""
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    return render(request, 'core/notifications.html', {'notifications': notifs})


@login_required
@require_POST          # Prevent marking reads via GET (CSRF-safe)
def mark_notification_read(request, pk):
    """Mark a single notification as read (POST only)."""
    notif = Notification.objects.filter(pk=pk, user=request.user).first()
    if notif:
        notif.is_read = True
        notif.save(update_fields=['is_read'])
    return JsonResponse({'status': 'ok'})


# ─────────────────────────────────────────────────────────────
# ACADEMIC ADMIN
# ─────────────────────────────────────────────────────────────

@login_required
def departments_view(request):
    departments = Department.objects.filter(is_active=True, code__in=ENGINEERING_DEPARTMENT_CODES).select_related('hod')
    return render(request, 'core/departments.html', {'departments': departments})


# ─────────────────────────────────────────────────────────────
# USER MANAGEMENT  (Admin / Superuser only)
# ─────────────────────────────────────────────────────────────

def _is_admin(user):
    return user.is_superuser or user.role == 'admin'


def _is_admin_or_principal(user):
    return user.is_superuser or user.role in ('admin', 'principal')


@login_required
def user_management_view(request):
    """Admin interface: list, search, and filter all users."""
    if not _is_admin_or_principal(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')

    qs = CustomUser.objects.all().order_by('-date_joined')

    role_filter   = request.GET.get('role', '').strip()
    status_filter = request.GET.get('status', '').strip()
    search_q      = request.GET.get('q', '').strip()

    if role_filter:
        valid_roles = [r[0] for r in CustomUser.ROLE_CHOICES]
        if role_filter in valid_roles:
            qs = qs.filter(role=role_filter)

    if status_filter in ('active', 'inactive'):
        qs = qs.filter(is_active=(status_filter == 'active'))

    if search_q:
        qs = qs.filter(
            Q(first_name__icontains=search_q) |
            Q(last_name__icontains=search_q)  |
            Q(username__icontains=search_q)   |
            Q(email__icontains=search_q)
        )

    context = {
        'users':          qs,
        'total_users':    CustomUser.objects.count(),
        'active_users':   CustomUser.objects.filter(is_active=True).count(),
        'inactive_users': CustomUser.objects.filter(is_active=False).count(),
        'roles':          CustomUser.ROLE_CHOICES,
    }
    return render(request, 'core/user_management.html', context)


@login_required
@require_POST
def assign_role_view(request, pk):
    """Admin-only: change a user's role. Cannot change own role."""
    if not _is_admin(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')

    # Prevent privilege escalation on own account
    if request.user.pk == pk:
        messages.error(request, 'You cannot change your own role.')
        return redirect('user_management')

    user = get_object_or_404(CustomUser, pk=pk)
    new_role = request.POST.get('role', '').strip()
    valid_roles = [r[0] for r in CustomUser.ROLE_CHOICES]

    if new_role and new_role in valid_roles:
        user.role = new_role
        user.save(update_fields=['role'])
        messages.success(request, f"Role updated to '{new_role}' for {user.username}.")
    else:
        messages.error(request, 'Invalid role selected.')

    return redirect('user_management')


@login_required
@require_POST
def toggle_user_status_view(request, pk):
    """Admin-only: activate or deactivate a user. Cannot deactivate self."""
    if not _is_admin(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')

    # Prevent self-lockout
    if request.user.pk == pk:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('user_management')

    user = get_object_or_404(CustomUser, pk=pk)
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f"User {user.username} has been {status}.")
    return redirect('user_management')
