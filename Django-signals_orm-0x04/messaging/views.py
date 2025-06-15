from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponseForbidden
from .models import Message
from django.db import models

def get_threaded_messages(message, user):
    """Recursively fetch message and its replies for the given user."""
    replies = Message.objects.filter(parent_message=message).filter(
        models.Q(sender=user) | models.Q(receiver=user)
    ).select_related('sender', 'receiver', 'parent_message').prefetch_related('replies__sender', 'replies__receiver')
    
    reply_data = [
        get_threaded_messages(reply, user) for reply in replies
    ]
    return {
        'id': message.id,
        'sender': message.sender.username,
        'receiver': message.receiver.username,
        'content': message.content,
        'timestamp': message.timestamp.isoformat(),
        'edited': message.edited,
        'parent_message_id': message.parent_message_id,
        'replies': reply_data
    }

@login_required
def message_history(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if request.user not in [message.sender, message.receiver]:
        return HttpResponseForbidden({'error': 'You do not have permission to view this message'})
    
    history = message.history.all()
    history_data = [
        {
            'old_content': entry.old_content,
            'edited_by': entry.edited_by.username,
            'edited_at': entry.edited_at.isoformat()
        } for entry in history
    ]
    message_data = {
        'id': message.id,
        'sender': message.sender.username,
        'receiver': message.receiver.username,
        'content': message.content,
        'timestamp': message.timestamp.isoformat(),
        'edited': message.edited
    }
    return JsonResponse({
        'message': message_data,
        'history': history_data
    })

@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        username = user.username
        logout(request)
        user.delete()
        return JsonResponse({'message': f'User {username} deleted successfully'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def threaded_conversation(request, message_id):
    message = get_object_or_404(
        Message.objects.filter(
            models.Q(sender=request.user) | models.Q(receiver=request.user)
        ).select_related('sender', 'receiver', 'parent_message'),
        id=message_id
    )
    threaded_data = get_threaded_messages(message, request.user)
    return JsonResponse({'conversation': threaded_data})

@login_required
def unread_messages(request):
    """
    Fetch unread messages for the current user using the custom manager.
    """
    messages = Message.unread.unread_for_user(request.user).select_related('sender').only(
        'id', 'sender__username', 'content', 'timestamp', 'read'
    )
    messages_data = [
        {
            'id': message.id,
            'sender': message.sender.username,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'read': message.read
        } for message in messages
    ]
    return JsonResponse({'unread_messages': messages_data})