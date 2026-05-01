"""
Synthetic data smoke tests for the phishing pipeline.

These tests exercise parser, analyzer, database, and CSV loading behavior
using local demo files instead of live phishing URLs.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import analyzer
import database
import parser
import url_collector


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


def load_synthetic_html(filename):
    """Load synthetic HTML from the project data directory."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def test_parser_with_synthetic():
    """Test parser and analyzer with synthetic HTML samples."""
    print("=" * 60)
    print("TESTING PARSER WITH SYNTHETIC DATA")
    print("=" * 60)

    test_cases = [
        ("synthetic_high_risk.html", "http://fake-paypal.com/login"),
        ("synthetic_medium_risk.html", "http://example.com/verify"),
        ("synthetic_low_risk.html", "http://example-company.com"),
    ]

    for filename, url in test_cases:
        print(f"\nTesting: {filename}")
        print("-" * 40)

        html = load_synthetic_html(filename)
        indicators = parser.parse_indicators(html, url)
        result = analyzer.analyze(url, indicators)

        print(f"URL: {url}")
        print(f"Indicators found: {len(indicators)}")
        for indicator in indicators:
            print(f"  - {indicator['indicator']}: +{indicator['score']}")
            if indicator.get("detail"):
                print(f"    Detail: {indicator['detail']}")

        print(f"Risk Level: {result['risk_level']}")
        print(f"Total Score: {result['total_score']}")


def test_database_with_synthetic():
    """Test database operations with synthetic results."""
    print("\n" + "=" * 60)
    print("TESTING DATABASE WITH SYNTHETIC DATA")
    print("=" * 60)

    test_db = os.path.join(DATA_DIR, "test_synthetic.db")
    if os.path.exists(test_db):
        os.remove(test_db)

    database.init_database(test_db)

    test_cases = [
        {
            "url": "http://phish-test-high.com",
            "status_code": 200,
            "indicators": [
                {"indicator": "hidden_iframe", "score": 3, "detail": "Hidden iframe test"},
                {"indicator": "external_login_form", "score": 3, "detail": "External form test"},
                {"indicator": "password_field", "score": 2, "detail": "Password field test"},
            ],
            "total_score": 8,
            "risk_level": "HIGH",
        },
        {
            "url": "http://phish-test-medium.com",
            "status_code": 200,
            "indicators": [
                {"indicator": "password_field", "score": 2, "detail": "Password field test"},
                {"indicator": "urgency_keywords", "score": 1, "detail": "Urgency test"},
                {"indicator": "no_https_links", "score": 1, "detail": "Insecure links test"},
            ],
            "total_score": 4,
            "risk_level": "MEDIUM",
        },
        {
            "url": "http://phish-test-low.com",
            "status_code": 200,
            "indicators": [],
            "total_score": 0,
            "risk_level": "LOW",
        },
    ]

    print("\nStoring test results...")
    for case in test_cases:
        url_id = database.store_result(
            url=case["url"],
            status_code=case["status_code"],
            indicators=case["indicators"],
            total_score=case["total_score"],
            risk_level=case["risk_level"],
            db_path=test_db,
        )
        print(f"  Stored: {case['url']} (ID: {url_id})")

    results = database.get_all_results(db_path=test_db)
    print(f"\nTotal results: {len(results)}")
    for result in results:
        print(f"  - {result['url']} -> {result['risk_level']} (score: {result['total_score']})")

    stats = database.get_statistics(test_db)
    print("\nStatistics:")
    print(f"  Total: {stats['total_urls']}")
    print(f"  High: {stats['high_count']}")
    print(f"  Medium: {stats['medium_count']}")
    print(f"  Low: {stats['low_count']}")
    print(f"  Avg Score: {stats['average_score']}")

    high_results = database.get_all_results(risk_level="HIGH", db_path=test_db)
    print(f"\nHIGH risk filter count: {len(high_results)}")

    detail = database.get_result_by_id(1, test_db)
    if detail:
        print(f"Detail retrieval URL: {detail['url']}")
        print(f"Detail indicator count: {len(detail['indicators'])}")

    os.remove(test_db)
    print("\nDatabase test complete; temporary DB removed.")


def test_with_csv_urls():
    """Test loading URLs from the local CSV sample."""
    print("\n" + "=" * 60)
    print("TESTING WITH CSV URL FILE")
    print("=" * 60)

    csv_path = os.path.join(DATA_DIR, "sample_urls.csv")
    urls = url_collector.load_from_file(csv_path)

    print(f"\nLoaded {len(urls)} URLs from CSV")
    print("First 5 URLs:")
    for url in urls[:5]:
        print(f"  - {url}")


def run_all_tests():
    """Run all synthetic data tests."""
    print("\n" + "=" * 60)
    print("SYNTHETIC DATA TEST SUITE")
    print("=" * 60)

    test_parser_with_synthetic()
    test_database_with_synthetic()
    test_with_csv_urls()

    print("\n" + "=" * 60)
    print("ALL SYNTHETIC TESTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
