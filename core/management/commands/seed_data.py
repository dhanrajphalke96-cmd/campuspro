from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random

from core.models import CustomUser, Department, Course, AcademicYear, Semester, Notification, ENGINEERING_DEPARTMENT_CODES
from students.models import StudentProfile, ParentDetail, AcademicHistory
from attendance.models import Subject
from fees.models import FeeStructure
from hrms.models import StaffProfile, LeaveType
from payroll.models import SalaryStructure
from library.models import Book, LibraryCard


class Command(BaseCommand):
    help = 'Seed the database with demo data for College ERP'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...\n')

        # ─── Remove non-engineering departments ───
        Department.objects.exclude(code__in=ENGINEERING_DEPARTMENT_CODES).delete()

        # ─── Academic Year & Semesters ───
        ay, _ = AcademicYear.objects.get_or_create(
            label='2025-26',
            defaults={'start_date': date(2025, 6, 1), 'end_date': date(2026, 5, 31), 'is_current': True}
        )
        for i in range(1, 9):
            Semester.objects.get_or_create(number=i, academic_year=ay)
        self.stdout.write(self.style.SUCCESS('[OK] Academic Year & Semesters'))

        # ─── Departments ───
        depts_data = [
            ('Computer Science', 'CS'),
            ('Electronics and Telecommunication', 'ENTC'),
            ('Mechanical Engineering', 'ME'),
            ('Civil Engineering', 'CE'),
            ('Artificial Intelligence and Data Science', 'AIDS'),
        ]
        depts = {}
        for name, code in depts_data:
            dept, _ = Department.objects.get_or_create(code=code, defaults={'name': name})
            depts[code] = dept
        self.stdout.write(self.style.SUCCESS('[OK] Departments'))

        # ─── Courses ───
        courses_data = [
            ('B.Tech Computer Science', 'BT_CS', 'CS', 'UG', 4, 8, 60),
            ('B.Tech Electronics and Telecommunication', 'BT_ENTC', 'ENTC', 'UG', 4, 8, 60),
            ('B.Tech Mechanical Engineering', 'BT_ME', 'ME', 'UG', 4, 8, 60),
            ('B.Tech Civil Engineering', 'BT_CE', 'CE', 'UG', 4, 8, 60),
            ('B.Tech AI and Data Science', 'BT_AIDS', 'AIDS', 'UG', 4, 8, 60),
        ]
        courses = {}
        for name, code, dept_code, ctype, dur, sems, seats in courses_data:
            course, _ = Course.objects.get_or_create(
                code=code,
                defaults={'name': name, 'department': depts[dept_code], 'course_type': ctype,
                          'duration_years': dur, 'total_semesters': sems, 'total_seats': seats}
            )
            courses[code] = course
        self.stdout.write(self.style.SUCCESS('[OK] Courses'))

        # ─── Admin User ───
        admin_user, created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'System', 'last_name': 'Admin',
                'email': 'admin@college.edu', 'role': 'admin',
                'is_staff': True, 'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()

        # ─── Principal ───
        principal, created = CustomUser.objects.get_or_create(
            username='principal',
            defaults={
                'first_name': 'Dr. Rajesh', 'last_name': 'Sharma',
                'email': 'principal@college.edu', 'role': 'principal',
            }
        )
        if created:
            principal.set_password('pass123')
            principal.save()

        # ─── HODs ───
        hod_names = [
            ('hod_cs', 'Dr. Amit', 'Patel', 'CS'),
            ('hod_entc', 'Dr. Sunita', 'Deshmukh', 'ENTC'),
            ('hod_me', 'Dr. Manoj', 'Kulkarni', 'ME'),
            ('hod_ce', 'Dr. Ramesh', 'Joshi', 'CE'),
            ('hod_aids', 'Dr. Priya', 'Sharma', 'AIDS'),
        ]
        for uname, fname, lname, dept_code in hod_names:
            hod, created = CustomUser.objects.get_or_create(
                username=uname,
                defaults={'first_name': fname, 'last_name': lname,
                          'email': f'{uname}@college.edu', 'role': 'hod'}
            )
            if created:
                hod.set_password('pass123')
                hod.save()
            depts[dept_code].hod = hod
            depts[dept_code].save()

        # ─── Faculty ───
        faculty_data = [
            ('faculty1', 'Priya', 'Joshi', 'CS'), ('faculty2', 'Rahul', 'Singh', 'CS'),
            ('faculty3', 'Neha', 'Gupta', 'ENTC'), ('faculty4', 'Vikram', 'Mehta', 'ENTC'),
            ('faculty5', 'Anjali', 'Patil', 'ME'), ('faculty6', 'Sanjay', 'Kumar', 'ME'),
            ('faculty7', 'Pooja', 'Reddy', 'CE'), ('faculty8', 'Arjun', 'Nair', 'CE'),
            ('faculty9', 'Rina', 'Kadam', 'AIDS'), ('faculty10', 'Amit', 'Desai', 'AIDS'),
        ]
        faculty_users = []
        for uname, fname, lname, dept_code in faculty_data:
            fu, created = CustomUser.objects.get_or_create(
                username=uname,
                defaults={'first_name': fname, 'last_name': lname,
                          'email': f'{uname}@college.edu', 'role': 'faculty',
                          'phone': f'98765{random.randint(10000,99999)}'}
            )
            if created:
                fu.set_password('pass123')
                fu.save()
            faculty_users.append((fu, dept_code))
        self.stdout.write(self.style.SUCCESS('[OK] Faculty Users'))

        # ─── Staff Profiles ───
        designations = ['professor', 'assoc_professor', 'asst_professor', 'lecturer']
        for i, (fu, dept_code) in enumerate(faculty_users):
            StaffProfile.objects.get_or_create(
                user=fu,
                defaults={
                    'employee_id': f'EMP-{1001+i}',
                    'department': depts[dept_code],
                    'designation': designations[i % len(designations)],
                    'date_of_joining': date(2020, 1, 1) + timedelta(days=random.randint(0, 1000)),
                    'qualification': random.choice(['Ph.D', 'M.Tech', 'M.Sc']),
                    'experience_years': random.randint(2, 20),
                }
            )

        # ─── Other Role Users ───
        other_roles = [
            ('accountant1', 'Ravi', 'Verma', 'accountant'),
            ('hr1', 'Meera', 'Saxena', 'hr'),
            ('librarian1', 'Deepak', 'Yadav', 'librarian'),
        ]
        for uname, fname, lname, role in other_roles:
            u, created = CustomUser.objects.get_or_create(
                username=uname,
                defaults={'first_name': fname, 'last_name': lname,
                          'email': f'{uname}@college.edu', 'role': role}
            )
            if created:
                u.set_password('pass123')
                u.save()
            # Staff profile for these users too
            StaffProfile.objects.get_or_create(
                user=u,
                defaults={
                    'employee_id': f'EMP-{2001 + list(r[0] for r in other_roles).index(uname)}',
                    'department': depts['CS'],
                    'designation': 'other',
                    'date_of_joining': date(2021, 7, 1),
                }
            )
        self.stdout.write(self.style.SUCCESS('[OK] Staff & Other Roles'))

        # ─── Students ───
        first_names = ['Aarav', 'Ananya', 'Arjun', 'Diya', 'Ishaan', 'Kavya', 'Rohan', 'Riya',
                       'Vihaan', 'Aisha', 'Atharv', 'Saanvi', 'Reyansh', 'Myra', 'Krishna',
                       'Anika', 'Vivaan', 'Pari', 'Aditya', 'Zara', 'Sai', 'Tanvi', 'Harsh',
                       'Nisha', 'Pranav', 'Kiara', 'Dhruv', 'Isha', 'Yash', 'Meera']
        last_names = ['Patil', 'Sharma', 'Singh', 'Kumar', 'Deshmukh', 'Joshi', 'Gupta',
                      'Reddy', 'Patel', 'Mehta', 'Kulkarni', 'Verma', 'Nair', 'Yadav', 'Kadam']
        categories = ['general', 'obc', 'sc', 'st', 'ews']
        blood_groups = ['A+', 'B+', 'O+', 'AB+', 'A-', 'B-']

        course_keys = list(courses.keys())
        student_count = 0
        for i in range(50):
            fname = first_names[i % len(first_names)]
            lname = last_names[i % len(last_names)]
            uname = f'student{i+1}'

            su, created = CustomUser.objects.get_or_create(
                username=uname,
                defaults={
                    'first_name': fname, 'last_name': lname,
                    'email': f'{uname}@student.college.edu', 'role': 'student',
                    'phone': f'97{random.randint(10000000,99999999)}',
                    'date_of_birth': date(2000 + random.randint(0, 5), random.randint(1, 12), random.randint(1, 28)),
                }
            )
            if created:
                su.set_password('pass123')
                su.save()

            course_code = course_keys[i % len(course_keys)]
            course = courses[course_code]
            sem = random.randint(1, min(course.total_semesters, 6))

            sp, sp_created = StudentProfile.objects.get_or_create(
                user=su,
                defaults={
                    'enrollment_no': f'{course.code}-{2024}-{1001+i}',
                    'department': course.department,
                    'course': course,
                    'current_semester': sem,
                    'division': random.choice(['A', 'B']),
                    'admission_date': date(2024, 7, 1),
                    'academic_year': ay,
                    'blood_group': random.choice(blood_groups),
                    'category': random.choice(categories),
                }
            )
            if sp_created:
                student_count += 1
                # Parent detail
                ParentDetail.objects.get_or_create(
                    student=sp,
                    defaults={
                        'father_name': f'{random.choice(first_names)} {lname}',
                        'mother_name': f'{random.choice(first_names)} {lname}',
                        'father_phone': f'98{random.randint(10000000,99999999)}',
                        'annual_income': random.randint(200000, 1500000),
                    }
                )
        self.stdout.write(self.style.SUCCESS(f'[OK] {student_count} Students'))

        # ─── Subjects ───
        subjects_data = [
            ('Engineering Mathematics I', 'CS101', 'CS', 1), ('Programming Fundamentals', 'CS102', 'CS', 1),
            ('Data Structures', 'CS201', 'CS', 3), ('Operating Systems', 'CS301', 'CS', 5),
            ('Digital Electronics', 'ENTC201', 'ENTC', 2), ('Analog Communication', 'ENTC301', 'ENTC', 3),
            ('Microprocessors', 'ENTC401', 'ENTC', 7), ('Circuit Theory', 'ENTC101', 'ENTC', 1),
            ('Engineering Mechanics', 'ME201', 'ME', 2), ('Thermodynamics', 'ME301', 'ME', 3),
            ('Machine Design', 'ME401', 'ME', 7), ('Structural Analysis', 'CE201', 'CE', 2),
            ('Fluid Mechanics', 'CE301', 'CE', 3), ('Reinforced Concrete Design', 'CE401', 'CE', 7),
            ('Machine Learning', 'AIDS201', 'AIDS', 2), ('Deep Learning', 'AIDS301', 'AIDS', 3),
            ('Data Science Fundamentals', 'AIDS101', 'AIDS', 1), ('Python for Data Science', 'AIDS102', 'AIDS', 1),
        ]
        for name, code, dept_code, sem in subjects_data:
            Subject.objects.get_or_create(
                code=code,
                defaults={'name': name, 'department': depts[dept_code], 'semester': sem, 'credits': random.choice([3, 4])}
            )
        self.stdout.write(self.style.SUCCESS('[OK] Subjects'))

        # ─── Fee Structures ───
        for code, course in courses.items():
            for sem in range(1, course.total_semesters + 1):
                base = 25000 if course.course_type == 'UG' else 40000
                FeeStructure.objects.get_or_create(
                    course=course, academic_year=ay, semester=sem,
                    defaults={
                        'tuition_fee': base, 'exam_fee': 2000,
                        'library_fee': 1000, 'lab_fee': 1500,
                        'sports_fee': 500, 'development_fee': 1000,
                        'due_date': date(2025, 7, 15) if sem % 2 == 1 else date(2026, 1, 15),
                    }
                )
        self.stdout.write(self.style.SUCCESS('[OK] Fee Structures'))

        # ─── Leave Types ───
        for name, days in [('Casual Leave', 12), ('Sick Leave', 10), ('Earned Leave', 15), ('Maternity Leave', 180)]:
            LeaveType.objects.get_or_create(name=name, defaults={'max_days_per_year': days})
        self.stdout.write(self.style.SUCCESS('[OK] Leave Types'))

        # ─── Salary Structures ───
        salary_data = [
            ('Professor', 120000, 24000, 12000, 5000, 3000, 14400, 10000, 200),
            ('Associate Professor', 90000, 18000, 9000, 4000, 2500, 10800, 7500, 200),
            ('Assistant Professor', 65000, 13000, 6500, 3000, 2000, 7800, 5000, 200),
            ('Lecturer', 45000, 9000, 4500, 2000, 1500, 5400, 3000, 200),
            ('Lab Assistant', 25000, 5000, 2500, 1000, 1000, 3000, 1500, 200),
            ('Clerk', 22000, 4400, 2200, 800, 800, 2640, 1200, 200),
        ]
        for desig, basic, hra, da, ta, med, pf, tax, pt in salary_data:
            SalaryStructure.objects.get_or_create(
                designation=desig,
                defaults={
                    'basic_pay': basic, 'hra': hra, 'da': da, 'ta': ta,
                    'medical': med, 'pf_deduction': pf, 'tax_deduction': tax,
                    'professional_tax': pt,
                }
            )
        self.stdout.write(self.style.SUCCESS('[OK] Salary Structures'))

        # ─── Library Books ───
        books_data = [
            ('Introduction to Algorithms', 'Cormen, Leiserson', '9780262033848', 'textbook', 'Computer Science'),
            ('Database System Concepts', 'Silberschatz', '9780078022159', 'textbook', 'Computer Science'),
            ('Operating System Concepts', 'Galvin', '9781119800361', 'textbook', 'Computer Science'),
            ('Computer Networking', 'Kurose', '9780133594140', 'textbook', 'Electronics'),
            ('Python Crash Course', 'Eric Matthes', '9781593279288', 'textbook', 'Computer Science'),
            ('Clean Code', 'Robert C. Martin', '9780132350884', 'reference', 'Software Engineering'),
            ('Design Patterns', 'Gang of Four', '9780201633610', 'reference', 'Software Engineering'),
            ('Artificial Intelligence', 'Stuart Russell', '9780134610993', 'textbook', 'Artificial Intelligence'),
            ('Engineering Economics', 'K. K. Dewett', '9788181312285', 'textbook', 'Engineering Economics'),
            ('Engineering Management', 'S. Datta', '9780070666487', 'textbook', 'Engineering Management'),
            ('Engineering Mathematics', 'B.S. Grewal', '9788174091154', 'textbook', 'Engineering Mathematics'),
            ('Digital Electronics', 'Morris Mano', '9780132774208', 'textbook', 'Electronics'),
            ('Discrete Mathematics', 'Kenneth Rosen', '9780073383095', 'textbook', 'Engineering Mathematics'),
            ('Applied Thermodynamics', 'R.K. Rajput', '9788121920450', 'textbook', 'Mechanical Engineering'),
            ('Structural Analysis', 'R.C. Hibbeler', '9780134319650', 'textbook', 'Civil Engineering'),
        ]
        for title, author, isbn, cat, subj in books_data:
            copies = random.randint(3, 10)
            Book.objects.get_or_create(
                isbn=isbn,
                defaults={
                    'title': title, 'author': author, 'category': cat,
                    'subject': subj, 'total_copies': copies,
                    'available_copies': copies,
                    'shelf_number': f'{random.choice("ABCDEF")}-{random.randint(1,20)}',
                    'publisher': 'Publisher',
                }
            )
        self.stdout.write(self.style.SUCCESS('[OK] Library Books'))

        # ─── Sample Notifications ───
        Notification.objects.get_or_create(
            user=admin_user, title='System Ready',
            defaults={'message': 'College ERP system has been initialized with demo data.',
                      'notification_type': 'success'}
        )
        self.stdout.write(self.style.SUCCESS('[OK] Notifications'))

        self.stdout.write(self.style.SUCCESS('\n=== Database seeded successfully! ==='))
        self.stdout.write(self.style.SUCCESS('-' * 40))
        self.stdout.write(f'  Admin:      admin / admin123')
        self.stdout.write(f'  Principal:  principal / pass123')
        self.stdout.write(f'  HODs:       hod_cs / pass123, hod_entc / pass123, hod_me / pass123, hod_ce / pass123, hod_aids / pass123')
        self.stdout.write(f'  Faculty:    faculty1 / pass123')
        self.stdout.write(f'  Student:    student1 / pass123')
        self.stdout.write(f'  Accountant: accountant1 / pass123')
        self.stdout.write(f'  HR:         hr1 / pass123')
        self.stdout.write(f'  Librarian:  librarian1 / pass123')
        self.stdout.write(self.style.SUCCESS('-' * 40))
