"""
Services package for the PaceNote app.
"""
from core.utils.s3_client import S3Client
from core.services.open_router_service import OpenRouterService
from .prompt_service import PromptService

# Create aliases for backward compatibility
S3Service = S3Client 