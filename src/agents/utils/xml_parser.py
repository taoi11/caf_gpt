"""
src/agents/utils/xml_parser.py

Shared XML parsing utilities for agent response handling.
Centralizes XML parsing logic to ensure consistent error handling and response structure.

Top-level declarations:
- ParsedXMLResponse: Base dataclass for parsed XML responses
- parse_xml_response: Main XML parsing function with type-specific handlers
"""

import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

from src.agents.types import XMLParseError


@dataclass
class ParsedXMLResponse:
    # Base structure for parsed XML responses with common fields
    type: str  # Response type from XML root tag (reply, no_response, research, rank)
    content: Optional[str] = None  # Text content from response
    extra: Optional[Dict[str, Any]] = None  # Additional type-specific data


def parse_xml_response(
    response: str,
    type_handlers: Optional[Dict[str, Callable[[ET.Element], Dict[str, Any]]]] = None,
) -> ParsedXMLResponse:
    # Parse XML response string with optional custom type handlers for specific tags
    # Default behavior extracts type, content from text or <body> element
    # Custom handlers can extract additional data into 'extra' field
    # Raises XMLParseError if parsing fails or unknown tag encountered
    try:
        root = ET.fromstring(response)
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

        # Validate known types (extend this list as needed)
        elif type_ not in ["reply", "no_response"]:
            # Unknown type without handler
            if not type_handlers or type_ not in type_handlers:
                raise XMLParseError(response, f"Unknown XML tag: {type_}")

        return ParsedXMLResponse(type=type_, content=content, extra=extra if extra else None)

    except ET.ParseError as e:
        raise XMLParseError(response, str(e))
