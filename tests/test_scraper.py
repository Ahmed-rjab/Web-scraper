"""
Unit Tests for Scraper Engine Component
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scraper


class TestScraper(unittest.TestCase):
    """Test cases for scraper module."""
    
    def test_fetch_page_success(self):
        """Test successful page fetch."""
        status_code, html, error = scraper.fetch_page("https://httpbin.org/html")
        
        self.assertIsNotNone(status_code)
        self.assertEqual(status_code, 200)
        self.assertIsNone(error)
        self.assertIsInstance(html, str)
        self.assertGreater(len(html), 0)
    
    def test_fetch_page_timeout(self):
        """Test page fetch with timeout."""
        # Use a non-responsive host
        status_code, html, error = scraper.fetch_page(
            "http://10.255.255.1", 
            timeout=2
        )
        
        self.assertIsNone(status_code)
        self.assertIsNone(html)
        self.assertIsNotNone(error)
        self.assertIn("error", error.lower())
    
    def test_fetch_page_invalid_url(self):
        """Test fetch with invalid URL."""
        status_code, html, error = scraper.fetch_page("not-a-url")
        
        self.assertIsNone(status_code)
        self.assertIsNone(html)
        self.assertIsNotNone(error)
    
    def test_get_domain(self):
        """Test domain extraction."""
        self.assertEqual(
            scraper.get_domain("https://example.com/path"), 
            "example.com"
        )
        self.assertEqual(
            scraper.get_domain("http://sub.domain.com/page"), 
            "sub.domain.com"
        )
        self.assertEqual(
            scraper.get_domain("invalid"), 
            "unknown"
        )


class TestScraperIntegration(unittest.TestCase):
    """Integration tests for scraper."""
    
    def test_scrape_urls_generator(self):
        """Test that scrape_urls returns a generator."""
        urls = ["https://httpbin.org/html"]
        results = list(scraper.scrape_urls(urls))
        
        self.assertEqual(len(results), 1)
        self.assertIn("url", results[0])
        self.assertIn("status_code", results[0])
        self.assertIn("html", results[0])
        self.assertIn("error", results[0])
    
    def test_scrape_multiple_urls(self):
        """Test scraping multiple URLs."""
        urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/delay/1"
        ]
        
        results = list(scraper.scrape_urls(urls, delay_range=(0, 0)))
        
        self.assertEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main()