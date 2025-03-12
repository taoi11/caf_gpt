# S3 Client Implementation

## Task Description
Create an S3 client utility class for interacting with Storj S3-compatible storage. This utility will be used by both PaceNoteFoo and PolicyFoo apps to list and read files from an S3 bucket.

## Task Instructions
1. Create an S3Client class in `core/utils/s3_client.py` with the following features:
   - Methods for listing and reading files from S3
   - Comprehensive error handling for S3 operations
   - Configuration via environment variables with hardcoded fallbacks
   - Logging of operations and errors

2. Implement the following methods:
   - `__init__`: Initialize the client with configuration
   - `list_files`: List files in a directory/prefix
   - `read_file`: Read a file's contents
   - `file_exists`: Check if a file exists
   - `get_file_metadata`: Get metadata for a file

3. Use the following hardcoded values as fallbacks:
   - URL: https://gateway.storjshare.io
   - Bucket: policies

4. Add proper docstrings and type hints to all methods

## Relevant File Structure
```yaml
core:
  utils:
    - __init__.py
    - s3_client.py  # Create this file
```

## Example Usage
```python
# Example usage in a view
from core.utils.s3_client import S3Client

def some_view(request):
    s3_client = S3Client()
    
    # List files with a prefix
    files = s3_client.list_files(prefix="documents/")
    
    # Read a specific file
    content = s3_client.read_file("documents/policy.pdf")
    
    # Check if a file exists
    exists = s3_client.file_exists("documents/policy.pdf")
    
    # Get file metadata
    metadata = s3_client.get_file_metadata("documents/policy.pdf")
```

## Dependencies
- boto3 for AWS S3 API
- python-dotenv for environment variable loading

## Error Handling Requirements
- Handle connection errors
- Handle authentication errors
- Handle file not found errors
- Handle permission errors
- Return meaningful error messages

## Environment Variables
- `S3_ENDPOINT_URL`: Custom S3 endpoint URL (default: https://gateway.storjshare.io)
- `S3_BUCKET_NAME`: S3 bucket name (default: policies)
- `AWS_ACCESS_KEY_ID`: AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key
- `S3_REGION_NAME`: AWS region name (optional)
