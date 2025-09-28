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

from core.utils.turnstile_utils import validate_turnstile_token

logger = logging.getLogger(__name__)


class PaceNoteView(TemplateView):
    """
    Renders the main PaceNote generator interface (pace_notes.html).

    Now uses Cloudflare Turnstile for bot protection instead of rate limiting.
    """
    template_name = 'pacenote_foo/pace_notes.html'

    def get_context_data(self, **kwargs):
        """
        Adds Turnstile configuration to the template context.
        """
        context = super().get_context_data(**kwargs)

        # Add Turnstile site key for frontend integration
        from django.conf import settings
        context['turnstile_site_key'] = getattr(settings, 'TURNSTILE_SITE_KEY', '')

        return context


@method_decorator(csrf_exempt, name='dispatch')
class PaceNoteGeneratorView(View):
    """
    Handles the AJAX POST request to generate a pace note.

    This view is responsible for:
    1. Validating Turnstile token for bot protection
    2. Parsing request data
    3. Validating input
    4. Delegating to service layer for pace note generation
    5. Returning appropriate JSON responses
    """

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request logic for pace note generation.
        """
        try:
            # --- Turnstile Validation ---
            is_valid, error_response = validate_turnstile_token(request)
            if not is_valid:
                return error_response

            # --- Parse and Validate Input ---
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

            # --- Generate Pace Note ---
            # Delegate to service layer for pace note generation
            from .services import generate_pace_note
            result = generate_pace_note(user_input, rank)

            # Log successful generation
            if result['status'] == 'success':
                logger.info("Successfully generated pace note")

            # Return the result directly
            return JsonResponse(result)

        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON format'
            }, status=400)
        except Exception as e:
            logger.error(f"Error generating pace note: {e}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
