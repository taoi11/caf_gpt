"""
PaceNoteFoo app views.
"""
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json


class ChatInterfaceView(TemplateView):
    """
    View for the chat interface.
    """
    template_name = 'pacenote_foo/chat_interface.html'


@method_decorator(csrf_exempt, name='dispatch')
class RagSearchView(View):
    """
    View for RAG search functionality.
    """
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for RAG search.
        """
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            
            # Placeholder for RAG search implementation
            # In a real implementation, this would call a service to perform the search
            results = {
                'query': query,
                'results': [
                    {'title': 'Sample Result 1', 'content': 'This is a sample result.'},
                    {'title': 'Sample Result 2', 'content': 'This is another sample result.'},
                ],
                'status': 'success'
            }
            
            return JsonResponse(results)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400) 