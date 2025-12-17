"""
tests/test_agent_coordinator.py

Integration tests for AgentCoordinator orchestration logic.
Tests all response type paths, circuit breaker integration, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.agents.agent_coordinator import AgentCoordinator
from src.agents.constants import ResponseType
from src.agents.types import (
    AgentResponse,
    PrimeFooResponse,
    ResearchRequest,
    FeedbackNoteRequest,
    XMLParseError,
)


@pytest.fixture
def mock_prompt_manager():
    # Mock PromptManager for testing
    manager = Mock()
    manager.get_prompt.return_value = "Test prompt for {{context}}"
    return manager


@pytest.fixture
def coordinator(mock_prompt_manager):
    # Create AgentCoordinator with mocked dependencies
    return AgentCoordinator(mock_prompt_manager)


class TestSimpleReplyPath:
    # Tests for ResponseType.REPLY - verify signature appended and success returned

    @patch("src.agents.agent_coordinator.call_llm_with_retry")
    @patch("src.agents.agent_coordinator.increment_circuit_breaker")
    def test_reply_returns_with_signature(
        self, mock_increment, mock_call_llm, coordinator
    ):
        # Test that simple reply path returns content with signature appended
        mock_call_llm.return_value = (
            "<reply>Leave approved</reply>",
            PrimeFooResponse(type=ResponseType.REPLY, content="Leave approved"),
        )

        result = coordinator.process_email_with_prime_foo("Test email context")

        assert result.reply is not None
        assert "Leave approved" in result.reply
        assert "CAF-GPT" in result.reply
        assert "Source Code" in result.reply
        assert result.no_response is False
        assert result.error is None
        # Verify circuit breaker incremented once
        assert mock_increment.call_count == 1

    @patch("src.agents.agent_coordinator.call_llm_with_retry")
    @patch("src.agents.agent_coordinator.increment_circuit_breaker")
    def test_reply_with_none_content_returns_error(
        self, mock_increment, mock_call_llm, coordinator
    ):
        # Test that reply with None content triggers error path (line 94-96)
        mock_call_llm.return_value = (
            "<reply></reply>",
            PrimeFooResponse(type=ResponseType.REPLY, content=None),
        )

        result = coordinator.process_email_with_prime_foo("Test email context")

        assert result.error is not None
        assert "unexpected error" in result.error.lower()
        assert result.reply is None


class TestNoResponsePath:
    # Tests for ResponseType.NO_RESPONSE - verify no email sent

    @patch("src.agents.agent_coordinator.call_llm_with_retry")
    @patch("src.agents.agent_coordinator.increment_circuit_breaker")
    def test_no_response_returns_correctly(
        self, mock_increment, mock_call_llm, coordinator
    ):
        # Test that no_response path returns no_response=True
        mock_call_llm.return_value = (
            "<no_response />",
            PrimeFooResponse(type=ResponseType.NO_RESPONSE),
        )

        result = coordinator.process_email_with_prime_foo("Test email context")

        assert result.no_response is True
        assert result.reply is None
        assert result.error is None


class TestResearchDelegation:
    # Tests for ResponseType.RESEARCH - verify loop and sub-agent delegation

    @patch("src.agents.agent_coordinator.call_llm_with_retry")
    @patch("src.agents.agent_coordinator.increment_circuit_breaker")
    def test_research_delegation_then_reply(
        self, mock_increment, mock_call_llm, coordinator
    ):
        # Test research delegation followed by reply
        # First call returns research request
        research_req = ResearchRequest(
            queries=["What is the leave policy?"], agent_type="leave_foo"
        )
        # Second call returns reply after research
        mock_call_llm.side_effect = [
            (
                "<research><sub_agent name='leave_foo'><query>What is the leave policy?</query></sub_agent></research>",
                PrimeFooResponse(type=ResponseType.RESEARCH, research=research_req),
            ),
            (
                "<reply>Based on research: Leave approved</reply>",
                PrimeFooResponse(
                    type=ResponseType.REPLY, content="Based on research: Leave approved"
                ),
            ),
        ]

        # Mock the sub-agent
        mock_sub_agent = Mock()
        mock_sub_agent.research.return_value = "Leave policy: 30 days annual"
        coordinator.sub_agents["leave_foo"] = mock_sub_agent

        result = coordinator.process_email_with_prime_foo("Can I take leave?")

        # Verify sub-agent was called
        mock_sub_agent.research.assert_called_once_with("What is the leave policy?")
        # Verify final reply includes signature
        assert result.reply is not None
        assert "Based on research: Leave approved" in result.reply
        assert "CAF-GPT" in result.reply
        # Verify circuit breaker incremented twice (research + reply)
        assert mock_increment.call_count == 2

    @patch("src.agents.agent_coordinator.call_llm_with_retry")
    @patch("src.agents.agent_coordinator.increment_circuit_breaker")
    def test_research_multiple_queries_aggregated(
        self, mock_increment, mock_call_llm, coordinator
    ):
        # Test that multiple research queries are aggregated (line 193)
        research_req = ResearchRequest(
            queries=["Query 1", "Query 2", "Query 3"], agent_type="leave_foo"
        )
        mock_call_llm.side_effect = [
            (
                "<research>...</research>",
                PrimeFooResponse(type=ResponseType.RESEARCH, research=research_req),
            ),
            (
                "<reply>Final answer</reply>",
                PrimeFooResponse(type=ResponseType.REPLY, content="Final answer"),
            ),
        ]

        # Mock sub-agent to return different responses
        mock_sub_agent = Mock()
        mock_sub_agent.research.side_effect = ["Answer 1", "Answer 2", "Answer 3"]
        coordinator.sub_agents["leave_foo"] = mock_sub_agent

        result = coordinator.process_email_with_prime_foo("Test context")

        # Verify all queries were processed
        assert mock_sub_agent.research.call_count == 3
        assert result.reply is not None

    @patch("src.agents.agent_coordinator.call_llm_with_retry")
    @patch("src.agents.agent_coordinator.increment_circuit_breaker")
    def test_research_with_none_research_returns_error(
        self, mock_increment, mock_call_llm, coordinator
    ):
        # Test research type with None research triggers error (line 100-102)
        mock_call_llm.return_value = (
            "<research></research>",
            PrimeFooResponse(type=ResponseType.RESEARCH, research=None),
        )

        result = coordinator.process_email_with_prime_foo("Test context")

        assert result.error is not None
        assert result.reply is None

    @patch("src.agents.agent_coordinator.call_llm_with_retry")
    @patch("src.agents.agent_coordinator.increment_circuit_breaker")
    def test_research_unknown_sub_agent_returns_error(
        self, mock_increment, mock_call_llm, coordinator
    ):
        # Test unknown sub-agent raises ValueError (line 184-185)
        research_req = ResearchRequest(
            queries=["Test query"], agent_type="unknown_agent"
        )
        mock_call_llm.return_value = (
            "<research>...</research>",
            PrimeFooResponse(type=ResponseType.RESEARCH, research=research_req),
        )

        result = coordinator.process_email_with_prime_foo("Test context")

        # Should return error due to ValueError
        assert result.error is not None


class TestFeedbackNoteDelegation:
    # Tests for ResponseType.FEEDBACK_NOTE - verify pacenote flow

    @patch("src.agents.agent_coordinator.call_llm_with_retry")
    @patch("src.agents.agent_coordinator.increment_circuit_breaker")
    def test_feedback_note_delegation_then_reply(
        self, mock_increment, mock_call_llm, coordinator
    ):
        # Test feedback note delegation followed by reply wrapper
        feedback_req = FeedbackNoteRequest(
            rank="mcpl", context="MCpl Smith organized a successful event"
        )
        mock_call_llm.side_effect = [
            (
                "<feedback_note rank='mcpl'>MCpl Smith organized a successful event</feedback_note>",
                PrimeFooResponse(
                    type=ResponseType.FEEDBACK_NOTE, feedback_note=feedback_req
                ),
            ),
            (
                "<reply>Here is your feedback note...</reply>",
                PrimeFooResponse(
                    type=ResponseType.REPLY, content="Here is your feedback note..."
                ),
            ),
        ]

        # Mock pacenote sub-agent
        mock_pacenote = Mock()
        mock_pacenote.generate_note.return_value = (
            "FEEDBACK NOTE: MCpl Smith demonstrated strong leadership"
        )
        coordinator.sub_agents["pacenote"] = mock_pacenote

        result = coordinator.process_email_with_prime_foo(
            "Please write a feedback note for MCpl Smith"
        )

        # Verify pacenote agent was called
        mock_pacenote.generate_note.assert_called_once_with(
            "mcpl", "MCpl Smith organized a successful event"
        )
        # Verify final reply
        assert result.reply is not None
        assert "Here is your feedback note..." in result.reply
        # Verify circuit breaker incremented twice
        assert mock_increment.call_count == 2

    @patch("src.agents.agent_coordinator.call_llm_with_retry")
    @patch("src.agents.agent_coordinator.increment_circuit_breaker")
    def test_feedback_note_with_none_request_returns_error(
        self, mock_increment, mock_call_llm, coordinator
    ):
        # Test feedback_note type with None request triggers error (line 119-121)
        mock_call_llm.return_value = (
            "<feedback_note></feedback_note>",
            PrimeFooResponse(type=ResponseType.FEEDBACK_NOTE, feedback_note=None),
        )

        result = coordinator.process_email_with_prime_foo("Test context")

        assert result.error is not None
        assert result.reply is None


class TestCircuitBreakerIntegration:
    # Tests that circuit breaker triggers at max_calls limit

    @patch("src.agents.agent_coordinator.call_llm_with_retry")
    @patch("src.agents.agent_coordinator.increment_circuit_breaker")
    def test_circuit_breaker_allows_max_six_calls(
        self, mock_increment, mock_call_llm, coordinator
    ):
        # Test that circuit breaker allows up to 6 LLM calls (line 74: @circuit_breaker(max_calls=6))
        # Create a chain of 5 research calls, then final reply (total 6 calls)
        research_req = ResearchRequest(queries=["Test"], agent_type="leave_foo")

        def create_research_response():
            return (
                "<research>...</research>",
                PrimeFooResponse(type=ResponseType.RESEARCH, research=research_req),
            )

        def create_reply_response():
            return (
                "<reply>Final</reply>",
                PrimeFooResponse(type=ResponseType.REPLY, content="Final"),
            )

        # 5 research calls + 1 reply = 6 total
        mock_call_llm.side_effect = [
            create_research_response(),
            create_research_response(),
            create_research_response(),
            create_research_response(),
            create_research_response(),
            create_reply_response(),
        ]

        # Mock sub-agent
        mock_sub_agent = Mock()
        mock_sub_agent.research.return_value = "Research result"
        coordinator.sub_agents["leave_foo"] = mock_sub_agent

        result = coordinator.process_email_with_prime_foo("Complex query")

        # Should complete successfully with 6 calls
        assert result.reply is not None
        assert mock_increment.call_count == 6

    @patch("src.agents.agent_coordinator.call_llm_with_retry")
    @patch("src.agents.agent_coordinator.increment_circuit_breaker")
    def test_circuit_breaker_triggers_on_seventh_call(
        self, mock_increment, mock_call_llm, coordinator
    ):
        # Test that circuit breaker raises RuntimeError on 7th call
        research_req = ResearchRequest(queries=["Test"], agent_type="leave_foo")

        # Create infinite research loop
        mock_call_llm.return_value = (
            "<research>...</research>",
            PrimeFooResponse(type=ResponseType.RESEARCH, research=research_req),
        )

        # Mock sub-agent
        mock_sub_agent = Mock()
        mock_sub_agent.research.return_value = "Research result"
        coordinator.sub_agents["leave_foo"] = mock_sub_agent

        # Mock increment to raise on 7th call
        call_count = [0]

        def increment_with_limit():
            call_count[0] += 1
            if call_count[0] > 6:
                raise RuntimeError(
                    "Circuit breaker: exceeded maximum 6 LLM calls per email"
                )

        mock_increment.side_effect = increment_with_limit

        result = coordinator.process_email_with_prime_foo("Complex query")

        # Should return error due to circuit breaker
        assert result.error is not None


class TestXMLParseErrorHandling:
    # Tests for XML parse error recovery via retry

    @patch("src.agents.agent_coordinator.call_llm_with_retry")
    @patch("src.agents.agent_coordinator.increment_circuit_breaker")
    def test_xml_parse_error_logged_and_returns_error(
        self, mock_increment, mock_call_llm, coordinator
    ):
        # Test that XMLParseError is caught and returns generic error (line 68-72)
        mock_call_llm.side_effect = XMLParseError(
            "Invalid XML", "Missing closing tag"
        )

        result = coordinator.process_email_with_prime_foo("Test context")

        assert result.error is not None
        assert "unexpected error" in result.error.lower()


class TestSubAgentLoading:
    # Tests that sub-agents are properly loaded in coordinator

    def test_coordinator_loads_sub_agents(self, coordinator):
        # Test that _load_sub_agents registers expected sub-agents (line 53-57)
        assert "leave_foo" in coordinator.sub_agents
        assert "doad_foo" in coordinator.sub_agents
        assert "pacenote" in coordinator.sub_agents

    def test_signature_appending(self, coordinator):
        # Test that _add_signature properly appends signature
        content = "Test reply"
        result = coordinator._add_signature(content)

        assert "Test reply" in result
        assert "CAF-GPT" in result
        assert "Source Code" in result
        assert "github.com/taoi11/caf_gpt" in result
