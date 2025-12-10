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
from .feedback_note_agent import FeedbackNoteAgent
from src.llm_interface import llm_client
from src.config import config

logger = logging.getLogger(__name__)


class AgentCoordinator:
    # Main class coordinating LLM calls, parsing, and sub-agent delegation

    # Signature appended to all agent replies
    SIGNATURE = """

CAF-GPT
[Source Code](https://github.com/taoi11/caf_gpt)
How to use CAF-GPT: [Documentation](placeholder_for_docs_link)"""

    def __init__(self, prompt_manager: PromptManager):
        # Initialize with prompt manager and load available sub-agents
        self.prompt_manager = prompt_manager
        self.sub_agents: Dict[str, Any] = {}
        self._load_sub_agents()
        # Initialize feedback note agent
        self.feedback_note_agent = FeedbackNoteAgent(self.prompt_manager)

    def _load_sub_agents(self):
        # Dynamically load sub-agents like LeaveFooAgent with prompt manager access
        self.sub_agents["leave_foo"] = LeaveFooAgent(self.prompt_manager)

    def _call_llm_with_retry(self, messages: list, model: str) -> tuple[str, "PrimeFooResponse"]:
        # Call LLM and parse response, with 1 retry on XML parse failure
        response = llm_client.generate_response(messages, openrouter_model=model)
        try:
            parsed = self.parse_prime_foo_response(response)
            return response, parsed
        except XMLParseError as e:
            logger.warning(f"XML parse failed, retrying: {e.parse_error}")
            # Send error feedback and retry once
            retry_messages = messages + [
                {"role": "assistant", "content": response},
                {
                    "role": "user",
                    "content": f"Your response was not valid XML. Parse error: {e.parse_error}. Please respond with properly formatted XML.",
                },
            ]
            response = llm_client.generate_response(retry_messages, openrouter_model=model)
            # No more retries - let it raise if it fails again
            parsed = self.parse_prime_foo_response(response)
            return response, parsed

    def process_email_with_prime_foo(self, email_context: str) -> AgentResponse:
        # Main coordination loop: send to prime_foo, parse response, handle research/reply/no_response iteratively
        try:
            prime_prompt = self.prompt_manager.get_prompt("prime_foo")
            messages = [
                {"role": "system", "content": prime_prompt},
                {"role": "user", "content": email_context},
            ]
            response, parsed = self._call_llm_with_retry(messages, config.llm.prime_foo_model)

            while True:
                if parsed.type == "no_response":
                    return self.handle_no_response()
                elif parsed.type == "reply":
                    # Append signature to policy agent replies
                    if not parsed.content:
                        logger.error("Reply type received but content is None")
                        return self.get_generic_error_response()
                    reply_with_signature = parsed.content + self.SIGNATURE
                    return AgentResponse(reply=reply_with_signature)
                elif parsed.type == "research":
                    if not parsed.research:
                        logger.error("Research type received but research is None")
                        return self.get_generic_error_response()
                    research_result = self.handle_research_request(parsed.research)
                    # Send research results back to prime_foo
                    follow_up_messages = messages + [
                        {"role": "assistant", "content": response},
                        {"role": "user", "content": f"Research results: {research_result}"},
                    ]
                    response, parsed = self._call_llm_with_retry(
                        follow_up_messages, config.llm.prime_foo_model
                    )
                else:
                    return self.get_generic_error_response()
        except XMLParseError as e:
            logger.error(f"XML parse failed after retry: {e.parse_error}")
            return self.get_generic_error_response()
        except Exception as e:
            logger.error(f"Error in coordination: {e}")
            return self.get_generic_error_response()

    def _parse_xml_response(self, response: str, parse_research: bool = False) -> PrimeFooResponse:
        # Shared XML parser for both prime_foo and feedback_note responses
        # Raises XMLParseError if response is not valid XML
        try:
            root = ET.fromstring(response)
            type_ = root.tag
            content = root.text.strip() if root.text else ""
            research = None
            if type_ == "research" and parse_research:
                sub_agent_elem = root.find("sub_agent")
                if sub_agent_elem is not None:
                    agent_type = sub_agent_elem.get("name", "")
                    queries = []
                    for query_elem in sub_agent_elem.findall("query"):
                        if query_elem.text:
                            queries.append(query_elem.text.strip())
                    if queries:
                        research = ResearchRequest(queries=queries, agent_type=agent_type)
            elif type_ == "reply":
                body_elem = root.find("body")
                if body_elem is not None and body_elem.text:
                    content = body_elem.text.strip()
            return PrimeFooResponse(type=type_, content=content, research=research)
        except ET.ParseError as e:
            raise XMLParseError(response, str(e))

    def parse_prime_foo_response(self, response: str) -> PrimeFooResponse:
        # Parse XML for prime_foo responses, raises XMLParseError on failure
        return self._parse_xml_response(response, parse_research=True)

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

    def handle_no_response(self) -> AgentResponse:
        # Return structured no_response from AgentResponse model
        return AgentResponse(no_response=True)

    def get_generic_error_response(self) -> AgentResponse:
        # Return generic error from AgentResponse model for unexpected cases
        return AgentResponse(error="An unexpected error occurred while processing your email.")

    def process_email_with_feedback_note(self, email_context: str) -> AgentResponse:
        # Process email through feedback note agent for pacenote workflow
        try:
            response = self.feedback_note_agent.process_email(email_context)
            parsed = self._parse_xml_response(response, parse_research=False)

            if parsed.type == "no_response":
                return self.handle_no_response()
            elif parsed.type == "reply":
                # Append signature to feedback note replies
                if not parsed.content:
                    logger.error("Reply type received but content is None")
                    return self.get_generic_error_response()
                reply_with_signature = parsed.content + self.SIGNATURE
                return AgentResponse(reply=reply_with_signature)
            else:
                return self.get_generic_error_response()

        except XMLParseError as e:
            logger.error(f"XML parse failed in feedback note: {e.parse_error}")
            return self.get_generic_error_response()
        except Exception as e:
            logger.error(f"Error in feedback note coordination: {e}")
            return self.get_generic_error_response()
