from django.db import models
from students.models import StudentProfile
import uuid


class Book(models.Model):
    CATEGORY_CHOICES = [
        ('textbook', 'Textbook'), ('reference', 'Reference'),
        ('journal', 'Journal'), ('magazine', 'Magazine'),
        ('fiction', 'Fiction'), ('non_fiction', 'Non-Fiction'),
        ('research', 'Research Paper'), ('other', 'Other'),
    ]
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True, blank=True, verbose_name='ISBN')
    publisher = models.CharField(max_length=100, blank=True)
    edition = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='textbook')
    subject = models.CharField(max_length=100, blank=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    shelf_number = models.CharField(max_length=20, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author}"


class LibraryCard(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='library_card')
    card_number = models.CharField(max_length=20, unique=True, editable=False)
    issued_date = models.DateField(auto_now_add=True)
    valid_until = models.DateField()
    max_books = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.card_number:
            self.card_number = f"LIB-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.card_number} - {self.student.user.get_full_name()}"


class BookIssue(models.Model):
    STATUS_CHOICES = [('requested', 'Requested'), ('issued', 'Issued'), ('returned', 'Returned'), ('overdue', 'Overdue')]
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='book_issues')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='requested')
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ['-issue_date']
        
    def clean(self):
        from django.core.exceptions import ValidationError
        # 1. Prevent generating multiple active issues (requested/issued/overdue) for the same book by the same student
        active_statuses = ['requested', 'issued', 'overdue']
        if self.status in active_statuses:
            existing_issues = BookIssue.objects.filter(
                book=self.book, student=self.student, status__in=active_statuses
            ).exclude(pk=self.pk)
            if existing_issues.exists():
                raise ValidationError("Student already has an active request or issue for this book.")
                
        # 2. Check max books allowed
        if self.status == 'issued' or self.status == 'requested':
            if hasattr(self.student, 'library_card'):
                card = self.student.library_card
                active_count = BookIssue.objects.filter(
                    student=self.student, status__in=['issued', 'overdue']
                ).exclude(pk=self.pk).count()
                if active_count >= card.max_books:
                    raise ValidationError(f"Student has reached the maximum library issue limit ({card.max_books}).")
            else:
                raise ValidationError("Student does not have an assigned library card.")
                
        # 3. Prevent issuing unavailable books
        if not self.pk and self.status == 'issued':
            if self.book.available_copies <= 0:
                raise ValidationError("No copies of this book are available.")

    def save(self, *args, **kwargs):
        from django.utils import timezone
        
        # Calculate fine automatically if returning
        if self.status == 'returned' and self.return_date and self.due_date:
            if self.return_date > self.due_date:
                days_late = (self.return_date - self.due_date).days
                if days_late > 0:
                    self.fine_amount = days_late * 5  # Rule: Rs 5 per day late
                    
        # Track previous status and adjust copies
        if self.pk:
            old_instance = BookIssue.objects.get(pk=self.pk)
            if old_instance.status in ['requested'] and self.status == 'issued':
                self.book.available_copies -= 1
                self.book.save()
            elif old_instance.status in ['issued', 'overdue'] and self.status == 'returned':
                self.book.available_copies += 1
                self.book.save()
        else:
            # If created directly as issued
            if self.status == 'issued':
                self.book.available_copies -= 1
                self.book.save()
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} -> {self.student.enrollment_no}"


class Fine(models.Model):
    book_issue = models.ForeignKey(BookIssue, on_delete=models.CASCADE, related_name='fines')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    reason = models.CharField(max_length=100, default='Late return')
    paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fine ₹{self.amount} - {self.book_issue}"
