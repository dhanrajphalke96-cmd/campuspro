from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Book, LibraryCard, BookIssue, Fine


@login_required
def library_dashboard(request):
    books = Book.objects.filter(is_active=True)
    search = request.GET.get('search')
    category = request.GET.get('category')
    if search:
        books = books.filter(Q(title__icontains=search) | Q(author__icontains=search) | Q(isbn__icontains=search))
    if category:
        books = books.filter(category=category)

    total_books = Book.objects.filter(is_active=True).count()
    issued_count = BookIssue.objects.filter(status='issued').count()
    overdue_count = BookIssue.objects.filter(status='overdue').count()

    return render(request, 'library/dashboard.html', {
        'books': books, 'total_books': total_books,
        'issued_count': issued_count, 'overdue_count': overdue_count,
    })


@login_required
def book_issue_list(request):
    issues = BookIssue.objects.select_related('book', 'student__user').order_by('-issue_date')
    return render(request, 'library/issue_list.html', {'issues': issues})


@login_required
@role_required('librarian')
def book_issue_create(request):
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=request.POST['book'])
        from students.models import StudentProfile
        student = get_object_or_404(StudentProfile, pk=request.POST['student'])
        due_days = int(request.POST.get('due_days', 14))

        if book.available_copies <= 0:
            messages.error(request, 'No copies available.')
            return redirect('book_issue_create')

        from datetime import timedelta
        issue = BookIssue.objects.create(
            book=book, student=student,
            due_date=timezone.now().date() + timedelta(days=due_days),
            status='issued',
        )
        messages.success(request, f'Book issued to {student.user.get_full_name()}.')
        return redirect('book_issue_list')

    books = Book.objects.filter(is_active=True, available_copies__gt=0)
    from students.models import StudentProfile
    students = StudentProfile.objects.filter(is_active=True).select_related('user')
    return render(request, 'library/issue_create.html', {'books': books, 'students': students})


@login_required
@role_required('librarian')
def book_return(request, pk):
    issue = get_object_or_404(BookIssue, pk=pk)
    if request.method == 'POST':
        issue.return_date = timezone.now().date()
        issue.status = 'returned'
        # Fine calculation
        if issue.return_date > issue.due_date:
            days_late = (issue.return_date - issue.due_date).days
            fine_amount = days_late * 5  # ₹5 per day
            issue.fine_amount = fine_amount
            Fine.objects.create(book_issue=issue, amount=fine_amount)
        issue.save()
        issue.book.available_copies += 1
        issue.book.save()
        messages.success(request, f'Book returned. Fine: ₹{issue.fine_amount}')
        return redirect('book_issue_list')
    return render(request, 'library/book_return.html', {'issue': issue})


@login_required
@role_required('librarian')
def library_card_list(request):
    cards = LibraryCard.objects.select_related('student__user').filter(is_active=True)
    return render(request, 'library/card_list.html', {'cards': cards})
