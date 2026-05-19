from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatMessage, ChatSession
from .serializers import ChatMessageSerializer
from .utils import (
    build_system_prompt,
    call_llm,
    count_tokens,
    get_chatbot_max_messages_per_day,
)


@login_required
def chatbot_page(request):
    """Display the chatbot page."""
    user = request.user
    sessions = ChatSession.objects.filter(user=user).order_by('-created_at')
    context = {
        'sessions': sessions,
    }
    return render(request, 'chatbot/chatbot.html', context)


class ChatbotMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        daily_messages = ChatMessage.objects.filter(
            session__user=user,
            timestamp__date=timezone.localdate(),
        ).count()
        if daily_messages >= get_chatbot_max_messages_per_day():
            return Response(
                {
                    'detail': 'You have reached your daily chatbot message limit. Please try again tomorrow or contact your administrator.'
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        message_content = (request.data.get('message') or '').strip()
        if not message_content:
            return Response({'detail': 'A message is required.'}, status=status.HTTP_400_BAD_REQUEST)

        session_id = request.data.get('session_id')
        session = None
        if session_id:
            session = ChatSession.objects.filter(pk=session_id, user=user).first()

        if not session:
            session = ChatSession.objects.create(user=user)

        recent_messages = list(
            ChatMessage.objects.filter(session=session)
            .select_related('session')
            .order_by('-timestamp')[:10]
        )
        recent_messages.reverse()

        system_prompt = build_system_prompt(user)
        llm_messages = [{'role': 'system', 'content': system_prompt}]
        for saved_message in recent_messages:
            llm_messages.append({'role': saved_message.role, 'content': saved_message.content})
        llm_messages.append({'role': 'user', 'content': message_content})

        ChatMessage.objects.create(
            session=session,
            role='user',
            content=message_content,
            token_count=count_tokens(message_content),
        )

        try:
            assistant_text, usage = call_llm(llm_messages)
        except Exception as exc:
            return Response(
                {'detail': str(exc) or 'Unable to generate a chatbot response at this time.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        assistant_message = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=assistant_text,
            token_count=count_tokens(assistant_text),
        )

        serialized = ChatMessageSerializer(assistant_message)
        return Response(
            {
                'reply': serialized.data['content'],
                'session_id': session.pk,
                'usage': usage,
            },
            status=status.HTTP_200_OK,
        )
