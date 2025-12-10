"""
tests/test_document_retriever.py

Unit tests for DocumentRetriever caching functionality.
Tests cache hit/miss, size limits, eviction policy, and persistent file protection.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys

# Mock the config module before importing DocumentRetriever
mock_storage_config = Mock()
mock_storage_config.s3_endpoint_url = None
mock_storage_config.s3_access_key = "test_key"
mock_storage_config.s3_secret_key = "test_secret"
mock_storage_config.s3_region = "us-east-1"
mock_storage_config.use_path_style_endpoint = False
mock_storage_config.s3_bucket_name = "test-bucket"

mock_config = Mock()
mock_config.storage = mock_storage_config
sys.modules["src.config"] = Mock(config=mock_config)

from src.utils.document_retriever import DocumentRetriever, CacheEntry


@pytest.fixture
def mock_s3_client():
    """Mock boto3 S3 client."""
    with patch("src.utils.document_retriever.boto3.client") as mock_client:
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        yield mock_s3


@pytest.fixture
def retriever(mock_s3_client):
    """Create DocumentRetriever with mocked S3 client."""
    return DocumentRetriever()


def test_cache_miss_and_add(retriever, mock_s3_client):
    """Test that a cache miss fetches from S3 and adds to cache."""
    # Mock S3 response
    mock_response = {"Body": MagicMock()}
    mock_response["Body"].read.return_value = b"Test content"
    mock_s3_client.get_object.return_value = mock_response

    # First call should be a cache miss
    result = retriever.get_document("test", "file.md")

    assert result == "Test content"
    assert "test/file.md" in retriever._cache
    assert retriever._cache["test/file.md"].content == "Test content"
    assert retriever._current_cache_size == len("Test content".encode("utf-8"))
    mock_s3_client.get_object.assert_called_once()


def test_cache_hit(retriever, mock_s3_client):
    """Test that a cache hit returns cached content without S3 call."""
    # Pre-populate cache
    object_key = "test/file.md"
    content = "Cached content"
    retriever._cache[object_key] = CacheEntry(
        content=content,
        size_bytes=len(content.encode("utf-8")),
        last_accessed=datetime.now(),
        object_key=object_key,
    )
    retriever._current_cache_size = len(content.encode("utf-8"))

    # Call should be a cache hit
    result = retriever.get_document("test", "file.md")

    assert result == "Cached content"
    mock_s3_client.get_object.assert_not_called()


def test_cache_hit_updates_last_accessed(retriever):
    """Test that cache hits update the last_accessed timestamp."""
    object_key = "test/file.md"
    old_time = datetime.now() - timedelta(hours=1)
    content = "Test content"

    retriever._cache[object_key] = CacheEntry(
        content=content,
        size_bytes=len(content.encode("utf-8")),
        last_accessed=old_time,
        object_key=object_key,
    )

    # Access the cached document
    retriever.get_document("test", "file.md")

    # Last accessed should be updated
    assert retriever._cache[object_key].last_accessed > old_time


def test_persistent_files_not_evicted(retriever, mock_s3_client):
    """Test that persistent files are not evicted from cache."""
    # Pre-populate cache with persistent file
    persistent_key = "paceNote/cpl.md"
    persistent_content = "A" * 1000
    retriever._cache[persistent_key] = CacheEntry(
        content=persistent_content,
        size_bytes=len(persistent_content.encode("utf-8")),
        last_accessed=datetime.now() - timedelta(hours=2),  # Oldest
        object_key=persistent_key,
    )
    retriever._current_cache_size = len(persistent_content.encode("utf-8"))

    # Add another non-persistent file
    non_persistent_key = "leave/leave_policy_2025.md"
    non_persistent_content = "B" * 500
    retriever._cache[non_persistent_key] = CacheEntry(
        content=non_persistent_content,
        size_bytes=len(non_persistent_content.encode("utf-8")),
        last_accessed=datetime.now() - timedelta(hours=1),
        object_key=non_persistent_key,
    )
    retriever._current_cache_size += len(non_persistent_content.encode("utf-8"))

    # Mock S3 to return large content that would trigger eviction
    large_content = "C" * (25 * 1024 * 1024)  # 25MB
    mock_response = {"Body": MagicMock()}
    mock_response["Body"].read.return_value = large_content.encode("utf-8")
    mock_s3_client.get_object.return_value = mock_response

    # Try to add a large file
    retriever.get_document("test", "large.md")

    # Persistent file should still be in cache, non-persistent should be evicted
    assert persistent_key in retriever._cache
    assert non_persistent_key not in retriever._cache


def test_eviction_oldest_first(retriever, mock_s3_client):
    """Test that oldest non-persistent files are evicted first."""
    # Add three non-persistent files with different access times
    old_time = datetime.now() - timedelta(hours=3)
    middle_time = datetime.now() - timedelta(hours=2)
    recent_time = datetime.now() - timedelta(hours=1)

    file1_key = "test/file1.md"
    file2_key = "test/file2.md"
    file3_key = "test/file3.md"

    content = "X" * 1000

    retriever._cache[file1_key] = CacheEntry(
        content=content,
        size_bytes=len(content.encode("utf-8")),
        last_accessed=old_time,
        object_key=file1_key,
    )
    retriever._cache[file2_key] = CacheEntry(
        content=content,
        size_bytes=len(content.encode("utf-8")),
        last_accessed=middle_time,
        object_key=file2_key,
    )
    retriever._cache[file3_key] = CacheEntry(
        content=content,
        size_bytes=len(content.encode("utf-8")),
        last_accessed=recent_time,
        object_key=file3_key,
    )
    retriever._current_cache_size = 3 * len(content.encode("utf-8"))

    # Mock S3 to return content that would require eviction
    new_content = "Y" * (25 * 1024 * 1024)  # 25MB
    mock_response = {"Body": MagicMock()}
    mock_response["Body"].read.return_value = new_content.encode("utf-8")
    mock_s3_client.get_object.return_value = mock_response

    # Add new file that requires eviction
    retriever.get_document("test", "new.md")

    # Oldest file should be evicted first
    assert file1_key not in retriever._cache
    # Other files may or may not be evicted depending on size, but oldest goes first


def test_cache_size_limit(retriever, mock_s3_client):
    """Test that cache respects the 25MB size limit."""
    # Add files up to the limit
    total_size = 0
    for i in range(10):
        content = f"Content {i}" * 1000
        mock_response = {"Body": MagicMock()}
        mock_response["Body"].read.return_value = content.encode("utf-8")
        mock_s3_client.get_object.return_value = mock_response

        retriever.get_document("test", f"file{i}.md")
        total_size += len(content.encode("utf-8"))

    # Cache size should not exceed limit
    assert retriever._current_cache_size <= DocumentRetriever.MAX_CACHE_SIZE_BYTES


def test_persistent_files_identification(retriever):
    """Test that persistent files are correctly identified."""
    assert retriever._is_persistent_file("paceNote/examples.md")
    assert retriever._is_persistent_file("paceNote/cpl.md")
    assert retriever._is_persistent_file("paceNote/mcpl.md")
    assert retriever._is_persistent_file("paceNote/sgt.md")
    assert retriever._is_persistent_file("paceNote/wo.md")
    assert not retriever._is_persistent_file("leave/leave_policy_2025.md")
    assert not retriever._is_persistent_file("test/other.md")


def test_cache_size_calculation(retriever, mock_s3_client):
    """Test that cache size is calculated using len(content.encode('utf-8'))."""
    content = "Test UTF-8 content with emojis 🎉"
    expected_size = len(content.encode("utf-8"))

    mock_response = {"Body": MagicMock()}
    mock_response["Body"].read.return_value = content.encode("utf-8")
    mock_s3_client.get_object.return_value = mock_response

    retriever.get_document("test", "utf8.md")

    assert retriever._current_cache_size == expected_size
    assert retriever._cache["test/utf8.md"].size_bytes == expected_size


def test_all_persistent_files_cache_full(retriever, mock_s3_client):
    """Test behavior when cache is full of only persistent files."""
    # Fill cache with persistent files
    persistent_files = ["examples.md", "cpl.md", "mcpl.md", "sgt.md", "wo.md"]
    total_size = 0

    for filename in persistent_files:
        content = "X" * (5 * 1024 * 1024)  # 5MB each
        retriever._cache[f"paceNote/{filename}"] = CacheEntry(
            content=content,
            size_bytes=len(content.encode("utf-8")),
            last_accessed=datetime.now(),
            object_key=f"paceNote/{filename}",
        )
        total_size += len(content.encode("utf-8"))

    retriever._current_cache_size = total_size

    # Try to add a new file - should not cache it
    new_content = "Y" * 1000
    mock_response = {"Body": MagicMock()}
    mock_response["Body"].read.return_value = new_content.encode("utf-8")
    mock_s3_client.get_object.return_value = mock_response

    result = retriever.get_document("test", "new.md")

    # Should return content but not cache it
    assert result == new_content
    assert "test/new.md" not in retriever._cache
    # Persistent files should remain
    for filename in persistent_files:
        assert f"paceNote/{filename}" in retriever._cache
