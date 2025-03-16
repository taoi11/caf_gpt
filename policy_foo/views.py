"""
PolicyFoo app views.
"""
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

from .models import PolicyDocument


class ChatInterfaceView(TemplateView):
    """
    View for the policy chat interface.
    """
    template_name = 'policy_foo/chat_interface.html'


class DocumentSearchView(ListView):
    """
    View for searching policy documents.
    """
    model = PolicyDocument
    template_name = 'policy_foo/document_search.html'
    context_object_name = 'documents'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(title__icontains=query) | queryset.filter(content__icontains=query)
        return queryset


@method_decorator(csrf_exempt, name='dispatch')
class PolicyRetrieverView(View):
    """
    API view for policy retrieval.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for policy retrieval.
        """
        try:
            data = json.loads(request.body)
            query = data.get('query', '')

            # Placeholder for policy retrieval implementation
            # In a real implementation, this would call a service to perform the search
            results = {
                'query': query,
                'response': 'This is a sample policy response.',
                'citations': [
                    {'document_id': 'policy-001', 'title': 'Sample Policy 1', 'excerpt': 'Relevant excerpt from policy.'},
                    {'document_id': 'policy-002', 'title': 'Sample Policy 2', 'excerpt': 'Another relevant excerpt.'},
                ],
                'status': 'success'
            }

            return JsonResponse(results)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
