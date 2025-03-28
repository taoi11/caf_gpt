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

rate_limit_service = RateLimitService()

class PaceNoteView(TemplateView):
    """
    View for the PaceNote generator interface.
    """
    template_name = 'pacenote_foo/pace_notes.html'


@method_decorator(csrf_exempt, name='dispatch')
class PaceNoteGeneratorView(View):
    """
    View for generating pace notes.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for pace note generation.
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

            # Get the IP address from the request headers
            ip = request.META.get('HTTP_CF_CONNECTING_IP') or request.META.get('HTTP_CF_PSEUDO_IPV4') or request.META.get('REMOTE_ADDR')

            # Increment the rate limit counter
            if not rate_limit_service.increment(ip):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Rate limit exceeded. Please try again later.'
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

            # Generate pace note
            pace_note = open_router_service.generate_completion(prompt)

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
    View for checking API rate limits.
    """

    def get(self, request, *args, **kwargs):
        """
        Return the current rate limits for the user.
        """
        ip = request.META.get('HTTP_CF_CONNECTING_IP') or request.META.get('HTTP_CF_PSEUDO_IPV4') or request.META.get('REMOTE_ADDR')
        usage = rate_limit_service.get_usage(ip)

        return JsonResponse({
            'hourly': {
                'limit': rate_limit_service.hourly_limit,
                'remaining': max(0, rate_limit_service.hourly_limit - usage['hourly']),
                'reset': 3600,  # seconds until reset
            },
            'daily': {
                'limit': rate_limit_service.daily_limit,
                'remaining': max(0, rate_limit_service.daily_limit - usage['daily']),
                'reset': 86400,  # seconds until reset
            }
        })
