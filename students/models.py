from django.db import models
from core.models import CustomUser, Department, Course, AcademicYear


class StudentProfile(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),
    ]
    CATEGORY_CHOICES = [
        ('general','General'),('obc','OBC'),('sc','SC'),('st','ST'),('ews','EWS'),('nt','NT'),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    enrollment_no = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='studentprofile')
    current_semester = models.IntegerField(default=1)
    division = models.CharField(max_length=5, blank=True, default='A')
    admission_date = models.DateField()
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='general')
    nationality = models.CharField(max_length=30, default='Indian')
    religion = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['enrollment_no']

    def __str__(self):
        return f"{self.enrollment_no} - {self.user.get_full_name()}"


class ParentDetail(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='parent_detail')
    father_name = models.CharField(max_length=100)
    father_occupation = models.CharField(max_length=100, blank=True)
    father_phone = models.CharField(max_length=15, blank=True)
    mother_name = models.CharField(max_length=100)
    mother_occupation = models.CharField(max_length=100, blank=True)
    mother_phone = models.CharField(max_length=15, blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Parents of {self.student.user.get_full_name()}"


class AcademicHistory(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='academic_history')
    semester = models.IntegerField()
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True)
    sgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('pass','Pass'),('fail','Fail'),('backlog','Backlog')], default='pass')
    total_credits = models.IntegerField(default=0)
    earned_credits = models.IntegerField(default=0)

    class Meta:
        unique_together = ['student', 'semester', 'academic_year']
        ordering = ['semester']

    def __str__(self):
        return f"{self.student.enrollment_no} - Sem {self.semester}"
