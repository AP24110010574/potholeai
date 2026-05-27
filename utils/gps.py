import streamlit as st
from streamlit_js_eval import streamlit_js_eval

def get_gps():
    """Get real GPS from browser using HTTPS — works on Streamlit Cloud"""
    try:
        coords = streamlit_js_eval(
            js_expressions="""
            await new Promise((resolve) => {
                if (!navigator.geolocation) {
                    resolve(null);
                    return;
                }
                navigator.geolocation.getCurrentPosition(
                    pos => resolve({
                        lat: pos.coords.latitude,
                        lng: pos.coords.longitude,
                        accuracy: pos.coords.accuracy
                    }),
                    err => resolve(null),
                    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
                );
            })
            """,
            key="gps_location"
        )
        if coords and isinstance(coords, dict) and coords.get("lat"):
            lat = float(coords["lat"])
            lng = float(coords["lng"])
            acc = coords.get("accuracy", 0)
            print(f"Browser GPS: {lat}, {lng} (accuracy: {acc}m)")
            return lat, lng
    except Exception as e:
        print(f"GPS error: {e}")
    # Fallback to Amaravati
    return 16.4308, 80.5682
