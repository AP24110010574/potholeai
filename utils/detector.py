import cv2
import numpy as np
from datetime import datetime
import streamlit as st
import os

CONFIDENCE_THRESHOLD = 0.25
COLOR_HIGH   = (239, 68,  68)
COLOR_MEDIUM = (249, 115, 22)
COLOR_LOW    = (234, 179,  8)

@st.cache_resource(show_spinner="Loading AI model…")
def load_model():
    try:
        from ultralytics import YOLO
        # Try local model first
        model_paths = [
            "pothole_model.pt",
            "runs/detect/pothole_trained-2/weights/best.pt",
            "runs/detect/pothole_trained/weights/best.pt",
        ]
        for path in model_paths:
            if os.path.exists(path):
                print(f"Loading model from {path}")
                return YOLO(path)
        # Fallback to base YOLOv8
        print("No trained model found, using base YOLOv8n")
        return YOLO("yolov8n.pt")
    except Exception as e:
        st.error(f"Model load error: {e}")
        return None

def detect_potholes(frame: np.ndarray, model, conf: float = CONFIDENCE_THRESHOLD):
    if model is None:
        return frame, []
    results = model(frame, conf=conf, verbose=False)[0]
    detections = []
    for box in results.boxes:
        conf_score = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        if conf_score >= 0.70:
            color = COLOR_HIGH
        elif conf_score >= 0.50:
            color = COLOR_MEDIUM
        else:
            color = COLOR_LOW
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        tag = f"POTHOLE  {conf_score:.0%}"
        (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 8, y1), color, -1)
        cv2.putText(frame, tag, (x1 + 4, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        detections.append({
            "confidence": conf_score,
            "bbox": (x1, y1, x2, y2),
            "label": "Pothole",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        })
    _draw_hud(frame, len(detections))
    return frame, detections

def _draw_hud(frame: np.ndarray, count: int):
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 38), (13, 17, 23), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    status = f"POTHOLEAI  |  DETECTED: {count}"
    color  = (239, 68, 68) if count > 0 else (34, 197, 94)
    cv2.putText(frame, status, (10, 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)
    ts = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    cv2.putText(frame, ts, (w - 220, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (110, 118, 129), 1)
