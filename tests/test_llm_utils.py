"""
tests/test_llm_utils.py

Unit tests for LLM utilities including CircuitBreaker decorator pattern.
Tests the instance-based circuit breaker for limiting LLM calls per email.
"""

import pytest
from unittest.mock import Mock, patch

from src.agents.llm_utils import (
    CircuitBreaker,
    circuit_breaker,
    increment_circuit_breaker,
    call_llm_with_retry,
)
from src.agents.types import XMLParseError


class TestCircuitBreakerClass:
    # Tests for CircuitBreaker class instance behavior

    def test_circuit_breaker_allows_max_calls(self):
        # Test that circuit breaker allows exactly max_calls increments
        cb = CircuitBreaker(max_calls=3)

        # Should allow 3 increments
        cb.increment()  # 1
        cb.increment()  # 2
        cb.increment()  # 3

        # No exception raised yet
        assert cb.count == 3

    def test_circuit_breaker_blocks_excess_calls(self):
        # Test that circuit breaker raises on max_calls + 1
        cb = CircuitBreaker(max_calls=3)

        cb.increment()  # 1
        cb.increment()  # 2
        cb.increment()  # 3

        # 4th increment should raise
        with pytest.raises(RuntimeError, match="Circuit breaker"):
            cb.increment()

    def test_circuit_breaker_error_message(self):
        # Test that error message includes max_calls value
        cb = CircuitBreaker(max_calls=5)

        for _ in range(5):
            cb.increment()

        with pytest.raises(RuntimeError, match="exceeded maximum 5 LLM calls"):
            cb.increment()


class TestCircuitBreakerDecorator:
    # Tests for circuit_breaker decorator pattern

    def test_decorator_allows_max_calls(self):
        # Test that decorator creates fresh instance per call and enforces limit
        call_count = [0]

        @circuit_breaker(max_calls=3)
        def test_function():
            for _ in range(3):
                increment_circuit_breaker()
                call_count[0] += 1

        # Should complete successfully
        test_function()
        assert call_count[0] == 3

    def test_decorator_blocks_excess_calls(self):
        # Test that decorator raises when increment exceeds max_calls

        @circuit_breaker(max_calls=3)
        def test_function():
            for _ in range(4):  # Try 4 increments with max=3
                increment_circuit_breaker()

        # Should raise on 4th increment
        with pytest.raises(RuntimeError, match="Circuit breaker"):
            test_function()

    def test_decorator_resets_between_invocations(self):
        # Test that each decorated function call gets fresh CircuitBreaker instance
        call_count = [0]

        @circuit_breaker(max_calls=2)
        def test_function():
            increment_circuit_breaker()
            increment_circuit_breaker()
            call_count[0] += 1

        # First call should succeed
        test_function()
        assert call_count[0] == 1

        # Second call should also succeed (fresh instance)
        test_function()
        assert call_count[0] == 2

    def test_decorator_cleanup_on_exception(self):
        # Test that decorator cleans up _current_breaker even on exception

        @circuit_breaker(max_calls=5)
        def failing_function():
            increment_circuit_breaker()
            raise ValueError("Test error")

        # Function should raise ValueError
        with pytest.raises(ValueError, match="Test error"):
            failing_function()

        # Breaker should be cleaned up (None)
        # Verify by calling increment outside - should log warning but not crash
        increment_circuit_breaker()  # Should log warning but not raise

    def test_nested_decorators_use_same_breaker(self):
        # Test that nested calls within same decorated function share breaker

        @circuit_breaker(max_calls=3)
        def outer_function():
            increment_circuit_breaker()  # 1
            inner_helper()
            increment_circuit_breaker()  # 3

        def inner_helper():
            increment_circuit_breaker()  # 2

        # Should succeed with 3 total increments
        outer_function()


class TestIncrementCircuitBreaker:
    # Tests for increment_circuit_breaker function

    @patch("src.agents.llm_utils._current_breaker", None)
    def test_increment_outside_decorator_logs_warning(self, caplog):
        # Test that increment outside decorated method logs warning (line 132-135)
        import logging

        with caplog.at_level(logging.WARNING):
            increment_circuit_breaker()

        assert "increment_circuit_breaker called outside decorated method" in caplog.text

    def test_increment_within_decorator(self):
        # Test that increment within decorator updates count

        @circuit_breaker(max_calls=5)
        def test_function():
            increment_circuit_breaker()
            increment_circuit_breaker()
            increment_circuit_breaker()
            # Should have incremented 3 times
            from src.agents.llm_utils import _current_breaker

            assert _current_breaker.count == 3

        test_function()


