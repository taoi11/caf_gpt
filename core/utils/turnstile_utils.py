"""
Utility functions for Cloudflare Turnstile validation.
"""
import logging
from django.http import JsonResponse
from core.services.turnstile_service import turnstile_service

logger = logging.getLogger(__name__)


def validate_turnstile_token(request):
    """
    Validate Turnstile token from request body.

    Args:
        request: Django request object

    Returns:
        tuple: (is_valid: bool, response: JsonResponse or None)
               If is_valid is False, response contains the error response
               If is_valid is True, response is None
    """
    # Check if Turnstile is configured
    if not turnstile_service.is_configured():
        logger.error("Turnstile is not properly configured")
        return False, JsonResponse({
            'status': 'error',
            'message': 'Bot protection service is not configured'
        }, status=500)

    # Get token from request body (JSON or POST)
    token = None
    if request.content_type == 'application/json':
        try:
            import json
            body = json.loads(request.body.decode('utf-8'))
            token = body.get('turnstile_token')
        except Exception as e:
            logger.warning(f"Error parsing JSON body: {e}")
    if not token:
        token = request.POST.get('turnstile_token')
    if not token:
        logger.warning("Missing Turnstile token in request body")
        return False, JsonResponse({
            'status': 'error',
            'message': 'Missing verification token'
        }, status=400)

    # Get client IP for additional validation
    ip = (
        request.META.get('HTTP_CF_CONNECTING_IP') or
        request.META.get('HTTP_CF_PSEUDO_IPV4') or
        request.META.get('REMOTE_ADDR')
    )

    # Verify token with Cloudflare
    is_valid, error_message = turnstile_service.verify_token(token, ip)

    if not is_valid:
        logger.warning(f"Turnstile validation failed for IP {ip}: {error_message}")
        return False, JsonResponse({
            'status': 'error',
            'message': error_message
        }, status=400)

    logger.info(f"Turnstile validation successful for IP: {ip}")
    return True, None


def get_client_ip(request):
    """
    Extract client IP address from request, prioritizing Cloudflare headers.

    Args:
        request: Django request object

    Returns:
        str: Client IP address or None if not found
    """
    return (
        request.META.get('HTTP_CF_CONNECTING_IP') or
        request.META.get('HTTP_CF_PSEUDO_IPV4') or
        request.META.get('REMOTE_ADDR')
    )
