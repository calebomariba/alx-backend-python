from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['user_id', 'email', 'first_name', 'last_name', 'phone_number', 'bio']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField(max_length=1000, required=True)

    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'sender', 'message_body', 'sent_at']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model."""
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    conversation_name = serializers.CharField(read_only=True, source='get_conversation_name')

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'conversation_name', 'created_at', 'messages']

    def get_messages(self, obj):
        """Return recent messages for the conversation."""
        messages = obj.messages.order_by('-sent_at')[:10]  # Last 10 messages
        return MessageSerializer(messages, many=True).data

    def get_conversation_name(self, obj):
        """Generate a name based on participants."""
        names = [f"{p.first_name} {p.last_name}" for p in obj.participants.all()]
        return ", ".join(names) or "Unnamed Conversation"

    def validate_participants(self, value):
        """Ensure at least two participants in the conversation."""
        if len(value) < 2:
            raise serializers.ValidationError("Conversation must have at least two participants.")
        return value