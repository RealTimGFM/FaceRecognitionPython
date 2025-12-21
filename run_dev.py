import os
from app import create_app

if __name__ == "__main__":
    # Local defaults
    os.environ.setdefault("FLASK_ENV", "development")
    os.environ.setdefault("FLASK_DEBUG", "1")

    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
