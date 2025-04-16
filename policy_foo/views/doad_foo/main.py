"""
Agent responsible for synthesizing a final answer from extracted policy content.

This acts as the 'Synthesizer' agent in the DOAD workflow.
"""
import logging
from pathlib import Path
from core.services import OpenRouterService

logger = logging.getLogger(__name__)

# Define the specific model for the Synthesizer agent
SYNTHESIZER_MODEL_NAME = "anthropic/claude-3.5-sonnet"

# Define base path for prompts relative to this file's directory
PROMPT_DIR = Path(__file__).parent.parent / 'prompts' / 'doad_foo'
SYNTHESIZER_PROMPT_TEMPLATE_PATH = PROMPT_DIR / 'main.md'


def synthesize_answer(context: str, messages: list) -> str:
    """
    Synthesizes a final answer using an LLM based on provided context and conversation history.

    Args:
        context: A string containing the concatenated results (expected XML) from reader agents.
        messages: A list of message dictionaries representing the conversation history.

    Returns:
        A string containing the final assistant response, expected to be in the
        specified XML format (<response><answer>...</answer>...</response>).
        Returns a fallback error XML if a critical error occurs.
    """
    logger.info(f"DOAD Synthesizer: Starting synthesis using model {SYNTHESIZER_MODEL_NAME}.")
    open_router_service = OpenRouterService(model=SYNTHESIZER_MODEL_NAME)

    try:
        logger.debug(f"DOAD Synthesizer: Loading prompt template from: {SYNTHESIZER_PROMPT_TEMPLATE_PATH}")
        with open(SYNTHESIZER_PROMPT_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            system_prompt_template = f.read()

        system_prompt = system_prompt_template.format(policies_content=context)
        logger.debug("DOAD Synthesizer: System prompt formatted successfully.")

        llm_messages = [{"role": "system", "content": system_prompt}]
        llm_messages.extend(messages)
        logger.debug(f"DOAD Synthesizer: Prepared {len(llm_messages)} messages for LLM.")

        llm_response_text = open_router_service.generate_completion(
            messages=llm_messages,
            temperature=0.4,
            max_tokens=1000
        )

        if isinstance(llm_response_text, str) and llm_response_text.strip():
            if llm_response_text.startswith("Error") or llm_response_text.startswith("OpenRouter API error"):
                logger.error(f"DOAD Synthesizer: Received error from OpenRouterService: {llm_response_text}")
                return (
                    "<response>"
                    "<answer>Sorry, I encountered an error while generating the final response.</answer>"
                    "<citations></citations>"
                    "<follow_up>Please try rephrasing your question.</follow_up>"
                    "</response>"
                )

            result = llm_response_text.strip()
            logger.info("DOAD Synthesizer: LLM returned synthesized response.")
            if not result.startswith("<response>"):
                logger.warning("DOAD Synthesizer: LLM response might not be in expected XML format. Returning as is.")
            return result
        else:
            logger.error(f"DOAD Synthesizer: Failed to get valid content from LLM response. Received: {llm_response_text}")
            return (
                "<response>"
                "<answer>Sorry, I couldn't generate a response based on the retrieved information.</answer>"
                "<citations></citations>"
                "<follow_up>You could try asking in a different way.</follow_up>"
                "</response>"
            )

    except FileNotFoundError as e:
        logger.exception(f"DOAD Synthesizer: Prompt file not found: {e}. Cannot proceed.")
        return (
            "<response>"
            "<answer>Internal error: Synthesizer prompt missing.</answer>"
            "<citations></citations>"
            "<follow_up>Please contact support.</follow_up>"
            "</response>"
        )
    except Exception as e:
        logger.exception(f"DOAD Synthesizer: An unexpected error occurred: {e}")
        return (
            "<response>"
            "<answer>An unexpected internal error occurred while synthesizing the response.</answer>"
            "<citations></citations>"
            "<follow_up>Please try again later.</follow_up>"
            "</response>"
        )


"""
Workflow:
1. Receives concatenated XML string (containing extracted information from relevant DOADs)
   and the original user query/conversation history from the orchestrator (`doad_foo/__init__.py`).
2. Loads the system prompt from `policy_foo/prompts/doad_foo/main.md` (or a dedicated synthesizer prompt).
    - Replaces the `{POLICY_CONTENT}` placeholder in the system prompt
      with the concatenated XML string.
3. Constructs the messages payload for the final synthesis LLM call, including:
    - The formatted system prompt.
    - The user query and conversation history.
4. Sends the synthesis request to the LLM service (`core/services/open_router_service.py`).
5. Receives the final synthesized response string from the LLM.
6. Returns the final assistant message back to the orchestrator (`doad_foo/__init__.py`).

Note: Parsing of the final LLM response is handled by the frontend.
"""
