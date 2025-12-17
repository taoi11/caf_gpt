"""
tests/test_doad_foo_agent.py

Unit tests for DoadFooAgent sub-agent functionality.
Tests the two-call pattern: selector → load documents → answer.
"""

import pytest
from unittest.mock import Mock, patch

from src.agents.sub_agents.doad_foo_agent import DoadFooAgent, MAX_DOAD_FILES


@pytest.fixture
def mock_prompt_manager():
    # Mock PromptManager for testing
    manager = Mock()

    def get_prompt_side_effect(name):
        if name == "DOAD_Table":
            return "| DOAD Number | Title |\n|---|---|\n| 5019-0 | Conduct |\n| 5019-1 | Relationships |"
        elif name == "doad_foo_selector":
            return "Select DOAD numbers. {{doad_table}}"
        elif name == "doad_foo_answer":
            return "Answer using {{doad_content}}"
        return ""

    manager.get_prompt.side_effect = get_prompt_side_effect
    return manager


@pytest.fixture
def doad_agent(mock_prompt_manager):
    # Create DoadFooAgent with mocked dependencies
    with patch("src.utils.document_retriever.document_retriever"):
        return DoadFooAgent(mock_prompt_manager)


class TestParseDoadNumbers:
    # Tests for XML parsing of <doad_numbers> tag

    def test_parse_single_number(self, doad_agent):
        # Test parsing single DOAD number
        response = "<doad_numbers>5019-0</doad_numbers>"
        result = doad_agent._parse_doad_numbers(response)
        assert result == ["5019-0"]

    def test_parse_multiple_numbers(self, doad_agent):
        # Test parsing comma-separated DOAD numbers
        response = "<doad_numbers>5019-0, 5019-1, 5002-3</doad_numbers>"
        result = doad_agent._parse_doad_numbers(response)
        assert result == ["5019-0", "5019-1", "5002-3"]

    def test_parse_trims_whitespace(self, doad_agent):
        # Test that whitespace is stripped from numbers
        response = "<doad_numbers>  5019-0 ,  5019-1  </doad_numbers>"
        result = doad_agent._parse_doad_numbers(response)
        assert result == ["5019-0", "5019-1"]

    def test_parse_limits_to_max_files(self, doad_agent):
        # Test that parsing limits to MAX_DOAD_FILES (3)
        response = "<doad_numbers>5019-0, 5019-1, 5019-2, 5019-3, 5019-4</doad_numbers>"
        result = doad_agent._parse_doad_numbers(response)
        assert len(result) == MAX_DOAD_FILES
        assert result == ["5019-0", "5019-1", "5019-2"]

    def test_parse_no_tag_returns_empty(self, doad_agent):
        # Test that missing tag returns empty list
        response = "I think you should look at DOAD 5019-0"
        result = doad_agent._parse_doad_numbers(response)
        assert result == []

    def test_parse_empty_tag_returns_empty(self, doad_agent):
        # Test that empty tag content returns empty list
        response = "<doad_numbers></doad_numbers>"
        result = doad_agent._parse_doad_numbers(response)
        assert result == []

    def test_parse_multiline_tag(self, doad_agent):
        # Test parsing with newlines inside tag
        response = "<doad_numbers>\n5019-0,\n5019-1\n</doad_numbers>"
        result = doad_agent._parse_doad_numbers(response)
        assert result == ["5019-0", "5019-1"]


