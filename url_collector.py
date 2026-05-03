"""
Component 1: URL Feed
Fetches phishing URLs from PhishTank and URLhaus public feeds.
"""
import requests
import csv
import io
from urllib.parse import urlparse
import random
import ipaddress
import os


# Public phishing data sources
PHISHTANK_ONLINE_CSV = "https://data.phishtank.com/data/online-valid.csv"
URLHAUS_URL = "https://urlhaus-api.abuse.ch/downloads/csv_recent/"
URLHAUS_EXPORT_URL = "https://urlhaus-api.abuse.ch/v2/files/exports/{auth_key}/recent.csv"


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
        hostname = parsed.hostname
        if not hostname or parsed.scheme not in ("http", "https"):
            return None

        try:
            ipaddress.ip_address(hostname)
            return url
        except ValueError:
            pass

        if "." in hostname or hostname == "localhost":
            return url
    except Exception:
        pass
    return None


def _row_is_verified(row):
    """Return True if the CSV row indicates the entry is verified/valid."""
    if not row or not isinstance(row, dict):
        return False

    # Common column names that indicate verification/validity
    verification_keys = ("verified", "valid", "is_valid", "is_verified", "online")
    for key in row:
        if not key:
            continue
        if key.lower().strip() in verification_keys:
            val = (row.get(key) or "").strip().lower()
            return val in ("1", "true", "t", "y", "yes")

    # If no explicit verification column exists (e.g., the 'online-valid.csv'
    # feed already contains only valid entries), assume the row is verified.
    return True


def _extract_url_from_row(row):
    """Try to extract a URL from a CSV row (dict)."""
    if not row or not isinstance(row, dict):
        return None

    # Prefer columns with 'url' in the header
    for key in row:
        if key and "url" in key.lower():
            candidate = (row.get(key) or "").strip()
            if candidate:
                return candidate

    # Fallback: find any value starting with http(s)
    for v in row.values():
        v = (v or "").strip()
        if v.startswith("http://") or v.startswith("https://"):
            return v
    return None


def fetch_phishtank(local_csv_path=None, download_url=PHISHTANK_ONLINE_CSV, timeout=30):
    """
    Download and parse the PhishTank CSV (or read a local file).

    - Downloads from `https://data.phishtank.com/data/online-valid.csv` by default.
    - Parses with the `csv` module using `csv.DictReader`.
    - Filters for verified/valid entries only.
    - Removes duplicates while preserving order.

    Args:
        local_csv_path: Optional path to a locally saved PhishTank CSV file.
        download_url: URL to download the CSV from (default: PhishTank online file).
        timeout: HTTP request timeout in seconds.

    Returns:
        list: Deduplicated, validated URL strings.
    """
    urls = []

    # 1) Try to read a local CSV if provided
    if local_csv_path:
        print(f"[URL_COLLECTOR] Loading PhishTank URLs from: {local_csv_path}")
        try:
            with open(local_csv_path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not _row_is_verified(row):
                        continue
                    url = _extract_url_from_row(row)
                    if not url:
                        continue
                    validated = validate_url(url)
                    if validated:
                        urls.append(validated)

            unique = list(dict.fromkeys(urls))
            print(f"[URL_COLLECTOR] Loaded {len(unique)} unique URLs from PhishTank CSV")
            return unique
        except FileNotFoundError:
            print(f"[URL_COLLECTOR] PhishTank file not found: {local_csv_path}")
        except Exception as e:
            print(f"[URL_COLLECTOR ERROR] PhishTank (local): {e}")

    # 2) Download the CSV from PhishTank
    try:
        print(f"[URL_COLLECTOR] Downloading PhishTank CSV from: {download_url}")
        response = requests.get(
            download_url,
            timeout=timeout,
            headers={"User-Agent": "PhishingScanner/1.0 (Academic Research)"}
        )
        response.raise_for_status()

        # Decode and parse CSV
        text = response.content.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))

        for row in reader:
            if not _row_is_verified(row):
                continue
            url = _extract_url_from_row(row)
            if not url:
                continue
            validated = validate_url(url)
            if validated:
                urls.append(validated)

        unique = list(dict.fromkeys(urls))
        print(f"[URL_COLLECTOR] Downloaded and parsed {len(unique)} unique URLs from PhishTank")
        return unique

    except requests.RequestException as e:
        print(f"[URL_COLLECTOR ERROR] Failed to download PhishTank CSV: {e}")
    except Exception as e:
        print(f"[URL_COLLECTOR ERROR] Parsing PhishTank CSV: {e}")

    return []


def fetch_urlhaus():
    """Fetch recent malicious URLs from URLhaus."""
    urls = []
    auth_key = os.getenv("URLHAUS_AUTH_KEY")
    if not auth_key:
        print("[URL_COLLECTOR] URLhaus now requires URLHAUS_AUTH_KEY for CSV downloads")
        return urls

    try:
        print("[URL_COLLECTOR] Fetching from URLhaus...")
        response = requests.get(
            URLHAUS_EXPORT_URL.format(auth_key=auth_key),
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
        # URLhaus (may require URLHAUS_AUTH_KEY)
        try:
            urlhaus_urls = fetch_urlhaus()
            all_urls.extend(urlhaus_urls)
        except Exception as e:
            print(f"[URL_COLLECTOR] URLhaus fetch failed: {e}")

        # PhishTank: prefer the online 'online-valid.csv' feed but allow
        # an override via `phishtank_file` pointing to a local CSV.
        try:
            if phishtank_file:
                phishtank_urls = fetch_phishtank(phishtank_file)
            else:
                phishtank_urls = fetch_phishtank()
            all_urls.extend(phishtank_urls)
        except Exception as e:
            print(f"[URL_COLLECTOR] PhishTank fetch failed: {e}")
    
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
