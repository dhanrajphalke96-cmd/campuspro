from django.test import TestCase, Client
from django.urls import reverse
from core.models import CustomUser, Department, Course, AcademicYear
from students.models import StudentProfile
from fees.models import FeeStructure, FeePayment

class FeeDashboardTests(TestCase):
    def setUp(self):
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
        self.client = Client()

    def test_student_can_access_fees_dashboard(self):
        self.client.login(username='student1', password='pass')
        resp = self.client.get(reverse('fees_dashboard'))
        self.assertEqual(resp.status_code, 200)
