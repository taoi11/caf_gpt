"""
Local prompt reader service for pace note data.

This module reads prompt data from local files instead of S3,
removing the S3 dependency completely.
"""
import logging
import pathlib

logger = logging.getLogger(__name__)

# Base path to the prompts directory
PROMPTS_BASE_PATH = pathlib.Path(__file__).parent.parent / "prompts"

# Map ranks to their corresponding file names
RANK_TO_FILE_MAP = {
    'cpl': 'cpl.md',
    'mcpl': 'mcpl.md', 
    'sgt': 'sgt.md',
    'wo': 'wo.md'
}

def get_competency_list(rank: str) -> str:
    """
    Retrieves the competency list for a given rank from local files.
    
    Args:
        rank: The rank identifier (e.g., "cpl", "mcpl", "sgt", "wo")
    
    Returns:
        str: The competency list content
        
    Raises:
        Exception: If there's an error reading the file
    """
    # Get the correct filename for the rank, defaulting to cpl.md
    competency_filename = RANK_TO_FILE_MAP.get(rank, 'cpl.md')
    competency_path = PROMPTS_BASE_PATH / "competencies" / competency_filename
    
    try:
        with open(competency_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info(f"Successfully retrieved competency list for rank: {rank}")
        return content
    except Exception as e:
        logger.error(f"Failed to retrieve competency list for rank {rank}: {e}")
        raise

def get_examples() -> str:
    """
    Retrieves the examples file from local files.
    
    Returns:
        str: The examples content
        
    Raises:
        Exception: If there's an error reading the file
    """
    examples_path = PROMPTS_BASE_PATH / "competencies" / "examples.md"
    
    try:
        with open(examples_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info("Successfully retrieved examples from local file")
        return content
    except Exception as e:
        logger.error(f"Failed to retrieve examples from local file: {e}")
        raise