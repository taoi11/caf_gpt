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
        """
        Verify a Turnstile token with Cloudflare.

        Args:
            token: The Turnstile token to verify
            remote_ip: The client's IP address (optional but recommended)

        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not self.secret_key:
            logger.error("Turnstile secret key not configured")
            return False, "Turnstile not properly configured"

        if not token:
            logger.warning("Empty token provided for verification")
            return False, "Missing verification token"

        # Prepare verification request
        data = {
            'secret': self.secret_key,
            'response': token,
        }

        # Include IP if provided for additional security
        if remote_ip:
            data['remoteip'] = remote_ip

        try:
            # Make verification request to Cloudflare
            response = requests.post(
                self.VERIFY_URL,
                data=data,
                timeout=10,  # 10 second timeout
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()

            result = response.json()

            if result.get('success', False):
                logger.info(f"Turnstile verification successful for IP: {remote_ip}")
                return True, ""
            else:
                # Log the specific error codes for debugging
                error_codes = result.get('error-codes', [])
                logger.warning(f"Turnstile verification failed. Error codes: {error_codes}, IP: {remote_ip}")

                # Return user-friendly error message
                if 'timeout-or-duplicate' in error_codes:
                    return False, "Verification expired. Please try again."
                elif 'invalid-input-response' in error_codes:
                    return False, "Invalid verification token."
                else:
                    return False, "Verification failed. Please try again."

        except requests.exceptions.Timeout:
            logger.error("Turnstile verification request timed out")
            return False, "Verification service temporarily unavailable"
        except requests.exceptions.RequestException as e:
            logger.error(f"Turnstile verification request failed: {e}")
            return False, "Verification service temporarily unavailable"
        except Exception as e:
            logger.error(f"Unexpected error during Turnstile verification: {e}")
            return False, "Verification failed"

    def is_configured(self) -> bool:
        """
        Check if Turnstile is properly configured.

        Returns:
            True if both site key and secret key are configured
        """
        return bool(self.secret_key and self.site_key)


# Global instance for easy import
turnstile_service = TurnstileService()
