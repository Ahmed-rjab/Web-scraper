"""
Component 6: Flask Dashboard
Web interface for viewing phishing analysis results.
"""
from flask import Flask, render_template, request, redirect, url_for, send_file
import database


app = Flask(__name__)
DATABASE_FILE = "phishing_intel.db"


@app.route("/")
def index():
    """Dashboard home with summary statistics."""
    stats = database.get_statistics(DATABASE_FILE)
    recent = database.get_all_results(limit=10, db_path=DATABASE_FILE)
    
    return render_template(
        "dashboard.html",
        page="home",
        stats=stats,
        recent_results=recent
    )


@app.route("/results")
def results():
    """Full results table with filtering."""
    risk_filter = request.args.get("risk_level")
    limit = int(request.args.get("limit", 100))
    
    results = database.get_all_results(
        limit=limit,
        risk_level=risk_filter,
        db_path=DATABASE_FILE
    )
    
    return render_template(
        "dashboard.html",
        page="results",
        results=results,
        current_filter=risk_filter
    )


@app.route("/result/<int:url_id>")
def result_detail(url_id):
    """Detailed view for a single URL."""
    result = database.get_result_by_id(url_id, DATABASE_FILE)
    
    if not result:
        return "URL not found", 404
    
    return render_template(
        "dashboard.html",
        page="detail",
        result=result
    )


@app.route("/export")
def export():
    """Export results as CSV."""
    import tempfile
    import os
    
    # Create temp file
    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False,
        encoding="utf-8"
    )
    temp_path = temp_file.name
    temp_file.close()
    
    # Export
    database.export_to_csv(temp_path, DATABASE_FILE)
    
    return send_file(
        temp_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name="phishing_results.csv"
    )


@app.route("/run", methods=["POST"])
def run_scanner():
    """Run the full scanning pipeline."""
    from main import run_pipeline
    
    max_urls = int(request.form.get("max_urls", 10))
    run_pipeline(max_urls=max_urls)
    
    return redirect(url_for("results"))


if __name__ == "__main__":
    # Initialize database on first run
    database.init_database(DATABASE_FILE)
    
    # Run the app
    print("[DASHBOARD] Starting Flask server on http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)