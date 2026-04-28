from django.db import models
from core.models import CustomUser, Department


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=15, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    semester = models.IntegerField()
    credits = models.IntegerField(default=3)
    is_elective = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    assigned_faculty = models.ManyToManyField(CustomUser, blank=True, limit_choices_to={'role': 'faculty'}, related_name='assigned_subjects')

    class Meta:
        ordering = ['semester', 'name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class AttendanceSession(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='sessions')
    faculty = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attendance_sessions',
                                 limit_choices_to={'role': 'faculty'})
    date = models.DateField()
    semester = models.IntegerField()
    division = models.CharField(max_length=5, default='A')
    period = models.IntegerField(default=1)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['subject', 'date', 'period', 'division']
        ordering = ['-date']
        
    def clean(self):
        from django.core.exceptions import ValidationError
        # Verify faculty assignment
        if self.faculty and not self.subject.assigned_faculty.filter(pk=self.faculty.pk).exists():
            raise ValidationError(f"Faculty {self.faculty} is not assigned to teach {self.subject.name}.")
            
        # Lock validation
        if self.pk:
            old_instance = AttendanceSession.objects.get(pk=self.pk)
            if old_instance.is_locked and getattr(self, '_admin_override', False) is False:
                # Allow unlocking only if explicitly bypassing it (e.g. handled in views by admins)
                if self.is_locked:
                    raise ValidationError("This attendance session is locked and cannot be modified.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject.code} - {self.date} - Period {self.period}"


class Attendance(models.Model):
    STATUS_CHOICES = [('present', 'Present'), ('absent', 'Absent'), ('late', 'Late')]
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['session', 'student']

    def __str__(self):
        return f"{self.student.enrollment_no} - {self.get_status_display()}"


class AttendanceAlert(models.Model):
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='attendance_alerts')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    alert_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert: {self.student.enrollment_no} - {self.subject.code} ({self.percentage}%)"
