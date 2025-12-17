"""
src/agents/utils/xml_parser.py

Shared XML parsing utilities for agent response handling.
Centralizes XML parsing logic to ensure consistent error handling and response structure.

Top-level declarations:
- ParsedXMLResponse: Base dataclass for parsed XML responses
- parse_xml_response: Main XML parsing function with type-specific handlers
"""

import re
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

from src.agents.types import XMLParseError

# Pre-compiled regex for finding any known tag in a single pass
# Matches both self-closing tags and tags with content, including attributes
_KNOWN_TAGS_PATTERN = re.compile(
    r"<(reply|no_response|research|rank|feedback_note)(?:\s+[^>]*)?(?:\s*/>|>(.*?)</\1>)",
    re.DOTALL,
)


@dataclass
class ParsedXMLResponse:
    # Base structure for parsed XML responses with common fields
    type: str  # Response type from XML root tag (reply, no_response, research, rank, feedback_note)
    content: Optional[str] = None  # Text content from response
    extra: Optional[Dict[str, Any]] = None  # Additional type-specific data


def parse_xml_response(
    response: str,
    type_handlers: Optional[Dict[str, Callable[[ET.Element], Dict[str, Any]]]] = None,
) -> ParsedXMLResponse:
    # Parse XML response by extracting known tags (reply, no_response, research, rank, feedback_note)
    # Uses single regex pass instead of multiple patterns for better performance
    # Ignores everything outside the tags (markdown fences, explanations, etc)
    # Custom handlers can extract additional data into 'extra' field
    # Raises XMLParseError if no valid tags found or parsing fails
    try:
        # Single regex to find any known tag
        match = _KNOWN_TAGS_PATTERN.search(response)

        if match:
            tag = match.group(1)
            inner_content = match.group(2)

            # Self-closing tag (inner_content is None)
            if inner_content is None:
                return ParsedXMLResponse(type=tag, content="", extra=None)

            # Tag with content - parse the extracted XML
            xml_content = match.group(0)
            root = ET.fromstring(xml_content)
            type_ = root.tag
            content = root.text.strip() if root.text else ""
            extra: Dict[str, Any] = {}

            # Apply custom handler if provided for this type
            if type_handlers and type_ in type_handlers:
                handler_result = type_handlers[type_](root)
                extra.update(handler_result)
                # Allow handler to override content
                if "content" in handler_result:
                    content = handler_result["content"]

            # Default behavior: extract body element if present
            elif type_ == "reply":
                body_elem = root.find("body")
                if body_elem is not None and body_elem.text:
                    content = body_elem.text.strip()

            return ParsedXMLResponse(type=type_, content=content, extra=extra if extra else None)

        # No known tags found
        raise XMLParseError(
            response, "No valid XML tags found (reply, no_response, research, rank, feedback_note)"
        )

    except ET.ParseError as e:
        raise XMLParseError(response, str(e))
