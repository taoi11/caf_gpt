"""
PolicyFoo app views.
"""
from django.views.generic import TemplateView


class ChatInterfaceView(TemplateView):
    """
    View for the policy chat interface.
    """
    template_name = 'policy_foo/chat_interface.html'
