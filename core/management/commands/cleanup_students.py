from django.core.management.base import BaseCommand
from django.db.models import Q
from students.models import StudentProfile
from core.models import Course
from attendance.models import AttendanceSession, Attendance
from examination.models import Exam, MarksEntry


class Command(BaseCommand):
    help = 'Clean up and remove student data from inactive courses or specific courses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--course-code',
            type=str,
            help='Remove all students from a specific course (by code)',
        )
        parser.add_argument(
            '--remove-inactive',
            action='store_true',
            help='Remove all students from inactive courses',
        )
        parser.add_argument(
            '--remove-related-data',
            action='store_true',
            help='Also remove related attendance and marks data when removing students',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', True)
        course_code = options.get('course_code')
        remove_inactive = options.get('remove_inactive')
        remove_related = options.get('remove_related_data')

        if not any([course_code, remove_inactive]):
            self.stdout.write(self.style.WARNING('No action specified. Use --course-code or --remove-inactive'))
            return

        students_to_delete = StudentProfile.objects.none()

        # Get students from specific course
        if course_code:
            try:
                course = Course.objects.get(code=course_code)
                students_to_delete = StudentProfile.objects.filter(course=course)
                self.stdout.write(f'\nCourse found: {course.name} ({course_code})')
                self.stdout.write(f'Students to remove: {students_to_delete.count()}\n')
            except Course.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Course with code {course_code} not found'))
                return

        # Get students from inactive courses
        elif remove_inactive:
            students_to_delete = StudentProfile.objects.filter(course__is_active=False)
            self.stdout.write(f'\nInactive course students to remove: {students_to_delete.count()}\n')

        if students_to_delete.exists():
            # Show details
            for student in students_to_delete:
                self.stdout.write(f'  - {student.enrollment_no}: {student.user.get_full_name()} ({student.course.name})')

            if remove_related:
                # Count related data
                attendance_records = Attendance.objects.filter(student__in=students_to_delete)
                marks_records = MarksEntry.objects.filter(student__in=students_to_delete)
                self.stdout.write(f'\nRelated data to be removed:')
                self.stdout.write(f'  Attendance records: {attendance_records.count()}')
                self.stdout.write(f'  Marks entries: {marks_records.count()}')

            if not dry_run:
                self.stdout.write(self.style.WARNING('\nRemoving students...'))
                if remove_related:
                    Attendance.objects.filter(student__in=students_to_delete).delete()
                    MarksEntry.objects.filter(student__in=students_to_delete).delete()
                    self.stdout.write('✓ Related data removed')
                
                students_to_delete.delete()
                self.stdout.write(self.style.SUCCESS('✓ Students removed'))
            else:
                self.stdout.write(self.style.WARNING('\n(DRY RUN - No data was deleted)'))
                self.stdout.write('Add --remove flag to actually delete the records')
        else:
            self.stdout.write(self.style.SUCCESS('No students found to remove'))
