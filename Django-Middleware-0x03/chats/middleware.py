import logging
from datetime import datetime

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