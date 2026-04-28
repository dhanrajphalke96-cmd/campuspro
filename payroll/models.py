from django.db import models
from hrms.models import StaffProfile


class SalaryStructure(models.Model):
    designation = models.CharField(max_length=50, unique=True)
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='HRA')
    da = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='DA')
    ta = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='TA')
    medical = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pf_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='PF')
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Tax')
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=200)

    @property
    def gross_salary(self):
        return self.basic_pay + self.hra + self.da + self.ta + self.medical

    @property
    def total_deductions(self):
        return self.pf_deduction + self.tax_deduction + self.professional_tax

    @property
    def net_salary(self):
        return self.gross_salary - self.total_deductions

    def __str__(self):
        return f"{self.designation} - ₹{self.net_salary}"


class Payslip(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('processed', 'Processed'), ('paid', 'Paid')]
    MONTH_CHOICES = [(i, m) for i, m in enumerate(
        ['', 'January', 'February', 'March', 'April', 'May', 'June',
         'July', 'August', 'September', 'October', 'November', 'December'], 0
    ) if i > 0]

    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='payslips')
    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.SET_NULL, null=True)
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    bank_reference = models.CharField(max_length=50, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['staff', 'month', 'year']
        ordering = ['-year', '-month']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.pk:
            old = Payslip.objects.get(pk=self.pk)
            if old.status in ['processed', 'paid'] and self.status not in ['processed', 'paid']:
                raise ValidationError("Cannot revert the status of a processed or paid payslip.")
            if old.status == 'paid' and self.status != 'paid':
                raise ValidationError("Cannot modify a paid payslip.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.staff.employee_id} - {self.get_month_display()} {self.year}"


class Allowance(models.Model):
    payslip = models.ForeignKey(Payslip, on_delete=models.CASCADE, related_name='allowances')
    name = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"


class Deduction(models.Model):
    payslip = models.ForeignKey(Payslip, on_delete=models.CASCADE, related_name='deductions')
    name = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"
