from django.urls import path
from . import views

urlpatterns = [
    path('', views.fees_dashboard, name='fees_dashboard'),
    path('pay/', views.fees_pay, name='fees_pay'),
    path('history/', views.fees_history, name='fees_history'),
]
