from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .api import *

router = DefaultRouter()

# Core
router.register(r'users', CustomUserViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'academic-years', AcademicYearViewSet)
router.register(r'semesters', SemesterViewSet)
router.register(r'notifications', NotificationViewSet)

# Students
router.register(r'students', StudentProfileViewSet)
router.register(r'parents', ParentDetailViewSet)
router.register(r'academic-history', AcademicHistoryViewSet)

# Admission
router.register(r'admissions', AdmissionApplicationViewSet)
router.register(r'admission-documents', AdmissionDocumentViewSet)
router.register(r'admission-fee-payments', AdmissionFeePaymentViewSet)
router.register(r'merit-lists', MeritListViewSet)

# Attendance
router.register(r'subjects', SubjectViewSet)
router.register(r'attendance-sessions', AttendanceSessionViewSet)
router.register(r'attendance', AttendanceViewSet)

# Fees
router.register(r'fee-structures', FeeStructureViewSet)
router.register(r'fees', FeePaymentViewSet)
router.register(r'scholarships', ScholarshipViewSet)

# Examination
router.register(r'exams', ExamViewSet)
router.register(r'marks-entries', MarksEntryViewSet)
router.register(r'results', ResultViewSet)

# HRMS
router.register(r'staff', StaffProfileViewSet)
router.register(r'leaves', LeaveRequestViewSet)
router.register(r'staff-attendance', StaffAttendanceViewSet)

# Payroll
router.register(r'salary-structures', SalaryStructureViewSet)
router.register(r'payslips', PayslipViewSet)

# Library
router.register(r'books', BookViewSet)
router.register(r'library-cards', LibraryCardViewSet)
router.register(r'book-issues', BookIssueViewSet)
router.register(r'fines', FineViewSet)

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
