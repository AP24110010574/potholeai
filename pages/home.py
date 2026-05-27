import streamlit as st

def show():
    st.markdown("""
    <div class='brand-header'>POTHOLE AI</div>
    <div class='brand-sub'>Road Safety Detection System</div>
    """, unsafe_allow_html=True)

    # Hero stats row
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("🚧", "Detection Mode", "YOLOv8"),
        ("⚡", "Speed", "Real-Time"),
        ("🎯", "Accuracy", "~85%"),
        ("📱", "Platform", "Any Device"),
    ]
    for col, (icon, label, val) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size:1.8rem;'>{icon}</div>
                <div class='metric-value' style='font-size:1.3rem;'>{val}</div>
                <div class='metric-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Two-column layout: about + how to use
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("<div class='section-title'>About This System</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='color:#8b949e; line-height:1.8; font-size:0.92rem;'>
        <b style='color:#e6edf3;'>PotholeAI</b> is a real-time road safety application that uses
        deep learning to detect potholes from live camera feeds, uploaded images, and videos.<br><br>
        The system uses <b style='color:#f97316;'>YOLOv8</b> (You Only Look Once), one of the fastest
        and most accurate object detection models available today, capable of processing
        video at <b style='color:#f97316;'>30+ frames per second</b>.<br><br>
        Detected pothole locations are plotted on an interactive map, and all session data
        is shown on a live dashboard — giving both drivers and administrators actionable insights.
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("<div class='section-title'>How To Use</div>", unsafe_allow_html=True)
        steps = [
            ("📷", "Live Detection", "Open camera page, allow browser camera access, and start real-time detection."),
            ("🖼️", "Image & Video", "Upload any road photo or dashcam video for pothole analysis."),
            ("🗺️", "Pothole Map", "View all detected pothole locations plotted on an interactive map."),
            ("📊", "Dashboard", "Monitor detection stats, confidence trends, and session history."),
        ]
        for icon, title, desc in steps:
            st.markdown(f"""
            <div style='display:flex; gap:12px; margin-bottom:14px; align-items:flex-start;'>
                <div style='font-size:1.4rem; margin-top:2px;'>{icon}</div>
                <div>
                    <div style='color:#e6edf3; font-weight:600; font-family:Rajdhani,sans-serif;
                                font-size:1rem; letter-spacing:1px;'>{title}</div>
                    <div style='color:#6e7681; font-size:0.83rem; margin-top:2px;'>{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Technology Stack</div>", unsafe_allow_html=True)

    tech_cols = st.columns(5)
    techs = [
        ("🧠", "YOLOv8", "Object Detection"),
        ("🐍", "Python", "Core Language"),
        ("📊", "Streamlit", "Web Framework"),
        ("👁️", "OpenCV", "Image Processing"),
        ("🗺️", "Folium", "Map Rendering"),
    ]
    for col, (icon, name, role) in zip(tech_cols, techs):
        with col:
            st.markdown(f"""
            <div style='background:#161b22; border:1px solid #30363d; border-radius:10px;
                        padding:1rem; text-align:center;'>
                <div style='font-size:1.5rem;'>{icon}</div>
                <div style='font-family:Rajdhani,sans-serif; color:#f97316;
                            font-weight:700; font-size:1rem; margin-top:4px;'>{name}</div>
                <div style='color:#6e7681; font-size:0.72rem; margin-top:2px;'>{role}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <br>
    <div style='background:#161b22; border:1px solid #30363d; border-radius:10px;
                padding:1rem 1.5rem; color:#8b949e; font-size:0.82rem; text-align:center;'>
        ⚡ Navigate using the sidebar to get started  •  
        Built for APSAC Internship  •  SRM University AP
    </div>
    """, unsafe_allow_html=True)