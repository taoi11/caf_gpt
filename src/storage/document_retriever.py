"""
src/storage/document_retriever.py

Implementation of DocumentRetriever for fetching documents from S3-compatible storage.
This class provides read-only access to documents stored in an S3 bucket.

Top-level declarations:
- DocumentRetriever: Class handling connection to S3 and document retrieval
"""

import logging
from typing import Optional

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

from ..config import config

logger = logging.getLogger(__name__)


class DocumentRetriever:
    # Class handling connection to S3 and document retrieval
    def __init__(self):
        """Initialize the S3 client with configuration from AppConfig."""
        storage_config = config.storage

        # Create an S3 client with the appropriate endpoint if provided
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=storage_config.s3_endpoint_url or None,
            aws_access_key_id=storage_config.s3_access_key,
            aws_secret_access_key=storage_config.s3_secret_key,
            region_name=storage_config.s3_region or None,
            use_ssl=True,
        )

        # Configure path style if needed (for some S3-compatible services)
        if storage_config.use_path_style_endpoint:
            self.s3_client.meta.events.register(
                "choose-signer.s3.*", lambda **kwargs: kwargs["chooser"].use_legacy()
            )

    def get_document(self, category: str, filename: str) -> Optional[str]:
        # Retrieve a document from S3 storage by category and filename
        try:
            # Build the object key (path) in S3
            object_key = self._build_object_key(category, filename)

            # Fetch the raw bytes from S3
            content = self._fetch_from_s3(object_key)

            # Convert to string with appropriate encoding detection
            return self._decode_content(content)
        except (NoCredentialsError, PartialCredentialsError) as e:
            logger.error(f"S3 credentials error: {e}")
            return None
        except ClientError as e:
            logger.error(f"S3 client error: {e}")
            if e.response["Error"]["Code"] == "404":
                logger.warning(f"Document not found: {object_key}")
            return None

    def _build_object_key(self, category: str, filename: str) -> str:
        # Construct the S3 object key from category and filename
        # Ensures proper path format for S3 objects
        if category and not category.startswith("/"):
            return f"{category}/{filename}"
        return filename

    def _fetch_from_s3(self, key: str) -> bytes:
        # Fetch the raw content of an S3 object
        # Uses bucket name from configuration
        try:
            response = self.s3_client.get_object(Bucket=config.storage.s3_bucket_name, Key=key)
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"Failed to fetch {key} from S3: {e}")
            raise

    def _decode_content(self, content: bytes) -> str:
        # Convert byte content to string with appropriate encoding detection
        # Tries UTF-8 first, falls back to ISO-8859-1 if needed
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return content.decode("iso-8859-1")
            except Exception as e:
                logger.error(f"Failed to decode content: {e}")
                raise ValueError("Unable to decode document content")
