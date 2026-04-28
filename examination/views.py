from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.decorators import role_required
from .models import Exam, MarksEntry, Result


@login_required
def exam_list(request):
    exams = Exam.objects.select_related('subject', 'academic_year').order_by('-date')
    return render(request, 'examination/list.html', {'exams': exams})


@login_required
def exam_detail(request, pk):
    exam = get_object_or_404(Exam.objects.select_related('subject'), pk=pk)
    marks = MarksEntry.objects.filter(exam=exam).select_related('student__user').order_by('student__enrollment_no')
    return render(request, 'examination/detail.html', {'exam': exam, 'marks': marks})


@login_required
@role_required('faculty', 'admin')
def marks_entry(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    
    if request.user.role == 'faculty' and not exam.subject.assigned_faculty.filter(pk=request.user.pk).exists():
        messages.error(request, "You are not assigned to teach this subject.")
        return redirect('exam_detail', pk=pk)
        
    if exam.is_published:
        messages.error(request, "Cannot enter marks for an already published exam.")
        return redirect('exam_detail', pk=pk)
    from students.models import StudentProfile
    students = StudentProfile.objects.filter(
        department=exam.subject.department,
        current_semester=exam.semester,
        is_active=True
    ).select_related('user')

    if request.method == 'POST':
        count = 0
        for student in students:
            marks = request.POST.get(f'marks_{student.pk}')
            absent = request.POST.get(f'absent_{student.pk}')
            if marks:
                MarksEntry.objects.update_or_create(
                    exam=exam, student=student,
                    defaults={
                        'marks_obtained': float(marks) if not absent else 0,
                        'is_absent': bool(absent),
                        'entered_by': request.user,
                    }
                )
                count += 1
        messages.success(request, f'Marks saved for {count} students.')
        return redirect('exam_detail', pk=pk)

    return render(request, 'examination/marks_entry.html', {
        'exam': exam, 'students': students,
    })


@login_required
def result_list(request):
    results = Result.objects.filter(is_published=True).select_related('student__user', 'academic_year').order_by('-academic_year__start_date', 'semester')
    return render(request, 'examination/results.html', {'results': results})
