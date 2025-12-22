# Face Recognition Web App (Flask + face-api.js)

[![CI](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/ci.yml)
[![Deploy to Render](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/deploy-render.yml/badge.svg?branch=main)](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/deploy-render.yml)
[![CodeQL](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/codeql.yml)
[![Dependency Review](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/dependency-review.yml)
[![License](https://img.shields.io/github/license/RealTimGFM/FaceRecognitionPython)](LICENSE)
[![Live Demo](https://img.shields.io/website?url=https%3A%2F%2Ffacerecog-web.onrender.com&label=demo)](https://facerecog-web.onrender.com)

A Flask-based face recognition web app that supports **password login** and **Face ID login directly in the browser** using **face-api.js**.

## Live Demo
https://facerecog-web.onrender.com

---

## What this app does (simple)
- Users can **register + login with a password**
- Users can **enroll Face ID** (camera in the browser)
- Users can **login with Face ID** (camera in the browser)
- Face recognition happens **client-side** (face-api.js), then the server verifies embeddings

---

## How Face ID works (high-level)
1) Browser loads face-api.js models from `static/models/`
2) Browser captures a face embedding (vector)
3) Browser calls backend endpoints (Flask) to:
   - **enroll** (store a profile / samples)
   - **verify** (compare embedding to stored profile using thresholds)

---

## Project structure
- `app.py` – Flask app + routes (register/login/Face ID pages + cleanup task)
- `wsgi.py` – WSGI entrypoint for Gunicorn (`gunicorn wsgi:app`)
- `faceid/` – Face ID logic (enroll/verify, math, storage, profile stats)
- `templates/` – HTML pages (Bootstrap)
- `static/` – JS + face-api.js models
- `tests/` – pytest tests (happy paths + edge cases)

---

## Run locally

### 1) Create a venv + install dependencies
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Run the server
```bash
python -m flask --app app run --debug
# or (if you prefer):
python app.py
```

Open: http://127.0.0.1:5000

---

## Environment variables

### Required (production)
- `SECRET_KEY`  
  Flask session secret (set a strong random string)

### Optional
- `DATABASE_URL`  
  If not set, the app falls back to a local SQLite DB: `sqlite:///app.db`

  If you deploy to Render and attach a Postgres DB, Render will provide `DATABASE_URL` automatically.  
  For **SQLAlchemy + psycopg v3** compatibility, normalize the URL in `create_app()`:

  - `postgres://...` → `postgresql://...`
  - `postgresql://...` → `postgresql+psycopg://...`

- `FACEID_STORE_DIR` (recommended)
  Directory where FaceID profiles are stored (JSON).  
  Example for Render:
  - `/tmp/faceid_store` (ephemeral; resets on redeploy)

- `TASK_TOKEN` (optional)
  Protects the cleanup endpoint `POST /tasks/cleanup` via header `X-Task-Token`.

---

## Deploy to Render (quick checklist)
1) Render: create a **Web Service** from this repo
2) Build command: `pip install -r requirements.txt`
3) Start command: `gunicorn wsgi:app`
4) Attach a **Postgres** instance (optional, but recommended)  
   - If attached, Render will set `DATABASE_URL`
5) Set env vars:
   - `SECRET_KEY` (required)
   - `FACEID_STORE_DIR=/tmp/faceid_store` (recommended)
   - `TASK_TOKEN` (optional)
6) Health check path:
   - If you set it to `/healthz`, make sure you have a `/healthz` route in the app.

---

## CI / Security
This repo uses GitHub Actions:
- **CI** (`ci.yml`): ruff critical lint + pytest
- **Dependency Review** (`dependency-review.yml`): blocks vulnerable PR dependency changes
- **CodeQL** (`codeql.yml`): code scanning (security)

---

## Run tests
```bash
pytest -q
```

---

## Notes
- If you see Dependabot alerts, update `requirements.txt` and merge the fixes into **main** (alerts are evaluated on the default branch).
- If your PR is stuck on “Expected — waiting for status”, check your branch protection required check names match the actual check run names (see `troubleshooting_tips.md`).
