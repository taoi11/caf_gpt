"""Initialize views module and define public API."""
from django.views.generic import TemplateView
from django.conf import settings


class ChatInterfaceView(TemplateView):
    """
    View for the policy chat interface.
    """
    template_name = 'policy_foo/chat_interface.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['turnstile_site_key'] = settings.TURNSTILE_SITE_KEY
        return context