class TestResearch:
    # Tests for the main research() method

    @patch("src.agents.sub_agents.base_agent.llm_client")
    def test_research_happy_path(self, mock_llm_client, doad_agent):
        # Test successful flow: select 2 files, load both, get answer
        mock_llm_client.generate_response.side_effect = [
            "<doad_numbers>5019-0, 5019-1</doad_numbers>",  # Selector call
            "According to DOAD 5019-0, conduct standards require...",  # Answer call
        ]

        with patch.object(doad_agent, "_load_document") as mock_load:
            mock_load.side_effect = ["Content of DOAD 5019-0", "Content of DOAD 5019-1"]
            result = doad_agent.research("What are the conduct standards?")

        assert "According to DOAD 5019-0" in result
        assert mock_llm_client.generate_response.call_count == 2
        assert mock_load.call_count == 2

    @patch("src.agents.sub_agents.base_agent.llm_client")
    def test_research_partial_load(self, mock_llm_client, doad_agent):
        # Test that research continues when some files fail to load
        mock_llm_client.generate_response.side_effect = [
            "<doad_numbers>5019-0, 9999-9, 5019-1</doad_numbers>",  # One fake number
            "Based on available documents...",
        ]

        with patch.object(doad_agent, "_load_document") as mock_load:
            # First file loads, second fails (empty string), third loads
            mock_load.side_effect = ["Content of 5019-0", "", "Content of 5019-1"]
            result = doad_agent.research("Question about policies")

        assert "Based on available documents" in result
        assert mock_llm_client.generate_response.call_count == 2

    @patch("src.agents.sub_agents.base_agent.llm_client")
    def test_research_all_files_fail(self, mock_llm_client, doad_agent):
        # Test error message when all selected files fail to load
        mock_llm_client.generate_response.return_value = (
            "<doad_numbers>9999-9, 8888-8</doad_numbers>"
        )

        with patch.object(doad_agent, "_load_document") as mock_load:
            mock_load.return_value = ""  # All loads fail
            result = doad_agent.research("Question about non-existent policy")

        assert "No relevant DOAD files found" in result
        # Answer LLM should NOT be called if no files loaded
        assert mock_llm_client.generate_response.call_count == 1

    @patch("src.agents.sub_agents.base_agent.llm_client")
    def test_research_selector_no_tag(self, mock_llm_client, doad_agent):
        # Test error when selector doesn't return proper XML tag
        mock_llm_client.generate_response.return_value = (
            "I recommend looking at DOAD 5019-0"  # No XML tag
        )

        result = doad_agent.research("What policy covers this?")

        assert "couldn't identify relevant DOAD documents" in result
        assert mock_llm_client.generate_response.call_count == 1

    @patch("src.agents.sub_agents.base_agent.llm_client")
    def test_research_handles_llm_exception(self, mock_llm_client, doad_agent):
        # Test graceful handling of LLM errors
        mock_llm_client.generate_response.side_effect = Exception("API timeout")

        result = doad_agent.research("Any question")

        assert "couldn't retrieve the DOAD policy information" in result


class TestSelectFiles:
    # Tests for the _select_files() method

    @patch("src.agents.sub_agents.base_agent.llm_client")
    def test_select_files_builds_correct_prompt(self, mock_llm_client, doad_agent):
        # Test that selector prompt includes DOAD table and query
        mock_llm_client.generate_response.return_value = "<doad_numbers>5019-0</doad_numbers>"

        doad_agent._select_files("What is the fraternization policy?")

        call_args = mock_llm_client.generate_response.call_args
        messages = call_args[0][0]

        # System message should contain DOAD table
        system_content = messages[0]["content"]
        assert "5019-0" in system_content or "Conduct" in system_content

        # User message should contain the query
        user_content = messages[1]["content"]
        assert "fraternization" in user_content


class TestLoadDoadFiles:
    # Tests for the _load_doad_files() method

    def test_load_files_concatenates_with_headers(self, doad_agent):
        # Test that loaded files are properly formatted with XML tags
        with patch.object(doad_agent, "_load_document") as mock_load:
            mock_load.side_effect = ["Policy content A", "Policy content B"]
            result = doad_agent._load_doad_files(["5019-0", "5019-1"])

        assert "<DOAD_5019-0>" in result
        assert "</DOAD_5019-0>" in result
        assert "<DOAD_5019-1>" in result
        assert "</DOAD_5019-1>" in result
        assert "Policy content A" in result
        assert "Policy content B" in result

    def test_load_files_skips_empty_loads(self, doad_agent):
        # Test that empty loads (failures) are excluded
        with patch.object(doad_agent, "_load_document") as mock_load:
            mock_load.side_effect = ["Policy A", "", "Policy C"]
            result = doad_agent._load_doad_files(["5019-0", "9999-9", "5019-2"])

        assert "<DOAD_5019-0>" in result
        assert "<DOAD_5019-2>" in result
        assert "9999-9" not in result

    def test_load_files_returns_empty_when_all_fail(self, doad_agent):
        # Test empty string returned when all files fail to load
        with patch.object(doad_agent, "_load_document") as mock_load:
            mock_load.return_value = ""
            result = doad_agent._load_doad_files(["9999-9", "8888-8"])

        assert result == ""


class TestAnswerQuery:
    # Tests for the _answer_query() method

    @patch("src.agents.sub_agents.base_agent.llm_client")
    def test_answer_query_includes_documents_and_query(self, mock_llm_client, doad_agent):
        # Test that answer prompt contains loaded documents and original query
        mock_llm_client.generate_response.return_value = "The answer is..."

        doad_agent._answer_query("What is the policy?", "## DOAD 5019-0\n\nContent here")

        call_args = mock_llm_client.generate_response.call_args
        messages = call_args[0][0]

        # System should have document content
        system_content = messages[0]["content"]
        assert "DOAD 5019-0" in system_content or "Content here" in system_content

        # User should have query
        user_content = messages[1]["content"]
        assert "policy" in user_content
