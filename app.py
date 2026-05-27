import streamlit as st
st.set_page_config(page_title="PotholeAI", layout="wide", page_icon="🚧")

import cv2, numpy as np, time
from utils.detector import load_model, detect_potholes
from utils.db import save_detection, fetch_all_detections
import folium
from streamlit_folium import st_folium

st.markdown("""
<style>
body, .stApp { background:#0d1117; color:#e6edf3; }
.title { font-size:2rem; font-weight:800; letter-spacing:3px;
         background:linear-gradient(90deg,#f97316,#ef4444);
         -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.status-ok  { background:rgba(34,197,94,0.15); border:1px solid #22c55e;
              border-radius:8px; padding:0.8rem 1rem; color:#86efac;
              font-size:1.1rem; font-weight:600; text-align:center; }
.status-bad { background:rgba(239,68,68,0.15); border:1px solid #ef4444;
              border-radius:8px; padding:0.8rem 1rem; color:#fca5a5;
              font-size:1.1rem; font-weight:600; text-align:center; }
</style>
""", unsafe_allow_html=True)

# ── GPS via browser ───────────────────────────────────────────────────────────
# We use a query param trick to pass GPS from browser to Streamlit
from utils.gps import get_gps
gps_lat, gps_lng = get_gps()

st.markdown("""
<script>
navigator.geolocation.watchPosition(function(pos) {
    const lat = pos.coords.latitude.toFixed(6);
    const lng = pos.coords.longitude.toFixed(6);
    // Update URL params so Streamlit reads real GPS
    const url = new URL(window.parent.location.href);
    url.searchParams.set('lat', lat);
    url.searchParams.set('lng', lng);
    window.parent.history.replaceState({}, '', url);
}, function(err) {
    console.log('GPS unavailable:', err.message);
}, { enableHighAccuracy: true, maximumAge: 3000 });
</script>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🚧 POTHOLEAI — LIVE DETECTION</div>",
            unsafe_allow_html=True)
st.markdown(f"<div style='color:#6e7681;font-size:0.85rem;margin-bottom:1rem;'>"
            f"APSRTC Road Safety System — SRM University AP &nbsp;|&nbsp; "
            f"📍 {gps_lat:.5f}, {gps_lng:.5f}</div>",
            unsafe_allow_html=True)

model = load_model()

# ── Session state ─────────────────────────────────────────────────────────────
if "running"        not in st.session_state: st.session_state["running"] = False
if "last_saved"     not in st.session_state: st.session_state["last_saved"] = 0
if "total_detected" not in st.session_state: st.session_state["total_detected"] = 0

cam_col, map_col = st.columns([1, 1], gap="large")

with cam_col:
    st.markdown("#### 📷 Live Camera Detection")

    # Show current GPS
    st.info(f"📍 GPS: {gps_lat:.5f}, {gps_lng:.5f} "
            f"{'(Live)' if gps_lat != 16.3067 else '(Default — allow location in browser)'}")

    # Start / Stop
    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("▶ START", use_container_width=True, type="primary"):
            st.session_state["running"] = True
    with btn2:
        if st.button("⏹ STOP", use_container_width=True):
            st.session_state["running"] = False

    status_box = st.empty()
    frame_box  = st.empty()
    alert_box  = st.empty()
    count_box  = st.empty()

    if st.session_state["running"]:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("❌ Cannot open camera.")
            st.session_state["running"] = False
        else:
            status_box.markdown(
                "<div class='status-ok'>🟢 LIVE DETECTION RUNNING</div>",
                unsafe_allow_html=True)

            frame_count = 0
            while st.session_state["running"]:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1

                # Detect every 5th frame — reduces false saves
                if frame_count % 5 == 0:
                    annotated, detections = detect_potholes(
                        frame, model, conf=0.35)
                    annotated_rgb = cv2.cvtColor(
                        annotated, cv2.COLOR_BGR2RGB)
                    frame_box.image(annotated_rgb,
                                    use_container_width=True)

                    if detections:
                        best = max(d["confidence"] for d in detections)
                        alert_box.markdown(
                            f"<div class='status-bad'>"
                            f"🚨 POTHOLE DETECTED! {best:.0%} confidence"
                            f"</div>",
                            unsafe_allow_html=True)

                        # ── Save only once every 10 seconds ──────────────
                        # This prevents saving 100 times for same pothole
                        now = time.time()
                        if now - st.session_state["last_saved"] > 10:
                            best_det = max(detections,
                                           key=lambda d: d["confidence"])
                            sev = ("High"   if best_det["confidence"] >= 0.70
                                   else "Medium" if best_det["confidence"] >= 0.50
                                   else "Low")
                            save_detection(
                                lat=gps_lat,
                                lng=gps_lng,
                                confidence=best_det["confidence"],
                                severity=sev)
                            st.session_state["last_saved"] = now
                            st.session_state["total_detected"] += 1
                            count_box.success(
                                f"✅ Saved pothole #{st.session_state['total_detected']} "
                                f"at {gps_lat:.4f}, {gps_lng:.4f}")
                    else:
                        alert_box.markdown(
                            "<div class='status-ok'>✅ Road Clear</div>",
                            unsafe_allow_html=True)

                time.sleep(0.05)
            cap.release()
    else:
        status_box.markdown(
            "<div class='status-ok'>📷 Press START to begin</div>",
            unsafe_allow_html=True)

with map_col:
    st.markdown("#### 🗺️ Live Pothole Map")

    # Auto refresh every 10 seconds
    refresh = st.empty()
    potholes = fetch_all_detections()

    center = [gps_lat, gps_lng]
    m = folium.Map(location=center, zoom_start=15,
                   tiles="Esri.WorldImagery", attr="Esri")

    # Current location marker
    folium.Marker(
        location=center,
        tooltip="📍 You are here",
        icon=folium.Icon(color="blue", icon="bus", prefix="fa")
    ).add_to(m)

    COLORS = {"High": "#ef4444", "Medium": "#f97316", "Low": "#eab308"}
    for p in potholes:
        color = COLORS.get(p.get("severity", "Medium"), "#f97316")
        folium.CircleMarker(
            location=[p["lat"], p["lng"]],
            radius=10, color=color, fill=True,
            fill_color=color, fill_opacity=0.85,
            tooltip=f"{p.get('severity','?')} — {p['confidence']:.0%}",
            popup=folium.Popup(
                f"<b>{p.get('severity','?')} Risk</b><br>"
                f"Confidence: {p['confidence']:.0%}<br>"
                f"{p['lat']:.5f}, {p['lng']:.5f}",
                max_width=200)
        ).add_to(m)

    st_folium(m, width=None, height=500, returned_objects=[])

    total = len(potholes)
    high  = sum(1 for p in potholes if p.get("severity") == "High")
    med   = sum(1 for p in potholes if p.get("severity") == "Medium")
    low   = sum(1 for p in potholes if p.get("severity") == "Low")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", total)
    c2.metric("🔴 High",   high)
    c3.metric("🟠 Medium", med)
    c4.metric("🟡 Low",    low)

    if st.button("🔄 Refresh Map"):
        st.rerun()

    # Auto refresh every 10 seconds
    time.sleep(10)
    st.rerun()
