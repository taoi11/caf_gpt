"""
Core app middleware.
"""
from django.http import JsonResponse


class HealthCheckMiddleware:
    """
    Middleware to handle health check requests before ALLOWED_HOSTS validation.

    This allows health checks to work from any host without compromising
    the security of ALLOWED_HOSTS for other endpoints.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Handle health check requests immediately, bypassing all other middleware
        if request.path == '/health/' and request.method == 'GET':
            return JsonResponse({
                'status': 'ok',
                'service': 'caf_gpt',
                'timestamp': request.META.get('HTTP_DATE', 'unknown'),  # Safe debugging info
            })

        # For all other requests, continue normal processing
        response = self.get_response(request)
        return response
