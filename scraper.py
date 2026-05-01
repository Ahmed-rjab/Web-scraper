"""
Component 2: Scraper Engine
Performs HTTP requests to fetch HTML content from target URLs.
"""
import requests
import time
import random
from urllib.parse import urlparse


# Configuration
DEFAULT_TIMEOUT = 10  # seconds
MIN_DELAY = 1  # minimum seconds between requests
MAX_DELAY = 3  # maximum seconds between requests


def fetch_page(url, timeout=DEFAULT_TIMEOUT, user_agent=None):
    """
    Fetch a web page and return its content.
    
    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        user_agent: Custom User-Agent string
    
    Returns:
        tuple: (status_code, html_content, error_message)
               On success: (int, str, None)
               On failure: (None, None, str)
    """
    if not url:
        return (None, None, "Empty URL provided")
    
    if not url.startswith(("http://", "https://")):
        return (None, None, "Invalid URL scheme - must start with http:// or https://")
    
    if not user_agent:
        user_agent = "PhishingScanner/1.0 (Academic Research; +https://example.com/contact)"
    
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
            allow_redirects=True,
            verify=False  # Skip SSL verification for phishing sites
        )
        
        # Check for empty response
        if not response.text:
            return (response.status_code, None, "Empty response body")
        
        return (response.status_code, response.text, None)
    
    except requests.Timeout:
        return (None, None, f"Timeout error after {timeout}s")
    except requests.ConnectionError as e:
        return (None, None, f"Connection error: {str(e)[:80]}")
    except requests.TooManyRedirects:
        return (None, None, "Too many redirects")
    except requests.SSLError as e:
        return (None, None, f"SSL error: {str(e)[:50]}")
    except requests.RequestException as e:
        return (None, None, f"Request error: {str(e)[:80]}")
    except Exception as e:
        return (None, None, f"Unexpected error: {str(e)[:80]}")


def scrape_urls(urls, delay_range=(MIN_DELAY, MAX_DELAY), progress_callback=None):
    """
    Scrape multiple URLs with rate limiting.
    
    Args:
        urls: List of URL strings to scrape
        delay_range: Tuple of (min_delay, max_delay) in seconds
        progress_callback: Optional callback function(current, total, url, result)
    
    Yields:
        dict: {url, status_code, html, error}
    """
    total = len(urls)
    
    for i, url in enumerate(urls, 1):
        # Fetch the page
        status_code, html, error = fetch_page(url)
        
        result = {
            "url": url,
            "status_code": status_code,
            "html": html,
            "error": error
        }
        
        # Progress callback
        if progress_callback:
            progress_callback(i, total, url, result)
        else:
            if i % 10 == 0 or error:
                print(f"[SCRAPER] Progress: {i}/{total} - {url[:50]}...")
        
        # Rate limiting between requests
        if i < total:
            delay = random.uniform(delay_range[0], delay_range[1])
            time.sleep(delay)
        
        yield result


def get_domain(url):
    """Extract domain from URL for logging."""
    try:
        return urlparse(url).netloc or "unknown"
    except Exception:
        return "unknown"


if __name__ == "__main__":
    # Test the scraper
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html",
    ]
    
    print("[SCRAPER] Testing scraper engine...")
    for result in scrape_urls(test_urls):
        print(f"  URL: {result['url']}")
        print(f"  Status: {result['status_code']}")
        print(f"  Error: {result['error']}")
        print(f"  Content length: {len(result['html']) if result['html'] else 0}")
        print()
