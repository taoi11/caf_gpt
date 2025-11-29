"""
PaceNoteFoo app views.
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views import View

from core.services.rate_limit_service import RateLimitService

logger = logging.getLogger(__name__)

# Initialize rate limit service
rate_limit_service = RateLimitService()

class PaceNoteView(TemplateView):
    """
    Renders the main PaceNote generator interface (pace_notes.html).

    This view also fetches the initial rate limit status for the current user's IP
    and passes it to the template context so the UI can display it on load.
    """
    template_name = 'pacenote_foo/pace_notes.html'

    def get_context_data(self, **kwargs):
        """
        Adds initial rate limit data to the template context.
        """
        context = super().get_context_data(**kwargs)
        request = self.request
        # Determine the client's IP address. Prioritize Cloudflare headers
        # (HTTP_CF_CONNECTING_IP, HTTP_CF_PSEUDO_IPV4) over the standard REMOTE_ADDR
        # as the app might be behind a proxy or load balancer like Cloudflare.
        ip = request.META.get('HTTP_CF_CONNECTING_IP') or \
            request.META.get('HTTP_CF_PSEUDO_IPV4') or \
            request.META.get('REMOTE_ADDR')

        if ip:
            usage = rate_limit_service.get_usage(ip)
            context['rate_limit_hourly_used'] = usage.get('hourly', 0)
            context['rate_limit_daily_used'] = usage.get('daily', 0)
        else:
            # Handle cases where IP might not be available (e.g., tests)
            context['rate_limit_hourly_used'] = 0
            context['rate_limit_daily_used'] = 0
            logger.warning("Could not determine IP address for rate limit context.")

        context['rate_limit_hourly_limit'] = rate_limit_service.hourly_limit
        context['rate_limit_daily_limit'] = rate_limit_service.daily_limit
        return context


@method_decorator(csrf_exempt, name='dispatch')
class PaceNoteGeneratorView(View):
    """
    Handles the AJAX POST request to generate a pace note.

    This view is responsible for:
    1. Parsing request data
    2. Validating input
    3. Checking rate limits
    4. Delegating to service layer for pace note generation
    5. Incrementing rate limits on success
    6. Returning appropriate JSON responses
    """

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request logic for pace note generation.
        """
        try:
            data = json.loads(request.body)
            user_input = data.get('user_input', '').strip()
            rank = data.get('rank', 'cpl')

            # Validate user input
            if not user_input:
                logger.warning("Empty user input provided for pace note generation")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please provide some input text to generate a pace note'
                }, status=400)

            logger.info(f"Generating pace note for rank: {rank}")

            # --- IP Address Determination ---
            # Determine the client's IP address for rate limiting
            ip = request.META.get('HTTP_CF_CONNECTING_IP') or \
                request.META.get('HTTP_CF_PSEUDO_IPV4') or \
                request.META.get('REMOTE_ADDR')

            # Handle cases where IP cannot be determined (should be rare)
            if not ip:
                logger.error("Could not determine client IP address for rate limiting.")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Could not determine your IP address.'
                }, status=400)

            # --- Rate Limit Check ---
            if not rate_limit_service.check_limits(ip):
                logger.warning(f"Rate limit exceeded for IP: {ip}")
                # Fetch current usage to include in the error message
                usage = rate_limit_service.get_usage(ip)
                message = (
                    f"Rate limit exceeded. "
                    f"Hourly: {usage.get('hourly', 0)}/{rate_limit_service.hourly_limit}, "
                    f"Daily: {usage.get('daily', 0)}/{rate_limit_service.daily_limit}. "
                    f"Please try again later."
                )
                return JsonResponse({
                    'status': 'error',
                    'message': message
                }, status=429)

            # --- Generate Pace Note ---
            # Delegate to service layer for pace note generation
            from .services import generate_pace_note
            result = generate_pace_note(user_input, rank)
            
            # --- Rate Limit Increment (Success Case) ---
            # Increment rate limit only on successful generation
            if result['status'] == 'success':
                if not rate_limit_service.increment(ip):
                    logger.warning(f"Rate limit increment failed post-generation for IP: {ip}, but proceeding.")
                logger.info(f"Successfully generated pace note for IP: {ip}")
            
            # Return the result directly
            return JsonResponse(result)
            
        except Exception as e:
            logger.error(f"Error generating pace note: {e}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)


class RateLimitsView(View):
    """
    Provides an API endpoint (`/pacenote/api/rate-limits/`) for the frontend
    to fetch the current rate limit status for the user's IP address.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve the current rate limit status.

        Returns a JSON response containing hourly and daily limits,
        remaining counts, and reset times (in seconds).
        """
        # Determine the client's IP address using the same logic as PaceNoteGeneratorView
        ip = request.META.get('HTTP_CF_CONNECTING_IP') or \
            request.META.get('HTTP_CF_PSEUDO_IPV4') or \
            request.META.get('REMOTE_ADDR')

        # Get current usage counts for the IP from the service
        usage = rate_limit_service.get_usage(ip)

        # Calculate remaining counts, ensuring they don't go below zero
        hourly_remaining = max(0, rate_limit_service.hourly_limit - usage.get('hourly', 0))
        daily_remaining = max(0, rate_limit_service.daily_limit - usage.get('daily', 0))

        return JsonResponse({
            'hourly': {
                'limit': rate_limit_service.hourly_limit,
                'remaining': hourly_remaining,
                'reset': 3600,  # Approximate seconds until hourly reset (1 hour)
            },
            'daily': {
                'limit': rate_limit_service.daily_limit,
                'remaining': daily_remaining,
                'reset': 86400,  # Approximate seconds until daily reset (24 hours)
            }
        })