class TestCallLLMWithRetry:
    # Tests for call_llm_with_retry shared retry logic

    @patch("src.agents.llm_utils.llm_client")
    def test_successful_parse_returns_result(self, mock_llm_client):
        # Test successful LLM call and parse
        mock_llm_client.generate_response.return_value = "<reply>Test</reply>"

        def parser(response):
            return {"parsed": True, "content": response}

        response, parsed = call_llm_with_retry(
            [{"role": "user", "content": "test"}], "test-model", parser
        )

        assert response == "<reply>Test</reply>"
        assert parsed["parsed"] is True
        assert mock_llm_client.generate_response.call_count == 1

    @patch("src.agents.llm_utils.llm_client")
    def test_xml_parse_error_triggers_retry(self, mock_llm_client):
        # Test that XMLParseError triggers one retry (line 155-172)
        mock_llm_client.generate_response.side_effect = [
            "Invalid XML",  # First call
            "<reply>Valid</reply>",  # Retry call
        ]

        parse_count = [0]

        def parser(response):
            parse_count[0] += 1
            if parse_count[0] == 1:
                raise XMLParseError(response, "Missing tag")
            return {"content": response}

        response, parsed = call_llm_with_retry(
            [{"role": "user", "content": "test"}], "test-model", parser
        )

        # Should have called LLM twice
        assert mock_llm_client.generate_response.call_count == 2
        assert parsed["content"] == "<reply>Valid</reply>"

    @patch("src.agents.llm_utils.llm_client")
    def test_xml_parse_error_retry_includes_feedback(self, mock_llm_client):
        # Test that retry includes parse error feedback (line 162)
        mock_llm_client.generate_response.side_effect = [
            "Invalid XML",
            "<reply>Valid</reply>",
        ]

        def parser(response):
            if response == "Invalid XML":
                raise XMLParseError(response, "Missing closing tag")
            return {"content": response}

        call_llm_with_retry(
            [{"role": "user", "content": "test"}], "test-model", parser
        )

        # Check retry messages include error feedback
        retry_call_args = mock_llm_client.generate_response.call_args_list[1]
        retry_messages = retry_call_args[0][0]

        # Should have original message + assistant response + error feedback
        assert len(retry_messages) == 3
        assert retry_messages[2]["role"] == "user"
        assert "not valid XML" in retry_messages[2]["content"]
        assert "Missing closing tag" in retry_messages[2]["content"]

    @patch("src.agents.llm_utils.llm_client")
    def test_xml_parse_error_on_retry_raises(self, mock_llm_client):
        # Test that XMLParseError on retry is not caught (line 170-172)
        mock_llm_client.generate_response.side_effect = [
            "Invalid XML 1",
            "Invalid XML 2",
        ]

        def parser(response):
            raise XMLParseError(response, "Always fails")

        # Second parse error should raise
        with pytest.raises(XMLParseError, match="Always fails"):
            call_llm_with_retry(
                [{"role": "user", "content": "test"}], "test-model", parser
            )

        # Should have called LLM twice (original + 1 retry)
        assert mock_llm_client.generate_response.call_count == 2

    @patch("src.agents.llm_utils.llm_client")
    def test_log_response_option(self, mock_llm_client, caplog):
        # Test log_response parameter logs LLM output
        import logging

        mock_llm_client.generate_response.return_value = "Test response"

        def parser(response):
            return {"content": response}

        with caplog.at_level(logging.INFO):
            call_llm_with_retry(
                [{"role": "user", "content": "test"}],
                "test-model",
                parser,
                log_response=True,
            )

        assert "LLM raw response: Test response" in caplog.text


class TestLLMInterface:
    # Tests for LLMInterface class

    @patch("src.agents.llm_utils.requests.post")
    def test_generate_response_success(self, mock_post):
        # Test successful OpenRouter API call
        from src.agents.llm_utils import LLMInterface

        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "LLM response"}}]
        }
        mock_post.return_value = mock_response

        llm = LLMInterface()
        result = llm.generate_response(
            [{"role": "user", "content": "test"}], temperature=0.7
        )

        assert result == "LLM response"
        mock_post.assert_called_once()

    @patch("src.agents.llm_utils.requests.post")
    def test_generate_response_unexpected_format(self, mock_post):
        # Test handling of unexpected API response format
        from src.agents.llm_utils import LLMInterface

        mock_response = Mock()
        mock_response.json.return_value = {"unexpected": "format"}
        mock_post.return_value = mock_response

        llm = LLMInterface()

        with pytest.raises(ValueError, match="Unexpected OpenRouter response format"):
            llm.generate_response([{"role": "user", "content": "test"}])

    @patch("src.agents.llm_utils.requests.post")
    def test_generate_response_request_exception(self, mock_post):
        # Test handling of request exceptions
        from src.agents.llm_utils import LLMInterface
        import requests

        mock_post.side_effect = requests.RequestException("Network error")

        llm = LLMInterface()

        with pytest.raises(RuntimeError, match="Failed to get response from OpenRouter"):
            llm.generate_response([{"role": "user", "content": "test"}])
