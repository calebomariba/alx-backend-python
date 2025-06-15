from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponseForbidden
from .models import Message

def get_threaded_messages(message):
    """Recursively fetch message and its replies in a threaded structure."""
    replies = [
        get_threaded_messages(reply) for reply in message.replies.all()
    ]
    return {
        'id': message.id,
        'sender': message.sender.username,
        'receiver': message.receiver.username,
        'content': message.content,
        'timestamp': message.timestamp.isoformat(),
        'edited': message.edited,
        'parent_message_id': message.parent_message_id,
        'replies': replies
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
    """
    Fetch a message and its threaded replies using optimized queries.
    """
    # Optimize query with select_related and prefetch_related
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver', 'parent_message')
                       .prefetch_related('replies__sender', 'replies__receiver', 'replies__replies'),
        id=message_id
    )
    # Restrict access to sender or receiver
    if request.user not in [message.sender, message.receiver]:
        return HttpResponseForbidden({'error': 'You do not have permission to view this conversation'})
    
    # Get threaded structure
    threaded_data = get_threaded_messages(message)
    return JsonResponse({'conversation': threaded_data})