# College ERP System

A production-ready, modular College ERP system designed for Indian colleges. Built with **Django**, **Django REST Framework**, and a modern, responsive **Dark-Themed UI**.

## Features

This ERP consists of 8 interconnected modules spanning academic and administrative operations:
- **Core Engine & Admin:** Role-based access control (Admin, Principal, HOD, Faculty, Student, Accountant, HR, Librarian), unified dark dashboard, notifications.
- **Admission Management:** Application submission, document tracking, application fees, merit lists.
- **Student Records:** Student profiles, parent details, tracking of branch, semester, and unified academic history.
- **Attendance Management:** Subject-wise daily attendance marking, automated status (Present, Absent, Late), overall percentage reporting.
- **Fees Management:** Configurable fee structures per branch/semester, logging of fee receipts, UPI/cash payments tracking.
- **Examination Management:** Exam schedules, bulk-entry marks sheets for faculty, automated SGPA/CGPA evaluation, result publishing.
- **HRMS (Human Resources):** Staff directory profiles, leave type tracking, multi-tier leave approval workflow.
- **Payroll Management:** Basic salary structure calculations including HRA/DA/PF, automated monthly payslip generation.
- **Library Management:** Catalog of books, issuance tracking, library cards, due dates, late-return fine calculator.
- **REST APIs:** Secured via JWT (`/api/token`), providing a scalable headless backend interface for integrations via DRF ViewSets.

## Technology Stack

- **Backend Framework:** Django 6.0
- **API Engine:** Django REST Framework (DRF)
- **Authentication:** Sessions for Web + JWT for API
- **Database:** SQLite (default for development; production-ready for PostgreSQL/MySQL)
- **Frontend / UI:** Django Templates, Vanilla CSS (Dark Theme System), minimal JavaScript, Bootstrap 5 components

## Local Setup & Installation

### 1. Requirements

Ensure you have **Python 3+** installed.

### 2. Clone and Setup Environment

Clone the repository and set up a virtual environment (recommended):
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

*(Note: Ensure Pillow, reportlab, djangorestframework, djangorestframework-simplejwt, django-cors-headers, and django-filter are correctly successfully installed.)*

### 4. Database Migrations & Initial Setup

Navigate to your workspace directory and prepare the database:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed Test Data

The system includes a massive demo-data seeder out of the box (populates students, subjects, staff, structures, fee rules, etc.). Run:
```bash
python manage.py seed_data
```

### 6. Run the Server
```bash
python manage.py runserver
```
Visit http://127.0.0.1:8000/ to access the application.

## Demo Users
Running the `seed_data` script will provide you with the following user accounts to quickly demo features. The password for all is `pass123` (except Admin).

| Role | Username | Password |
|---|---|---|
| **Admin** | `admin` | `admin123` |
| **Principal** | `principal` | `pass123` |
| **HOD** | `hod_cs` | `pass123` |
| **Faculty** | `faculty1` | `pass123` |
| **Student** | `student1` | `pass123` |
| **Accountant**| `accountant1` | `pass123` |
| **HR** | `hr1` | `pass123` |
| **Librarian** | `librarian1`| `pass123` |

## License
MIT License.
