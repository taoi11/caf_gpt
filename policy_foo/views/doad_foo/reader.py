"""
Agent responsible for retrieving the content of a specific DOAD document
and extracting relevant information using an LLM.
"""
import logging
from pathlib import Path
from core.services import OpenRouterService, doad_service, DocumentNotFoundError

logger = logging.getLogger(__name__)

# Define the specific model for the Reader agent
READER_MODEL_NAME = "google/gemini-2.0-flash-001"

# Define base path for prompts relative to the policy_foo app directory
PROMPT_DIR = Path(__file__).parent.parent.parent / 'prompts' / 'doad_foo'
READER_PROMPT_TEMPLATE_PATH = PROMPT_DIR / 'reader.md'


def read_doad_content(doad_number: str, messages: list) -> str:
    """
    Retrieves a DOAD document from the database, uses an LLM to extract relevant sections
    based on the conversation history, and returns the result as an XML string.

    Args:
        doad_number: The specific DOAD number (e.g., "1000-1").
        messages: A list of message dictionaries representing the conversation history.

    Returns:
        An XML string containing the extracted relevant content or a
        "Not relevant" indicator within the XML structure. Returns an empty
        string if the DOAD file cannot be found or a critical error occurs.
    """
    logger.info(f"DOAD Reader: Starting content retrieval for DOAD {doad_number} using model {READER_MODEL_NAME}.")
    open_router_service = OpenRouterService(model=READER_MODEL_NAME)

    # Retrieve DOAD content from database
    try:
        logger.debug(f"DOAD Reader: Attempting to read DOAD document: {doad_number}")
        policy_content = doad_service.get_doad_content(doad_number)
        logger.info(f"DOAD Reader: Successfully read {len(policy_content)} characters from database")
        logger.debug(f"DOAD Reader: First 100 chars of content: {policy_content[:100]}")  # Log snippet of content
    except DocumentNotFoundError:
        logger.error(f"DOAD Reader: DOAD document not found in database: {doad_number}")
        return ""
    except Exception as db_ex:
        logger.exception(f"DOAD Reader: Error reading from database (DOAD {doad_number}): {db_ex}")
        return ""

    try:
        # Load and format prompt
        logger.debug(f"DOAD Reader: Loading reader prompt template from: {READER_PROMPT_TEMPLATE_PATH}")
        with open(READER_PROMPT_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            system_prompt_template = f.read()

        system_prompt = system_prompt_template.format(POLICY_CONTENT=policy_content)
        logger.debug("DOAD Reader: System prompt formatted successfully.")

        # Prepare messages for LLM
        llm_messages = [{"role": "system", "content": system_prompt}]
        llm_messages.extend(messages)
        logger.debug(f"DOAD Reader: Prepared {len(llm_messages)} messages for LLM.")
        logger.debug(f"DOAD Reader [{doad_number}]: Sending messages to LLM: {llm_messages}")  # Log messages being sent

        # Call LLM Service
        llm_response_text = open_router_service.generate_completion(
            prompt=llm_messages,
            temperature=0.2
        )
        logger.debug(f"DOAD Reader [{doad_number}]: Raw response from LLM: '{llm_response_text}'")  # Log raw response

        # Process and return response
        if isinstance(llm_response_text, str) and llm_response_text.strip():
            if llm_response_text.startswith("Error") or llm_response_text.startswith("OpenRouter API error"):
                logger.error(f"DOAD Reader: Received error from OpenRouterService for DOAD {doad_number}: {llm_response_text}")
                return (
                    f"<policy_extract>"
                    f"<policy_number>{doad_number}</policy_number>"
                    f"<section></section>"
                    f"<content>Error processing document.</content>"
                    f"</policy_extract>"
                )

            result = llm_response_text.strip()
            logger.info(f"DOAD Reader: LLM returned content for DOAD {doad_number}.")
            if not result.startswith("<policy_extract>"):
                logger.warning(f"DOAD Reader: LLM response for {doad_number} might not be in expected XML format. Returning as is.")
            return result
        else:
            logger.error(f"DOAD Reader: Failed to get valid content from LLM response for DOAD {doad_number}. Received: {llm_response_text}")
            return (
                f"<policy_extract>"
                f"<policy_number>{doad_number}</policy_number>"
                f"<section></section>"
                f"<content>No relevant content identified or error processing.</content>"
                f"</policy_extract>"
            )

    except FileNotFoundError as e:
        logger.exception(f"DOAD Reader: Prompt file not found: {e}. Cannot proceed for DOAD {doad_number}.")
        return (
            f"<policy_extract>"
            f"<policy_number>{doad_number}</policy_number>"
            f"<section></section>"
            f"<content>Internal error: Reader prompt missing.</content>"
            f"</policy_extract>"
        )
    except Exception as e:
        logger.exception(f"DOAD Reader: An unexpected error occurred while processing DOAD {doad_number}: {e}")
        return (
            f"<policy_extract>"
            f"<policy_number>{doad_number}</policy_number>"
            f"<section></section>"
            f"<content>Internal error processing document.</content>"
            f"</policy_extract>"
        )
