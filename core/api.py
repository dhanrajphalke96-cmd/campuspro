from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# Core Permissions
from core.permissions import (
    IsAdminUserOrReadOnly,
    IsAdminOrHR,
    IsAdminOrAccountant,
    IsAdminOrFaculty,
    IsAdminOrLibrarian,
)

# Core
from core.models import CustomUser, Department, Course, AcademicYear, Semester, Notification, ENGINEERING_DEPARTMENT_CODES
from core.serializers import *

# Students
from students.models import StudentProfile, ParentDetail, AcademicHistory
from students.serializers import *

# Admission
from admission.models import AdmissionApplication, AdmissionDocument, MeritList, AdmissionFeePayment
from admission.serializers import *

# Attendance
from attendance.models import Subject, AttendanceSession, Attendance
from attendance.serializers import *

# Fees
from fees.models import FeePayment, FeeStructure, Scholarship
from fees.serializers import *

# Examination
from examination.models import Exam, MarksEntry, Result
from examination.serializers import *

# HRMS
from hrms.models import StaffProfile, LeaveRequest, StaffAttendance
from hrms.serializers import *

# Payroll
from payroll.models import SalaryStructure, Payslip
from payroll.serializers import *

# Library
from library.models import Book, LibraryCard, BookIssue, Fine
from library.serializers import *


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
        }
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'role']


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.filter(code__in=ENGINEERING_DEPARTMENT_CODES)
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['code', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['department', 'course_type', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['label', 'is_current']
    ordering_fields = ['start_date', 'label']


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['number', 'academic_year', 'is_current']
    ordering_fields = ['number']


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'notification_type', 'is_read']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at']


class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.select_related('user', 'department', 'course', 'academic_year').all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['department', 'course', 'current_semester', 'academic_year', 'is_active']
    search_fields = ['enrollment_no', 'user__first_name', 'user__last_name']
    ordering_fields = ['enrollment_no', 'current_semester']


class ParentDetailViewSet(viewsets.ModelViewSet):
    queryset = ParentDetail.objects.all()
    serializer_class = ParentDetailSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['student']
    ordering_fields = ['student']


class AcademicHistoryViewSet(viewsets.ModelViewSet):
    queryset = AcademicHistory.objects.select_related('student', 'academic_year').all()
    serializer_class = AcademicHistorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['student', 'semester', 'academic_year']
    ordering_fields = ['semester']


class AdmissionApplicationViewSet(viewsets.ModelViewSet):
    queryset = AdmissionApplication.objects.all()
    serializer_class = AdmissionApplicationSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['status', 'course', 'academic_year']
    search_fields = ['application_id', 'first_name', 'last_name', 'email']
    ordering_fields = ['applied_at', 'status']


class AdmissionDocumentViewSet(viewsets.ModelViewSet):
    queryset = AdmissionDocument.objects.all()
    serializer_class = AdmissionDocumentSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['application', 'document_type']
    ordering_fields = ['uploaded_at']


class AdmissionFeePaymentViewSet(viewsets.ModelViewSet):
    queryset = AdmissionFeePayment.objects.all()
    serializer_class = AdmissionFeePaymentSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['status', 'payment_mode', 'application']
    ordering_fields = ['created_at', 'amount']


class MeritListViewSet(viewsets.ModelViewSet):
    queryset = MeritList.objects.all()
    serializer_class = MeritListSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['course', 'academic_year', 'is_published']
    ordering_fields = ['generated_at']


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['department', 'semester', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['semester', 'name']


class AttendanceSessionViewSet(viewsets.ModelViewSet):
    queryset = AttendanceSession.objects.all()
    serializer_class = AttendanceSessionSerializer
    permission_classes = [IsAdminOrFaculty]
    filterset_fields = ['subject', 'faculty', 'date', 'semester', 'division', 'is_locked']
    ordering_fields = ['date', 'subject']


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrFaculty]
    filterset_fields = ['session', 'student', 'status']
    search_fields = ['student__enrollment_no', 'student__user__first_name', 'student__user__last_name', 'session__subject__name']
    ordering_fields = ['marked_at']


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['course', 'academic_year', 'semester', 'is_active']
    ordering_fields = ['semester']


class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer
    permission_classes = [IsAdminOrAccountant]
    filterset_fields = ['student', 'fee_structure', 'status', 'payment_mode']
    search_fields = ['receipt_number', 'student__enrollment_no', 'student__user__first_name', 'student__user__last_name']
    ordering_fields = ['created_at', 'amount_paid']


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.all()
    serializer_class = ScholarshipSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['student', 'academic_year', 'status']
    ordering_fields = ['applied_date']


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAdminOrFaculty]
    filterset_fields = ['subject', 'academic_year', 'semester', 'is_published', 'exam_type']
    search_fields = ['name', 'subject__name']
    ordering_fields = ['date']


class MarksEntryViewSet(viewsets.ModelViewSet):
    queryset = MarksEntry.objects.all()
    serializer_class = MarksEntrySerializer
    permission_classes = [IsAdminOrFaculty]
    filterset_fields = ['exam', 'student', 'entered_by', 'verified']
    ordering_fields = ['created_at']


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAdminOrFaculty]
    filterset_fields = ['student', 'semester', 'academic_year', 'is_published', 'status']
    ordering_fields = ['semester', 'percentage']


class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.all()
    serializer_class = StaffProfileSerializer
    permission_classes = [IsAdminOrHR]
    filterset_fields = ['department', 'designation', 'is_active']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name']
    ordering_fields = ['employee_id']


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['staff', 'leave_type', 'status']
    search_fields = ['staff__employee_id', 'staff__user__first_name', 'staff__user__last_name', 'reason']
    ordering_fields = ['applied_at']


class StaffAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StaffAttendance.objects.all()
    serializer_class = StaffAttendanceSerializer
    permission_classes = [IsAdminOrHR]
    filterset_fields = ['staff', 'date', 'status']
    ordering_fields = ['date']


class SalaryStructureViewSet(viewsets.ModelViewSet):
    queryset = SalaryStructure.objects.all()
    serializer_class = SalaryStructureSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    ordering_fields = ['designation']


class PayslipViewSet(viewsets.ModelViewSet):
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer
    permission_classes = [IsAdminOrHR]
    filterset_fields = ['staff', 'month', 'year', 'status']
    search_fields = ['staff__employee_id', 'staff__user__first_name', 'staff__user__last_name']
    ordering_fields = ['year', 'month']


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrLibrarian]
    filterset_fields = ['category', 'author', 'subject', 'is_active']
    search_fields = ['title', 'author', 'isbn']
    ordering_fields = ['title', 'author']


class LibraryCardViewSet(viewsets.ModelViewSet):
    queryset = LibraryCard.objects.all()
    serializer_class = LibraryCardSerializer
    permission_classes = [IsAdminOrLibrarian]
    filterset_fields = ['student', 'is_active']
    ordering_fields = ['issued_date']


class BookIssueViewSet(viewsets.ModelViewSet):
    queryset = BookIssue.objects.all()
    serializer_class = BookIssueSerializer
    permission_classes = [IsAdminOrLibrarian]
    filterset_fields = ['student', 'book', 'status']
    ordering_fields = ['issue_date', 'due_date']


class FineViewSet(viewsets.ModelViewSet):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer
    permission_classes = [IsAdminOrLibrarian]
    filterset_fields = ['book_issue', 'paid']
    ordering_fields = ['created_at']

