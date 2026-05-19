import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_erp.settings')
django.setup()

from core.models import Course
from students.models import StudentProfile
from django.db.models import Count

print("\n========== REMOVED/INACTIVE COURSES ==========\n")

inactive_courses = Course.objects.filter(is_active=False).annotate(
    student_count=Count('studentprofile')
)

if not inactive_courses.exists():
    print("✓ No inactive courses - database is clean!\n")
else:
    print(f"Found {inactive_courses.count()} inactive courses:\n")
    for course in inactive_courses:
        print(f"✗ {course.name} ({course.code})")
        print(f"  Department: {course.department.name} ({course.department.code})")
        print(f"  Students still enrolled: {course.student_count}")
        
        if course.student_count > 0:
            students = StudentProfile.objects.filter(course=course)
            for student in students:
                print(f"    - {student.enrollment_no}: {student.user.get_full_name()}")
        print("")

print("\n========== ACTIVE COURSES ==========\n")
active_courses = Course.objects.filter(is_active=True).annotate(
    student_count=Count('studentprofile')
)

for course in active_courses:
    print(f"✓ {course.name} ({course.code}) - {course.student_count} students")
