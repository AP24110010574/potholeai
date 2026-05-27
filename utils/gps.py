import geocoder

def get_gps():
    """Get real location from IP/WiFi — works without browser permission"""
    try:
        g = geocoder.ip('me')
        if g.latlng and len(g.latlng) == 2:
            lat, lng = g.latlng
            print(f"GPS: {lat}, {lng}")
            return float(lat), float(lng)
    except Exception as e:
        print(f"GPS error: {e}")
    # Fallback
    return 16.4308, 80.5682
