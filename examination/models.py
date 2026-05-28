from django.db import models
from core.models import AcademicYear
from attendance.models import Subject
from students.models import StudentProfile


class Exam(models.Model):
    EXAM_TYPE_CHOICES = [
        ('internal', 'Internal'), ('external', 'External'),
        ('practical', 'Practical'), ('viva', 'Viva'),
    ]
    name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    semester = models.IntegerField()
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    total_marks = models.IntegerField(default=100)
    passing_marks = models.IntegerField(default=40)
    is_moderated = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} - {self.subject.name}"


class MarksEntry(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marks')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='marks')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    is_absent = models.BooleanField(default=False)
    remarks = models.CharField(max_length=100, blank=True)
    entered_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['exam', 'student']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.pk:
            old = MarksEntry.objects.get(pk=self.pk)
            if old.exam.is_published:
                raise ValidationError("Cannot modify marks after the exam result is published.")
        elif self.exam.is_published:
            raise ValidationError("Cannot enter marks for an already published exam.")


    @property
    def is_pass(self):
        return self.marks_obtained >= self.exam.passing_marks

    def __str__(self):
        return f"{self.student.enrollment_no} - {self.exam.name}: {self.marks_obtained}"


class Result(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='results')
    semester = models.IntegerField()
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    sgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_marks = models.IntegerField(default=0)
    obtained_marks = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=[
        ('pass','Pass'),('fail','Fail'),('backlog','Backlog'),('withheld','Withheld')
    ], default='pass')
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'semester', 'academic_year']

    def save(self, *args, **kwargs):
        # Auto-flag backlog if percentage < 40
        if self.status != 'withheld' and self.percentage is not None:
            if self.percentage < 40 or self.status == 'fail':
                self.status = 'backlog'
            elif self.percentage >= 40 and self.status == 'backlog':
                self.status = 'pass'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.enrollment_no} - Sem {self.semester} - {self.status}"


class HallTicket(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='hall_tickets')
    exam_name = models.CharField(max_length=100)
    semester = models.IntegerField()
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=20)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Hall Ticket - {self.student.enrollment_no} - {self.exam_name}"
