"""
Database service for shared database integration.

This module provides services for retrieving document content from the shared
PostgreSQL database.
"""
import logging
from typing import List, Optional, Dict, Any
from django.db import connection
from core.models import DoadDocument, LeaveDocument

logger = logging.getLogger(__name__)


class DatabaseServiceError(Exception):
    """Base exception class for database service errors."""
    pass


class DocumentNotFoundError(DatabaseServiceError):
    """Exception raised when a document is not found in the database."""
    pass


class DatabaseConnectionError(DatabaseServiceError):
    """Exception raised when database connection fails."""
    pass


class BasePolicyDatabaseService:
    """
    Base service class for database operations.

    Provides common functionality for document retrieval and error handling.
    """

    def __init__(self):
        """Initialize the database service."""
        self.logger = logger

    def test_connection(self) -> bool:
        """
        Test database connection health.

        Returns:
            bool: True if connection is healthy, False otherwise.
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            return False

    def _aggregate_text_chunks(self, chunks) -> str:
        """
        Aggregate text chunks into a single document.

        Args:
            chunks: QuerySet of document chunks

        Returns:
            str: Combined text content
        """
        if not chunks:
            return ""

        # Combine all text chunks, ordered by creation time
        combined_text = "\n".join(chunk.text_chunk for chunk in chunks)

        self.logger.info(f"Aggregated {len(chunks)} chunks into {len(combined_text)} characters")
        return combined_text

    def _format_metadata_for_logging(self, metadata: Optional[Dict[str, Any]]) -> str:
        """Format metadata for logging purposes."""
        if not metadata:
            return "No metadata"

        # Extract key fields for logging
        title = metadata.get('title', metadata.get('subject', 'Unknown'))
        section = metadata.get('section', metadata.get('chapter', 'Unknown'))
        return f"Title: {title}, Section: {section}"


class DoadDatabaseService(BasePolicyDatabaseService):
    """
    Service for DOAD (Defence Operations and Activities Directive) document operations.

    Provides methods to retrieve DOAD documents from the database.
    """

    def get_doad_content(self, doad_number: str) -> str:
        """
        Get the complete content of a DOAD document by number.

        Args:
            doad_number: The DOAD number (e.g., "1000-1")

        Returns:
            str: The complete DOAD document content

        Raises:
            DocumentNotFoundError: If the DOAD document is not found
            DatabaseConnectionError: If database connection fails
        """
        self.logger.info(f"Retrieving DOAD content for number: {doad_number}")

        try:
            # Get all chunks for this DOAD number
            chunks = DoadDocument.get_by_doad_number(doad_number)

            if not chunks.exists():
                self.logger.error(f"DOAD document not found: {doad_number}")
                raise DocumentNotFoundError(f"DOAD document not found: {doad_number}")

            # Log metadata from first chunk for debugging
            first_chunk = chunks.first()
            if first_chunk and first_chunk.metadata:
                metadata_info = self._format_metadata_for_logging(first_chunk.metadata)
                self.logger.debug(f"DOAD {doad_number} metadata: {metadata_info}")

            # Aggregate all chunks into complete document
            content = self._aggregate_text_chunks(chunks)

            self.logger.info(f"Successfully retrieved DOAD {doad_number}: {len(content)} characters")
            return content

        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving DOAD {doad_number}: {e}")
            raise DatabaseConnectionError(f"Failed to retrieve DOAD document: {e}")

    def get_available_doads(self) -> List[str]:
        """
        Get list of all available DOAD numbers.

        Returns:
            List[str]: List of available DOAD numbers

        Raises:
            DatabaseConnectionError: If database connection fails
        """
        try:
            doad_numbers = list(DoadDocument.get_available_doad_numbers())
            self.logger.info(f"Found {len(doad_numbers)} available DOAD documents")
            return doad_numbers
        except Exception as e:
            self.logger.error(f"Error retrieving available DOADs: {e}")
            raise DatabaseConnectionError(f"Failed to retrieve DOAD list: {e}")

    def get_doad_metadata(self, doad_number: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific DOAD document.

        Args:
            doad_number: The DOAD number

        Returns:
            Optional[Dict[str, Any]]: Metadata dictionary or None if not found
        """
        try:
            first_chunk = DoadDocument.get_by_doad_number(doad_number).first()
            if first_chunk:
                return first_chunk.metadata
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving DOAD metadata for {doad_number}: {e}")
            return None


