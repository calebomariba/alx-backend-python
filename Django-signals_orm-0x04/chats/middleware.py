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