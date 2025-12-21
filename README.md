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
- Face recognition happens client-side (face-api.js), then the server verifies embeddings safely

---

## How Face ID works (high-level)
1) Browser loads face-api.js models from `static/models/`
2) Browser captures a face embedding (vector)
3) Browser calls backend endpoints (Flask) to:
   - **enroll** (store a profile / samples)
   - **verify** (compare embedding to stored profile using thresholds)

---

## Project structure
- `app.py` – Flask app + routes (register/login/Face ID pages + task endpoints)
- `faceid/` – Face ID logic (enroll/verify, math, storage, profile stats)
- `templates/` – HTML pages (Bootstrap)
- `static/` – JS + face-api.js models
- `tests/` – pytest unit tests (happy paths, edge cases, error states)

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
pip install pytest
