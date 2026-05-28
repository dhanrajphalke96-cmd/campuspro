from django.test import TestCase, Client
from django.urls import reverse
from core.models import CustomUser, Department, Course, AcademicYear
from students.models import StudentProfile
from attendance.models import Subject, AttendanceSession, Attendance

class AttendanceMarkTests(TestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_user(username='admin1', password='pass', role='admin')
        self.faculty_user = CustomUser.objects.create_user(username='faculty1', password='pass', role='faculty')
        self.dept = Department.objects.create(name='CS', code='CS')
        self.course = Course.objects.create(name='BCA', code='BCA', department=self.dept)
        self.year = AcademicYear.objects.create(label='2025-26', start_date='2025-01-01', end_date='2025-12-31', is_current=True)
        self.student_user = CustomUser.objects.create_user(username='student1', password='pass', role='student')
        self.student = StudentProfile.objects.create(
            user=self.student_user,
            enrollment_no='ST1',
            department=self.dept,
            course=self.course,
            admission_date='2025-01-01',
            academic_year=self.year
        )
        self.subject = Subject.objects.create(name='Algo', code='CS101', department=self.dept, semester=1)
        self.subject.assigned_faculty.add(self.faculty_user)
        self.client = Client()

    def test_admin_can_mark_attendance_without_crashing(self):
        self.client.login(username='admin1', password='pass')
        resp = self.client.post(reverse('attendance_mark'), {
            'subject': self.subject.pk,
            'date': '2026-01-01',
            'division': 'A',
            'period': 1
        })
        self.assertEqual(resp.status_code, 200)
