"""
pages/pothole_map.py  — real MongoDB data + demo fallback
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.db import fetch_all_detections

DEMO_POTHOLES = [
    {"lat": 16.5193, "lng": 80.5169, "confidence": 0.91, "severity": "High"},
    {"lat": 16.5210, "lng": 80.5185, "confidence": 0.78, "severity": "Medium"},
    {"lat": 16.5175, "lng": 80.5150, "confidence": 0.85, "severity": "High"},
    {"lat": 16.5230, "lng": 80.5200, "confidence": 0.62, "severity": "Low"},
    {"lat": 16.5160, "lng": 80.5220, "confidence": 0.88, "severity": "High"},
]
SEVERITY_COLOR = {"High": "#ef4444", "Medium": "#f97316", "Low": "#eab308"}

def _severity(conf):
    if conf >= 0.70: return "High"
    if conf >= 0.50: return "Medium"
    return "Low"

def _make_map(potholes):
    center = [16.5193, 80.5169]
    if potholes:
        center = [
            sum(p["lat"] for p in potholes) / len(potholes),
            sum(p["lng"] for p in potholes) / len(potholes),
        ]
    m = folium.Map(location=center, zoom_start=14, tiles="CartoDB dark_matter")
    for p in potholes:
        sev   = p.get("severity") or _severity(p["confidence"])
        color = SEVERITY_COLOR.get(sev, "#f97316")
        ts    = str(p.get("timestamp", ""))[:19]
        folium.CircleMarker(
            location=[p["lat"], p["lng"]],
            radius=10 if sev == "High" else 7 if sev == "Medium" else 5,
            color=color, fill=True, fill_color=color, fill_opacity=0.8,
            popup=folium.Popup(
                f"<b style='color:{color};'>⚠ {sev}</b><br>"
                f"Confidence: {p['confidence']:.0%}<br>"
                f"Time: {ts}<br>"
                f"Coords: {p['lat']:.4f}, {p['lng']:.4f}",
                max_width=220
            ),
            tooltip=f"{sev} — {p['confidence']:.0%}"
        ).add_to(m)
    legend = """
    <div style='position:fixed;bottom:30px;left:30px;z-index:1000;
                background:rgba(13,17,23,0.9);border:1px solid #30363d;
                border-radius:8px;padding:12px 16px;font-family:sans-serif;'>
        <b style='color:#e6edf3;font-size:13px;'>SEVERITY</b><br>
        <span style='color:#ef4444;'>●</span> <span style='color:#ccc;font-size:12px;'>High</span><br>
        <span style='color:#f97316;'>●</span> <span style='color:#ccc;font-size:12px;'>Medium</span><br>
        <span style='color:#eab308;'>●</span> <span style='color:#ccc;font-size:12px;'>Low</span>
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))
    return m

def show():
    st.markdown("<div class='brand-header' style='font-size:2rem;'>POTHOLE MAP</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-sub'>Live Location Intelligence — Andhra Pradesh</div>", unsafe_allow_html=True)

    ctrl1, ctrl2, ctrl3 = st.columns(3)
    with ctrl1:
        use_live = st.toggle("Live MongoDB Data", value=True)
    with ctrl2:
        severity_filter = st.multiselect("Filter Severity",
            ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
    with ctrl3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh"): st.rerun()

    st.markdown("<hr style='border-color:#30363d;'>", unsafe_allow_html=True)

    if use_live:
        raw = fetch_all_detections()
        potholes = raw if raw else DEMO_POTHOLES
        source_label = f"🟢 Live — {len(raw)} real detections from MongoDB" if raw else "🟡 No live data yet — showing demo"
    else:
        potholes = DEMO_POTHOLES
        source_label = "⚪ Demo mode"

    st.markdown(f"<div style='color:#6e7681;font-size:0.82rem;margin-bottom:1rem;'>{source_label}</div>",
                unsafe_allow_html=True)

    potholes = [p for p in potholes
                if (_severity(p["confidence"]) if not p.get("severity") else p["severity"]) in severity_filter]

    high   = sum(1 for p in potholes if (p.get("severity") or _severity(p["confidence"])) == "High")
    medium = sum(1 for p in potholes if (p.get("severity") or _severity(p["confidence"])) == "Medium")
    low    = sum(1 for p in potholes if (p.get("severity") or _severity(p["confidence"])) == "Low")

    s1, s2, s3, s4 = st.columns(4)
    with s1: st.metric("Total Mapped", len(potholes))
    with s2: st.metric("🔴 High",   high)
    with s3: st.metric("🟠 Medium", medium)
    with s4: st.metric("🟡 Low",    low)

    st.markdown("<br>", unsafe_allow_html=True)
    map_col, info_col = st.columns([2, 1], gap="large")

    with map_col:
        st.markdown("<div class='section-title'>Live Pothole Map</div>", unsafe_allow_html=True)
        st_folium(_make_map(potholes), width=None, height=500, returned_objects=[])

    with info_col:
        st.markdown("<div class='section-title'>Recent Potholes</div>", unsafe_allow_html=True)
        for i, p in enumerate(potholes[:10], 1):
            sev   = p.get("severity") or _severity(p["confidence"])
            color = SEVERITY_COLOR.get(sev, "#f97316")
            ts    = str(p.get("timestamp", ""))[:16]
            st.markdown(f"""
            <div style='background:#161b22;border:1px solid #30363d;border-left:3px solid {color};
                        border-radius:8px;padding:0.7rem 1rem;margin-bottom:8px;'>
                <div style='display:flex;justify-content:space-between;'>
                    <span style='color:#e6edf3;font-size:0.85rem;font-weight:600;'>#{i} Pothole</span>
                    <span style='color:{color};font-weight:700;'>{p['confidence']:.0%}</span>
                </div>
                <div style='color:#6e7681;font-size:0.75rem;margin-top:3px;'>
                    {p['lat']:.4f}°N, {p['lng']:.4f}°E<br>
                    <span style='color:{color};'>{sev}</span>
                    {"&nbsp;|&nbsp;" + ts if ts else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)
