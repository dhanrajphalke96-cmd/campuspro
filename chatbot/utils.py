import json
import math
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from decouple import config
from django.db.models import Count, Sum
from django.utils import timezone

from core.models import CustomUser, Department
from attendance.models import Attendance, Subject
from examination.models import Exam
from fees.models import FeePayment
from hrms.models import LeaveRequest, StaffAttendance
from library.models import BookIssue
from students.models import AcademicHistory, StudentProfile


def count_tokens(text: str) -> int:
    return max(1, len(text.split()))


def get_chatbot_max_messages_per_day() -> int:
    return config('CHATBOT_MAX_MESSAGES_PER_DAY', default=50, cast=int)


def get_chatbot_model() -> str:
    return config('CHATBOT_MODEL', default='gpt-4o')


def get_available_api_key() -> tuple[str, str]:
    openai_key = config('OPENAI_API_KEY', default='')
    gemini_key = config('GEMINI_API_KEY', default='')
    return openai_key, gemini_key


def build_system_prompt(user: CustomUser) -> str:
    role = 'admin' if user.is_superuser else user.role
    prompt_map = {
        'student': (
            'You are an ERP assistant for a student. Help with: checking attendance, viewing fee dues, exam results, SGPA/CGPA, timetable, library books, and leave applications. '
            'Be concise and friendly.'
        ),
        'faculty': (
            'You are an ERP assistant for a faculty member. Help with: marking attendance, entering marks, viewing assigned subjects, managing leave requests, and payslip queries. '
            'Be concise and professional.'
        ),
        'hod': (
            'You are an ERP assistant for a Head of Department. Help with: department reports, approving leaves, exam schedules, faculty management, and student performance summaries. '
            'Be concise and informative.'
        ),
        'admin': (
            'You are an ERP assistant for a system administrator. Help with: user management, fee structure configuration, generating reports, seeding data, system settings, and module overviews. '
            'Be direct and helpful.'
        ),
        'principal': (
            'You are an ERP assistant for the Principal. Help with: institution-wide analytics, staff/student summaries, approval workflows, and policy-level queries. '
            'Be strategic and clear.'
        ),
        'accountant': (
            'You are an ERP assistant for an Accountant. Help with: fee collection reports, pending dues, payment receipts, payroll summaries, and salary structure details. '
            'Be accurate and practical.'
        ),
        'hr': (
            'You are an ERP assistant for an HR officer. Help with: leave approvals, staff attendance, payroll inputs, and employee profile management. '
            'Be courteous and precise.'
        ),
        'librarian': (
            'You are an ERP assistant for the Librarian. Help with: book issuance/returns, due date tracking, late fine calculations, catalog search, and library card management. '
            'Be helpful and concise.'
        ),
    }

    base_prompt = prompt_map.get(role, prompt_map['admin'])
    live_context = get_live_context(user)
    if live_context:
        return f"{base_prompt}\n\nLive ERP context:\n{live_context}\n\nIf the user asks about details beyond available CampusPro data, answer with general guidance and suggest using the dashboard pages."
    return f"{base_prompt}\n\nIf the user asks about details beyond available CampusPro data, answer with general guidance and suggest using the dashboard pages."


