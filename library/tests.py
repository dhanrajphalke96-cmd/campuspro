from django.test import TestCase, Client
from django.urls import reverse
from core.models import CustomUser, Department, Course, AcademicYear
from students.models import StudentProfile
from library.models import Book, BookIssue, LibraryCard

class LibraryIssueTests(TestCase):
    def setUp(self):
        self.librarian_user = CustomUser.objects.create_user(username='lib1', password='pass', role='librarian')
        self.student_user = CustomUser.objects.create_user(username='student1', password='pass', role='student')
        self.dept = Department.objects.create(name='CS', code='CS')
        self.course = Course.objects.create(name='BCA', code='BCA', department=self.dept)
        self.year = AcademicYear.objects.create(label='2025-26', start_date='2025-01-01', end_date='2025-12-31', is_current=True)
        self.student = StudentProfile.objects.create(
            user=self.student_user,
            enrollment_no='ST1',
            department=self.dept,
            course=self.course,
            admission_date='2025-01-01',
            academic_year=self.year
        )
        self.card = LibraryCard.objects.create(
            student=self.student,
            valid_until='2026-12-31'
        )
        self.book = Book.objects.create(
            title='Python Guide',
            author='John Doe',
            total_copies=5,
            available_copies=5
        )
        self.client = Client()

    def test_book_issue_status_is_issued_and_decrements_copies_once(self):
        self.client.login(username='lib1', password='pass')
        resp = self.client.post(reverse('book_issue_create'), {
            'book': self.book.pk,
            'student': self.student.pk,
            'due_days': 14
        })
        self.assertEqual(resp.status_code, 302)
        
        # Check that the issue has status 'issued'
        issue = BookIssue.objects.get(book=self.book, student=self.student)
        self.assertEqual(issue.status, 'issued')
        
        # Check that available copies is exactly 4
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 4)
