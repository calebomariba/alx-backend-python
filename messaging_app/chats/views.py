from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for listing and creating conversations."""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def get_queryset(self):
        """Filter conversations for the authenticated user."""
        return self.queryset.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a new conversation with participants."""
        participant_ids = request.data.get('participant_ids', [])
        if not participant_ids:
            return Response({"error": "At least one participant required"},
                            status=status.HTTP_400_BAD_REQUEST)
        conversation = Conversation.objects.create()
        conversation.participants.add(*participant_ids, request.user)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for listing and creating messages."""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_queryset(self):
        """Filter messages by conversation."""
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            return self.queryset.filter(conversation__conversation_id=conversation_id)
        return self.queryset

    def create(self, request, *args, **kwargs):
        """Create a new message in a conversation."""
        conversation_id = request.data.get('conversation')
        if not conversation_id:
            return Response({"error": "Conversation ID required"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
            if request.user not in conversation.participants.all():
                return Response({"error": "User not in conversation"},
                                status=status.HTTP_403_FORBIDDEN)
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                message_body=request.data.get('message_body', '')
            )
            serializer = self.get_serializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"},
                            status=status.HTTP_404_NOT_FOUND)
