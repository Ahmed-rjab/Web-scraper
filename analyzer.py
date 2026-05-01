import datetime

def analyze(url, indicators):
    """
    Component 4: Threat Analyzer
    Applies rule-based scoring and risk classification.
    """
    indicators = indicators or []

    try:
        total_score = sum(item.get("score", 0) for item in indicators)

        if total_score >= 7:
            risk_level = "HIGH"
        elif total_score >= 4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "url": url,
            "indicators": indicators,
            "indicator_count": len(indicators),
            "total_score": total_score,
            "risk_level": risk_level,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"[ANALYZER ERROR] {url}: {e}")
        return {
            "url": url,
            "indicators": [],
            "indicator_count": 0,
            "total_score": 0,
            "risk_level": "ERROR",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }