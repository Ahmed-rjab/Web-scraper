from bs4 import BeautifulSoup
from urllib.parse import urlparse

def parse_indicators(html, page_url):
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    indicators = []
    
    # Standardize domain for comparison
    parsed_page = urlparse(page_url)
    page_domain = parsed_page.netloc.lower().replace("www.", "")

    # Pre-extract text once for efficiency (Rules 5 and 7)
    body_text = soup.get_text().lower()
    title_tag = soup.find("title")
    title_text = title_tag.get_text().lower() if title_tag else ""

    # ── Rule 1: Hidden iframes (+3) ──────────────────────────────
    for iframe in soup.find_all("iframe"):
        style = iframe.get("style", "").lower().replace(" ", "")
        width = iframe.get("width", "")
        height = iframe.get("height", "")
        
        # Detect if hidden via CSS or zero-sizing attributes
        is_hidden = any([
            "display:none" in style,
            "visibility:hidden" in style,
            "opacity:0" in style,
            width == "0",
            height == "0"
        ])
        
        if is_hidden:
            indicators.append({
                "indicator": "hidden_iframe",
                "score": 3,
                "detail": str(iframe)[:100]
            })
            break # Count once per page

    # ── Rule 2: External login form (+3) ─────────────────────────
    for form in soup.find_all("form"):
        action = form.get("action", "").lower()
        # Only flag if it's an absolute URL (starts with http)
        if action.startswith("http"):
            form_domain = urlparse(action).netloc.lower().replace("www.", "")
            # Flag if the data is being sent to a different domain
            if form_domain and form_domain != page_domain:
                indicators.append({
                    "indicator": "external_login_form",
                    "score": 3,
                    "detail": f"Form submits to: {form_domain}"
                })
                break

    # ── Rule 3: Password field (+2) ──────────────────────────────
    # Simple check: phishing sites almost always have a password input
    pw_field = soup.find("input", {"type": "password"})
    if pw_field:
        indicators.append({
            "indicator": "password_field",
            "score": 2,
            "detail": "Password input tag detected"
        })

    # ── Rule 4: External scripts (+2) ────────────────────────────
    external_scripts = []
    for script in soup.find_all("script", src=True):
        src = script.get("src", "").lower()
        if src.startswith("http"):
            script_domain = urlparse(src).netloc.lower().replace("www.", "")
            if script_domain and script_domain != page_domain:
                external_scripts.append(script_domain)
    
    if external_scripts:
        indicators.append({
            "indicator": "suspicious_script",
            "score": 2,
            "detail": f"Scripts hosted on: {', '.join(list(set(external_scripts))[:2])}"
        })
        CDN_WHITELIST = {
    "cdnjs.cloudflare.com", "ajax.googleapis.com",
    "code.jquery.com", "cdn.jsdelivr.net", "stackpath.bootstrapcdn.com"
    }

    external_scripts = []
    for script in soup.find_all("script", src=True):
        src = script.get("src", "").lower()
        if src.startswith("http"):
            script_domain = urlparse(src).netloc.lower().replace("www.", "")
            if script_domain and script_domain != page_domain and script_domain not in CDN_WHITELIST:
                external_scripts.append(script_domain)

    # ── Rule 5: Urgency keywords (+1) ────────────────────────────
    # We use a set for faster lookup and check once per page
    urgency_words = [
        "verify now", "account suspended", "click immediately",
        "confirm your identity", "unusual activity", "limited time",
        "action required", "security alert"
    ]
    
    found_words = [word for word in urgency_words if word in body_text]
    if found_words:
        indicators.append({
            "indicator": "urgency_keywords",
            "score": 1,
            "detail": f"Found: {', '.join(found_words[:3])}" # Show first 3 found
        })

    # ── Rule 6: No HTTPS links (+1) ──────────────────────────────
    # Only flags if the page actually HAS links and NONE are https
    all_links = soup.find_all("a", href=True)
    if all_links:
        # Check if any link starts with https://
        has_https = any(a["href"].startswith("https://") for a in all_links)
        
        if not has_https:
            indicators.append({
                "indicator": "no_https_links",
                "score": 1,
                "detail": f"All {len(all_links)} links are insecure or relative"
            })

    # ── Rule 7: Mismatched title (+2) ────────────────────────────
    known_brands = [
        "paypal", "facebook", "google", "apple", "amazon", "microsoft", 
        "netflix", "instagram", "twitter", "linkedin", "outlook", "icloud"
    ]
    
    # Only check if there is actually a title to analyze
    if title_text:
        for brand in known_brands:
            # If the brand is in the title but NOT in the actual URL domain
            if brand in title_text and brand not in page_domain:
                indicators.append({
                    "indicator": "mismatched_title",
                    "score": 2,
                    "detail": f"Title mentions '{brand}' but domain is '{page_domain}'"
                })
                break # Only flag once

    return indicators