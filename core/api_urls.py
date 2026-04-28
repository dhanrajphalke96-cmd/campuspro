from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .api import *

router = DefaultRouter()

# Core
router.register(r'users', CustomUserViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'courses', CourseViewSet)

# Students
router.register(r'students', StudentProfileViewSet)

# Admission
router.register(r'admissions', AdmissionApplicationViewSet)

# Attendance
router.register(r'attendance', AttendanceViewSet)

# Fees
router.register(r'fees', FeePaymentViewSet)

# Examination
router.register(r'exams', ExamViewSet)

# HRMS
router.register(r'staff', StaffProfileViewSet)
router.register(r'leaves', LeaveRequestViewSet)

# Payroll
router.register(r'payslips', PayslipViewSet)

# Library
router.register(r'books', BookViewSet)
router.register(r'book-issues', BookIssueViewSet)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
