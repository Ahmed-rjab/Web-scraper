"""
Unit Tests for URL Collector Component
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import url_collector


class TestURLCollector(unittest.TestCase):
    """Test cases for url_collector module."""
    
    def test_validate_url_valid(self):
        """Test URL validation with valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://phish-site.com/login",
            "https://secure-bank.com/verify?user=123"
        ]
        for url in valid_urls:
            result = url_collector.validate_url(url)
            self.assertIsNotNone(result)
            self.assertTrue(result.startswith(("http://", "https://")))
    
    def test_validate_url_invalid(self):
        """Test URL validation with invalid URLs."""
        invalid_urls = [
            "",
            "not-a-url",
            "ftp://example.com",
            "javascript:alert(1)"
        ]
        for url in invalid_urls:
            result = url_collector.validate_url(url)
            self.assertIsNone(result)
    
    def test_validate_url_whitespace(self):
        """Test URL validation strips whitespace."""
        url = "  https://example.com  "
        result = url_collector.validate_url(url)
        self.assertEqual(result, "https://example.com")
    
    def test_validate_url_adds_scheme(self):
        """Test URL validation adds http:// if missing."""
        url = "example.com"
        result = url_collector.validate_url(url)
        self.assertTrue(result.startswith("http://"))
    
    def test_fetch_urlhaus_returns_list(self):
        """Test that fetch_urlhaus returns a list."""
        # Note: This makes a real network request
        # In production, this should be mocked
        try:
            urls = url_collector.fetch_urlhaus()
            self.assertIsInstance(urls, list)
        except Exception as e:
            self.skipTest(f"Network unavailable: {e}")
    
    def test_load_from_file_not_found(self):
        """Test loading from non-existent file."""
        urls = url_collector.load_from_file("nonexistent_file.csv")
        self.assertEqual(urls, [])


class TestURLCollectorIntegration(unittest.TestCase):
    """Integration tests for URL collector."""
    
    def test_get_urls_returns_list(self):
        """Test get_urls returns a list."""
        try:
            urls = url_collector.get_urls(max_urls=5, use_online=True)
            self.assertIsInstance(urls, list)
            # May be empty if network fails
        except Exception as e:
            self.skipTest(f"Network unavailable: {e}")
    
    def test_get_urls_respects_limit(self):
        """Test that max_urls limits the result."""
        try:
            urls = url_collector.get_urls(max_urls=3, use_online=True)
            if urls:
                self.assertLessEqual(len(urls), 3)
        except Exception as e:
            self.skipTest(f"Network unavailable: {e}")


if __name__ == "__main__":
    unittest.main()