"""
Contains the view for checking API rate limits for the PolicyFoo app.

The actual incrementing of rate limits happens in the PolicyRouterView
after a successful response is generated.
"""
import logging
from django.http import JsonResponse
from django.views import View

from core.services import RateLimitService

logger = logging.getLogger(__name__)


class RateLimitsView(View):
    """
    Provides an API endpoint (`/policy/api/rate-limits/`) for the frontend
    to fetch the current rate limit status for the user's IP address.
    """
    rate_limit_service = RateLimitService()

    def get(self, request, *args, **kwargs):
        """
        Return the current rate limits and usage for the user's IP address.
        """
        ip_address = request.META.get('REMOTE_ADDR')
        if not ip_address:
            logger.warning("Could not determine client IP address for rate limit check.")
            return JsonResponse({'error': 'Could not determine client IP address.'}, status=400)

        # Check if IP is whitelisted
        if self.rate_limit_service.is_whitelisted(ip_address):
            logger.debug(f"Rate limit check for whitelisted IP: {ip_address}")
            # Return unlimited status for whitelisted IPs
            return JsonResponse({
                'hourly': {'limit': 'Unlimited', 'remaining': 'Unlimited', 'reset': 0},
                'daily': {'limit': 'Unlimited', 'remaining': 'Unlimited', 'reset': 0}
            })

        # Get usage and limits from the service
        usage = self.rate_limit_service.get_usage(ip_address)
        hourly_usage_count = usage['hourly']
        daily_usage_count = usage['daily']

        # Get limits from settings (or RateLimitService defaults if not set)
        hourly_limit = self.rate_limit_service.hourly_limit
        daily_limit = self.rate_limit_service.daily_limit

        # Calculate remaining requests
        hourly_remaining = max(0, hourly_limit - hourly_usage_count)
        daily_remaining = max(0, daily_limit - daily_usage_count)

        # Calculate time until reset (approximate)
        hourly_reset = 0  # Placeholder
        daily_reset = 0  # Placeholder

        logger.debug(f"Rate limit check for IP {ip_address}: Hourly {hourly_usage_count}/{hourly_limit}, Daily {daily_usage_count}/{daily_limit}")

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
