# FaceRecognitionPython (Flask + face-api.js)

Password + Face ID login in the browser (using **face-api.js**) with a **Flask** backend.  
Users register, capture a face frame, and then log in by face. A scheduled cleanup deletes accounts and label images older than **24 hours**.

## Features
- Browser-side detection & recognition (face-api.js: Tiny/SSD + 68 landmarks + recognition)
- Flask + SQLAlchemy (SQLite locally, Postgres in production)
- Stores label images under `static/labels/<username>/`
- **Hourly auto-cleanup** endpoint removes users older than 24h and deletes their label folders
- Ready for **Render** deployment (HTTPS camera access)

## Quick Start (local, Windows)
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
