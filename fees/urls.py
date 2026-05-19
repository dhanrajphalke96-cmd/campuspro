from django.urls import path
from . import views

urlpatterns = [
    path('', views.fees_dashboard, name='fees_dashboard'),
    path('pay/', views.fees_pay, name='fees_pay'),
    path('history/', views.fees_history, name='fees_history'),
    path('purchase/', views.purchase_list, name='purchase_list'),
    path('purchase/create/', views.purchase_create, name='purchase_create'),
    path('purchase/<int:pk>/approve/', views.purchase_approve, name='purchase_approve'),
    path('purchase/<int:pk>/reject/', views.purchase_reject, name='purchase_reject'),
]
