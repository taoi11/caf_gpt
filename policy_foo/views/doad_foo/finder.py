"""
Agent responsible for identifying relevant DOAD document numbers based on the user query and conversation history.
"""
import logging
from pathlib import Path
from core.services import OpenRouterService

logger = logging.getLogger(__name__)

# Define the specific model for the Finder agent
FINDER_MODEL_NAME = "google/gemini-2.0-flash-001"

# Define base path for prompts relative to this file's directory
PROMPT_DIR = Path(__file__).parent.parent / 'prompts' / 'doad_foo'
FINDER_PROMPT_TEMPLATE_PATH = PROMPT_DIR / 'finder.md'
DOAD_LIST_TABLE_PATH = PROMPT_DIR / 'DOAD-list-table.md'


def find_doad_numbers(messages: list) -> str:
    """
    Identifies relevant DOAD numbers using an LLM based on conversation history.

    Args:
        messages: A list of message dictionaries representing the conversation history.
                  Each dictionary should have 'role' ('user' or 'assistant') and 'content'.

    Returns:
        A string containing comma-separated DOAD numbers or "none".
        Returns "none" if an error occurs during processing.
    """
    logger.info(f"DOAD Finder: Starting DOAD number identification using model: {FINDER_MODEL_NAME}.")
    open_router_service = OpenRouterService(model=FINDER_MODEL_NAME)

    try:
        # Load prompts
        logger.debug(f"DOAD Finder: Loading finder prompt template from: {FINDER_PROMPT_TEMPLATE_PATH}")
        with open(FINDER_PROMPT_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            system_prompt_template = f.read()

        logger.debug(f"DOAD Finder: Loading DOAD list table from: {DOAD_LIST_TABLE_PATH}")
        with open(DOAD_LIST_TABLE_PATH, 'r', encoding='utf-8') as f:
            policies_table_content = f.read()

        # Format system prompt
        system_prompt = system_prompt_template.format(policies_table=policies_table_content)
        logger.debug("DOAD Finder: System prompt formatted successfully.")

        # Prepare messages for LLM
        llm_messages = [{"role": "system", "content": system_prompt}]
        llm_messages.extend(messages)
        logger.debug(f"DOAD Finder: Prepared {len(llm_messages)} messages for LLM.")

        # Call LLM Service
        llm_response_text = open_router_service.generate_completion(
            messages=llm_messages,
            temperature=0.1,
            max_tokens=50
        )

        # Process and return response
        # Check if the response is a non-empty string and doesn't indicate an error from the service
        if isinstance(llm_response_text, str) and llm_response_text.strip():
            # Check for known error prefixes from OpenRouterService (optional but safer)
            if llm_response_text.startswith("Error") or llm_response_text.startswith("OpenRouter API error"):
                logger.error(f"DOAD Finder: Received error from OpenRouterService: {llm_response_text}")
                return "none"

            result = llm_response_text.strip()
            logger.info(f"DOAD Finder: LLM returned DOAD numbers: '{result}'")
            return result
        else:
            logger.error(f"DOAD Finder: Failed to get valid content from LLM response. Received: {llm_response_text}")
            return "none"

    except FileNotFoundError as e:
        logger.exception(f"DOAD Finder: Prompt file not found: {e}. Cannot proceed.")
        return "none"
    except Exception as e:
        logger.exception(f"DOAD Finder: An unexpected error occurred: {e}")
        return "none"
