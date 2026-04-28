from django.urls import path
from . import views

urlpatterns = [
    path('', views.library_dashboard, name='library_dashboard'),
    path('issues/', views.book_issue_list, name='book_issue_list'),
    path('issues/new/', views.book_issue_create, name='book_issue_create'),
    path('issues/<int:pk>/return/', views.book_return, name='book_return'),
    path('cards/', views.library_card_list, name='library_card_list'),
]
