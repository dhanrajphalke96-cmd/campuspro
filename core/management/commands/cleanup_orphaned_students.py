from django.core.management.base import BaseCommand
from students.models import StudentProfile
from core.models import Course


class Command(BaseCommand):
    help = 'Remove students from inactive/deleted courses or find orphaned student records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Only check and display orphaned students without deleting',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete students from inactive courses',
        )

    def handle(self, *args, **options):
        check_only = options.get('check', True)
        delete = options.get('delete', False)

        # Find students with inactive courses
        inactive_students = StudentProfile.objects.filter(course__is_active=False)
        deleted_courses = StudentProfile.objects.filter(course__isnull=True)

        total_inactive = inactive_students.count()
        total_deleted_ref = deleted_courses.count()

        self.stdout.write(self.style.WARNING(f'\n=== ORPHANED STUDENT RECORDS ===\n'))
        self.stdout.write(self.style.WARNING(f'Students with INACTIVE courses: {total_inactive}'))
        self.stdout.write(self.style.WARNING(f'Students with DELETED course references: {total_deleted_ref}'))

        if total_inactive > 0:
            self.stdout.write(self.style.SUCCESS('\n--- Students in Inactive Courses ---'))
            for student in inactive_students:
                self.stdout.write(f'  Enrollment: {student.enrollment_no} | User: {student.user.get_full_name()} | Course: {student.course.name} (ID: {student.course.id})')

        if total_deleted_ref > 0:
            self.stdout.write(self.style.SUCCESS('\n--- Students with Deleted Course References ---'))
            for student in deleted_courses:
                self.stdout.write(f'  Enrollment: {student.enrollment_no} | User: {student.user.get_full_name()} | Course: NULL')

        if delete:
            if total_inactive > 0:
                self.stdout.write(self.style.WARNING(f'\nDeleting {total_inactive} students from inactive courses...'))
                inactive_students.delete()
                self.stdout.write(self.style.SUCCESS('✓ Inactive course students deleted'))

            if total_deleted_ref > 0:
                self.stdout.write(self.style.WARNING(f'\nDeleting {total_deleted_ref} students with null course references...'))
                deleted_courses.delete()
                self.stdout.write(self.style.SUCCESS('✓ Orphaned students deleted'))

            self.stdout.write(self.style.SUCCESS(f'\n✓ Total cleaned up: {total_inactive + total_deleted_ref} records'))
        else:
            self.stdout.write(self.style.WARNING('\n⚠ Run with --delete flag to remove these records'))
            self.stdout.write(self.style.WARNING('Example: python manage.py cleanup_orphaned_students --delete\n'))
