"""
pages/image_video.py
────────────────────
Upload an image or video file for pothole detection.
"""

import streamlit as st
import numpy as np
import cv2
from PIL import Image
import tempfile, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.detector import load_model, detect_potholes


def show():
    st.markdown("<div class='brand-header' style='font-size:2rem;'>IMAGE & VIDEO</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-sub'>Upload & Analyse Road Media</div>", unsafe_allow_html=True)

    model = load_model()
    if model is None:
        st.markdown("<div class='alert-warn'>⚠️ Model not loaded. Run <code>pip install ultralytics</code>.</div>",
                    unsafe_allow_html=True)
        return

    tab_img, tab_vid = st.tabs(["🖼️  IMAGE ANALYSIS", "🎬  VIDEO ANALYSIS"])

    # ──────────────────────────────────────────────────────────────────────────
    # IMAGE TAB
    # ──────────────────────────────────────────────────────────────────────────
    with tab_img:
        st.markdown("<br>", unsafe_allow_html=True)
        conf = st.slider("Confidence Threshold", 0.20, 0.90, 0.35, 0.05, key="img_conf")

        uploaded = st.file_uploader(
            "Drop a road image here",
            type=["jpg", "jpeg", "png", "bmp", "webp"],
            help="Supported: JPG, PNG, BMP, WEBP"
        )

        if uploaded:
            pil_img = Image.open(uploaded).convert("RGB")
            frame   = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

            col_orig, col_result = st.columns(2, gap="large")
            with col_orig:
                st.markdown("<div class='section-title'>Original</div>", unsafe_allow_html=True)
                st.image(pil_img, width="stretch")

            with col_result:
                st.markdown("<div class='section-title'>Detection Result</div>", unsafe_allow_html=True)
                with st.spinner("Analysing…"):
                    annotated, detections = detect_potholes(frame, model, conf=conf)
                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                st.image(annotated_rgb, width="stretch")

            # Update session
            if detections:
                st.session_state.total_detected += len(detections)
                st.session_state.high_confidence += sum(1 for d in detections if d["confidence"] >= 0.70)
                st.session_state.session_detections.extend(detections)

            # Summary
            st.markdown("<div class='section-title'>Analysis Summary</div>", unsafe_allow_html=True)
            s1, s2, s3, s4 = st.columns(4)
            max_conf = max((d["confidence"] for d in detections), default=0)
            avg_conf = (sum(d["confidence"] for d in detections) / len(detections)) if detections else 0
            h, w = frame.shape[:2]

            with s1: st.metric("Potholes Found", len(detections))
            with s2: st.metric("Max Confidence", f"{max_conf:.0%}" if detections else "—")
            with s3: st.metric("Avg Confidence", f"{avg_conf:.0%}" if detections else "—")
            with s4: st.metric("Image Size", f"{w}×{h}")

            if detections:
                st.markdown(f"<div class='alert-danger'>🚨 <b>{len(detections)} pothole(s) detected</b> in this image!</div>",
                            unsafe_allow_html=True)
            else:
                st.markdown("<div class='alert-safe'>✅ No potholes detected — road appears clear.</div>",
                            unsafe_allow_html=True)

            # Detailed table
            if detections:
                st.markdown("<div class='section-title'>Bounding Box Details</div>", unsafe_allow_html=True)
                for i, d in enumerate(detections, 1):
                    x1, y1, x2, y2 = d["bbox"]
                    w_box = x2 - x1; h_box = y2 - y1
                    conf_pct = d["confidence"]
                    bar_color = "#ef4444" if conf_pct >= 0.70 else "#f97316" if conf_pct >= 0.50 else "#eab308"
                    st.markdown(f"""
                    <div style='background:#161b22; border:1px solid #30363d; border-radius:8px;
                                padding:0.8rem 1.2rem; margin-bottom:8px; display:flex;
                                justify-content:space-between; align-items:center;'>
                        <span style='color:#e6edf3; font-weight:600;'>Pothole #{i}</span>
                        <span style='color:#6e7681; font-size:0.82rem;'>
                            Position: ({x1}, {y1}) &nbsp;|&nbsp; Size: {w_box}×{h_box}px
                        </span>
                        <span style='color:{bar_color}; font-weight:700; font-size:1.1rem;'>
                            {conf_pct:.0%}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────────
    # VIDEO TAB
    # ──────────────────────────────────────────────────────────────────────────
    with tab_vid:
        st.markdown("<br>", unsafe_allow_html=True)
        conf_v = st.slider("Confidence Threshold", 0.20, 0.90, 0.35, 0.05, key="vid_conf")
        max_frames = st.slider("Max frames to process", 30, 300, 100, 10,
                               help="More frames = longer processing time.")

        video_file = st.file_uploader(
            "Drop a dashcam video here",
            type=["mp4", "avi", "mov", "mkv"],
            help="Tip: shorter clips (< 30 sec) process faster."
        )

        if video_file:
            # Save to temp file so OpenCV can read it
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(video_file.read())
                tmp_path = tmp.name

            cap = cv2.VideoCapture(tmp_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps          = cap.get(cv2.CAP_PROP_FPS) or 25

            st.markdown(f"""
            <div style='color:#8b949e; font-size:0.85rem; margin-bottom:1rem;'>
                📹 Video info: <b style='color:#e6edf3;'>{total_frames} frames</b> at
                <b style='color:#e6edf3;'>{fps:.0f} FPS</b> — processing
                <b style='color:#f97316;'>{min(max_frames, total_frames)} frames</b>
            </div>
            """, unsafe_allow_html=True)

            progress_bar = st.progress(0, text="Processing video…")
            status_text  = st.empty()
            preview_slot = st.empty()
            summary_slot = st.empty()

            all_detections = []
            frame_idx = 0
            pothole_frames = 0

            while cap.isOpened() and frame_idx < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                annotated, dets = detect_potholes(frame, model, conf=conf_v)
                all_detections.extend(dets)
                if dets:
                    pothole_frames += 1

                # Show every 5th frame as preview
                if frame_idx % 5 == 0:
                    rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                    preview_slot.image(rgb, caption=f"Frame {frame_idx}", width="stretch")

                frame_idx += 1
                pct = int((frame_idx / min(max_frames, total_frames)) * 100)
                progress_bar.progress(pct, text=f"Processing frame {frame_idx}/{min(max_frames, total_frames)}…")
                status_text.markdown(
                    f"<span style='color:#f97316;'>Potholes found so far: {len(all_detections)}</span>",
                    unsafe_allow_html=True
                )

            cap.release()
            os.unlink(tmp_path)
            progress_bar.progress(100, text="✅ Processing complete!")

            # Update session
            if all_detections:
                st.session_state.total_detected += len(all_detections)
                st.session_state.high_confidence += sum(1 for d in all_detections if d["confidence"] >= 0.70)
                st.session_state.session_detections.extend(all_detections)

            # Final summary
            st.markdown("<div class='section-title'>Video Analysis Summary</div>", unsafe_allow_html=True)
            v1, v2, v3, v4 = st.columns(4)
            avg_c = (sum(d["confidence"] for d in all_detections) / len(all_detections)) if all_detections else 0
            with v1: st.metric("Frames Processed", frame_idx)
            with v2: st.metric("Pothole Frames",   pothole_frames)
            with v3: st.metric("Total Detections", len(all_detections))
            with v4: st.metric("Avg Confidence",   f"{avg_c:.0%}" if all_detections else "—")

            if all_detections:
                pct_danger = pothole_frames / frame_idx * 100 if frame_idx else 0
                st.markdown(f"""
                <div class='alert-danger'>
                    🚨 <b>{len(all_detections)} potholes detected across {pothole_frames} frames
                    ({pct_danger:.1f}% of video).</b>
                    This road section has significant pothole risk!
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<div class='alert-safe'>✅ No potholes detected in the video.</div>",
                            unsafe_allow_html=True)