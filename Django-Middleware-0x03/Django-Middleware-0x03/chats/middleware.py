import logging
from datetime import datetime
from django.http import HttpResponseForbidden
from django.urls import resolve


# Configure logger
logger = logging.getLogger('requests')
logger.setLevel(logging.INFO)
# Create file handler for requests.log
file_handler = logging.FileHandler('requests.log')
file_handler.setLevel(logging.INFO)
# Create formatter
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
# Add handler to logger
logger.addHandler(file_handler)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        """Initialize middleware with get_response callable."""
        self.get_response = get_response

    def __call__(self, request):
        """Log request details and call the view."""
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        """Initialize middleware with get_response callable."""
        self.get_response = get_response

    def __call__(self, request):
        """Restrict access to chat app outside 9 AM to 6 PM."""
        current_time = datetime.now().time()
        start_time = datetime.strptime("09:00", "%H:%M").time()
        end_time = datetime.strptime("18:00", "%H:%M").time()

        # Check if current time is outside allowed hours
        if not (start_time <= current_time <= end_time):
            return HttpResponseForbidden("Access to the chat app is restricted outside 9 AM to 6 PM.")

        # Proceed to next middleware or view
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        """Initialize middleware with get_response callable."""
        self.get_response = get_response
        # Simple list of offensive words (extend as needed)
        self.offensive_words = {'badword1', 'badword2', 'offensive'}

    def __call__(self, request):
        """Check POST requests for offensive language in message body."""
        if request.method == 'POST' and request.path == '/api/chats/messages/':
            try:
                # Parse JSON body
                import json
                body = json.loads(request.body.decode('utf-8'))
                message_body = body.get('message_body', '').lower()
                # Check for offensive words
                if any(word in message_body for word in self.offensive_words):
                    return HttpResponse(
                        "Message contains offensive language.",
                        status=403  # Forbidden
                    )
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass  # Skip if body is invalid

        # Proceed to next middleware or view
        response = self.get_response(request)
        return response


class RolePermissionMiddleware:
    def __init__(self, get_response):
        """Initialize the middleware with the get_response callable."""
        self.get_response = get_response
        # Define protected views that require admin/moderator role
        self.protected_views = [
            'admin_action_view_name',  # Replace with actual view names
            'moderator_action_view_name',
        ]

    def __call__(self, request):
        """Process each request and check user role permissions."""
        # Get the view name from the request
        view_name = resolve(request.path_info).url_name

        # Check if the requested view is protected
        if view_name in self.protected_views:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required")

            # Check if user has admin or moderator role
            if not (hasattr(request.user, 'role') and 
                   request.user.role in ['admin', 'moderator']):
                return HttpResponseForbidden("Admin or Moderator role required")

        # Proceed with the request if checks pass
        response = self.get_response(request)
        return response