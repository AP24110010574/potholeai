# 🚧 PotholeAI — Road Safety Detection System
### APSAC Internship Project | SRM University AP

---

## 📋 What This App Does

PotholeAI is a professional web-based application that:
- **Detects potholes in real time** using your phone/laptop camera
- **Analyses uploaded images and videos** for potholes
- **Shows detected pothole locations** on an interactive map
- **Displays analytics** like confidence scores and detection history

Built with **Python + YOLOv8 + Streamlit** — works on any device with a browser.

---

## 🖥️ How To Run (Step by Step)

### Step 1 — Make sure Python is installed
Open Command Prompt / Terminal and type:
```
python --version
```
You need Python 3.9 or higher. Download from https://python.org if needed.

---

### Step 2 — Open the project folder
```
cd pothole_app
```

---

### Step 3 — Install all required libraries (do this only once)
```
pip install -r requirements.txt
```
This will install Streamlit, YOLOv8, OpenCV, and other libraries.
It may take 2-5 minutes. The YOLOv8 model (~6 MB) downloads automatically on first run.

---

### Step 4 — Run the app
```
streamlit run app.py
```

The app will open in your browser at: **http://localhost:8501**

To open on your phone (on the same WiFi):
- Note the **Network URL** shown in the terminal (e.g. http://192.168.1.5:8501)
- Open that URL on your phone browser

---

## 📁 Project Structure (explained simply)

```
pothole_app/
│
├── app.py                  ← MAIN file (start here — handles navigation & styling)
│
├── requirements.txt        ← List of libraries to install
│
├── pages/
│   ├── home.py             ← Home page (intro, tech stack)
│   ├── live_detection.py   ← Camera page (take photo → detect)
│   ├── image_video.py      ← Upload image or video → detect
│   ├── pothole_map.py      ← Interactive map of pothole locations
│   └── dashboard.py        ← Analytics & session stats
│
└── utils/
    └── detector.py         ← Core AI detection code (loads YOLOv8, runs inference)
```

---

## 🧠 How the Detection Works (explain to your sir)

1. A **camera frame / image** is captured
2. It is passed to **YOLOv8** (a deep learning model)
3. YOLOv8 splits the image into a grid and predicts bounding boxes + confidence scores
4. If confidence > threshold (default 35%), a **POTHOLE** label is drawn
5. Results are shown on screen and saved to session analytics

---

## 🎯 Using a Custom Pothole Model (Recommended for better accuracy)

The app works with a general YOLOv8 model by default.
For a pothole-specific model:

1. Go to https://universe.roboflow.com and search "pothole detection"
2. Download a YOLOv8 model (.pt file)
3. Place it in the `pothole_app/` folder and rename it to `pothole_model.pt`
4. The app automatically uses it on next launch

---

## 🔧 How To Make Changes

### Change detection confidence:
- In the app: use the **slider** on Live Detection or Image pages
- In code: edit `CONFIDENCE_THRESHOLD = 0.35` in `utils/detector.py`

### Add your own map locations:
- Edit `DEMO_POTHOLES` list in `pages/pothole_map.py`
- Each entry: `{"lat": ..., "lon": ..., "conf": ..., "severity": "High/Medium/Low", "road": "..."}`

### Change the app name/colours:
- App name: edit `page_title` in `app.py`
- Orange colour (#f97316) → search and replace in `app.py`

---

## ❓ Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| Camera not working | Allow camera access in browser pop-up |
| Model download stuck | Check internet connection |
| Port already in use | Run `streamlit run app.py --server.port 8502` |

---

## 📊 Technologies Used

| Library | Purpose |
|---------|---------|
| Streamlit | Web app framework (UI) |
| YOLOv8 (Ultralytics) | Pothole object detection |
| OpenCV | Image processing |
| Folium | Interactive maps |
| Pillow | Image handling |
| NumPy | Array operations |

---

*Built for APSAC Internship — SRM University Amaravathi, Andhra Pradesh*
