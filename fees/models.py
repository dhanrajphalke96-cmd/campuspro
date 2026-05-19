from django.db import models
from core.models import Course, AcademicYear
from students.models import StudentProfile
import uuid


class FeeStructure(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='fee_structures')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    semester = models.IntegerField()
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exam_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    library_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sports_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    development_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField(null=True, blank=True)
    late_fee_per_day = models.DecimalField(max_digits=6, decimal_places=2, default=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['course', 'academic_year', 'semester']

    @property
    def total_fee(self):
        return (self.tuition_fee + self.exam_fee + self.library_fee +
                self.lab_fee + self.sports_fee + self.development_fee + self.other_fee)

    def __str__(self):
        return f"{self.course.name} - Sem {self.semester} - {self.academic_year}"


class FeePayment(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('upi', 'UPI'), ('netbanking', 'Net Banking'),
        ('card', 'Debit/Credit Card'), ('cash', 'Cash'), ('dd', 'Demand Draft'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'), ('refunded', 'Refunded'),
    ]
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='fee_payments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='payments')
    receipt_number = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=15, choices=PAYMENT_MODE_CHOICES)
    transaction_id = models.CharField(max_length=50, blank=True)
    installment_number = models.IntegerField(default=1)
    late_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Payment immutability logic
        if self.pk:
            old = FeePayment.objects.get(pk=self.pk)
            # Once paid, it can only be modified to explicitly refunded
            if old.status == 'paid' and self.status not in ['paid', 'refunded']:
                raise ValidationError("A paid fee record cannot be modified unless it is being refunded.")
            if old.status == 'refunded' and self.status != 'refunded':
                raise ValidationError("A refunded fee record cannot be modified.")

    def save(self, *args, **kwargs):
        from django.utils import timezone
        
        self.clean()
        
        # Auto late fee calculation
        if self.status != 'paid' and self.fee_structure.due_date:
            today = timezone.now().date()
            if today > self.fee_structure.due_date:
                days_late = (today - self.fee_structure.due_date).days
                if days_late > 0:
                    self.late_fee = days_late * self.fee_structure.late_fee_per_day
        
        # Only assign receipt when paid/pending receipt flow
        if not self.receipt_number and self.status == 'paid':
            self.receipt_number = f"RCP-{uuid.uuid4().hex[:8].upper()}"
            self.paid_at = timezone.now()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receipt_number} - {self.student.enrollment_no}"


class Scholarship(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='scholarships')
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True)
    applied_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[
        ('applied','Applied'),('approved','Approved'),('rejected','Rejected'),('disbursed','Disbursed')
    ], default='applied')

    def __str__(self):
        return f"{self.name} - {self.student.enrollment_no}"


class FeeReminder(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='fee_reminders')
    message = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.student.enrollment_no}"


class PurchaseRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    item_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_by = models.ForeignKey('core.CustomUser', on_delete=models.CASCADE, related_name='purchase_requests')
    approved_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_purchases')
    approval_remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.item_name} ({self.quantity}) - {self.status}"

