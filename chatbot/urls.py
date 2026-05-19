from django.urls import path

from .views import ChatbotMessageView, chatbot_page

urlpatterns = [
    path('', chatbot_page, name='chatbot_page'),
    path('message/', ChatbotMessageView.as_view(), name='chatbot-message'),
]
