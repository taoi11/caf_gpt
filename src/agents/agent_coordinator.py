"""
/workspace/caf_gpt/src/agents/agent_coordinator.py

Orchestrator for prime_foo and sub-agent interactions, handling response parsing and research delegation.

Top-level declarations:
- AgentCoordinator: Main class coordinating LLM calls, parsing, and sub-agent delegation
"""

import logging
from typing import Dict, Any
import xml.etree.ElementTree as ET


from .prompt_manager import PromptManager
from .types import AgentResponse, PrimeFooResponse, ResearchRequest
from .sub_agents.leave_foo_agent import LeaveFooAgent
from src.llm_interface import llm_client

logger = logging.getLogger(__name__)


class AgentCoordinator:
    def __init__(self, prompt_manager: PromptManager):
        self.prompt_manager = prompt_manager
        self.sub_agents: Dict[str, Any] = {}
        self._load_sub_agents()

    def _load_sub_agents(self):
        # Dynamically load sub-agents like LeaveFooAgent with prompt manager access
        self.sub_agents["leave_foo"] = LeaveFooAgent(self.prompt_manager)

    def process_email_with_prime_foo(self, email_context: str) -> AgentResponse:
        # Main coordination loop: send to prime_foo, parse response, handle research/reply/no_response iteratively
        try:
            prime_prompt = self.prompt_manager.get_prompt("prime_foo")
            messages = [
                {"role": "system", "content": prime_prompt},
                {"role": "user", "content": email_context},
            ]
            response = llm_client.generate_response(
                messages, openrouter_model="x-ai/grok-4"
            )
            parsed = self.parse_prime_foo_response(response)

            while True:
                if parsed.type == "no_response":
                    return self.handle_no_response()
                elif parsed.type == "reply":
                    return AgentResponse(reply=parsed.content)
                elif parsed.type == "research":
                    research_result = self.handle_research_request(parsed.research)
                    # Send research results back to prime_foo
                    follow_up_messages = messages + [
                        {"role": "assistant", "content": response},
                        {"role": "user", "content": f"Research results: {research_result}"},
                    ]
                    response = llm_client.generate_response(
                        follow_up_messages, openrouter_model="x-ai/grok-4"
                    )
                    parsed = self.parse_prime_foo_response(response)
                else:
                    return self.get_generic_error_response()
        except Exception as e:
            logger.error(f"Error in coordination: {e}")
            return self.get_generic_error_response()

    def parse_prime_foo_response(self, response: str) -> PrimeFooResponse:
        # Parse XML or fallback string for prime_foo responses, extracting type, content, and research details
        from typing import List  # For queries list

        try:
            root = ET.fromstring(response)
            type_ = root.tag
            content = root.text.strip() if root.text else ""
            research = None
            if type_ == "research":
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
        except ET.ParseError:
            # Fallback parsing for non-XML responses
            if "<no_response>" in response:
                return PrimeFooResponse(type="no_response")
            elif "<reply>" in response:
                start = response.find("<reply>") + 7  # len("<reply>")
                end = response.find("</reply>", start)
                if end > start:
                    body_start = response.find("<body>", start) + 6
                    body_end = response.find("</body>", body_start)
                    if body_end > body_start:
                        content = response[body_start:body_end].strip()
                    else:
                        content = response[start:end].strip()
                return PrimeFooResponse(type="reply", content=content)
            else:
                # Default to research if unclear, extract simple queries
                queries = []
                start = 0
                while True:
                    q_start = response.find("<query>", start)
                    if q_start == -1:
                        break
                    q_end = response.find("</query>", q_start + 7)
                    if q_end > q_start:
                        query_text = response[q_start + 7 : q_end].strip()
                        if query_text:
                            queries.append(query_text)
                    start = q_end + 8
                agent_type = "leave_foo"  # Default assumption
                if queries:
                    research = ResearchRequest(queries=queries, agent_type=agent_type)
                return PrimeFooResponse(
                    type="research", research=research if "research" in locals() else None
                )

    def handle_research_request(self, research: ResearchRequest) -> str:
        # Delegate multiple queries to sub-agent and aggregate responses for follow-up
        agent = self.sub_agents.get(research.agent_type)
        if not agent:
            logger.warning(f"No sub-agent found for {research.agent_type}")
            return "No specialized agent available for this query."

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
