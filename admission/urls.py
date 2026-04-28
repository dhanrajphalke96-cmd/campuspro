from django.urls import path
from . import views

urlpatterns = [
    path('', views.admission_list, name='admission_list'),
    path('create/', views.admission_create, name='admission_create'),
    path('<int:pk>/', views.admission_detail, name='admission_detail'),
    path('merit-list/', views.merit_list_view, name='merit_list'),
]
