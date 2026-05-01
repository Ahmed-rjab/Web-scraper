"""Start the Flask dashboard for local demos without the debug reloader."""
import app
import database


if __name__ == "__main__":
    database.init_database(app.DATABASE_FILE)
    app.app.run(debug=False, host="0.0.0.0", port=5000)
