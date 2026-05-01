"""
Unit Tests for Threat Analyzer Component
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import analyzer
import datetime


class TestThreatAnalyzer(unittest.TestCase):
    """Test cases for analyzer module."""
    
    def test_analyze_empty_indicators(self):
        """Test analysis with no indicators."""
        result = analyzer.analyze("http://example.com", [])
        self.assertEqual(result["url"], "http://example.com")
        self.assertEqual(result["total_score"], 0)
        self.assertEqual(result["risk_level"], "LOW")
        self.assertEqual(result["indicator_count"], 0)
    
    def test_analyze_none_indicators(self):
        """Test analysis with None indicators."""
        result = analyzer.analyze("http://example.com", None)
        self.assertEqual(result["total_score"], 0)
        self.assertEqual(result["risk_level"], "LOW")
    
    def test_high_risk_classification(self):
        """Test HIGH risk classification (score >= 7)."""
        indicators = [
            {"indicator": "hidden_iframe", "score": 3},
            {"indicator": "external_login_form", "score": 3},
            {"indicator": "password_field", "score": 2}
        ]
        result = analyzer.analyze("http://example.com", indicators)
        self.assertEqual(result["total_score"], 8)
        self.assertEqual(result["risk_level"], "HIGH")
    
    def test_medium_risk_classification(self):
        """Test MEDIUM risk classification (score 4-6)."""
        indicators = [
            {"indicator": "password_field", "score": 2},
            {"indicator": "urgency_keywords", "score": 1},
            {"indicator": "no_https_links", "score": 1}
        ]
        result = analyzer.analyze("http://example.com", indicators)
        self.assertEqual(result["total_score"], 4)
        self.assertEqual(result["risk_level"], "MEDIUM")
    
    def test_low_risk_classification(self):
        """Test LOW risk classification (score < 4)."""
        indicators = [
            {"indicator": "urgency_keywords", "score": 1}
        ]
        result = analyzer.analyze("http://example.com", indicators)
        self.assertEqual(result["total_score"], 1)
        self.assertEqual(result["risk_level"], "LOW")
    
    def test_boundary_score_low(self):
        """Test boundary: score 3 should be LOW."""
        indicators = [
            {"indicator": "urgency_keywords", "score": 1},
            {"indicator": "no_https_links", "score": 1},
            {"indicator": "another_low", "score": 1}
        ]
        result = analyzer.analyze("http://example.com", indicators)
        self.assertEqual(result["risk_level"], "LOW")
    
    def test_boundary_score_medium(self):
        """Test boundary: score 4 should be MEDIUM."""
        indicators = [
            {"indicator": "password_field", "score": 2},
            {"indicator": "urgency_keywords", "score": 1},
            {"indicator": "no_https_links", "score": 1}
        ]
        result = analyzer.analyze("http://example.com", indicators)
        self.assertEqual(result["risk_level"], "MEDIUM")
    
    def test_boundary_score_high(self):
        """Test boundary: score 7 should be HIGH."""
        indicators = [
            {"indicator": "hidden_iframe", "score": 3},
            {"indicator": "external_login_form", "score": 3},
            {"indicator": "urgency_keywords", "score": 1}
        ]
        result = analyzer.analyze("http://example.com", indicators)
        self.assertEqual(result["risk_level"], "HIGH")
    
    def test_indicator_count(self):
        """Test that indicator count is correct."""
        indicators = [
            {"indicator": "a", "score": 1},
            {"indicator": "b", "score": 2},
            {"indicator": "c", "score": 3}
        ]
        result = analyzer.analyze("http://example.com", indicators)
        self.assertEqual(result["indicator_count"], 3)
    
    def test_timestamp_format(self):
        """Test that timestamp is in ISO format."""
        result = analyzer.analyze("http://example.com", [])
        self.assertIn("timestamp", result)
        # Should be parseable as ISO format
        try:
            datetime.datetime.fromisoformat(result["timestamp"])
        except ValueError:
            self.fail("Timestamp not in ISO format")
    
    def test_error_handling(self):
        """Test that errors are handled gracefully."""
        # This should not raise an exception
        result = analyzer.analyze("http://example.com", [{"score": "invalid"}])
        self.assertIn("risk_level", result)


if __name__ == "__main__":
    unittest.main()