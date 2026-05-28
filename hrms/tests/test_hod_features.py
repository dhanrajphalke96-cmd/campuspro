from django.test import TestCase, Client
from django.urls import reverse
from core.models import CustomUser, Department
from hrms.models import StaffProfile, LeaveRequest
from attendance.models import Subject


class HODFeatureTests(TestCase):
    def setUp(self):
        # Users
        self.hod_user = CustomUser.objects.create_user(username='hod1', password='pass', role='hod')
        self.admin_user = CustomUser.objects.create_user(username='admin1', password='pass', role='admin')

        # Departments
        self.dept = Department.objects.create(name='CS', code='CS', hod=self.hod_user)
        self.other_dept = Department.objects.create(name='EE', code='EE')

        # Staff
        self.staff1_user = CustomUser.objects.create_user(username='staff1', password='pass', role='faculty')
        self.staff2_user = CustomUser.objects.create_user(username='staff2', password='pass', role='faculty')
        self.staff1 = StaffProfile.objects.create(user=self.staff1_user, employee_id='S1', department=self.dept, designation='lecturer', date_of_joining='2020-01-01')
        self.staff2 = StaffProfile.objects.create(user=self.staff2_user, employee_id='S2', department=self.other_dept, designation='lecturer', date_of_joining='2020-01-01')

        # Leave type
        from hrms.models import LeaveType
        self.leave_type = LeaveType.objects.create(name='Annual')

        # Subject in HOD dept
        self.subject = Subject.objects.create(name='Algo', code='CS101', department=self.dept, semester=1)

        self.client = Client()

    def test_hod_sees_only_dept_leaves(self):
        # create leaves
        LeaveRequest.objects.create(staff=self.staff1, leave_type=self.leave_type, from_date='2026-01-01', to_date='2026-01-02', reason='r')
        LeaveRequest.objects.create(staff=self.staff2, leave_type=self.leave_type, from_date='2026-01-01', to_date='2026-01-02', reason='r')

        self.client.login(username='hod1', password='pass')
        resp = self.client.get(reverse('hrms_leave_list'))
        self.assertEqual(resp.status_code, 200)
        leaves = resp.context['leaves']
        # HOD should only see staff1's leave
        self.assertTrue(all(l.staff.department == self.dept for l in leaves))

    def test_hod_cannot_act_on_other_dept_leave(self):
        leave_other = LeaveRequest.objects.create(staff=self.staff2, leave_type=self.leave_type, from_date='2026-01-03', to_date='2026-01-04', reason='x')
        self.client.login(username='hod1', password='pass')
        # Try action endpoint
        action_resp = self.client.post(reverse('leave_action', args=[leave_other.pk]), {'action': 'approved'})
        # Refresh
        leave_other.refresh_from_db()
        self.assertEqual(leave_other.status, 'pending')

    def test_hod_can_assign_subject(self):
        self.client.login(username='hod1', password='pass')
        resp = self.client.post(reverse('assign_subjects'), {'subject': self.subject.pk, 'staff': self.staff1.pk})
        self.assertEqual(resp.status_code, 302)  # redirect after success
        self.assertTrue(self.subject.assigned_faculty.filter(pk=self.staff1_user.pk).exists())
