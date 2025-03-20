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

from core.services import OpenRouterService
from .services import S3Service, PromptService

logger = logging.getLogger(__name__)


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
            user_input = data.get('user_input', '')
            rank = data.get('rank', 'cpl_mcpl')  # Default to cpl_mcpl

            logger.info(f"Generating pace note for rank: {rank}")

            # Initialize services
            s3_client = S3Service(bucket_name="policies")
            prompt_service = PromptService()
            open_router_service = OpenRouterService()

            # Get competency list and examples from S3
            competency_path = f"paceNote/{rank}.md"
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
