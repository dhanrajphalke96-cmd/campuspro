from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('<int:pk>/', views.exam_detail, name='exam_detail'),
    path('<int:pk>/marks/', views.marks_entry, name='marks_entry'),
    path('results/', views.result_list, name='result_list'),
]
