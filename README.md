# Face Recognition (Flask + face-api.js)

[![CI](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/ci.yml)
[![CodeQL](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/codeql.yml)
[![Dependency Review](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/dependency-review.yml)
[![Deploy to Render](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/deploy-render.yml/badge.svg?branch=main)](https://github.com/RealTimGFM/FaceRecognitionPython/actions/workflows/deploy-render.yml)
[![License](https://img.shields.io/github/license/RealTimGFM/FaceRecognitionPython)](./LICENSE)

A Flask-based Face Recognition Web App that lets users log in using either **password** or **Face ID** directly in the browser (client-side face recognition with **face-api.js**).

## Live Demo
- https://facerecog-web.onrender.com

---

## Features
- Register + login with username/password
- Face ID setup (stores **one face image per user**)
- Face-based login in the browser (via webcam)
- Secure password hashing
- Automatic cleanup (old users + face data deleted after ~24h)
- Free deployment-friendly (Render web service + Render Postgres or SQLite)

---

## Tech Stack
- Backend: Flask (Python)
- Frontend: Bootstrap + custom CSS
- Face recognition: face-api.js (browser-side)
- Database: SQLite (local) / Render Postgres (hosted)
- DevOps: GitHub Actions (CI + security checks + optional Render deploy hook)

---

## Project Structure
```
.
├── app.py
├── requirements.txt
├── render.yaml
├── static/
│   ├── css/
│   ├── models/        # face-api.js models
│   └── labels/        # stored face images (auto-cleaned)
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── face_login.html
    └── setupfaceid.html
```

---

## Local Setup

### 1) Clone + install
```bash
git clone https://github.com/RealTimGFM/FaceRecognitionPython.git
cd FaceRecognitionPython
python -m venv .venv
```

### 2) Activate venv

**Windows (PowerShell)**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

### 3) Run the app
```bash
pip install -r requirements.txt
python app.py
```

Open:
- http://127.0.0.1:5000

---

## Face ID Setup (How to Use)
1. Register an account
2. Go to **Setup Face ID**
3. Allow webcam permissions
4. Capture a clear face image (good lighting, front-facing)
5. Use **Face Login** to log in using the webcam

Notes:
- Face matching runs in the browser using face-api.js models.
- Face images are stored under `static/labels/` and removed automatically by cleanup logic.

---

## DevOps / Automation (What’s included)
- **CI**: install + sanity checks + run pytest (only if tests exist)
- **Dependency Review**: flags risky dependency changes in PRs
- **CodeQL**: security scanning for Python
- **Deploy to Render (optional)**: triggers deploy via Render Deploy Hook secret

---

## Deployment (Render)
This repo includes a `render.yaml` to support Render deployments.

If you use the GitHub Actions deploy hook:
- Create a Render Deploy Hook in your Render service settings
- Add it as a GitHub secret:
  - `RENDER_DEPLOY_HOOK_URL`

---

## License
MIT © 2025 RealTimGFM
