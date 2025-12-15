"""
tests/test_pacenote_agent.py

Unit tests for PacenoteAgent sub-agent functionality.
Tests that the agent properly generates feedback notes based on rank and context.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.agents.sub_agents.pacenote_agent import PacenoteAgent, RANK_FILES


@pytest.fixture
def mock_prompt_manager():
    # Mock PromptManager for testing
    manager = Mock()
    manager.get_prompt.return_value = "Test prompt with {{competencies}} and {{examples}} for {{rank}}"
    return manager


@pytest.fixture
def pacenote_agent(mock_prompt_manager):
    # Create PacenoteAgent with mocked dependencies
    with patch("src.utils.document_retriever.document_retriever"):
        return PacenoteAgent(mock_prompt_manager)


@patch("src.agents.sub_agents.pacenote_agent.llm_client")
def test_generate_note_success(mock_llm_client, pacenote_agent):
    # Test that generate_note returns LLM response for valid rank and context
    mock_llm_client.generate_response.return_value = "The member organized a successful event. This demonstrates strong leadership competencies."

    with patch.object(pacenote_agent, "_load_competencies", return_value="Mock competencies"):
        with patch.object(pacenote_agent, "_load_examples", return_value="Mock examples"):
            result = pacenote_agent.generate_note("mcpl", "MCpl Smith organized a BBQ event")

    assert result == "The member organized a successful event. This demonstrates strong leadership competencies."
    assert mock_llm_client.generate_response.call_count == 1


@patch("src.agents.sub_agents.pacenote_agent.llm_client")
def test_generate_note_with_different_ranks(mock_llm_client, pacenote_agent):
    # Test that generate_note works with different ranks
    mock_llm_client.generate_response.return_value = "Feedback note content"

    for rank in ["cpl", "mcpl", "sgt", "wo"]:
        mock_llm_client.reset_mock()
        with patch.object(pacenote_agent, "_load_competencies", return_value=f"Competencies for {rank}"):
            with patch.object(pacenote_agent, "_load_examples", return_value="Mock examples"):
                result = pacenote_agent.generate_note(rank, "Test context")

        assert result == "Feedback note content"


@patch("src.agents.sub_agents.pacenote_agent.llm_client")
def test_generate_note_unknown_rank_defaults_to_cpl(mock_llm_client, pacenote_agent):
    # Test that unknown rank defaults to cpl competencies
    mock_llm_client.generate_response.return_value = "Feedback note content"

    with patch.object(pacenote_agent, "_load_document") as mock_load_doc:
        mock_load_doc.return_value = "Mock content"
        result = pacenote_agent.generate_note("unknown_rank", "Test context")

    # Should have tried to load cpl.md as fallback
    calls = mock_load_doc.call_args_list
    assert any("cpl.md" in str(call) for call in calls)


@patch("src.agents.sub_agents.pacenote_agent.llm_client")
def test_generate_note_handles_llm_error(mock_llm_client, pacenote_agent):
    # Test that generate_note handles LLM errors gracefully
    mock_llm_client.generate_response.side_effect = Exception("LLM API error")

    with patch.object(pacenote_agent, "_load_competencies", return_value="Mock competencies"):
        with patch.object(pacenote_agent, "_load_examples", return_value="Mock examples"):
            result = pacenote_agent.generate_note("cpl", "Test context")

    assert "couldn't generate the feedback note" in result


def test_rank_files_mapping():
    # Test that RANK_FILES contains expected rank mappings
    assert RANK_FILES["cpl"] == "cpl.md"
    assert RANK_FILES["mcpl"] == "mcpl.md"
    assert RANK_FILES["sgt"] == "sgt.md"
    assert RANK_FILES["wo"] == "wo.md"


@patch("src.agents.sub_agents.pacenote_agent.llm_client")
def test_prompt_includes_rank_and_context(mock_llm_client, pacenote_agent):
    # Test that the prompt is built with rank, competencies, and examples
    mock_llm_client.generate_response.return_value = "Feedback note"

    with patch.object(pacenote_agent, "_load_competencies", return_value="Cpl competencies"):
        with patch.object(pacenote_agent, "_load_examples", return_value="Example notes"):
            pacenote_agent.generate_note("cpl", "Test context for Cpl Smith")

    # Check that LLM was called with messages containing the context
    call_args = mock_llm_client.generate_response.call_args
    messages = call_args[0][0]

    # User message should have the context
    user_content = messages[1]["content"]
    assert "Test context for Cpl Smith" in user_content
