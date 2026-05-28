from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Subject, AttendanceSession, Attendance, Timetable, TimetableEntry
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
        if hasattr(request.user, 'student_profile'):
            student_profile = request.user.student_profile
        else:
            student_profile = None

        if student_profile:
            subjects = Subject.objects.filter(
                department=student_profile.department,
                semester=student_profile.current_semester,
                is_active=True
            ).select_related('department')

            # Calculate detailed subject-wise attendance
            subject_details = []
            overall_total = 0
            overall_present = 0

            for subject in subjects:
                # Total classes/sessions held for this subject, semester, division
                held_sessions = AttendanceSession.objects.filter(
                    subject=subject,
                    semester=student_profile.current_semester,
                    division=student_profile.division
                )
                total_held = held_sessions.count()

                # Attended classes
                attended = Attendance.objects.filter(
                    session__in=held_sessions,
                    student=student_profile,
                    status__in=['present', 'late']
                ).count()

                # Absent classes
                absent = total_held - attended

                # Percentage
                percentage = (attended / total_held * 100) if total_held > 0 else 0

                subject_details.append({
                    'subject': subject,
                    'held': total_held,
                    'present': attended,
                    'absent': absent,
                    'percentage': round(percentage, 1),
                })

                overall_total += total_held
                overall_present += attended

            overall_percentage = (overall_present / overall_total * 100) if overall_total > 0 else 0

            # Get recent 10 attendance records for the student
            recent_student_records = Attendance.objects.filter(
                student=student_profile,
                session__semester=student_profile.current_semester,
                session__division=student_profile.division
            ).select_related('session__subject', 'session__faculty').order_by('-session__date')[:10]

            return render(request, 'attendance/dashboard.html', {
                'subjects': subjects,
                'subject_details': subject_details,
                'overall_total': overall_total,
                'overall_present': overall_present,
                'overall_absent': overall_total - overall_present,
                'overall_percentage': round(overall_percentage, 1),
                'recent_student_records': recent_student_records,
                'total_subjects': subjects.count(),
            })
        else:
            subjects = Subject.objects.none()
            return render(request, 'attendance/dashboard.html', {
                'subjects': subjects,
                'subject_details': [],
                'overall_total': 0,
                'overall_present': 0,
                'overall_absent': 0,
                'overall_percentage': 0,
                'recent_student_records': [],
                'total_subjects': 0,
            })
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
    selected_date = timezone.now().date().isoformat()
    selected_division = 'A'
    selected_period = 1

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        date = request.POST.get('date')
        division = request.POST.get('division', 'A')
        period = request.POST.get('period', 1)

        if date:
            selected_date = date
        if division:
            selected_division = division
        if period:
            selected_period = int(period)

        if subject_id and date:
            selected_subject = Subject.objects.get(pk=subject_id)
            # Verify assignment
            if request.user.role == 'faculty':
                if not selected_subject.assigned_faculty.filter(pk=request.user.pk).exists():
                    messages.error(request, "You are not assigned to teach this subject.")
                    return redirect('attendance_dashboard')
                session_faculty = request.user
            else:
                session_faculty = selected_subject.assigned_faculty.first()
                if not session_faculty:
                    messages.error(request, f"No faculty member is assigned to {selected_subject.name}. Please assign a faculty member first.")
                    return redirect('attendance_dashboard')

            session, created = AttendanceSession.objects.get_or_create(
                subject=selected_subject,
                date=date,
                period=int(period),
                division=division,
                defaults={
                    'faculty': session_faculty,
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

            # Fetch existing attendance if it was already marked for this session
            attendance_map = {att.student_id: att.status for att in Attendance.objects.filter(session=session)}

            students = StudentProfile.objects.filter(
                department=selected_subject.department,
                current_semester=selected_subject.semester,
                division=division,
                is_active=True
            ).select_related('user')

            # Map existing status
            for student in students:
                student.current_status = attendance_map.get(student.pk)

            if not created and attendance_map:
                messages.info(request, "Existing attendance record loaded. You can modify and re-save.")

    return render(request, 'attendance/mark.html', {
        'subjects': subjects, 'departments': departments,
        'students': students, 'selected_subject': selected_subject,
        'today': timezone.now().date().isoformat(),
        'selected_date': selected_date,
        'selected_division': selected_division,
        'selected_period': selected_period,
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

@login_required
@role_required('admin', 'principal', 'hod', 'faculty')
def timetable_list(request):
    if request.user.role == 'hod':
        dept = Department.objects.filter(hod=request.user).first()
        timetables = Timetable.objects.filter(department=dept).order_by('-created_at')
    elif request.user.role == 'faculty':
        timetables = Timetable.objects.filter(created_by=request.user).order_by('-created_at')
    else:
        timetables = Timetable.objects.all().order_by('-created_at')
        
    return render(request, 'attendance/timetable_list.html', {'timetables': timetables})

@login_required
@role_required('hod', 'admin')
def timetable_approve(request, pk):
    from django.shortcuts import get_object_or_404
    timetable = get_object_or_404(Timetable, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            timetable.status = 'approved'
            timetable.approved_by = request.user
            messages.success(request, 'Timetable approved successfully.')
        elif action == 'reject':
            timetable.status = 'rejected'
            timetable.approved_by = request.user
            messages.warning(request, 'Timetable rejected.')
        timetable.save()
    return redirect('timetable_list')
