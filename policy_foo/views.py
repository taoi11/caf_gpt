"""
PolicyFoo app views.
"""
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from django.conf import settings

from core.services import RateLimitService


class ChatInterfaceView(TemplateView):
    """
    View for the policy chat interface.
    """
    template_name = 'policy_foo/chat_interface.html'


class RateLimitsView(View):
    """
    View for checking API rate limits.
    """
    rate_limit_service = RateLimitService()

    def get(self, request, *args, **kwargs):
        """
        Return the current rate limits for the user's IP address.
        """
        # Get client IP address
        ip_address = request.META.get('REMOTE_ADDR')
        if not ip_address:
            return JsonResponse({'error': 'Could not determine client IP address.'}, status=400)

        # Check if IP is whitelisted
        if self.rate_limit_service.is_whitelisted(ip_address):
            return JsonResponse({
                'hourly': {'limit': 'Unlimited', 'remaining': 'Unlimited', 'reset': 0},
                'daily': {'limit': 'Unlimited', 'remaining': 'Unlimited', 'reset': 0}
            })

        # Get usage and limits from the service
        usage = self.rate_limit_service.get_usage(ip_address)

        # Get limits from settings (or RateLimitService defaults if not set)
        hourly_limit = settings.RATE_LIMIT_HOURLY
        daily_limit = settings.RATE_LIMIT_DAILY

        # Calculate remaining requests
        hourly_remaining = max(0, hourly_limit - usage['hourly']['count'])
        daily_remaining = max(0, daily_limit - usage['daily']['count'])

        # Calculate time until reset (approximate)
        hourly_reset = usage['hourly']['reset']
        daily_reset = usage['daily']['reset']

        return JsonResponse({
            'hourly': {
                'limit': hourly_limit,
                'remaining': hourly_remaining,
                'reset': hourly_reset,
            },
            'daily': {
                'limit': daily_limit,
                'remaining': daily_remaining,
                'reset': daily_reset,
            }
        })
