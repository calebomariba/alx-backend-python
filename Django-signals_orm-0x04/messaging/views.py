from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponseForbidden
from .models import Message

@login_required
def message_history(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    # Restrict access to sender or receiver
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
        logout(request)  # Log out the user
        user.delete()  # Delete user, triggering CASCADE and post_delete signal
        return JsonResponse({'message': f'User {username} deleted successfully'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)