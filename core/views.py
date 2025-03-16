"""
Core app views.
"""
from django.http import JsonResponse
from django.views.generic import TemplateView


class LandingPageView(TemplateView):
    """
    Landing page view for the application.
    """
    template_name = 'core/landing_page.html'


class HealthCheckView(TemplateView):
    """
    Health check view for monitoring and load balancers.
    """

    def get(self, request, *args, **kwargs):
        """
        Return a simple JSON response indicating the service is up.
        """
        return JsonResponse({
            'status': 'ok',
            'service': 'caf_gpt',
        })
