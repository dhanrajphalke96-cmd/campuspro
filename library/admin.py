from django.contrib import admin
from .models import Book, LibraryCard, BookIssue, Fine

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'category', 'total_copies', 'available_copies']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'author', 'isbn']

@admin.register(LibraryCard)
class LibraryCardAdmin(admin.ModelAdmin):
    list_display = ['card_number', 'student', 'valid_until', 'is_active']
    list_filter = ['is_active']

@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ['book', 'student', 'issue_date', 'due_date', 'return_date', 'status', 'fine_amount']
    list_filter = ['status']

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ['book_issue', 'amount', 'paid', 'payment_date']
    list_filter = ['paid']
