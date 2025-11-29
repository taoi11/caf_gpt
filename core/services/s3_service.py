"""
S3 Service for interacting with Storj S3-compatible storage.

This module provides a service for interacting with S3-compatible storage services,
specifically configured for Storj by default. It handles listing files, reading
file contents, checking file existence, and retrieving file metadata.

The S3Service class is the primary interface for S3 operations, with S3Client
provided as an alias for backward compatibility.
"""
import os
import logging
from typing import Dict, List, Optional, Any

import boto3
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)


class S3ClientError(Exception):
    """Base exception class for S3Service errors."""
    pass


class S3ConnectionError(S3ClientError):
    """Exception raised when connection to S3 fails."""
    pass


class S3AuthenticationError(S3ClientError):
    """Exception raised when authentication with S3 fails."""
    pass


class S3FileNotFoundError(S3ClientError):
    """Exception raised when a file is not found in S3."""
    pass


class S3PermissionError(S3ClientError):
    """Exception raised when permission is denied for an S3 operation."""
    pass


class S3Service:
    """
    Service for interacting with S3-compatible storage services.

    This service is configured by default to work with Storj S3-compatible storage,
    but can be configured to work with any S3-compatible service through
    environment variables.

    Usage:
        s3_service = S3Service()
        files = s3_service.list_files('my-prefix/')
        content = s3_service.read_file('my-file.txt')
    """

    def __init__(self,
                 endpoint_url: Optional[str] = None,
                 bucket_name: Optional[str] = None,
                 access_key_id: Optional[str] = None,
                 secret_access_key: Optional[str] = None,
                 region_name: Optional[str] = None):
        """
        Initialize the S3 service with configuration.

        Args:
            endpoint_url: Custom S3 endpoint URL. Defaults to S3_ENDPOINT_URL env var or 'https://gateway.storjshare.io'.
            bucket_name: S3 bucket name. Defaults to S3_BUCKET_NAME env var or 'policies'.
            access_key_id: AWS access key ID. Defaults to AWS_ACCESS_KEY_ID env var.
            secret_access_key: AWS secret access key. Defaults to AWS_SECRET_ACCESS_KEY env var.
            region_name: AWS region name. Defaults to S3_REGION_NAME env var or 'us-east-1'.

        Raises:
            S3ConnectionError: If connection to S3 fails.
            S3AuthenticationError: If authentication with S3 fails.
        """
        # Get configuration from parameters, environment variables, or defaults
        self.endpoint_url = endpoint_url or os.environ.get('S3_ENDPOINT_URL', 'https://gateway.storjshare.io')
        self.bucket_name = bucket_name or os.environ.get('S3_BUCKET_NAME', 'policies')
        self.access_key_id = access_key_id or os.environ.get('AWS_ACCESS_KEY_ID')
        self.secret_access_key = secret_access_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.region_name = region_name or os.environ.get('S3_REGION_NAME', 'us-east-1')

        if not self.bucket_name:
            raise ValueError("Bucket name must be provided either as an argument or through S3_BUCKET_NAME env var")

        # Initialize the S3 client
        try:
            self.s3 = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region_name
            )
            logger.info(f"S3 service initialized with endpoint: {self.endpoint_url}, bucket: {self.bucket_name}")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code in ('InvalidAccessKeyId', 'SignatureDoesNotMatch'):
                logger.error(f"Authentication error initializing S3 service: {str(e)}")
                raise S3AuthenticationError(f"Authentication failed: {str(e)}")
            else:
                logger.error(f"Error initializing S3 service: {str(e)}")
                raise S3ConnectionError(f"Failed to initialize S3 service: {str(e)}")
        except BotoCoreError as e:
            logger.error(f"Connection error initializing S3 service: {str(e)}")
            raise S3ConnectionError(f"Failed to connect to S3: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error initializing S3 service: {str(e)}")
            raise S3ConnectionError(f"Unexpected error: {str(e)}")

    def list_files(self, prefix: str = '', delimiter: str = '/', max_keys: int = 1000) -> List[Dict[str, Any]]:
        """
        List files in the S3 bucket with the given prefix.

        Args:
            prefix: Prefix to filter files by. Default is empty string (list all).
            delimiter: Delimiter to use for hierarchical listing. Default is '/'.
            max_keys: Maximum number of keys to return. Default is 1000.

        Returns:
            List of dictionaries containing file information.

        Raises:
            S3ConnectionError: If connection to S3 fails.
            S3AuthenticationError: If authentication with S3 fails.
            S3PermissionError: If permission is denied.
        """
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                Delimiter=delimiter,
                MaxKeys=max_keys
            )

            files = []
            # Process regular files (Contents)
            for item in response.get('Contents', []):
                files.append({
                    'key': item.get('Key'),
                    'size': item.get('Size'),
                    'last_modified': item.get('LastModified'),
                    'type': 'file'
                })

            # Process prefixes (directories)
            for prefix_item in response.get('CommonPrefixes', []):
                files.append({
                    'key': prefix_item.get('Prefix'),
                    'type': 'directory'
                })

            logger.info(f"Listed {len(files)} files with prefix '{prefix}'")
            return files

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code in ('InvalidAccessKeyId', 'SignatureDoesNotMatch'):
                logger.error(f"Authentication error listing files: {str(e)}")
                raise S3AuthenticationError(f"Authentication failed: {str(e)}")
            elif error_code == 'AccessDenied':
                logger.error(f"Permission denied listing files: {str(e)}")
                raise S3PermissionError(f"Permission denied: {str(e)}")
            else:
                logger.error(f"Error listing files: {str(e)}")
                raise S3ConnectionError(f"Failed to list files: {str(e)}")
        except BotoCoreError as e:
            logger.error(f"Connection error listing files: {str(e)}")
            raise S3ConnectionError(f"Failed to connect to S3: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error listing files: {str(e)}")
            raise S3ConnectionError(f"Unexpected error: {str(e)}")

    def read_file(self, key: str) -> str:
        """
        Read a file from S3 and return its contents as a string.

        Args:
            key: The key (path) of the file to read.

        Returns:
            The contents of the file as a string.

        Raises:
            S3ConnectionError: If connection to S3 fails.
            S3AuthenticationError: If authentication with S3 fails.
            S3FileNotFoundError: If the file is not found.
            S3PermissionError: If permission is denied.
        """
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            content = response['Body'].read().decode('utf-8')
            logger.info(f"Read file '{key}' ({len(content)} bytes)")
            return content
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == '404' or error_code == 'NoSuchKey' or error_code == 'NotFound':
                logger.error(f"File not found: {key}")
                raise S3FileNotFoundError(f"File not found: {key}")
            elif error_code in ('InvalidAccessKeyId', 'SignatureDoesNotMatch'):
                logger.error(f"Authentication error reading file: {str(e)}")
                raise S3AuthenticationError(f"Authentication failed: {str(e)}")
            elif error_code == 'AccessDenied':
                logger.error(f"Permission denied reading file: {str(e)}")
                raise S3PermissionError(f"Permission denied: {str(e)}")
            else:
                logger.error(f"Error reading file: {str(e)}")
                raise S3ConnectionError(f"Failed to read file: {str(e)}")
        except BotoCoreError as e:
            logger.error(f"Connection error reading file: {str(e)}")
            raise S3ConnectionError(f"Failed to connect to S3: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error reading file: {str(e)}")
            raise S3ConnectionError(f"Unexpected error: {str(e)}")

    # Additional methods will be added here...


# For backward compatibility
S3Client = S3Service
