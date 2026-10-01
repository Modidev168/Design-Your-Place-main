from rest_framework import serializers  # type: ignore[import-not-found]
from .models import ChatConversation , ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "role",
            "content",
            "created_at",
        ]
class ChatConversationSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(
        many=True,
        read_only = True
    )
    class Meta:
        model = ChatConversation
        fields = [
            "id",
            "title",
            "created_at",
            "updated_at",
            "messages",
        ]
class SendMessageSerializer(serializers.Serializer):
     message = serializers.CharField(
        required=True,
        allow_blank = False
    )