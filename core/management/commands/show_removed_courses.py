from django.core.management.base import BaseCommand
from core.models import Course
from students.models import StudentProfile
from django.db.models import Count


class Command(BaseCommand):
    help = 'Show all removed/inactive courses and their student data'

    def handle(self, *args, **options):
        inactive_courses = Course.objects.filter(is_active=False).annotate(
            student_count=Count('studentprofile')
        )

        self.stdout.write(self.style.SUCCESS('\n========== REMOVED/INACTIVE COURSES ==========\n'))

        if not inactive_courses.exists():
            self.stdout.write(self.style.WARNING('No inactive courses found in database'))
        else:
            for course in inactive_courses:
                self.stdout.write(self.style.ERROR(f'✗ {course.name} ({course.code})'))
                self.stdout.write(f'  Department: {course.department.name} ({course.department.code})')
                self.stdout.write(f'  Students still enrolled: {course.student_count}')
                
                if course.student_count > 0:
                    students = StudentProfile.objects.filter(course=course)
                    for student in students:
                        self.stdout.write(f'    - {student.enrollment_no}: {student.user.get_full_name()}')
                self.stdout.write('')

        # Show active courses for reference
        self.stdout.write(self.style.SUCCESS('\n========== ACTIVE COURSES ==========\n'))
        active_courses = Course.objects.filter(is_active=True).annotate(
            student_count=Count('studentprofile')
        )
        
        for course in active_courses:
            self.stdout.write(f'✓ {course.name} ({course.code}) - {course.student_count} students')
