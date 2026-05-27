from flask import Flask, request, jsonify, send_from_directory
import cv2, numpy as np, os, io, folium
from PIL import Image
from utils.detector import load_model, detect_potholes
from utils.db import save_detection, fetch_all_detections

app = Flask(__name__, static_folder='static')
model = load_model()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/detect', methods=['POST'])
def detect():
    file = request.files['image']
    lat  = float(request.form.get('lat', 16.3067))
    lng  = float(request.form.get('lng', 80.4365))
    img   = Image.open(io.BytesIO(file.read())).convert('RGB')
    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    _, detections = detect_potholes(frame, model, conf=0.30)
    if detections:
        best = max(d['confidence'] for d in detections)
        for d in detections:
            sev = 'High' if d['confidence']>=0.70 else 'Medium' if d['confidence']>=0.50 else 'Low'
            save_detection(lat=lat, lng=lng, confidence=d['confidence'], severity=sev)
        return jsonify({'count': len(detections), 'confidence': best})
    return jsonify({'count': 0, 'confidence': 0.0})

@app.route('/map')
def map_view():
    potholes = fetch_all_detections()
    center = [16.3067, 80.4365]
    if potholes:
        center = [
            sum(p['lat'] for p in potholes)/len(potholes),
            sum(p['lng'] for p in potholes)/len(potholes),
        ]
    m = folium.Map(location=center, zoom_start=14, tiles='CartoDB dark_matter')
    COLORS = {'High':'#ef4444','Medium':'#f97316','Low':'#eab308'}
    for p in potholes:
        color = COLORS.get(p.get('severity','Medium'),'#f97316')
        folium.CircleMarker(
            location=[p['lat'], p['lng']],
            radius=8, color=color, fill=True,
            fill_color=color, fill_opacity=0.85,
            tooltip=f"{p.get('severity','?')} — {p['confidence']:.0%}"
        ).add_to(m)
    return m._repr_html_()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