def get_live_context(user: CustomUser) -> str:
    role = 'admin' if user.is_superuser else user.role
    pieces = []

    if role == 'student':
        student_profile = getattr(user, 'student_profile', None)
        if student_profile:
            total_attendance = Attendance.objects.filter(student=student_profile).count()
            present_attendance = Attendance.objects.filter(student=student_profile, status='present').count()
            percentage = None
            if total_attendance:
                percentage = round((present_attendance / total_attendance) * 100, 1)
            pending_dues = FeePayment.objects.filter(student=student_profile, status='pending').aggregate(total=Sum('amount_paid'))['total'] or 0
            latest_cgpa = (
                AcademicHistory.objects.filter(student=student_profile)
                .order_by('-semester')
                .values_list('cgpa', flat=True)
                .first()
            )
            issued_books = BookIssue.objects.filter(student=student_profile, status__in=['issued', 'overdue']).count()
            if percentage is not None:
                pieces.append(f"Current attendance is {percentage}%.")
            if pending_dues:
                pieces.append(f"Pending fee dues amount to ₹{pending_dues:.2f}.")
            if latest_cgpa is not None:
                pieces.append(f"Latest CGPA is {latest_cgpa}.")
            if issued_books:
                pieces.append(f"You currently have {issued_books} book(s) issued or overdue.")

    if role == 'faculty':
        assigned_subjects = user.assigned_subjects.filter(is_active=True).values_list('name', flat=True)
        if assigned_subjects:
            pieces.append(f"Assigned subjects: {', '.join(assigned_subjects)}.")
        pending_exams = (
            Exam.objects.filter(subject__assigned_faculty=user, is_published=False)
            .distinct()
            .count()
        )
        if pending_exams:
            pieces.append(f"There are {pending_exams} unpublished exams or pending marks entries for your subjects.")

    if role == 'hod':
        hod_dept = Department.objects.filter(hod=user).first()
        if hod_dept:
            faculty_count = CustomUser.objects.filter(role='faculty', staff_profile__department=hod_dept).count()
            student_count = CustomUser.objects.filter(role='student', student_profile__department=hod_dept).count()
            pieces.append(f"Department {hod_dept.name} has {faculty_count} faculty and {student_count} students.")

    if role == 'accountant':
        today = timezone.localdate()
        today_collection = (
            FeePayment.objects.filter(status='paid', paid_at__date=today)
            .aggregate(total=Sum('amount_paid'))['total'] or 0
        )
        pending_dues = FeePayment.objects.filter(status='pending').count()
        pieces.append(f"Today's collected amount is ₹{today_collection:.2f}.")
        pieces.append(f"There are {pending_dues} pending fee payments.")
        from fees.models import PurchaseRecord
        pending_purchases = PurchaseRecord.objects.filter(status='pending').count()
        pieces.append(f"There are {pending_purchases} pending purchase requests.")

    if role in ('hr', 'principal', 'admin'):
        pending_leaves = LeaveRequest.objects.filter(status='pending').count()
        pieces.append(f"Pending leave requests: {pending_leaves}.")
        if role in ('principal', 'admin'):
            from fees.models import PurchaseRecord
            pending_purchases = PurchaseRecord.objects.filter(status='pending').count()
            pieces.append(f"There are {pending_purchases} pending purchase requests awaiting your approval.")

    if role == 'librarian':
        overdue_books = BookIssue.objects.filter(status='overdue').count()
        issued_books = BookIssue.objects.filter(status='issued').count()
        pieces.append(f"There are {issued_books} currently issued books and {overdue_books} overdue books.")

    return '\n'.join(pieces)


def call_llm(messages: list[dict]) -> tuple[str, dict]:
    openai_key, gemini_key = get_available_api_key()
    model = get_chatbot_model()
    use_gemini = gemini_key and model.startswith('gemini')

    if use_gemini or (gemini_key and not openai_key):
        # Use Google Generative AI API (Gemini)
        endpoint = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}'
        headers = {'Content-Type': 'application/json'}
        
        # Convert OpenAI format to Gemini format
        contents = []
        for msg in messages:
            if msg['role'] != 'system':  # Gemini doesn't support system role in contents
                contents.append({
                    'role': 'user' if msg['role'] == 'user' else 'model',
                    'parts': [{'text': msg['content']}]
                })
        
        payload = {
            'contents': contents,
            'generationConfig': {
                'temperature': 0.3,
                'maxOutputTokens': 800,
            }
        }
        
        request_data = json.dumps(payload).encode('utf-8')
        request_obj = urllib.request.Request(endpoint, data=request_data, headers=headers, method='POST')
        
        try:
            with urllib.request.urlopen(request_obj, timeout=30) as response:
                raw = response.read().decode('utf-8')
                parsed = json.loads(raw)
        except urllib.error.HTTPError as exc:
            message = exc.read().decode('utf-8')
            raise RuntimeError(f'LLM API request failed: {message}') from exc
        
        # Parse Gemini response
        content = ''
        usage = {}
        if parsed.get('candidates'):
            candidate = parsed['candidates'][0]
            if candidate.get('content') and candidate['content'].get('parts'):
                content = candidate['content']['parts'][0].get('text', '')
        
        return content.strip(), usage
    
    elif openai_key:
        # Use OpenAI API
        payload = {
            'model': model,
            'messages': messages,
            'temperature': 0.3,
            'max_tokens': 800,
        }
        
        endpoint = 'https://api.openai.com/v1/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {openai_key}',
        }
        
        request_data = json.dumps(payload).encode('utf-8')
        request_obj = urllib.request.Request(endpoint, data=request_data, headers=headers, method='POST')
        
        try:
            with urllib.request.urlopen(request_obj, timeout=30) as response:
                raw = response.read().decode('utf-8')
                parsed = json.loads(raw)
        except urllib.error.HTTPError as exc:
            message = exc.read().decode('utf-8')
            raise RuntimeError(f'LLM API request failed: {message}') from exc
        
        content = ''
        usage = {}
        if parsed.get('choices'):
            choice = parsed['choices'][0]
            if isinstance(choice.get('message'), dict):
                content = choice['message'].get('content', '')
            else:
                content = choice.get('text', '')
        if parsed.get('usage'):
            usage = parsed['usage']
        
        return content.strip(), usage
    
    else:
        raise ValueError('Missing OPENAI_API_KEY or GEMINI_API_KEY environment variable.')
