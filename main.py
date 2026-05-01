"""
Main Entry Point: Phishing Threat Intelligence Pipeline
Orchestrates all components: URL Feed → Scraper → Parser → Analyzer → Database
"""
import sys
import time

# Import all components
import url_collector
import scraper
import parser
import analyzer
import database


DATABASE_FILE = "phishing_intel.db"


def run_pipeline(max_urls=10, local_file=None):
    """
    Run the complete phishing detection pipeline.
    
    Args:
        max_urls: Maximum number of URLs to process
        local_file: Optional local CSV file with URLs
    
    Returns:
        int: Number of URLs successfully processed
    """
    print("=" * 60)
    print("PHISHING THREAT INTELLIGENCE SCRAPER")
    print("=" * 60)
    
    # Initialize database
    print("\n[1/5] Initializing database...")
    database.init_database(DATABASE_FILE)
    
    # Step 1: Collect URLs
    print("\n[2/5] Collecting URLs from feed sources...")
    urls = url_collector.get_urls(
        max_urls=max_urls,
        use_online=True,
        local_file=local_file
    )
    
    if not urls:
        print("[PIPELINE] No URLs available. Exiting.")
        return 0
    
    print(f"[PIPELINE] Collected {len(urls)} unique URLs")
    
    # Step 2: Scrape URLs
    print(f"\n[3/5] Scraping {len(urls)} URLs (this may take a while)...")
    scraped_count = 0
    error_count = 0
    
    for result in scraper.scrape_urls(urls):
        url = result["url"]
        status_code = result["status_code"]
        html = result["html"]
        error = result["error"]
        
        if error:
            print(f"  [ERROR] {url}: {error}")
            error_count += 1
            # Store error result with empty indicators
            database.store_result(
                url=url,
                status_code=status_code,
                indicators=[],
                total_score=0,
                risk_level="ERROR"
            )
            continue
        
        if not html or len(html) < 100:
            print(f"  [SKIP] {url}: Empty or too small response")
            error_count += 1
            continue
        
        # Step 3: Parse HTML for indicators
        print(f"  [PARSING] {url[:60]}...")
        indicators = parser.parse_indicators(html, url)
        
        # Step 4: Analyze and score
        analysis = analyzer.analyze(url, indicators)
        
        # Step 5: Store in database
        database.store_result(
            url=url,
            status_code=status_code,
            indicators=analysis["indicators"],
            total_score=analysis["total_score"],
            risk_level=analysis["risk_level"]
        )
        
        scraped_count += 1
        print(f"    → Score: {analysis['total_score']} | Risk: {analysis['risk_level']}")
    
    # Final statistics
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Processed: {scraped_count} URLs")
    print(f"  Errors: {error_count} URLs")
    
    stats = database.get_statistics(DATABASE_FILE)
    print(f"\nDatabase Statistics:")
    print(f"  Total URLs in DB: {stats['total_urls']}")
    print(f"  High Risk: {stats['high_count']}")
    print(f"  Medium Risk: {stats['medium_count']}")
    print(f"  Low Risk: {stats['low_count']}")
    print(f"  Average Score: {stats['average_score']}")
    
    return scraped_count


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Phishing Threat Intelligence Scraper"
    )
    parser.add_argument(
        "-n", "--max-urls",
        type=int,
        default=10,
        help="Maximum number of URLs to process (default: 10)"
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Path to local CSV file with URLs (fallback)"
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Start the Flask dashboard after scanning"
    )
    
    args = parser.parse_args()
    
    # Run the pipeline
    count = run_pipeline(max_urls=args.max_urls, local_file=args.file)
    
    if args.dashboard:
        print("\n[DASHBOARD] Starting web interface...")
        import app
        app.app.run(debug=False, host="0.0.0.0", port=5000)
    
    return count


if __name__ == "__main__":
    main()