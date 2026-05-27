from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb+srv://myAtlasDBUser:Pothole123@myatlasclusteredu.ywffn6z.mongodb.net/pothole_db?appName=myAtlasClusterEDU"

_client = None

def get_collection():
    global _client
    if _client is None:
        _client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
            tlsAllowInvalidCertificates=True
        )
    return _client["pothole_db"]["detections"]

def save_detection(lat: float, lng: float, confidence: float, severity: str):
    try:
        get_collection().insert_one({
            "lat": lat,
            "lng": lng,
            "confidence": confidence,
            "severity": severity,
            "timestamp": datetime.utcnow(),
            "source": "apsrtc_bus"
        })
        print(f"✅ Saved: {lat}, {lng}, {severity}, {confidence:.2f}")
        return True
    except Exception as e:
        print(f"❌ Save failed: {e}")
        return False

def fetch_all_detections():
    try:
        return list(get_collection().find({}, {"_id": 0}).sort("timestamp", -1).limit(500))
    except Exception as e:
        print(f"❌ Fetch failed: {e}")
        return []
