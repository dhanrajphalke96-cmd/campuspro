from django.core.management.base import BaseCommand
from students.models import StudentProfile
from core.models import Course, Department
from attendance.models import Subject, AttendanceSession, Attendance
from examination.models import Exam, MarksEntry
from django.db.models import Count, Q


class Command(BaseCommand):
    help = 'Show detailed course and student data with orphaned records'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n========== COURSE ANALYSIS ==========\n'))

        # All courses
        all_courses = Course.objects.all().annotate(
            student_count=Count('studentprofile')
        )

        self.stdout.write(self.style.WARNING('ALL COURSES IN DATABASE:\n'))
        for course in all_courses:
            status = "✓ ACTIVE" if course.is_active else "✗ INACTIVE"
            self.stdout.write(
                f'  [{status}] {course.name} ({course.code}) | Dept: {course.department.code} | '
                f'Students: {course.student_count}'
            )

        # Inactive courses with data
        inactive_with_data = all_courses.filter(is_active=False).filter(student_count__gt=0)

        if inactive_with_data.exists():
            self.stdout.write(self.style.ERROR('\n⚠ INACTIVE COURSES WITH STUDENTS:\n'))
            for course in inactive_with_data:
                self.stdout.write(self.style.ERROR(f'  Course: {course.name} ({course.code})'))
                students = StudentProfile.objects.filter(course=course)
                for student in students:
                    self.stdout.write(f'    - {student.enrollment_no}: {student.user.get_full_name()}')
                self.stdout.write('')

        # Check for students without valid courses
        self.stdout.write(self.style.WARNING('\nSTUDENT STATISTICS:\n'))
        total_students = StudentProfile.objects.count()
        active_course_students = StudentProfile.objects.filter(course__is_active=True).count()
        inactive_course_students = StudentProfile.objects.filter(course__is_active=False).count()

        self.stdout.write(f'  Total Students: {total_students}')
        self.stdout.write(f'  In Active Courses: {active_course_students}')
        self.stdout.write(f'  In Inactive Courses: {inactive_course_students}')

        # Check for subjects/exams from inactive departments
        self.stdout.write(self.style.WARNING('\n========== ORPHANED DATA CHECK ==========\n'))

        orphan_subjects = Subject.objects.filter(is_active=False)
        orphan_exams = Exam.objects.filter(subject__is_active=False)
        orphan_marks = MarksEntry.objects.filter(exam__subject__is_active=False)
        orphan_attendance = Attendance.objects.filter(student__course__is_active=False)

        self.stdout.write(f'Inactive Subjects: {orphan_subjects.count()}')
        self.stdout.write(f'Exams for Inactive Subjects: {orphan_exams.count()}')
        self.stdout.write(f'Marks for Inactive Subjects: {orphan_marks.count()}')
        self.stdout.write(f'Attendance Records for Students in Inactive Courses: {orphan_attendance.count()}')

        if orphan_subjects.count() > 0:
            self.stdout.write(self.style.WARNING('\n--- Inactive Subjects ---'))
            for subject in orphan_subjects[:10]:
                self.stdout.write(f'  {subject.name} ({subject.code}) - Dept: {subject.department.code}')
            if orphan_subjects.count() > 10:
                self.stdout.write(f'  ... and {orphan_subjects.count() - 10} more')

        if orphan_exams.count() > 0:
            self.stdout.write(self.style.WARNING('\n--- Exams for Inactive Subjects ---'))
            for exam in orphan_exams[:10]:
                self.stdout.write(f'  {exam.name} - Subject: {exam.subject.name}')
            if orphan_exams.count() > 10:
                self.stdout.write(f'  ... and {orphan_exams.count() - 10} more')

        if orphan_marks.count() > 0:
            self.stdout.write(self.style.ERROR(f'\n⚠ MARKS ENTRIES TO CLEAN UP: {orphan_marks.count()}'))

        if orphan_attendance.count() > 0:
            self.stdout.write(self.style.ERROR(f'\n⚠ ATTENDANCE RECORDS TO CLEAN UP: {orphan_attendance.count()}'))
