from django.db import models
from core.models import Course, AcademicYear
import uuid


class AdmissionApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('admitted', 'Admitted'),
    ]
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('obc', 'OBC'),
        ('sc', 'SC'),
        ('st', 'ST'),
        ('ews', 'EWS'),
        ('nt', 'NT'),
    ]
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]

    application_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='general')
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50, default='Maharashtra')
    pincode = models.CharField(max_length=6)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='applications')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='applications')
    previous_qualification = models.CharField(max_length=100, blank=True)
    previous_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    merit_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']

    def save(self, *args, **kwargs):
        if not self.application_id:
            self.application_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.application_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class AdmissionDocument(models.Model):
    DOC_TYPES = [
        ('photo', 'Passport Photo'),
        ('marksheet', '10th/12th Marksheet'),
        ('certificate', 'Leaving Certificate'),
        ('caste', 'Caste Certificate'),
        ('aadhar', 'Aadhar Card'),
        ('other', 'Other'),
    ]
    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOC_TYPES)
    file = models.FileField(upload_to='admission_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.application.application_id}"


class MeritList(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='merit_lists')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    cutoff_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        unique_together = ['course', 'academic_year']

    def __str__(self):
        return f"Merit List - {self.course.name} ({self.academic_year})"


class AdmissionFeePayment(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
        ('card', 'Debit/Credit Card'),
        ('cash', 'Cash'),
        ('dd', 'Demand Draft'),
    ]
    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE, related_name='fee_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=15, choices=PAYMENT_MODE_CHOICES)
    transaction_id = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=10, choices=[('pending','Pending'),('paid','Paid'),('failed','Failed')], default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    receipt_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.receipt_number} - {self.application.application_id}"
