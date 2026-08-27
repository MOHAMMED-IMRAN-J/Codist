from rest_framework import serializers
from .models import ChatRequest, ChatSession, Message
from apps.users.serializers import UserSerializer

class ChatRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = ChatRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    participant1 = UserSerializer(read_only=True)
    participant2 = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ['id', 'participant1', 'participant2', 'created_at', 'updated_at', 'last_message']

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'id': str(last_msg.id),
                'content': last_msg.get_content(),
                'sender': last_msg.sender.username,
                'created_at': last_msg.created_at
            }
        return None

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    content = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'session', 'sender', 'content', 'is_read', 'created_at']

    def get_content(self, obj):
        return obj.get_content()
