"""
S3 reader service for pace note data.

This module provides a thin wrapper around core S3 service functions,
keeping the pacenote app's connection to core services simple and static.
"""
import logging
from core.services.s3_service import S3Service

logger = logging.getLogger(__name__)

# Initialize S3 client once at module level for reuse
s3_client = S3Service(bucket_name="policies")

# Map ranks to their corresponding file names
RANK_TO_FILE_MAP = {
    'cpl': 'cpl.md',
    'mcpl': 'mcpl.md', 
    'sgt': 'sgt.md',
    'wo': 'wo.md'
}

def get_competency_list(rank: str) -> str:
    """
    Retrieves the competency list for a given rank from S3.
    
    Args:
        rank: The rank identifier (e.g., "cpl", "mcpl", "sgt", "wo")
    
    Returns:
        str: The competency list content
        
    Raises:
        Exception: If there's an error retrieving the file from S3
    """
    # Get the correct filename for the rank, defaulting to cpl.md
    competency_filename = RANK_TO_FILE_MAP.get(rank, 'cpl.md')
    competency_path = f"paceNote/{competency_filename}"
    
    try:
        content = s3_client.read_file(competency_path)
        logger.info(f"Successfully retrieved competency list for rank: {rank}")
        return content
    except Exception as e:
        logger.error(f"Failed to retrieve competency list for rank {rank}: {e}")
        raise

def get_examples() -> str:
    """
    Retrieves the examples file from S3.
    
    Returns:
        str: The examples content
        
    Raises:
        Exception: If there's an error retrieving the file from S3
    """
    examples_path = "paceNote/examples.md"
    
    try:
        content = s3_client.read_file(examples_path)
        logger.info("Successfully retrieved examples from S3")
        return content
    except Exception as e:
        logger.error(f"Failed to retrieve examples from S3: {e}")
        raise