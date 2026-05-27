"""
pages/dashboard.py
──────────────────
Session analytics dashboard.
"""

import streamlit as st
import random
from datetime import datetime, timedelta


def show():
    st.markdown("<div class='brand-header' style='font-size:2rem;'>DASHBOARD</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-sub'>Session Analytics & Insights</div>", unsafe_allow_html=True)

    detections = st.session_state.get("session_detections", [])
    total      = st.session_state.get("total_detected", 0)
    high_conf  = st.session_state.get("high_confidence", 0)

    # ── Top KPI row ───────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    avg_conf = (
        sum(d["confidence"] for d in detections) / len(detections)
        if detections else 0
    )
    with k1: st.metric("Total Detected",   total)
    with k2: st.metric("High Confidence",  high_conf, help="Detections ≥ 70% confidence")
    with k3: st.metric("Avg Confidence",   f"{avg_conf:.0%}" if detections else "—")
    with k4: st.metric("Session Alerts",   len(detections))

    st.markdown("<hr style='border-color:#30363d; margin:1.5rem 0;'>", unsafe_allow_html=True)

    if not detections:
        # Empty state — show demo charts
        st.markdown("""
        <div style='background:#161b22; border:1px dashed #30363d; border-radius:12px;
                    padding:2rem; text-align:center; color:#484f58; margin-bottom:1.5rem;'>
            <div style='font-size:2.5rem; margin-bottom:0.5rem;'>📊</div>
            <div style='font-family:Rajdhani,sans-serif; font-size:1.1rem; letter-spacing:2px;'>
                NO SESSION DATA YET
            </div>
            <div style='font-size:0.82rem; margin-top:0.5rem;'>
                Run detections on Live Detection or Image & Video pages to populate analytics.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section-title'>Sample Dashboard Preview</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='color:#6e7681; font-size:0.85rem; margin-bottom:1rem;'>
            Below is how your dashboard will look after running detections.
        </div>
        """, unsafe_allow_html=True)

        # Generate fake data for demo
        import random
        detections = [
            {"confidence": random.uniform(0.35, 0.98),
             "timestamp": (datetime.now() - timedelta(minutes=random.randint(0, 60))).strftime("%H:%M:%S"),
             "label": "Pothole"}
            for _ in range(12)
        ]

    # ── Confidence distribution (pure HTML bars) ──────────────────────────────
    col_chart, col_list = st.columns([1, 1], gap="large")

    with col_chart:
        st.markdown("<div class='section-title'>Confidence Distribution</div>", unsafe_allow_html=True)

        bins = {"< 40%": 0, "40–59%": 0, "60–79%": 0, "≥ 80%": 0}
        for d in detections:
            c = d["confidence"]
            if c < 0.40:   bins["< 40%"]  += 1
            elif c < 0.60: bins["40–59%"] += 1
            elif c < 0.80: bins["60–79%"] += 1
            else:           bins["≥ 80%"]  += 1

        max_val = max(bins.values()) or 1
        bar_colors = {"< 40%": "#eab308", "40–59%": "#f97316", "60–79%": "#ef4444", "≥ 80%": "#dc2626"}

        for label, count in bins.items():
            pct = int(count / max_val * 100)
            color = bar_colors[label]
            st.markdown(f"""
            <div style='margin-bottom:14px;'>
                <div style='display:flex; justify-content:space-between;
                            color:#8b949e; font-size:0.82rem; margin-bottom:4px;'>
                    <span>{label}</span>
                    <span style='color:#e6edf3;'>{count}</span>
                </div>
                <div style='background:#161b22; border-radius:4px; height:10px;'>
                    <div style='background:{color}; width:{pct}%; height:10px;
                                border-radius:4px; transition:width 0.5s;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Severity breakdown
        st.markdown("<div class='section-title' style='margin-top:1.5rem;'>Severity Breakdown</div>",
                    unsafe_allow_html=True)
        high   = sum(1 for d in detections if d["confidence"] >= 0.70)
        medium = sum(1 for d in detections if 0.50 <= d["confidence"] < 0.70)
        low    = sum(1 for d in detections if d["confidence"] < 0.50)
        total_d = len(detections) or 1

        for label, val, color in [("HIGH", high, "#ef4444"), ("MEDIUM", medium, "#f97316"), ("LOW", low, "#eab308")]:
            pct_sev = int(val / total_d * 100)
            st.markdown(f"""
            <div style='background:#161b22; border:1px solid #30363d; border-radius:8px;
                        padding:0.7rem 1rem; margin-bottom:8px;
                        display:flex; align-items:center; gap:12px;'>
                <div style='width:10px; height:10px; border-radius:50%;
                            background:{color}; flex-shrink:0;'></div>
                <div style='flex:1; color:#8b949e; font-size:0.82rem;'>{label}</div>
                <div style='color:{color}; font-weight:700; font-size:1rem;'>{val}</div>
                <div style='color:#484f58; font-size:0.78rem;'>({pct_sev}%)</div>
            </div>
            """, unsafe_allow_html=True)

    with col_list:
        st.markdown("<div class='section-title'>Recent Detections</div>", unsafe_allow_html=True)

        sorted_dets = sorted(detections, key=lambda x: x["timestamp"], reverse=True)[:15]
        if not sorted_dets:
            st.markdown("<div style='color:#484f58;'>No detections yet.</div>", unsafe_allow_html=True)
        else:
            for i, d in enumerate(sorted_dets, 1):
                conf  = d["confidence"]
                color = "#ef4444" if conf >= 0.70 else "#f97316" if conf >= 0.50 else "#eab308"
                severity = "HIGH" if conf >= 0.70 else "MED" if conf >= 0.50 else "LOW"
                bar_w = int(conf * 100)
                st.markdown(f"""
                <div style='background:#161b22; border:1px solid #30363d; border-radius:8px;
                            padding:0.6rem 1rem; margin-bottom:6px;'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <span style='color:#e6edf3; font-size:0.85rem;'>Pothole #{i}</span>
                        <span style='color:{color}; font-size:0.75rem; font-weight:700;
                                    background:rgba(0,0,0,0.3); padding:2px 8px;
                                    border-radius:4px;'>{severity}</span>
                        <span style='color:{color}; font-weight:700;'>{conf:.0%}</span>
                    </div>
                    <div style='background:#0d1117; border-radius:3px; height:4px; margin-top:6px;'>
                        <div style='background:{color}; width:{bar_w}%; height:4px; border-radius:3px;'></div>
                    </div>
                    <div style='color:#484f58; font-size:0.72rem; margin-top:4px;'>
                        🕐 {d["timestamp"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Clear session button ───────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([3, 1, 3])
    with btn_col:
        if st.button("🗑  Clear Session Data"):
            st.session_state.total_detected = 0
            st.session_state.session_detections = []
            st.session_state.high_confidence = 0
            st.rerun()

    # ── Model info ────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Model Information</div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    infos = [
        ("Model",      "YOLOv8 Nano"),
        ("Framework",  "Ultralytics"),
        ("Input Size", "640 × 640"),
        ("Speed",      "~30 FPS"),
    ]
    for col, (k, v) in zip([m1, m2, m3, m4], infos):
        with col:
            st.markdown(f"""
            <div style='background:#161b22; border:1px solid #30363d; border-radius:10px;
                        padding:0.8rem 1rem; text-align:center;'>
                <div style='color:#6e7681; font-size:0.72rem; text-transform:uppercase;
                            letter-spacing:2px;'>{k}</div>
                <div style='color:#f97316; font-family:Rajdhani,sans-serif;
                            font-size:1.1rem; font-weight:700; margin-top:4px;'>{v}</div>
            </div>
            """, unsafe_allow_html=True)