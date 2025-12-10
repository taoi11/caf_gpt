"""
tests/spam_filter_test.py

Tests for spam filter functionality.
"""

import pytest
from src.utils.spam_filter import is_sender_allowed


class TestSpamFilter:
    """Tests for spam filter sender validation"""

    def test_allowed_forces_gc_ca_domain(self):
        """Test that emails from forces.gc.ca domain are allowed"""
        assert is_sender_allowed("user@forces.gc.ca") is True
        assert is_sender_allowed("john.doe@forces.gc.ca") is True
        assert is_sender_allowed("UPPERCASE@FORCES.GC.CA") is True

    def test_allowed_ecn_forces_gc_ca_domain(self):
        """Test that emails from ecn.forces.gc.ca domain are allowed"""
        assert is_sender_allowed("user@ecn.forces.gc.ca") is True
        assert is_sender_allowed("jane.smith@ecn.forces.gc.ca") is True

    def test_blocked_invalid_domains(self):
        """Test that emails from non-allowed domains are blocked"""
        assert is_sender_allowed("user@gmail.com") is False
        assert is_sender_allowed("spam@example.com") is False
        assert is_sender_allowed("attacker@malicious.com") is False

    def test_blocked_partial_domain_match(self):
        """Test that partial domain matches are blocked"""
        assert is_sender_allowed("user@notforces.gc.ca") is False
        assert is_sender_allowed("user@forces.gc.ca.fake.com") is False

    def test_empty_or_invalid_email(self):
        """Test that empty or invalid emails are blocked"""
        assert is_sender_allowed("") is False

    def test_case_insensitive_matching(self):
        """Test that domain matching is case insensitive"""
        assert is_sender_allowed("User@Forces.GC.CA") is True
        assert is_sender_allowed("USER@ECN.FORCES.GC.CA") is True

    def test_whitespace_handling(self):
        """Test that whitespace is properly handled"""
        assert is_sender_allowed("  user@forces.gc.ca  ") is True
        assert is_sender_allowed("\tuser@ecn.forces.gc.ca\n") is True
