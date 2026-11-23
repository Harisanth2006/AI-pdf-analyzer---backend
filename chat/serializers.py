# chat/serializers.py
from rest_framework import serializers
from .models import ChatMessage

class AskQuestionSerializer(serializers.Serializer):
    file_id = serializers.IntegerField(required=True)
    question = serializers.CharField(required=True, allow_blank=False)

class ChatMessageSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    file_id = serializers.IntegerField(source="document.id", read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "user_id",
            "file_id",
            "order_number",
            "question",
            "answer",
            "created_at",
        ]
