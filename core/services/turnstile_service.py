"""
Cloudflare Turnstile verification service.

This service handles token validation with Cloudflare's Turnstile API
to protect against bot abuse while maintaining invisible user experience.
"""
import logging
import requests
from django.conf import settings
from typing import Tuple

logger = logging.getLogger(__name__)


class TurnstileService:
    """
    Service for validating Cloudflare Turnstile tokens.

    Provides bot protection by validating tokens against Cloudflare's API
    before allowing access to protected endpoints.
    """

    VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

    def __init__(self):
        """Initialize the service with configuration from Django settings."""
        self.secret_key = getattr(settings, 'TURNSTILE_SECRET_KEY', None)
        self.site_key = getattr(settings, 'TURNSTILE_SITE_KEY', None)

        if not self.secret_key:
            logger.error("TURNSTILE_SECRET_KEY not configured")
        if not self.site_key:
            logger.error("TURNSTILE_SITE_KEY not configured")

    def verify_token(self, token: str, remote_ip: str = None) -> Tuple[bool, str]:
        self.remote_ip = remote_ip
        payload = self._build_payload(token, remote_ip)
        try:
            response = self._make_request(payload)
            return self._process_response(response)
        except requests.exceptions.RequestException as e:
            return False, str(e)

    def _build_payload(self, token: str, remote_ip: str) -> dict:
        return {
            "secret": self.secret_key,
            "response": token,
            "remoteip": remote_ip
        }

    def _make_request(self, payload: dict) -> requests.Response:
        response = requests.post(self.VERIFY_URL, data=payload, timeout=10)
        response.raise_for_status()
        return response

    def _process_response(self, response: requests.Response) -> Tuple[bool, str]:
        result = response.json()
        if result.get("success", False):
            logger.info(f"Turnstile verification successful for IP: {self.remote_ip}")
            return True, ""
        else:
            # Log the specific error codes for debugging
            error_codes = result.get('error-codes', [])
            logger.warning(f"Turnstile verification failed. Error codes: {error_codes}, IP: {self.remote_ip}")

            # Return user-friendly error message
            if 'timeout-or-duplicate' in error_codes:
                return False, "Verification expired. Please try again."
            elif 'invalid-input-response' in error_codes:
                return False, "Invalid verification token."
            else:
                return False, "Verification failed. Please try again."

    def is_configured(self) -> bool:
        """
        Check if Turnstile is properly configured.

        Returns:
            True if both site key and secret key are configured
        """
        return bool(self.secret_key and self.site_key)


# Global instance for easy import
turnstile_service = TurnstileService()
