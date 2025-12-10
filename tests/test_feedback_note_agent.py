"""
tests/test_feedback_note_agent.py

Unit tests for FeedbackNoteAgent circuit breaker functionality.
Tests that the agent properly limits LLM calls to prevent runaway loops.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock boto3 before any imports to prevent S3 client initialization
mock_boto3 = Mock()
mock_s3_client = Mock()
mock_boto3.client.return_value = mock_s3_client
sys.modules["boto3"] = mock_boto3

# Mock the config module before importing FeedbackNoteAgent
mock_config = Mock()
mock_config.llm.pacenote_model = "test-model"
sys.modules["src.config"] = Mock(config=mock_config)

from src.agents.feedback_note_agent import FeedbackNoteAgent, FeedbackNoteResponse


@pytest.fixture
def mock_prompt_manager():
    """Mock PromptManager for testing."""
    manager = Mock()
    manager.get_prompt.return_value = "Test prompt with {{competency_list}} and {{examples}}"
    return manager


@pytest.fixture
def feedback_agent(mock_prompt_manager):
    """Create FeedbackNoteAgent with mocked dependencies."""
    with patch("src.utils.document_retriever.document_retriever"):
        return FeedbackNoteAgent(mock_prompt_manager)


@patch("src.agents.llm_utils.llm_client")
def test_circuit_breaker_triggers_on_fourth_call(mock_llm_client, feedback_agent):
    """Test that circuit breaker triggers when LLM call limit is exceeded."""
    # Mock LLM responses that keep requesting ranks
    mock_llm_client.generate_response.side_effect = [
        "<rank>cpl</rank>",  # First call - requests rank
        "<rank>mcpl</rank>",  # Second call - requests another rank
        "<rank>sgt</rank>",  # Third call - requests yet another rank
        "<reply><body>Final response</body></reply>",  # Fourth call - should not be reached
    ]

    # Mock document retrieval
    with patch.object(feedback_agent, "_load_competencies", return_value="Mock competencies"):
        with patch.object(feedback_agent, "_load_examples", return_value="Mock examples"):
            # Circuit breaker should trigger and raise RuntimeError
            with pytest.raises(RuntimeError, match="Circuit breaker"):
                feedback_agent.process_email("Test email context")

    # Verify that exactly 3 LLM calls were made (circuit breaker prevented 4th)
    assert mock_llm_client.generate_response.call_count == 3


@patch("src.agents.llm_utils.llm_client")
def test_circuit_breaker_allows_three_calls(mock_llm_client, feedback_agent):
    """Test that circuit breaker allows up to 3 LLM calls."""
    # Mock LLM responses: 2 rank requests + 1 reply
    mock_llm_client.generate_response.side_effect = [
        "<rank>cpl</rank>",  # First call - requests rank
        "<rank>mcpl</rank>",  # Second call - requests another rank
        "<reply><body>Final response</body></reply>",  # Third call - returns reply
    ]

    # Mock document retrieval
    with patch.object(feedback_agent, "_load_competencies", return_value="Mock competencies"):
        with patch.object(feedback_agent, "_load_examples", return_value="Mock examples"):
            # Should succeed with 3 calls
            result = feedback_agent.process_email("Test email context")

    # Verify result is a FeedbackNoteResponse with type 'reply'
    assert isinstance(result, FeedbackNoteResponse)
    assert result.type == "reply"
    assert result.content == "Final response"
    # Verify that exactly 3 LLM calls were made
    assert mock_llm_client.generate_response.call_count == 3


@patch("src.agents.llm_utils.llm_client")
def test_circuit_breaker_allows_single_call(mock_llm_client, feedback_agent):
    """Test that circuit breaker allows single LLM call with immediate reply."""
    # Mock LLM response with immediate reply
    mock_llm_client.generate_response.return_value = "<reply><body>Quick response</body></reply>"

    # Should succeed with just 1 call
    result = feedback_agent.process_email("Test email context")

    # Verify result is a FeedbackNoteResponse with type 'reply'
    assert isinstance(result, FeedbackNoteResponse)
    assert result.type == "reply"
    assert result.content == "Quick response"
    # Verify that only 1 LLM call was made
    assert mock_llm_client.generate_response.call_count == 1


@patch("src.agents.llm_utils.llm_client")
def test_circuit_breaker_allows_two_calls(mock_llm_client, feedback_agent):
    """Test that circuit breaker allows 2 LLM calls."""
    # Mock LLM responses: 1 rank request + 1 reply
    mock_llm_client.generate_response.side_effect = [
        "<rank>sgt</rank>",  # First call - requests rank
        "<reply><body>Response with competencies</body></reply>",  # Second call - returns reply
    ]

    # Mock document retrieval
    with patch.object(feedback_agent, "_load_competencies", return_value="Mock competencies"):
        with patch.object(feedback_agent, "_load_examples", return_value="Mock examples"):
            # Should succeed with 2 calls
            result = feedback_agent.process_email("Test email context")

    # Verify result is a FeedbackNoteResponse with type 'reply'
    assert isinstance(result, FeedbackNoteResponse)
    assert result.type == "reply"
    assert result.content == "Response with competencies"
    # Verify that exactly 2 LLM calls were made
    assert mock_llm_client.generate_response.call_count == 2


@patch("src.agents.llm_utils.llm_client")
def test_circuit_breaker_handles_no_response(mock_llm_client, feedback_agent):
    """Test that circuit breaker handles no_response type."""
    # Mock LLM response with no_response
    mock_llm_client.generate_response.return_value = "<no_response/>"

    # Should succeed with just 1 call
    result = feedback_agent.process_email("Test email context")

    # Verify result is a FeedbackNoteResponse with type 'no_response'
    assert isinstance(result, FeedbackNoteResponse)
    assert result.type == "no_response"
    # Verify that only 1 LLM call was made
    assert mock_llm_client.generate_response.call_count == 1
