# FaceRecognitionPython (Flask + face-api.js)

Password + Face ID login in the browser (using **face-api.js**) with a **Flask** backend.  
Users register, capture a face frame, and then log in by face. A scheduled cleanup deletes accounts and label images older than **24 hours**.

---

## Features
- Browser-side detection & recognition (face-api.js: Tiny/SSD + 68 landmarks + recognition)
- Flask + SQLAlchemy (SQLite locally, Postgres in production)
- Stores label images under `static/labels/<username>/`
- **Hourly auto-cleanup** endpoint removes users older than 24h and deletes their label folders
- Ready for **Render** deployment (HTTPS camera access)

---

## Quick Start (local, Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 and then:

1) **Register a user**  
2) **Setup Face ID** (allow camera, click *Capture & Save*)  
3) **Try Face Login**

> Put the face-api model files in `static/models/` (already included).

---

## Environment Variables
- `SECRET_KEY` — random string (Flask sessions)
- `DATABASE_URL` — optional; e.g. Postgres on Render. Defaults to local SQLite.
- `TASK_TOKEN` — shared secret to authorize the cleanup endpoint
- `ACCOUNT_TTL_HOURS` — optional (default **24**)

---

## Cleanup Task (deletes old accounts + labels)
**Endpoint:** `POST /tasks/cleanup` with header `X-Task-Token: <TASK_TOKEN>`  
Deletes users with `created_at < now() - ACCOUNT_TTL_HOURS` and removes `static/labels/<username>/`.

Example:

```bash
curl -fsS -X POST -H "X-Task-Token: $TASK_TOKEN" "https://<your-app-url>/tasks/cleanup"
```

---

## Render Deployment

- Add `gunicorn` to `requirements.txt` (already included) and keep `render.yaml` in the repo.
- Push this repo to GitHub.
- On **Render**:
  1. **New → Blueprint** → pick this repo → **Apply**
  2. After deploy, set environment variables:
     - On the **web service**: `TASK_TOKEN` (and optionally `DATABASE_URL`, `ACCOUNT_TTL_HOURS`, `SECRET_KEY`)
     - On the **cron service**: set `TASK_TOKEN` and `APP_URL` (your web URL)

The cron runs hourly:

```bash
curl -fsS -X POST -H "X-Task-Token: $TASK_TOKEN" "$APP_URL/tasks/cleanup"
```

---

## Endpoints
- `GET /` — home
- `POST /register` — create account
- `POST /login` — password login
- `GET/POST /setupfaceid` — capture face (saves PNG to labels)
- `GET/POST /face-login` — camera login (client matches, server creates session)
- `GET /api/labels` — list users who have a saved label image
- `POST /tasks/cleanup` — hourly cleanup (authorized by `TASK_TOKEN`)

---

## Folder Structure

```
app.py
render.yaml
requirements.txt
static/
  css/style.css
  models/                  # face-api models (json + shards)
  labels/<username>/*.png  # saved captures
templates/
  base.html
  index.html
  login.html
  register.html
  setupfaceid.html
  face_login.html
```

---

## Notes
- Browsers require **HTTPS** for camera (`getUserMedia()`), except on **localhost**. Render gives HTTPS by default.
- Don’t commit real user images. `static/labels/` is ephemeral on production and cleaned by cron.

**License:** MIT

---