from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS
import cv2, numpy as np, threading, time, io
from PIL import Image
from utils.detector import load_model, detect_potholes
from utils.db import save_detection, fetch_all_detections
from utils.gps import get_gps
import os

app = Flask(__name__, static_folder='static')
CORS(app)
model = load_model()

class VideoStream:
    def __init__(self):
        self.running    = False
        self.frame      = None
        self.lock       = threading.Lock()
        self.status     = "idle"
        self.status_msg = "Press START"
        self.last_saved = 0
        self.total      = 0
        self.lat        = 16.3067
        self.lng        = 80.4365

stream = VideoStream()

def capture_loop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        stream.status_msg = "Cannot open camera"
        stream.running = False
        return

    det_cache = []
    det_counter = 0

    while stream.running:
        ret, frame = cap.read()
        if not ret:
            break

        det_counter += 1
        if det_counter % 10 == 0:
            _, det_cache = detect_potholes(frame.copy(), model, conf=0.35)
            if det_cache:
                best = max(d["confidence"] for d in det_cache)
                stream.status = "pothole"
                stream.status_msg = f"POTHOLE {best:.0%}"
                now = time.time()
                if now - stream.last_saved > 5:
                    best_det = max(det_cache, key=lambda d: d["confidence"])
                    sev = "High" if best_det["confidence"]>=0.70 else "Medium" if best_det["confidence"]>=0.50 else "Low"
                    save_detection(lat=stream.lat, lng=stream.lng,
                                   confidence=best_det["confidence"], severity=sev)
                    stream.last_saved = now
                    stream.last_lat = stream.lat
                    stream.last_lng = stream.lng
                    stream.total += 1
            else:
                stream.status = "clear"
                stream.status_msg = "Road Clear"

        # Draw boxes
        display = frame.copy()
        for d in det_cache:
            x1,y1,x2,y2 = d["bbox"]
            conf = d["confidence"]
            color = (0,0,239) if conf>=0.70 else (0,115,249) if conf>=0.50 else (8,179,234)
            cv2.rectangle(display, (x1,y1), (x2,y2), color, 2)
            cv2.putText(display, f"POTHOLE {conf:.0%}", (x1, y1-8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        with stream.lock:
            stream.frame = display

    cap.release()
    stream.running = False
    stream.status = "idle"
    stream.status_msg = "Press START"

def generate_frames():
    while True:
        with stream.lock:
            frame = stream.frame
        if frame is None:
            time.sleep(0.05)
            continue
        _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buf.tobytes() + b'\r\n')
        time.sleep(0.033)  # ~30fps

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start', methods=['POST'])
def start():
    data = request.json or {}
    stream.lat = float(data.get('lat', 16.3067))
    stream.lng = float(data.get('lng', 80.4365))
    if not stream.running:
        stream.running = True
        threading.Thread(target=capture_loop, daemon=True).start()
    return jsonify({'ok': True})

@app.route('/stop', methods=['POST'])
def stop():
    stream.running = False
    return jsonify({'ok': True})

@app.route('/status')
def status():
    return jsonify({
        'status': stream.status,
        'msg': stream.status_msg,
        'total': stream.total,
        'lat': stream.lat,
        'lng': stream.lng
    })

@app.route('/potholes')
def potholes():
    return jsonify(fetch_all_detections())

@app.route('/')
def index():
    return send_from_directory('static', 'live.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
