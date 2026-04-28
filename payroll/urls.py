from django.urls import path
from . import views

urlpatterns = [
    path('', views.payroll_dashboard, name='payroll_dashboard'),
    path('payslips/', views.payslip_list, name='payslip_list'),
]
