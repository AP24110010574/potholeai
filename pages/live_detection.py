"""
pages/live_detection.py
───────────────────────
Real-time pothole detection using the device camera.
Uses Streamlit's st.camera_input for broad browser compatibility.
"""

import streamlit as st
import numpy as np
import cv2
from PIL import Image
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.detector import load_model, detect_potholes
from utils.db import save_detection


def show():
    st.markdown("<div class='brand-header' style='font-size:2rem;'>LIVE DETECTION</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-sub'>Real-Time Camera Feed Analysis</div>", unsafe_allow_html=True)

    # ── Controls ──────────────────────────────────────────────────────────────
    ctrl_left, ctrl_right = st.columns([2, 1])
    with ctrl_left:
        confidence = st.slider(
            "Detection Confidence Threshold",
            min_value=0.20, max_value=0.90,
            value=0.35, step=0.05,
            help="Lower = more detections (may include false positives). Higher = fewer but more certain."
        )
    with ctrl_right:
        st.markdown("<br>", unsafe_allow_html=True)
        run_detection = st.toggle("Enable Detection", value=True)

    st.markdown("<hr style='border-color:#30363d;'>", unsafe_allow_html=True)

    # ── Load model ────────────────────────────────────────────────────────────
    model = load_model()
    if model is None:
        st.markdown("""
        <div class='alert-warn'>
            ⚠️ <b>Model not loaded.</b> Make sure you have run:<br>
            <code style='background:#0d1117; padding:2px 6px; border-radius:4px;'>
            pip install ultralytics</code><br>
            The model will auto-download (~6 MB) on first run.
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Camera input ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style='color:#8b949e; font-size:0.85rem; margin-bottom:0.5rem;'>
        📸 Click <b style='color:#f97316;'>Take Photo</b> to capture a frame for analysis.
        For continuous detection, keep clicking the button — or use the Video Upload page.
    </div>
    """, unsafe_allow_html=True)

    cam_col, result_col = st.columns([1, 1], gap="large")

    with cam_col:
        st.markdown("<div class='section-title'>Camera</div>", unsafe_allow_html=True)
        img_file = st.camera_input("", label_visibility="collapsed")

    with result_col:
        st.markdown("<div class='section-title'>Analysis Result</div>", unsafe_allow_html=True)

        if img_file is not None and run_detection:
            # Convert uploaded camera frame to numpy BGR
            pil_img = Image.open(img_file).convert("RGB")
            frame   = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

            # Run detection
            annotated, detections = detect_potholes(frame, model, conf=confidence)
            annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

            # Show result
            st.image(annotated_rgb, width="stretch")

            # Update session state
            if detections:
                st.session_state.total_detected += len(detections)
                high = sum(1 for d in detections if d["confidence"] >= 0.70)
                st.session_state.high_confidence += high
                st.session_state.session_detections.extend(detections)
                # Save to MongoDB with dummy GPS (Guntur centre)
                for d in detections:
                    save_detection(
                        lat=16.3067, lng=80.4365,
                        confidence=d['confidence'],
                        severity='High' if d['confidence']>=0.70 else 'Medium' if d['confidence']>=0.50 else 'Low'
                    )

            # Alert
            if detections:
                max_conf = max(d["confidence"] for d in detections)
                st.markdown(f"""
                <div class='alert-danger'>
                    🚨 <b>{len(detections)} POTHOLE(S) DETECTED!</b><br>
                    Highest confidence: <b>{max_conf:.0%}</b> — Slow down immediately!
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='alert-safe'>
                    ✅ <b>Road Clear</b> — No potholes detected in this frame.
                </div>
                """, unsafe_allow_html=True)

            # Detection details
            if detections:
                st.markdown("<div class='section-title' style='font-size:1rem;'>Detection Details</div>",
                            unsafe_allow_html=True)
                for i, d in enumerate(detections, 1):
                    conf = d["confidence"]
                    bar_color = "#ef4444" if conf >= 0.70 else "#f97316" if conf >= 0.50 else "#eab308"
                    bar_w = int(conf * 100)
                    st.markdown(f"""
                    <div style='background:#161b22; border:1px solid #30363d; border-radius:8px;
                                padding:0.8rem 1rem; margin-bottom:8px;'>
                        <div style='display:flex; justify-content:space-between; margin-bottom:6px;'>
                            <span style='color:#e6edf3; font-weight:600;'>Pothole #{i}</span>
                            <span style='color:{bar_color}; font-weight:700;'>{conf:.0%}</span>
                        </div>
                        <div style='background:#0d1117; border-radius:4px; height:6px;'>
                            <div style='background:{bar_color}; width:{bar_w}%;
                                        height:6px; border-radius:4px;'></div>
                        </div>
                        <div style='color:#6e7681; font-size:0.75rem; margin-top:4px;'>
                            Detected at {d["timestamp"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        elif img_file is None:
            st.markdown("""
            <div style='background:#161b22; border:1px dashed #30363d; border-radius:10px;
                        padding:3rem 2rem; text-align:center; color:#484f58;'>
                <div style='font-size:3rem; margin-bottom:1rem;'>📷</div>
                <div style='font-family:Rajdhani,sans-serif; font-size:1.1rem; letter-spacing:2px;'>
                    AWAITING CAMERA INPUT
                </div>
                <div style='font-size:0.8rem; margin-top:0.5rem;'>
                    Click "Take Photo" on the left to begin
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Tips ──────────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Detection Tips</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.columns(3)
    tips = [
        ("💡", "Lighting", "Good lighting improves accuracy. Avoid shooting directly into sunlight."),
        ("📐", "Angle", "Best results at 30–60° angle from the road surface (like a dashcam)."),
        ("🎯", "Distance", "Potholes should fill at least 10% of the frame for reliable detection."),
    ]
    for col, (icon, title, desc) in zip([t1, t2, t3], tips):
        with col:
            st.markdown(f"""
            <div style='background:#161b22; border:1px solid #30363d; border-radius:10px; padding:1rem;'>
                <div style='font-size:1.4rem;'>{icon}</div>
                <div style='color:#f97316; font-family:Rajdhani,sans-serif;
                            font-weight:600; margin:4px 0;'>{title}</div>
                <div style='color:#6e7681; font-size:0.82rem;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)