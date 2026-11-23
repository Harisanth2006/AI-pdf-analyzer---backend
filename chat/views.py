from django.shortcuts import render

# Create your views here.
# chat/views.py
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from document.models import Document
from document.utils.rag import quest
from .models import ChatMessage
from .serializers import AskQuestionSerializer, ChatMessageSerializer

class ChatAskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_id = serializer.validated_data["file_id"]
        question = serializer.validated_data["question"]

        # Ensure the document exists and belongs to the logged-in user
        document = get_object_or_404(Document, id=file_id, user=request.user)

        # Call your RAG pipeline to get the LLM answer
        rag_result = quest(question=question, file_id=document.id)
        answer_text = rag_result["answer"]

        # Save to database (order_number is auto-calculated in model.save())
        chat_msg = ChatMessage.objects.create(
            user=request.user,
            document=document,
            question=question,
            answer=answer_text,
        )

        return Response(
            ChatMessageSerializer(chat_msg).data,
            status=status.HTTP_201_CREATED,
        )


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        # Verify the user owns this document
        document = get_object_or_404(Document, id=file_id, user=request.user)

        # Ordered automatically by 'order_number' via ChatMessage.Meta
        messages = ChatMessage.objects.filter(user=request.user, document=document)
        serializer = ChatMessageSerializer(messages, many=True)

        return Response(
            {
                "file_id": document.id,
                "filename": document.name,
                "total_messages": messages.count(),
                "history": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
