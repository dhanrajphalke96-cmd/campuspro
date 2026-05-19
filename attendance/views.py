from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Subject, AttendanceSession, Attendance
from students.models import StudentProfile
from core.models import Department, ENGINEERING_DEPARTMENT_CODES
from core.decorators import role_required


@login_required
@role_required('admin', 'principal', 'hod', 'faculty', 'student')
def attendance_dashboard(request):
    if request.user.role == 'hod':
        from core.models import Department
        dept = Department.objects.filter(hod=request.user).first()
        subjects = Subject.objects.filter(is_active=True, department=dept)
        recent_sessions = AttendanceSession.objects.filter(subject__department=dept).select_related('subject', 'faculty').order_by('-date')[:10]
    elif request.user.role == 'faculty':
        subjects = request.user.assigned_subjects.filter(is_active=True)
        recent_sessions = AttendanceSession.objects.filter(faculty=request.user).select_related('subject', 'faculty').order_by('-date')[:10]
    elif request.user.role == 'student':
        subjects = Subject.objects.none()
        recent_sessions = AttendanceSession.objects.none()
    else:
        subjects = Subject.objects.filter(is_active=True).select_related('department')
        recent_sessions = AttendanceSession.objects.select_related('subject', 'faculty').order_by('-date')[:10]

    return render(request, 'attendance/dashboard.html', {
        'subjects': subjects, 'recent_sessions': recent_sessions,
        'total_subjects': subjects.count(),
    })


@login_required
@role_required('faculty', 'admin', 'principal')
def attendance_mark(request):
    if request.user.role == 'faculty':
        subjects = request.user.assigned_subjects.filter(is_active=True)
    else:
        subjects = Subject.objects.filter(is_active=True)
        
    departments = Department.objects.filter(is_active=True, code__in=ENGINEERING_DEPARTMENT_CODES)
    students = []
    selected_subject = None

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        date = request.POST.get('date')
        division = request.POST.get('division', 'A')
        period = request.POST.get('period', 1)

        if subject_id and date:
            selected_subject = Subject.objects.get(pk=subject_id)
            # Verify assignment
            if request.user.role == 'faculty' and not selected_subject.assigned_faculty.filter(pk=request.user.pk).exists():
                messages.error(request, "You are not assigned to teach this subject.")
                return redirect('attendance_dashboard')

            session, created = AttendanceSession.objects.get_or_create(
                subject=selected_subject,
                date=date,
                period=int(period),
                division=division,
                defaults={
                    'faculty': request.user,
                    'semester': selected_subject.semester,
                }
            )

            if session.is_locked and request.user.role != 'admin':
                messages.error(request, "This attendance session is locked and cannot be modified.")
                return redirect('attendance_dashboard')

            if 'save_attendance' in request.POST:
                students_list = StudentProfile.objects.filter(
                    department=selected_subject.department,
                    current_semester=selected_subject.semester,
                    division=division,
                    is_active=True
                )
                count = 0
                for student in students_list:
                    status = request.POST.get(f'status_{student.pk}', 'absent')
                    Attendance.objects.update_or_create(
                        session=session,
                        student=student,
                        defaults={'status': status}
                    )
                    count += 1
                session.is_locked = True
                setattr(session, '_admin_override', True) # Avoid validation error on save if needed
                session.save()
                messages.success(request, f'Attendance saved & locked for {count} students.')
                return redirect('attendance_dashboard')

            students = StudentProfile.objects.filter(
                department=selected_subject.department,
                current_semester=selected_subject.semester,
                division=division,
                is_active=True
            ).select_related('user')

    return render(request, 'attendance/mark.html', {
        'subjects': subjects, 'departments': departments,
        'students': students, 'selected_subject': selected_subject,
        'today': timezone.now().date().isoformat(),
    })


@login_required
@role_required('admin', 'principal', 'hod', 'faculty')
def attendance_report(request):
    departments = Department.objects.filter(is_active=True, code__in=ENGINEERING_DEPARTMENT_CODES)
    if request.user.role == 'hod':
        dept = Department.objects.filter(hod=request.user).first()
        subjects = Subject.objects.filter(is_active=True, department=dept)
        departments = Department.objects.filter(pk=dept.pk) if dept else Department.objects.none()
    elif request.user.role == 'faculty':
        subjects = request.user.assigned_subjects.filter(is_active=True)
        departments = Department.objects.none() # Usually faculty doesn't pick by dept
    else:
        subjects = Subject.objects.filter(is_active=True)
        
    report_data = []

    subject_id = request.GET.get('subject')
    if subject_id:
        subject = Subject.objects.get(pk=subject_id)
        students = StudentProfile.objects.filter(
            department=subject.department,
            current_semester=subject.semester,
            is_active=True
        ).select_related('user')

        for student in students:
            total = Attendance.objects.filter(
                session__subject=subject, student=student
            ).count()
            present = Attendance.objects.filter(
                session__subject=subject, student=student,
                status__in=['present', 'late']
            ).count()
            percentage = (present / total * 100) if total > 0 else 0
            report_data.append({
                'student': student,
                'total': total,
                'present': present,
                'absent': total - present,
                'percentage': round(percentage, 1),
            })

    return render(request, 'attendance/report.html', {
        'departments': departments, 'subjects': subjects,
        'report_data': report_data,
    })
