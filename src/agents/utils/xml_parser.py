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
    # Ignores everything outside the tags (markdown fences, explanations, etc)
    # Custom handlers can extract additional data into 'extra' field
    # Raises XMLParseError if no valid tags found or parsing fails
    try:
        # Known tags we're looking for
        known_tags = ["reply", "no_response", "research", "rank", "feedback_note"]
        
        # Try to find any of our known tags (handle both <tag>...</tag> and <tag/>)
        for tag in known_tags:
            # First try self-closing tag
            self_closing_pattern = f"<{tag}\\s*/>"
            match = re.search(self_closing_pattern, response)
            if match:
                # Self-closing tag with no content
                return ParsedXMLResponse(type=tag, content="", extra=None)
            
            # Then try regular tag with content
            pattern = f"<{tag}>(.*?)</{tag}>"
            match = re.search(pattern, response, re.DOTALL)
            if match:
                # Extract the full tag with content
                xml_content = match.group(0)
                
                # Parse the extracted XML
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
        raise XMLParseError(response, "No valid XML tags found (reply, no_response, research, rank, feedback_note)")

    except ET.ParseError as e:
        raise XMLParseError(response, str(e))
