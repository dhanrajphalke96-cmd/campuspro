from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from core.decorators import role_required
from .models import StudentProfile, ParentDetail, AcademicHistory


@login_required
@role_required('admin', 'principal', 'hod', 'faculty')
def student_list(request):
    students = StudentProfile.objects.select_related('user', 'department', 'course').filter(is_active=True)
    
    # HOD Isolation: Only show their department's students
    if request.user.role == 'hod':
        from core.models import Department
        hod_dept = Department.objects.filter(hod=request.user).first()
        if hod_dept:
            students = students.filter(department=hod_dept)
        else:
            students = StudentProfile.objects.none()
    search = request.GET.get('search')
    dept = request.GET.get('department')
    semester = request.GET.get('semester')
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search) |
            Q(enrollment_no__icontains=search) | Q(user__email__icontains=search)
        )
    if dept:
        students = students.filter(department_id=dept)
    if semester:
        students = students.filter(current_semester=semester)

    from core.models import Department
    departments = Department.objects.filter(is_active=True)
    return render(request, 'students/list.html', {
        'students': students, 'departments': departments,
        'total': students.count()
    })


@login_required
@role_required('admin', 'principal', 'hod', 'faculty', 'student')
def student_detail(request, pk):
    student = get_object_or_404(StudentProfile.objects.select_related(
        'user', 'department', 'course', 'academic_year'
    ), pk=pk)
    
    # Security: HOD can only view own dept students
    if request.user.role == 'hod':
        from core.models import Department
        hod_dept = Department.objects.filter(hod=request.user).first()
        if hod_dept and student.department != hod_dept:
            messages.error(request, "Access denied. Student belongs to another department.")
            return redirect('dashboard')
            
    # Security: Student can only view their own profile
    if request.user.role == 'student' and request.user != student.user:
        messages.error(request, "Access denied. You can only view your own profile.")
        return redirect('dashboard')
        
    parent = ParentDetail.objects.filter(student=student).first()
    academic = AcademicHistory.objects.filter(student=student).order_by('semester')
    return render(request, 'students/detail.html', {
        'student': student, 'parent': parent, 'academic_history': academic
    })
