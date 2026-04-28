from django.db import models
from core.models import CustomUser, Department


class StaffProfile(models.Model):
    DESIGNATION_CHOICES = [
        ('professor', 'Professor'), ('assoc_professor', 'Associate Professor'),
        ('asst_professor', 'Assistant Professor'), ('lecturer', 'Lecturer'),
        ('lab_assistant', 'Lab Assistant'), ('clerk', 'Clerk'),
        ('librarian', 'Librarian'), ('accountant', 'Accountant'),
        ('peon', 'Peon'), ('other', 'Other'),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='staff')
    designation = models.CharField(max_length=20, choices=DESIGNATION_CHOICES, default='lecturer')
    date_of_joining = models.DateField()
    qualification = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(default=0)
    specialization = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"


class LeaveType(models.Model):
    name = models.CharField(max_length=50)
    max_days_per_year = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('approved', 'Approved'),
        ('rejected', 'Rejected'), ('cancelled', 'Cancelled'),
    ]
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']

    @property
    def days(self):
        return (self.to_date - self.from_date).days + 1

    def __str__(self):
        return f"{self.staff.employee_id} - {self.leave_type.name} ({self.days} days)"


class StaffAttendance(models.Model):
    STATUS_CHOICES = [('present', 'Present'), ('absent', 'Absent'), ('half_day', 'Half Day'), ('on_leave', 'On Leave')]
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')

    class Meta:
        unique_together = ['staff', 'date']
        ordering = ['-date']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.status in ['present', 'half_day']:
            overlapping_leave = LeaveRequest.objects.filter(
                staff=self.staff,
                status='approved',
                from_date__lte=self.date,
                to_date__gte=self.date
            ).exists()
            if overlapping_leave:
                raise ValidationError("Cannot mark present/half-day; staff has an approved leave on this date.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.staff.employee_id} - {self.date} - {self.status}"
