"""
Component 5: SQLite Database
Handles persistent storage of analysis results.
"""
import sqlite3
import datetime
from contextlib import contextmanager


DATABASE_FILE = "phishing_intel.db"


def init_database(db_path=None):
    """Initialize the database with required tables."""
    if db_path is None:
        db_path = DATABASE_FILE
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        print(f"[DATABASE ERROR] Failed to connect: {e}")
        raise
    
    try:
        # Table: urls - stores URL metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                scraped_at DATETIME NOT NULL,
                status_code INTEGER
            )
        """)

        # Table: results - stores individual indicators
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER NOT NULL,
                indicator TEXT NOT NULL,
                score INTEGER NOT NULL,
                detail TEXT,
                FOREIGN KEY (url_id) REFERENCES urls (id)
            )
        """)

        # Table: scores - stores aggregated threat scores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                url_id INTEGER PRIMARY KEY,
                total_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                FOREIGN KEY (url_id) REFERENCES urls (id)
            )
        """)

        # Create indexes for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_urls_scraped_at ON urls(scraped_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_url_id ON results(url_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_risk_level ON scores(risk_level)")

        conn.commit()
        print(f"[DATABASE] Initialized: {db_path}")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"[DATABASE ERROR] Failed to initialize schema: {e}")
        raise
    finally:
        conn.close()


@contextmanager
def get_connection(db_path=None):
    """Context manager for database connections."""
    if db_path is None:
        db_path = DATABASE_FILE
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def store_result(url, status_code, indicators, total_score, risk_level, db_path=None):
    """
    Store a complete analysis result in the database.
    
    Args:
        url: The analyzed URL
        status_code: HTTP status code
        indicators: List of indicator dicts
        total_score: Aggregated threat score
        risk_level: Risk classification (LOW/MEDIUM/HIGH)
        db_path: Optional database path
    
    Returns:
        int: The URL ID in the database
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        timestamp = datetime.datetime.utcnow().isoformat()
        
        # 1. Insert URL metadata
        cursor.execute(
            "INSERT INTO urls (url, scraped_at, status_code) VALUES (?, ?, ?)",
            (url, timestamp, status_code)
        )
        url_id = cursor.lastrowid
        
        # 2. Insert each detected indicator
        for item in indicators:
            cursor.execute(
                "INSERT INTO results (url_id, indicator, score, detail) VALUES (?, ?, ?, ?)",
                (url_id, item.get("indicator"), item.get("score"), item.get("detail"))
            )
        
        # 3. Insert aggregated score
        cursor.execute(
            "INSERT INTO scores (url_id, total_score, risk_level) VALUES (?, ?, ?)",
            (url_id, total_score, risk_level)
        )
        
        conn.commit()
        return url_id


def get_all_results(limit=100, risk_level=None, db_path=None):
    """
    Retrieve analysis results with optional filtering.
    
    Args:
        limit: Maximum number of results to return
        risk_level: Filter by risk level (LOW/MEDIUM/HIGH)
        db_path: Optional database path
    
    Returns:
        list: List of result dicts
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT 
                u.id, u.url, u.scraped_at, u.status_code,
                s.total_score, s.risk_level
            FROM urls u
            JOIN scores s ON u.id = s.url_id
        """
        
        params = []
        if risk_level:
            query += " WHERE s.risk_level = ?"
            params.append(risk_level.upper())
        
        query += " ORDER BY u.scraped_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "url": row["url"],
                "scraped_at": row["scraped_at"],
                "status_code": row["status_code"],
                "total_score": row["total_score"],
                "risk_level": row["risk_level"]
            })
        
        return results


def get_result_by_id(url_id, db_path=None):
    """
    Get detailed results for a specific URL.
    
    Args:
        url_id: The URL ID
        db_path: Optional database path
    
    Returns:
        dict: URL details with all indicators
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Get URL and score
        cursor.execute("""
            SELECT u.id, u.url, u.scraped_at, u.status_code, s.total_score, s.risk_level
            FROM urls u
            JOIN scores s ON u.id = s.url_id
            WHERE u.id = ?
        """, (url_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        result = {
            "id": row["id"],
            "url": row["url"],
            "scraped_at": row["scraped_at"],
            "status_code": row["status_code"],
            "total_score": row["total_score"],
            "risk_level": row["risk_level"],
            "indicators": []
        }
        
        # Get indicators
        cursor.execute("""
            SELECT indicator, score, detail
            FROM results
            WHERE url_id = ?
        """, (url_id,))
        
        for row in cursor.fetchall():
            result["indicators"].append({
                "indicator": row["indicator"],
                "score": row["score"],
                "detail": row["detail"]
            })
        
        return result


def get_statistics(db_path=None):
    """
    Get aggregate statistics.
    
    Returns:
        dict: Statistics including counts by risk level
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Total URLs
        cursor.execute("SELECT COUNT(*) as total FROM urls")
        total = cursor.fetchone()["total"]
        
        # By risk level
        cursor.execute("""
            SELECT risk_level, COUNT(*) as count
            FROM scores
            GROUP BY risk_level
        """)
        by_risk = {row["risk_level"]: row["count"] for row in cursor.fetchall()}
        
        # Average score
        cursor.execute("SELECT AVG(total_score) as avg_score FROM scores")
        avg_score = cursor.fetchone()["avg_score"] or 0
        
        return {
            "total_urls": total,
            "high_count": by_risk.get("HIGH", 0),
            "medium_count": by_risk.get("MEDIUM", 0),
            "low_count": by_risk.get("LOW", 0),
            "average_score": round(avg_score, 2)
        }


def export_to_csv(filepath, db_path=None):
    """Export all results to a CSV file."""
    import csv
    
    results = get_all_results(limit=10000, db_path=db_path)
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "URL", "Scraped At", "Status Code", "Total Score", "Risk Level"])
        
        for r in results:
            writer.writerow([
                r["id"], r["url"], r["scraped_at"], 
                r["status_code"], r["total_score"], r["risk_level"]
            ])
    
    print(f"[DATABASE] Exported {len(results)} results to {filepath}")


if __name__ == "__main__":
    # Test database
    init_database()
    
    # Store a test result
    test_url = "http://example-phish.com/login"
    test_indicators = [
        {"indicator": "password_field", "score": 2, "detail": "Password input detected"},
        {"indicator": "external_login_form", "score": 3, "detail": "Form submits to: evil.com"}
    ]
    url_id = store_result(
        test_url, 
        status_code=200, 
        indicators=test_indicators,
        total_score=5,
        risk_level="MEDIUM"
    )
    print(f"[DATABASE] Stored test result with ID: {url_id}")
    
    # Get statistics
    stats = get_statistics()
    print(f"[DATABASE] Statistics: {stats}")
