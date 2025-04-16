"""Contains the main PolicyRouterView which acts as the central entry point for incoming chat requests.
"""
import json
import logging
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.services import RateLimitService
# Placeholder for future import: from .doad_foo import handle_doad_request

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class PolicyRouterView(View):
    """
    Handles incoming chat requests, validates them, routes them to the appropriate
    policy set handler, and manages rate limiting.
    """
    rate_limit_service = RateLimitService()
    supported_policy_sets = ['doad']  # Add more as they are implemented

    def _validate_request_data(self, data):
        """Validate the request data structure."""
        messages = data.get('messages')
        policy_set = data.get('policy_set')

        if not messages or not isinstance(messages, list):
            return None, HttpResponseBadRequest(
                json.dumps({'error': 'Missing or invalid "messages" field.'}),
                content_type='application/json'
            )
        if not policy_set or not isinstance(policy_set, str):
            return None, HttpResponseBadRequest(
                json.dumps({'error': 'Missing or invalid "policy_set" field.'}),
                content_type='application/json'
            )
        return (messages, policy_set), None

    def _validate_policy_set(self, policy_set):
        """Validate the requested policy set is supported."""
        if policy_set not in self.supported_policy_sets:
            error_msg = f'Unsupported policy_set: {policy_set}. Supported sets are: ' \
                f'{", ".join(self.supported_policy_sets)}'
            return HttpResponseBadRequest(
                json.dumps({'error': error_msg}),
                content_type='application/json'
            )
        return None

    def post(self, request, *args, **kwargs):
        """Handle POST requests containing chat messages and policy set information."""
        try:
            # Get and validate IP address
            ip_address = request.META.get('REMOTE_ADDR')
            if not ip_address:
                logger.warning("Could not determine client IP address for rate limit check.")
                return JsonResponse({'error': 'Could not determine client IP address.'}, status=400)

            # Check rate limits
            if not self.rate_limit_service.check_limits(ip_address):
                logger.warning(f"Rate limit exceeded for IP: {ip_address}")
                return JsonResponse({'error': 'Rate limit exceeded. Please try again later.'}, status=429)

            # Parse and validate request data
            data = json.loads(request.body)
            (messages, policy_set), error = self._validate_request_data(data)
            if error:
                return error

            logger.info(f"Received chat request for policy_set: {policy_set} from IP: {ip_address}")

            # Validate policy set
            error = self._validate_policy_set(policy_set)
            if error:
                return error

            # Route request
            if policy_set == 'doad':
                from .doad_foo import handle_doad_request
                assistant_response = handle_doad_request(messages)
            else:
                logger.error(f"Routing failed for validated policy_set: {policy_set}")
                return JsonResponse({'error': 'Internal server error: Routing failed.'}, status=500)

            # Increment rate limit counter
            if ip_address:
                self.rate_limit_service.increment(ip_address)
                logger.info(f"Incremented rate limit for IP: {ip_address}")

            return JsonResponse({'assistant_message': assistant_response})

        except json.JSONDecodeError:
            logger.error("Failed to decode JSON body.")
            return HttpResponseBadRequest(
                json.dumps({'error': 'Invalid JSON format.'}),
                content_type='application/json'
            )
        except Exception as e:
            logger.exception(f"An unexpected error occurred in PolicyRouterView: {e}")
            return JsonResponse({'error': 'An internal server error occurred.'}, status=500)
