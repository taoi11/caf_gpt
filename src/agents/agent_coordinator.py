"""
src/agents/agent_coordinator.py

Orchestrator for prime_foo and sub-agent interactions, handling response parsing and research delegation.

Top-level declarations:
- AgentCoordinator: Main class coordinating LLM calls, parsing, and sub-agent delegation
"""

import logging
from typing import Dict, Any
import xml.etree.ElementTree as ET


from .prompt_manager import PromptManager
from .types import AgentResponse, PrimeFooResponse, ResearchRequest, XMLParseError
from .sub_agents.leave_foo_agent import LeaveFooAgent
from .feedback_note_agent import FeedbackNoteAgent, FeedbackNoteResponse
from .llm_utils import call_llm_with_retry, circuit_breaker, increment_circuit_breaker
from .utils.xml_parser import parse_xml_response
from src.config import config

logger = logging.getLogger(__name__)


class AgentCoordinator:
    # Main class coordinating LLM calls, parsing, and sub-agent delegation

    # Signature appended to all agent replies (HTML format with proper links)
    SIGNATURE = """

CAF-GPT
<a href="https://github.com/taoi11/caf_gpt">Source Code</a>
How to use CAF-GPT: <a href="https://github.com/taoi11/caf_gpt/blob/main/docs/quick_start.md">Documentation</a>"""

    # Generic error message returned to users when processing fails
    GENERIC_ERROR_MSG = "An unexpected error occurred while processing your email."

    def __init__(self, prompt_manager: PromptManager):
        # Initialize with prompt manager and load available sub-agents
        self.prompt_manager = prompt_manager
        self.sub_agents: Dict[str, Any] = {}
        self._load_sub_agents()
        # Initialize feedback note agent
        self.feedback_note_agent = FeedbackNoteAgent(self.prompt_manager)

    def _load_sub_agents(self) -> None:
        # Dynamically load sub-agents like LeaveFooAgent with prompt manager access
        self.sub_agents["leave_foo"] = LeaveFooAgent(self.prompt_manager)

    def _add_signature(self, content: str) -> str:
        # Append signature to reply content, marking HTML as safe for email composer
        from markupsafe import Markup
        return content + Markup(self.SIGNATURE)

    def _handle_agent_errors(self, agent_name: str, error: Exception) -> AgentResponse:
        # Centralized error handling for agent processing failures
        # Logs specific error types and returns generic error response
        if isinstance(error, XMLParseError):
            logger.error(f"XML parse failed in {agent_name}: {error.parse_error}")
        else:
            logger.error(f"Error in {agent_name}: {error}")
        return AgentResponse.error_result(self.GENERIC_ERROR_MSG)

    @circuit_breaker(max_calls=6)
    def process_email_with_prime_foo(self, email_context: str) -> AgentResponse:
        # Main coordination loop: send to prime_foo, parse response, handle research/reply/no_response iteratively
        try:
            prime_prompt = self.prompt_manager.get_prompt("prime_foo")
            messages = [
                {"role": "system", "content": prime_prompt},
                {"role": "user", "content": email_context},
            ]

            increment_circuit_breaker()
            response, parsed = call_llm_with_retry(
                messages, config.llm.prime_foo_model, self.parse_prime_foo_response
            )

            while True:
                if parsed.type == "no_response":
                    return AgentResponse.no_response_result()
                elif parsed.type == "reply":
                    # Append signature to policy agent replies
                    if not parsed.content:
                        logger.error("Reply type received but content is None")
                        return AgentResponse.error_result(self.GENERIC_ERROR_MSG)
                    reply_with_signature = self._add_signature(parsed.content)
                    return AgentResponse.success(reply_with_signature)
                elif parsed.type == "research":
                    if not parsed.research:
                        logger.error("Research type received but research is None")
                        return AgentResponse.error_result(self.GENERIC_ERROR_MSG)
                    research_result = self.handle_research_request(parsed.research)
                    # Send research results back to prime_foo
                    follow_up_messages = messages + [
                        {"role": "assistant", "content": response},
                        {"role": "user", "content": f"Research results: {research_result}"},
                    ]

                    increment_circuit_breaker()
                    response, parsed = call_llm_with_retry(
                        follow_up_messages,
                        config.llm.prime_foo_model,
                        self.parse_prime_foo_response,
                    )
                else:
                    return AgentResponse.error_result(self.GENERIC_ERROR_MSG)
        except (XMLParseError, Exception) as e:
            return self._handle_agent_errors("prime_foo coordination", e)

    def parse_prime_foo_response(self, response: str) -> PrimeFooResponse:
        # Parse XML for prime_foo responses using shared parser with research handler
        # Raises XMLParseError on failure
        def handle_research(root: ET.Element) -> Dict[str, Any]:
            # Extract research request with sub-agent and queries
            sub_agent_elem = root.find("sub_agent")
            if sub_agent_elem is not None:
                agent_type = sub_agent_elem.get("name", "")
                queries = []
                for query_elem in sub_agent_elem.findall("query"):
                    if query_elem.text:
                        queries.append(query_elem.text.strip())
                if queries:
                    return {"research": ResearchRequest(queries=queries, agent_type=agent_type)}
            return {}

        parsed = parse_xml_response(response, type_handlers={"research": handle_research})

        # Convert ParsedXMLResponse to PrimeFooResponse
        research = parsed.extra.get("research") if parsed.extra else None
        return PrimeFooResponse(type=parsed.type, content=parsed.content, research=research)

    def handle_research_request(self, research: ResearchRequest) -> str:
        # Delegate queries to sub-agent and aggregate responses
        agent = self.sub_agents.get(research.agent_type)
        if not agent:
            raise ValueError(f"No sub-agent found for {research.agent_type}")

        results = []
        for query in research.queries:
            result = agent.research(query)
            results.append(f"Query: {query}\nResponse: {result}")

        # Aggregate results
        aggregated = "\n\n---\n\n".join(results)
        logger.info(
            f"Aggregated {len(research.queries)} research results for {research.agent_type}"
        )
        return aggregated

    def process_email_with_feedback_note(self, email_context: str) -> AgentResponse:
        # Process email through feedback note agent for pacenote workflow
        try:
            parsed = self.feedback_note_agent.process_email(email_context)

            if parsed.type == "no_response":
                return AgentResponse.no_response_result()
            elif parsed.type == "reply":
                # Append signature to feedback note replies
                if not parsed.content:
                    logger.error("Reply type received but content is None")
                    return AgentResponse.error_result(self.GENERIC_ERROR_MSG)
                reply_with_signature = self._add_signature(parsed.content)
                return AgentResponse.success(reply_with_signature)
            else:
                return AgentResponse.error_result(self.GENERIC_ERROR_MSG)

        except (XMLParseError, Exception) as e:
            return self._handle_agent_errors("feedback note coordination", e)
