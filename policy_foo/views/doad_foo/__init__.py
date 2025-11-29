"""
Orchestrates the DOAD policy question-answering workflow.

Acts as the main entry point for the DOAD policy set, coordinating the
finder, reader, and synthesizer agents to generate a response based on
user queries and conversation history.
"""
import logging
import traceback
from .finder import find_doad_numbers
from .reader import read_doad_content
from .main import synthesize_answer

logger = logging.getLogger(__name__)


def handle_doad_request(messages: list) -> str:
    """
    Main function to handle a DOAD policy request.

    Args:
        messages: A list of message dictionaries representing the conversation history.
                  Each dictionary should have 'role' ('user' or 'assistant') and 'content'.

    Returns:
        A string containing the final assistant response, expected to be XML formatted.
    """
    logger.info("DOAD Orchestrator: Starting request handling.")
    final_assistant_message = ""

    try:
        # Call the 'finder' agent
        logger.debug(f"DOAD Orchestrator: Calling finder with messages: {messages}")
        doad_numbers_str = find_doad_numbers(messages)
        logger.info(f"DOAD Orchestrator: Finder returned: '{doad_numbers_str}'")

        # Handle "none" from finder
        if not doad_numbers_str or doad_numbers_str.strip().lower() == "none":
            logger.info("DOAD Orchestrator: No relevant DOADs found by finder.")
            return (
                "<response>"
                "<answer>I couldn't find any specific DOAD documents relevant to your query.</answer>"
                "<citations></citations>"
                "<follow_up>Could you please rephrase your question?</follow_up>"
                "</response>"
            )

        # Process DOAD numbers
        doad_numbers = [num.strip() for num in doad_numbers_str.split(',') if num.strip()]
        logger.info(f"DOAD Orchestrator: Processing DOAD numbers: {doad_numbers}")

        all_reader_results = []
        for doad_num in doad_numbers:
            try:
                logger.debug(f"DOAD Orchestrator: Calling reader for DOAD: {doad_num}")
                reader_result = read_doad_content(doad_num, messages)
                if reader_result:
                    all_reader_results.append(reader_result)
            except Exception as reader_ex:
                logger.error(f"DOAD Orchestrator: Error calling reader for DOAD {doad_num}: {reader_ex}")
                logger.debug(traceback.format_exc())

        concatenated_context = "\n".join(all_reader_results)
        if not concatenated_context:
            logger.warning("DOAD Orchestrator: All reader calls failed.")
            return (
                "<response>"
                "<answer>I identified relevant DOADs but couldn't retrieve their content.</answer>"
                "<citations></citations>"
                "<follow_up>Please try again later.</follow_up>"
                "</response>"
            )

        logger.info(f"DOAD Orchestrator: Concatenated context length: {len(concatenated_context)}")
        final_assistant_message = synthesize_answer(concatenated_context, messages)
        logger.info("DOAD Orchestrator: Synthesizer returned final response.")

    except Exception:
        logger.exception("DOAD Orchestrator: An unexpected error occurred.")
        final_assistant_message = (
            "<response>"
            "<answer>I encountered an error processing your request.</answer>"
            "<citations></citations>"
            "<follow_up>You can try rephrasing your question.</follow_up>"
            "</response>"
        )

    return final_assistant_message

# Placeholder functions (Remove these once actual agents are implemented)
