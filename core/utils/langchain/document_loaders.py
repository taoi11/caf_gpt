"""
Simple document loader utilities for LangChain.

This module provides basic document loaders for text and markdown files,
including a simple S3 document loader that integrates with our S3 client.
"""
import logging
from typing import Dict, Any, Optional

from core.utils.s3_client import S3Client, S3FileNotFoundError

logger = logging.getLogger(__name__)


class DocumentLoaderError(Exception):
    """Base exception class for document loader errors."""
    pass


class TextLoader:
    """
    Simple loader for text files.
    """

    @staticmethod
    def load_from_file(file_path: str) -> str:
        """
        Load a text file and return its contents.

        Args:
            file_path: Path to the text file.

        Returns:
            The text content as a string.

        Raises:
            DocumentLoaderError: If the file cannot be read.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {str(e)}")
            raise DocumentLoaderError(f"Failed to load text file: {str(e)}")


class MarkdownLoader:
    """
    Simple loader for Markdown files.
    """

    @staticmethod
    def load_from_file(file_path: str) -> str:
        """
        Load a Markdown file and return its contents.

        Args:
            file_path: Path to the Markdown file.

        Returns:
            The Markdown content as a string.

        Raises:
            DocumentLoaderError: If the file cannot be read.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading Markdown file {file_path}: {str(e)}")
            raise DocumentLoaderError(f"Failed to load Markdown file: {str(e)}")


class S3DocumentLoader:
    """
    Simple loader for documents stored in S3.

    This class integrates with our custom S3Client to load documents from S3.
    """

    def __init__(
        self,
        s3_client: Optional[S3Client] = None,
        endpoint_url: Optional[str] = None,
        bucket_name: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        """
        Initialize the S3 document loader.

        Args:
            s3_client: Optional existing S3Client instance.
            endpoint_url: S3 endpoint URL (used if s3_client not provided).
            bucket_name: S3 bucket name (used if s3_client not provided).
            access_key_id: AWS access key ID (used if s3_client not provided).
            secret_access_key: AWS secret access key (used if s3_client not provided).
            region_name: AWS region name (used if s3_client not provided).
        """
        # Use provided S3Client or create a new one
        if s3_client:
            self.s3_client = s3_client
        else:
            self.s3_client = S3Client(
                endpoint_url=endpoint_url,
                bucket_name=bucket_name,
                access_key_id=access_key_id,
                secret_access_key=secret_access_key,
                region_name=region_name,
            )

        logger.info("S3DocumentLoader initialized")

    def load_document(self, key: str) -> str:
        """
        Load a document from S3 and return its contents.

        Args:
            key: The S3 key (path) of the document.

        Returns:
            The document content as a string.

        Raises:
            S3FileNotFoundError: If the file is not found in S3.
            DocumentLoaderError: If the file cannot be loaded.
        """
        try:
            # Read file content
            content = self.s3_client.read_file(key, decode=True)
            return content

        except S3FileNotFoundError:
            logger.error(f"File not found in S3: {key}")
            raise
        except Exception as e:
            logger.error(f"Error loading document from S3 {key}: {str(e)}")
            raise DocumentLoaderError(f"Failed to load document from S3: {str(e)}")

    def list_documents(self, prefix: str = '') -> Dict[str, Any]:
        """
        List documents in S3 with the given prefix.

        Args:
            prefix: Directory or prefix to list files from.

        Returns:
            List of dictionaries containing file information.
        """
        try:
            # List files in S3
            return self.s3_client.list_files(prefix=prefix)
        except Exception as e:
            logger.error(f"Error listing documents in S3 with prefix {prefix}: {str(e)}")
            raise DocumentLoaderError(f"Failed to list documents in S3: {str(e)}")
