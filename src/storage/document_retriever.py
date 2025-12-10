"""
src/storage/document_retriever.py

Implementation of DocumentRetriever for fetching documents from S3-compatible storage.
This class provides read-only access to documents stored in an S3 bucket.

Top-level declarations:
- DocumentRetriever: Class handling connection to S3 and document retrieval
- CacheEntry: Data class for cache entries with metadata
"""

import logging
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

from ..config import config

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with content and metadata for size tracking and LRU eviction."""

    content: str
    size_bytes: int
    last_accessed: datetime
    object_key: str


class DocumentRetriever:
    # Class handling connection to S3 and document retrieval with caching
    # Cache limit: 25MB, persistent files: examples.md, cpl.md, mcpl.md, sgt.md, wo.md
    MAX_CACHE_SIZE_BYTES = 25 * 1024 * 1024  # 25MB
    PERSISTENT_FILES = {"examples.md", "cpl.md", "mcpl.md", "sgt.md", "wo.md"}

    def __init__(self):
        # Initialize the S3 client with configuration from AppConfig
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

        # Initialize cache
        self._cache: dict[str, CacheEntry] = {}
        self._current_cache_size = 0

    def get_document(self, category: str, filename: str) -> Optional[str]:
        # Retrieve a document from S3 storage by category and filename, using cache
        try:
            # Build the object key (path) in S3
            object_key = self._build_object_key(category, filename)

            # Check cache first
            if object_key in self._cache:
                logger.debug(f"Cache hit for {object_key}")
                cache_entry = self._cache[object_key]
                # Update last accessed time
                cache_entry.last_accessed = datetime.now()
                return cache_entry.content

            logger.debug(f"Cache miss for {object_key}, fetching from S3")
            # Fetch the raw bytes from S3
            content = self._fetch_from_s3(object_key)

            # Convert to string with appropriate encoding detection
            decoded_content = self._decode_content(content)

            # Add to cache
            self._add_to_cache(object_key, decoded_content)

            return decoded_content
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
        if category and not category.startswith("/"):
            return f"{category}/{filename}"
        return filename

    def _fetch_from_s3(self, key: str) -> bytes:
        # Fetch the raw content of an S3 object
        try:
            response = self.s3_client.get_object(Bucket=config.storage.s3_bucket_name, Key=key)
            return bytes(response["Body"].read())
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

    def _add_to_cache(self, object_key: str, content: str) -> None:
        # Add document to cache, evicting oldest non-persistent entries if needed
        content_size = len(content.encode("utf-8"))

        # Evict oldest non-persistent entries until we have space
        while self._current_cache_size + content_size > self.MAX_CACHE_SIZE_BYTES:
            if not self._evict_oldest_non_persistent():
                # Could not evict anything, don't cache this document
                logger.warning(
                    f"Cannot cache {object_key}: would exceed cache limit and no evictable entries"
                )
                return

        # Add to cache
        self._cache[object_key] = CacheEntry(
            content=content,
            size_bytes=content_size,
            last_accessed=datetime.now(),
            object_key=object_key,
        )
        self._current_cache_size += content_size
        logger.info(
            f"Cached {object_key} ({content_size} bytes), total cache: {self._current_cache_size} bytes"
        )

    def _evict_oldest_non_persistent(self) -> bool:
        # Evict the oldest non-persistent file from cache, return True if evicted
        evictable_entries = [
            (key, entry) for key, entry in self._cache.items() if not self._is_persistent_file(key)
        ]

        if not evictable_entries:
            return False

        # Find oldest entry
        oldest_key, oldest_entry = min(evictable_entries, key=lambda x: x[1].last_accessed)

        # Remove from cache
        del self._cache[oldest_key]
        self._current_cache_size -= oldest_entry.size_bytes
        logger.info(
            f"Evicted {oldest_key} ({oldest_entry.size_bytes} bytes), cache now: {self._current_cache_size} bytes"
        )
        return True

    def _is_persistent_file(self, object_key: str) -> bool:
        # Check if the object key corresponds to a persistent file
        # Extract filename from object_key (e.g., "paceNote/cpl.md" -> "cpl.md")
        filename = object_key.split("/")[-1] if "/" in object_key else object_key
        return filename in self.PERSISTENT_FILES
