import pytest
from flask import Flask


@pytest.fixture()
def store_dir(tmp_path):
    return tmp_path / "face_store"


@pytest.fixture()
def make_app(store_dir):
    """
    Creates a minimal Flask app only for testing the FaceID blueprint.

    Assumes you will implement:
      from faceid.api import create_faceid_blueprint
    """
    def _make():
        from faceid.api import create_faceid_blueprint  # to be implemented

        app = Flask(__name__)
        app.config["TESTING"] = True
        app.config["FACEID_STORE_DIR"] = str(store_dir)
        app.register_blueprint(create_faceid_blueprint(url_prefix="/api/faceid"))
        return app

    return _make


@pytest.fixture()
def client(make_app):
    app = make_app()
    return app.test_client()
