from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

# Core Permissions
from core.permissions import IsAdminUserOrReadOnly, IsAdminOrHR, IsAdminOrAccountant, IsAdminOrFaculty, IsAdminOrLibrarian

# Core
from core.models import CustomUser, Department, Course, AcademicYear, Semester, Notification
from core.serializers import *

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminUserOrReadOnly]

# Students
from students.models import StudentProfile, ParentDetail, AcademicHistory
from students.serializers import *

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAdminUserOrReadOnly]

# Admission
from admission.models import AdmissionApplication, MeritList
from admission.serializers import *

class AdmissionApplicationViewSet(viewsets.ModelViewSet):
    queryset = AdmissionApplication.objects.all()
    serializer_class = AdmissionApplicationSerializer
    permission_classes = [IsAdminUserOrReadOnly]

# Attendance
from attendance.models import Attendance, AttendanceSession
from attendance.serializers import *

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrFaculty]

# Fees
from fees.models import FeePayment, FeeStructure
from fees.serializers import *

class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer
    permission_classes = [IsAdminOrAccountant]

# Examination
from examination.models import Exam, Result
from examination.serializers import *

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAdminOrFaculty]

# HRMS
from hrms.models import StaffProfile, LeaveRequest
from hrms.serializers import *

class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.all()
    serializer_class = StaffProfileSerializer
    permission_classes = [IsAdminOrHR]

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

# Payroll
from payroll.models import Payslip
from payroll.serializers import *

class PayslipViewSet(viewsets.ModelViewSet):
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer
    permission_classes = [IsAdminOrHR]

# Library
from library.models import Book, BookIssue
from library.serializers import *

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrLibrarian]

class BookIssueViewSet(viewsets.ModelViewSet):
    queryset = BookIssue.objects.all()
    serializer_class = BookIssueSerializer
    permission_classes = [IsAdminOrLibrarian]

