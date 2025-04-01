"""
PaceNoteFoo app views.
"""
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from core.services import OpenRouterService, S3Service
from .services import PromptService
from core.services.rate_limit_service import RateLimitService

logger = logging.getLogger(__name__)

# Instantiate the service once
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


@method_decorator(csrf_exempt, name='dispatch') # Disable CSRF for this API endpoint
class PaceNoteGeneratorView(View):
    """
    Handles the AJAX POST request to generate a pace note.

    It validates input, checks rate limits, calls the necessary services
    (S3, PromptService, OpenRouterService), generates the pace note,
    increments the rate limit counter on success, and returns the result
    or an error as a JSON response.
    """

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request logic for pace note generation.

        Steps:
        1. Parse request data.
        2. Validate user input.
        3. Determine client IP address.
        4. Check rate limits (return 429 if exceeded).
        5. Initialize services (S3, Prompt, AI).
        6. Fetch necessary data from S3.
        7. Construct the prompt.
        8. Generate the pace note via AI service.
        9. Increment rate limit counter (only on success).
        10. Return JSON response (success or error).
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
            # Determine the client's IP address, prioritizing Cloudflare headers.
            # This is crucial for accurate rate limiting.
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
            # Check if the IP has exceeded hourly or daily limits BEFORE performing
            # the expensive operation of generating a pace note.
            if not rate_limit_service.check_limits(ip):
                logger.warning(f"Rate limit exceeded for IP: {ip}")
                # Fetch current usage to include in the error message
                usage = rate_limit_service.get_usage(ip)
                return JsonResponse({
                    'status': 'error',
                    # Provide a detailed message about which limit was hit
                    'message': f"Rate limit exceeded. Hourly: {usage.get('hourly', 0)}/{rate_limit_service.hourly_limit}, Daily: {usage.get('daily', 0)}/{rate_limit_service.daily_limit}. Please try again later."
                }, status=429)

            # Initialize services
            s3_client = S3Service(bucket_name="policies")
            prompt_service = PromptService()
            open_router_service = OpenRouterService()

            # Map the form values to the correct S3 file paths
            rank_to_file_map = {
                'cpl': 'cpl.md',
                'mcpl': 'mcpl.md',  # Changed from mcpl_sgt.md to mcpl.md
                'sgt': 'sgt.md',  # Changed from sgt_wojtg.md to sgt.md
                'wo': 'wo.md'  # Changed from wojtg_mwopwo.md to wo.md
            }

            # Get competency list and examples from S3
            competency_filename = rank_to_file_map.get(rank, 'cpl.md')
            competency_path = f"paceNote/{competency_filename}"
            examples_path = "paceNote/examples.md"

            try:
                competency_list = s3_client.read_file(competency_path)
                examples = s3_client.read_file(examples_path)
            except Exception as e:
                logger.error(f"Error retrieving S3 content: {e}")
                return JsonResponse({
                    'status': 'error',
                    'message': f"Error retrieving content from S3: {str(e)}"
                }, status=500)

            # Construct prompt
            prompt = prompt_service.construct_prompt(user_input, competency_list, examples)

            # Generate pace note using the AI service
            pace_note = open_router_service.generate_completion(prompt)

            # --- Rate Limit Increment ---
            # Only increment the usage counter AFTER the request has been
            # successfully processed and the pace note generated.
            # This prevents penalizing users for failed requests (e.g., server errors).
            rate_limit_service.increment(ip)
            logger.info(f"Successfully generated pace note and incremented rate limit for IP: {ip}")

            # Return the successful result
            return JsonResponse({
                'status': 'success',
                'pace_note': pace_note
            })
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
