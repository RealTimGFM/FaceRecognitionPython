# Face Recognition (Flask version)

This is a minimal Flask port of your PHP face-recognition app. It keeps the same logic:
- Password login + optional **Face ID** login
- Browser-side face matching via **face-api.js**
- Stores a single captured face image per user in `static/labels/<username>/1.png`
- Saves username/password hash and face image path in a SQL database

## Quick Start (Windows)

1) Create and activate a virtualenv
```
python -m venv .venv
.\.venv\Scripts\activate
```

2) Install dependencies
```
pip install -r requirements.txt
```

3) (Default) Use SQLite – no extra setup needed. A `app.db` file will be created automatically.

   **Optional (MySQL):** Set the `DATABASE_URL` env var before running:
   ```powershell
   set DATABASE_URL=mysql+pymysql://root:password@localhost/aureolin_test
   ```
   Or adjust to your own user/password/db.

4) Copy the `models` folder from your old PHP project into `static/models` here.
   It should contain files like `ssd_mobilenetv1_model-weights_manifest.json`, etc.

5) Run the app
```
python app.py
```
Visit: http://127.0.0.1:5000

## Pages
- `/register` — Create an account
- `/login` — Password login
- `/setupfaceid` — Capture a face image (needs camera access)
- `/face-login` — Face login (loads models from `/static/models` and compares against saved label images)
- `/logout` — Log out

> Note: Face matching happens in the browser via `face-api.js`, similar to your previous setup. The server trusts a positive match and logs the user in.
