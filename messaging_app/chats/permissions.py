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