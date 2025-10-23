from __future__ import annotations
import os
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
import shutil
import base64
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# Database: default to SQLite; allow MySQL via DATABASE_URL
db_url = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR/'app.db'}")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    face_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())  # NEW

with app.app_context():
    db.create_all()

def is_logged_in() -> bool:
    return "user_id" in session

@app.route("/")
def index():
    if not is_logged_in():
        return redirect(url_for("login"))
    user = db.session.get(User, session["user_id"])
    return render_template("index.html", user=user)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        if not username or not password:
            flash("Username and password required.", "error")
            return redirect(url_for("register"))
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")
            return redirect(url_for("register"))
        u = User(username=username, password=generate_password_hash(password))
        db.session.add(u)
        db.session.commit()
        flash("Registered! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("index"))
        flash("Invalid credentials.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/setupfaceid", methods=["GET", "POST"])
def setupfaceid():
    if not is_logged_in():
        return redirect(url_for("login"))
    user = db.session.get(User, session["user_id"])
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        img_data_url = data.get("image")
        if not img_data_url or not img_data_url.startswith("data:image/png;base64,"):
            return jsonify({"ok": False, "error": "Invalid image data"}), 400

        # decode base64 image
        b64 = img_data_url.split(",", 1)[1]
        img_bytes = base64.b64decode(b64)

        # save under static/labels/<username>/1.png
        user_dir = BASE_DIR / "static" / "labels" / user.username
        user_dir.mkdir(parents=True, exist_ok=True)
        out_path = user_dir / "1.png"
        with open(out_path, "wb") as f:
            f.write(img_bytes)

        rel_path = f"static/labels/{user.username}/1.png"
        user.face_image = rel_path
        db.session.commit()
        return jsonify({"ok": True, "path": "/" + rel_path.replace('\\','/')})

    return render_template("setupfaceid.html", user=user)

@app.route("/face-login")
def face_login_page():
    return render_template("face_login.html")

@app.route("/login-face", methods=["POST"])
def login_face():
    # Called by browser after a positive face match (client-side).
    data = request.get_json(silent=True) or {}
    username = data.get("username","").strip()
    if not username:
        return jsonify({"ok": False, "error": "Missing username"}), 400
    user = User.query.filter_by(username=username).first()
    if not user or not user.face_image:
        return jsonify({"ok": False, "error": "User not found or no face set up"}), 404
    # Trust the front-end matcher (same as original PHP logic)
    session["user_id"] = user.id
    return jsonify({"ok": True})

@app.route("/api/labels")
def api_labels():
    # Return users that have a saved face image so the client can load them
    users = User.query.filter(User.face_image.isnot(None)).all()
    payload = [{"username": u.username, "image_url": "/" + u.face_image} for u in users if u.face_image]
    return jsonify(payload)
@app.route("/tasks/cleanup", methods=["POST"])
def tasks_cleanup():
    token = request.headers.get("X-Task-Token")
    if token != os.environ.get("TASK_TOKEN"):
        abort(401)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    gone = []
    for u in User.query.filter(User.created_at < cutoff).all():
        # delete label folder
        d = BASE_DIR / "static" / "labels" / u.username
        try: shutil.rmtree(d)
        except FileNotFoundError: pass

        gone.append(u.username)
        db.session.delete(u)

    db.session.commit()
    return jsonify({"ok": True, "deleted": gone})

if __name__ == "__main__":
    app.run(debug=True)
