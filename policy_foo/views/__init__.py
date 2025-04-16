"""Initialize views module and define public API."""
from django.views.generic import TemplateView


class ChatInterfaceView(TemplateView):
    """
    View for the policy chat interface.
    """
    template_name = 'policy_foo/chat_interface.html'
