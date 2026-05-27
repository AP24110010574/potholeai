import streamlit as st
from streamlit_js_eval import get_geolocation

def get_gps():
    """Get real GPS using streamlit_js_eval's built-in geolocation"""
    try:
        location = get_geolocation()
        if location and isinstance(location, dict):
            coords = location.get("coords", {})
            lat = coords.get("latitude")
            lng = coords.get("longitude")
            if lat and lng:
                return float(lat), float(lng)
    except Exception as e:
        print(f"GPS error: {e}")
    # Fallback to Amaravati
    return 16.4308, 80.5682
