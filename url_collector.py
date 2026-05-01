"""
Component 1: URL Feed
Fetches phishing URLs from PhishTank and URLhaus public feeds.
"""
import requests
import csv
import io
from urllib.parse import urlparse
import random


# Public phishing data sources
PHISHTANK_URL = "https://www.phishtank.com/phish_archive.php?valid=y&download=1"
URLHAUS_URL = "https://urlhaus-api.abuse.ch/downloads/csv_recent/"


def validate_url(url):
    """Validate and normalize URL format."""
    url = url.strip()
    if not url:
        return None
    
    # Ensure scheme
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    
    # Parse and validate
    try:
        parsed = urlparse(url)
        if parsed.netloc and parsed.scheme in ("http", "https"):
            return url
    except Exception:
        pass
    return None


def fetch_phishtank(local_csv_path=None):
    """
    Fetch URLs from PhishTank.
    
    For automated access, PhishTank requires API key registration.
    For academic use, you can:
    1. Manually download CSV from https://www.phishtank.com/
    2. Save it to a local file and pass the path
    
    Args:
        local_csv_path: Optional path to locally downloaded PhishTank CSV
    
    Returns:
        list: List of validated URLs
    """
    urls = []
    
    # Try to load from local file if provided
    if local_csv_path:
        print(f"[URL_COLLECTOR] Loading PhishTank URLs from: {local_csv_path}")
        try:
            with open(local_csv_path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header
                
                # Find URL column index
                url_col = 0
                if header:
                    for i, col in enumerate(header):
                        col_lower = col.lower()
                        if "url" in col_lower or "phish" in col_lower:
                            url_col = i
                            break
                
                for row in reader:
                    if len(row) > url_col:
                        url = row[url_col].strip()
                        validated = validate_url(url)
                        if validated:
                            urls.append(validated)
            
            print(f"[URL_COLLECTOR] Loaded {len(urls)} URLs from PhishTank CSV")
            return urls
            
        except FileNotFoundError:
            print(f"[URL_COLLECTOR] PhishTank file not found: {local_csv_path}")
        except Exception as e:
            print(f"[URL_COLLECTOR ERROR] PhishTank: {e}")
    
    # No local file - show instructions
    print("[URL_COLLECTOR] PhishTank: Automated download requires API key")
    print("[URL_COLLECTOR] To use PhishTank:")
    print("  1. Register at https://www.phishtank.com/")
    print("  2. Download the verified phishing CSV")
    print("  3. Save as 'data/phishtank.csv' or pass path to get_urls()")
    
    return []


def fetch_urlhaus():
    """Fetch recent malicious URLs from URLhaus."""
    urls = []
    try:
        print("[URL_COLLECTOR] Fetching from URLhaus...")
        response = requests.get(
            URLHAUS_URL,
            timeout=30,
            headers={"User-Agent": "PhishingScanner/1.0 (Academic Research)"}
        )
        response.raise_for_status()
        
        # Parse CSV
        reader = csv.reader(io.StringIO(response.text))
        next(reader, None)  # Skip header row
        
        for row in reader:
            if len(row) >= 2:
                url = row[1].strip()  # URL is typically in column 1
                validated = validate_url(url)
                if validated:
                    urls.append(validated)
        
        print(f"[URL_COLLECTOR] Retrieved {len(urls)} URLs from URLhaus")
        
    except requests.RequestException as e:
        print(f"[URL_COLLECTOR ERROR] URLhaus: {e}")
    except Exception as e:
        print(f"[URL_COLLECTOR ERROR] {e}")
    
    return urls


def load_from_file(filepath):
    """Load URLs from a local CSV file."""
    urls = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    url = row[0].strip()
                    validated = validate_url(url)
                    if validated:
                        urls.append(validated)
        print(f"[URL_COLLECTOR] Loaded {len(urls)} URLs from {filepath}")
    except FileNotFoundError:
        print(f"[URL_COLLECTOR] File not found: {filepath}")
    except Exception as e:
        print(f"[URL_COLLECTOR ERROR] {e}")
    
    return urls


def get_urls(max_urls=None, use_online=True, local_file=None, phishtank_file=None):
    """
    Main entry point: Get deduplicated list of phishing URLs.
    
    Args:
        max_urls: Maximum number of URLs to return
        use_online: Whether to fetch from online sources
        local_file: Path to local CSV file as fallback
        phishtank_file: Path to local PhishTank CSV (optional)
    
    Returns:
        Deduplicated list of URL strings
    """
    all_urls = []
    
    # Try online sources
    if use_online:
        urlhaus_urls = fetch_urlhaus()
        all_urls.extend(urlhaus_urls)
        
        # PhishTank - try local file if provided
        if phishtank_file:
            phishtank_urls = fetch_phishtank(phishtank_file)
            all_urls.extend(phishtank_urls)
    
    # Fallback to local file
    if local_file and not all_urls:
        all_urls.extend(load_from_file(local_file))
    
    # Deduplicate while preserving order
    seen = set()
    unique_urls = []
    for url in all_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    # Limit results
    if max_urls and len(unique_urls) > max_urls:
        unique_urls = random.sample(unique_urls, max_urls)
    
    print(f"[URL_COLLECTOR] Total unique URLs: {len(unique_urls)}")
    return unique_urls


if __name__ == "__main__":
    # Test the collector
    urls = get_urls(max_urls=10)
    for url in urls:
        print(f"  - {url}")