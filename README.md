# 🧠 Face Recognition (Flask + face-api.js)

A Flask-based **Face Recognition Web App** that lets users log in using **password** or **Face ID** directly in the browser.

Built with:
- **Flask** (Python backend)
- **face-api.js** (browser-side face recognition)
- **SQLite / Render Postgres**
- **Bootstrap + CSS frontend**
- **GitHub Actions** for automatic cleanup

---

## 🚀 Features

✅ Register & log in normally  
✅ Set up Face ID (stores 1 face image per user)  
✅ Face-based login directly in browser  
✅ Secure password hashing  
✅ Automatic cleanup (old users + face data deleted after 24h)  
✅ Deployable on [Render.com](https://facerecog-web.onrender.com) for free  

---

## 🗂️ Project Structure

```
facerecog_flask/
├── app.py                # Flask backend
├── requirements.txt      # Dependencies
├── render.yaml           # Render deploy config
├── static/
│   ├── css/style.css
│   ├── models/           # face-api.js pre-trained models
│   └── labels/           # user face images
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── face_login.html
    └── setupfaceid.html
```

---

## 🧑‍💻 Local Setup

```bash
git clone https://github.com/RealTimGFM/FaceRecognitionPython.git
cd FaceRecognitionPython
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000

---


## 📸 Notes
- Face recognition runs in-browser using **face-api.js**, so no GPU or cloud compute required.
- User images are stored under `static/labels/` and removed automatically.

---

## 🏷️ License
MIT License © 2025 [RealTimGFM](https://github.com/RealTimGFM)
