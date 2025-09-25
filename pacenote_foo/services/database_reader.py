"""
Database reader service for pace note data.

This module provides a thin wrapper around core database service functions,
keeping the pacenote app's connection to core services simple and static.
"""
import logging
from core.services import pacenote_service, DocumentNotFoundError

logger = logging.getLogger(__name__)

def get_competency_list(rank: str) -> str:
    """
    Retrieves the competency list for a given rank from the database.
    
    Args:
        rank: The rank identifier (e.g., "cpl", "mcpl", "sgt", "wo")
    
    Returns:
        str: The competency list content
        
    Raises:
        Exception: If there's an error retrieving the content from the database
    """
    try:
        content = pacenote_service.get_competency_content(rank)
        logger.info(f"Successfully retrieved competency list for rank: {rank}")
        return content
    except DocumentNotFoundError as e:
        logger.error(f"Competency list not found for rank {rank}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve competency list for rank {rank}: {e}")
        raise

def get_examples() -> str:
    """
    Retrieves the examples content from the database.
    
    Returns:
        str: The examples content
        
    Raises:
        Exception: If there's an error retrieving the content from the database
    """
    try:
        content = pacenote_service.get_examples_content()
        logger.info("Successfully retrieved examples from database")
        return content
    except DocumentNotFoundError as e:
        logger.error(f"Examples content not found in database: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve examples from database: {e}")
        raise