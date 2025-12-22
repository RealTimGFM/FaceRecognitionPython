from __future__ import annotations

import os
import shutil
import base64
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from faceid.api import create_faceid_blueprint
from faceid.store import FaceStore

from config import DevelopmentConfig, ProductionConfig

BASE_DIR = Path(__file__).resolve().parent

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    face_image = db.Column(db.String(255), nullable=True)  # preview image (optional)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


def _select_config():
    """
    Decide config based on environment.
    - Render sets ENV vars; we default to Production unless explicitly in dev.
    """
    env = os.environ.get("FLASK_ENV", "").lower()
    debug_flag = os.environ.get("FLASK_DEBUG", "").strip() in ("1", "true", "yes", "on")

    if env == "development" or debug_flag:
        return DevelopmentConfig
    return ProductionConfig

def _normalize_database_url(url: str) -> str:
    """
    Normalize DATABASE_URL for SQLAlchemy + psycopg v3.

    - Render often provides postgres://... (deprecated scheme)
    - SQLAlchemy defaults postgresql:// to psycopg2 unless driver specified
    - We force psycopg v3 by using postgresql+psycopg://
    """
    url = url.strip()

    # Render legacy scheme
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # Force psycopg v3 driver
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    return url

def create_app() -> Flask:
    app = Flask(__name__)
    cfg = _select_config()
    app.config.from_object(cfg)

    # ---- Database config ----
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        db_url = _normalize_database_url(db_url)
    else:
        db_url = f"sqlite:///{BASE_DIR / 'app.db'}"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url

    # ---- FaceID store dir ----
    store_dir = os.environ.get("FACEID_STORE_DIR")
    if not store_dir:
        store_dir = str(BASE_DIR / "instance" / "faceid_store")

    app.config["FACEID_STORE_DIR"] = store_dir

    # ---- Init extensions ----
    db.init_app(app)

    # ---- Register blueprint ----
    app.register_blueprint(create_faceid_blueprint(url_prefix="/api/faceid"))

    # ---- Create tables (simple init, safe for this project) ----
    with app.app_context():
        db.create_all()

    # ---------------- Routes ----------------

    def is_logged_in() -> bool:
        return bool(session.get("user_id"))
    @app.get("/healthz")
    def healthz():
        return {"ok": True}, 200

    @app.route("/")
    def index():
        user = None
        if is_logged_in():
            user = db.session.get(User, session["user_id"])
        return render_template("index.html", user=user)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            if not username or not password:
                flash("Username and password are required.", "error")
                return redirect(url_for("register"))

            if User.query.filter_by(username=username).first():
                flash("Username already exists.", "error")
                return redirect(url_for("register"))

            u = User(
                username=username,
                password_hash=generate_password_hash(password),
            )
            db.session.add(u)
            db.session.commit()

            flash("Account created. Please login.", "ok")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            user = User.query.filter_by(username=username).first()
            if not user or not check_password_hash(user.password_hash, password):
                flash("Invalid username or password.", "error")
                return redirect(url_for("login"))

            session["user_id"] = user.id
            flash("Logged in.", "ok")
            return redirect(url_for("index"))

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Logged out.", "ok")
        return redirect(url_for("index"))

    @app.route("/setupfaceid", methods=["GET", "POST"])
    def setupfaceid():
        if not is_logged_in():
            return redirect(url_for("login"))

        user = db.session.get(User, session["user_id"])

        if request.method == "POST":
            data = request.get_json(silent=True) or {}

            embeddings = data.get("embeddings")
            if not isinstance(embeddings, list) or len(embeddings) < 3:
                return jsonify({"ok": False, "error": "Need at least 3 face samples"}), 400

            store = FaceStore(app.config["FACEID_STORE_DIR"])
            try:
                store.enroll(user.username, embeddings=embeddings, min_samples=3)
            except Exception:
                return jsonify({"ok": False, "error": "Invalid face samples"}), 400

            img_data_url = data.get("image")
            if not img_data_url or not img_data_url.startswith("data:image/png;base64,"):
                return jsonify({"ok": False, "error": "Invalid image data"}), 400

            b64 = img_data_url.split(",", 1)[1]
            try:
                img_bytes = base64.b64decode(b64)
            except Exception:
                return jsonify({"ok": False, "error": "Invalid image data"}), 400

            user_dir = BASE_DIR / "static" / "labels" / user.username
            user_dir.mkdir(parents=True, exist_ok=True)
            out_path = user_dir / "1.png"
            with open(out_path, "wb") as f:
                f.write(img_bytes)

            rel_path = f"static/labels/{user.username}/1.png"
            user.face_image = rel_path
            db.session.commit()

            return jsonify({"ok": True, "path": "/" + rel_path.replace("\\", "/")})

        return render_template("setupfaceid.html", user=user)

    @app.route("/face-login")
    def face_login_page():
        return render_template("face_login.html")

    @app.route("/tasks/cleanup", methods=["POST"])
    def tasks_cleanup():
        token = request.headers.get("X-Task-Token")
        if token != os.environ.get("TASK_TOKEN"):
            abort(401)

        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        store = FaceStore(app.config["FACEID_STORE_DIR"])

        gone = []
        for u in User.query.filter(User.created_at < cutoff).all():
            d = BASE_DIR / "static" / "labels" / u.username
            try:
                shutil.rmtree(d)
            except FileNotFoundError:
                pass

            try:
                store.delete(u.username)
            except Exception:
                pass

            gone.append(u.username)
            db.session.delete(u)

        db.session.commit()

        try:
            store.prune_older_than(hours=24)
        except Exception:
            pass

        return jsonify({"ok": True, "deleted": gone})

    @app.route("/faceid/complete")
    def faceid_complete():
        username = session.get("faceid_user")
        if not username:
            return redirect(url_for("login"))

        user = User.query.filter_by(username=username).first()
        session.pop("faceid_user", None)

        if not user:
            flash("Face login failed.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        return redirect(url_for("index"))

    return app
