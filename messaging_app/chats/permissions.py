from rest_framework import permissions

class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Custom permission to allow users to access only their own messages
    or conversations they are part of.
    """
    def has_object_permission(self, request, view, obj):
        # For Message objects: check if user is the sender
        if hasattr(obj, 'user'):  # Assuming Message model has 'user' field
            return obj.user == request.user
        # For Conversation objects: check if user is a participant
        elif hasattr(obj, 'participants'):  # Assuming Conversation has 'participants' ManyToManyField
            return request.user in obj.participants.all()
        return False



class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only authenticated users who are participants
    in a conversation to view, send, update, or delete messages or access conversations.
    """
    def has_permission(self, request, view):
        # Ensure user is authenticated for all actions
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # For Message: Check if user is a participant in the message's conversation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        # For Conversation: Check if user is a participant
        elif hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        return False