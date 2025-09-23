"""
Core app views.
"""
import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render

logger = logging.getLogger(__name__)


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


@require_POST
@csrf_exempt
def csp_report_view(request):
    """
    Receives and logs CSP violation reports from browsers.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        if 'csp-report' in data:
            report = data['csp-report']
            logger.warning(
                "CSP Violation: %s",
                json.dumps(report, indent=2)
            )
    except Exception as e:
        logger.error(f"Error processing CSP report: {e}")

    return HttpResponse(status=204)  # No content response



