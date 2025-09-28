"""
Local file reader service for pace note data.

This module provides functions to read prompt data from local filesystem files,
replacing the previous database/S3-based storage system.
"""
import logging
import pathlib

logger = logging.getLogger(__name__)


class LocalFileReaderError(Exception):
    """Base exception for local file reader errors."""
    pass


class FileNotFoundError(LocalFileReaderError):
    """Raised when a required file is not found."""
    pass


def get_competency_list(rank: str) -> str:
    """
    Retrieves the competency list for a given rank from local files.

    Args:
        rank: The rank identifier (e.g., "cpl", "mcpl", "sgt", "wo")

    Returns:
        str: The competency list content

    Raises:
        FileNotFoundError: If the competency file is not found
        LocalFileReaderError: If there's an error reading the file
    """
    try:
        # Build path to the competency file
        prompts_dir = (
            pathlib.Path(__file__).parent.parent /
            "prompts" /
            "competencies"
        )
        competency_file = prompts_dir / f"{rank.lower()}.md"

        if not competency_file.exists():
            logger.error(f"Competency file not found for rank {rank}: {competency_file}")
            raise FileNotFoundError(f"Competency file not found for rank: {rank}")

        # Read the file content
        with open(competency_file, 'r', encoding='utf-8') as file:
            content = file.read().strip()

        logger.info(f"Successfully retrieved competency list for rank: {rank} ({len(content)} characters)")
        return content

    except FileNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve competency list for rank {rank}: {e}")
        raise LocalFileReaderError(f"Error reading competency file: {e}")


def get_examples() -> str:
    """
    Retrieves the examples content from local files.

    Returns:
        str: The examples content

    Raises:
        FileNotFoundError: If the examples file is not found
        LocalFileReaderError: If there's an error reading the file
    """
    try:
        # Build path to the examples file
        prompts_dir = (
            pathlib.Path(__file__).parent.parent /
            "prompts" /
            "competencies"
        )
        examples_file = prompts_dir / "examples.md"

        if not examples_file.exists():
            logger.error(f"Examples file not found: {examples_file}")
            raise FileNotFoundError("Examples file not found")

        # Read the file content
        with open(examples_file, 'r', encoding='utf-8') as file:
            content = file.read().strip()

        logger.info(f"Successfully retrieved examples from local file ({len(content)} characters)")
        return content

    except FileNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve examples from local file: {e}")
        raise LocalFileReaderError(f"Error reading examples file: {e}")


def get_base_prompt() -> str:
    """
    Retrieves the base prompt template from local files.

    Returns:
        str: The base prompt template content

    Raises:
        FileNotFoundError: If the base prompt file is not found
        LocalFileReaderError: If there's an error reading the file
    """
    try:
        # Build path to the base prompt file
        prompts_dir = (
            pathlib.Path(__file__).parent.parent /
            "prompts"
        )
        base_file = prompts_dir / "base.md"

        if not base_file.exists():
            logger.error(f"Base prompt file not found: {base_file}")
            raise FileNotFoundError("Base prompt file not found")

        # Read the file content
        with open(base_file, 'r', encoding='utf-8') as file:
            content = file.read().strip()

        logger.info(f"Successfully retrieved base prompt from local file ({len(content)} characters)")
        return content

    except FileNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve base prompt from local file: {e}")
        raise LocalFileReaderError(f"Error reading base prompt file: {e}")
