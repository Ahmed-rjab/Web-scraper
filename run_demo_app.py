"""Start the Flask dashboard for local demos without the debug reloader."""
import app
import database

# Pre-populate DB before starting demo dashboard
def _populate_demo_db(max_urls=20):
    try:
        # Import here to avoid circular imports at module import time
        from main import run_pipeline
        print(f"[DEMO] Running pipeline to pre-populate DB with {max_urls} URLs...")
        run_pipeline(max_urls=max_urls)
    except Exception as e:
        print(f"[DEMO] Failed to pre-populate DB: {e}")


if __name__ == "__main__":
    database.init_database(app.DATABASE_FILE)
    _populate_demo_db(max_urls=20)
    app.app.run(debug=False, host="0.0.0.0", port=5000)
