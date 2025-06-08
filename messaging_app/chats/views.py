from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer
from uuid import UUID
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .permissions import IsParticipantOfConversation



class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for listing and creating conversations."""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['participants__first_name', 'participants__last_name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter conversations for authenticated user."""
        if not self.request.user.is_authenticated:
            return Conversation.objects.none()
        return self.queryset.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a new conversation with participants."""
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"},
                            status=status.HTTP_401_UNAUTHORIZED)
        participant_ids = request.data.get('participant_ids', [])
        if not participant_ids:
            return Response({"error": "At least one participant required"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            participants = [request.user]
            for pid in participant_ids:
                UUID(pid, version=4)
                user = User.objects.get(user_id=pid)
                participants.append(user)
            conversation = Conversation.objects.create()
            conversation.participants.add(*participants)
            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError:
            return Response({"error": "Invalid UUID format"},
                            status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "One or more users not found"},
                            status=status.HTTP_404_NOT_FOUND)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for listing and creating messages."""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']

    def get_queryset(self):
        """Filter messages by conversation."""
        if not self.request.user.is_authenticated:
            return Message.objects.none()
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            try:
                UUID(conversation_id, version=4)
                return self.queryset.filter(
                    conversation__conversation_id=conversation_id,
                    conversation__participants=self.request.user
                )
            except ValueError:
                return Message.objects.none()
        return self.queryset.filter(conversation__participants=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a new message in a conversation."""
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"},
                            status=status.HTTP_401_UNAUTHORIZED)
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
        except ValueError:
            return Response({"error": "Invalid UUID format"},
                            status=status.HTTP_400_BAD_REQUEST)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"},
                            status=status.HTTP_404_NOT_FOUND)



class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, retrieving, updating, and deleting conversations.
    Only authenticated users who are participants can access conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        # Filter conversations to those where the user is a participant
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        # Add the requesting user as a participant during creation
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, retrieving, updating, and deleting messages.
    Only authenticated users who are participants in the conversation can access messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        # Filter messages to those in conversations the user is part of
        return Message.objects.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        # Set the requesting user as the message sender
        serializer.save(user=self.request.user)