class PaceNoteDatabaseService(BasePolicyDatabaseService):
    """
    Service for pace note document operations.

    Provides methods to retrieve pace note content from the database.
    """

    # Mapping from rank to chapter identifiers in the database
    RANK_TO_CHAPTER_MAP = {
        'cpl': 'cpl',
        'mcpl': 'mcpl',
        'sgt': 'sgt',
        'wo': 'wo'
    }

    def get_competency_content(self, rank: str) -> str:
        """
        Get competency content for a specific rank.

        Args:
            rank: The rank identifier (e.g., "cpl", "mcpl", "sgt", "wo")

        Returns:
            str: The competency content for the rank

        Raises:
            DocumentNotFoundError: If competency content is not found
            DatabaseConnectionError: If database connection fails
        """
        self.logger.info(f"Retrieving competency content for rank: {rank}")

        # Map rank to chapter identifier
        chapter = self.RANK_TO_CHAPTER_MAP.get(rank.lower(), 'cpl')  # Default to cpl

        try:
            # Get all chunks for this chapter
            chunks = LeaveDocument.get_by_chapter(chapter)

            if not chunks.exists():
                self.logger.error(f"Competency content not found for rank: {rank} (chapter: {chapter})")
                raise DocumentNotFoundError(f"Competency content not found for rank: {rank}")

            # Log metadata from first chunk for debugging
            first_chunk = chunks.first()
            if first_chunk and first_chunk.metadata:
                metadata_info = self._format_metadata_for_logging(first_chunk.metadata)
                self.logger.debug(f"Rank {rank} metadata: {metadata_info}")

            # Aggregate all chunks into complete content
            content = self._aggregate_text_chunks(chunks)

            self.logger.info(f"Successfully retrieved competency content for rank {rank}: {len(content)} characters")
            return content

        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving competency content for rank {rank}: {e}")
            raise DatabaseConnectionError(f"Failed to retrieve competency content: {e}")

    def get_examples_content(self) -> str:
        """
        Get examples content from the database.

        This method looks for content with 'examples' in the chapter or metadata.

        Returns:
            str: The examples content

        Raises:
            DocumentNotFoundError: If examples content is not found
            DatabaseConnectionError: If database connection fails
        """
        self.logger.info("Retrieving examples content")

        try:
            # Look for chunks with 'examples' in the chapter field
            chunks = LeaveDocument.objects.filter(
                chapter__icontains='examples'
            ).order_by('created_at')

            if not chunks.exists():
                # Fallback: look in metadata for examples
                chunks = LeaveDocument.objects.filter(
                    metadata__icontains='examples'
                ).order_by('created_at')

            if not chunks.exists():
                self.logger.error("Examples content not found in database")
                raise DocumentNotFoundError("Examples content not found")

            # Aggregate all chunks into complete content
            content = self._aggregate_text_chunks(chunks)

            self.logger.info(f"Successfully retrieved examples content: {len(content)} characters")
            return content

        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving examples content: {e}")
            raise DatabaseConnectionError(f"Failed to retrieve examples content: {e}")

    def get_available_ranks(self) -> List[str]:
        """
        Get list of available ranks based on chapter data.

        Returns:
            List[str]: List of available rank identifiers
        """
        try:
            chapters = list(LeaveDocument.get_available_chapters())
            # Filter chapters that match our rank mapping
            available_ranks = [
                rank for rank, chapter in self.RANK_TO_CHAPTER_MAP.items()
                if chapter in chapters
            ]
            self.logger.info(f"Found {len(available_ranks)} available ranks: {available_ranks}")
            return available_ranks
        except Exception as e:
            self.logger.error(f"Error retrieving available ranks: {e}")
            return list(self.RANK_TO_CHAPTER_MAP.keys())  # Return default list


# Convenience instances for easy import
doad_service = DoadDatabaseService()
pacenote_service = PaceNoteDatabaseService()
