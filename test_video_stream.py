#!/usr/bin/env python3
"""
Simple test for video streaming without YOLOv8
"""

import cv2
from flask import Flask, Response
import threading
import time

app = Flask(__name__)

def generate_test_frames():
    """Generate simple test frames"""
    cap = cv2.VideoCapture("live_cam.mp4")
    
    if not cap.isOpened():
        print("❌ Cannot open video file")
        return
    
    print("✅ Video file opened successfully")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("📹 End of video, looping...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        # Add simple text overlay
        cv2.putText(frame, "TEST STREAM", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        cv2.putText(frame, f"Time: {time.strftime('%H:%M:%S')}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ret:
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(1/30)  # 30 FPS

@app.route('/test_video')
def test_video():
    return Response(generate_test_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
    <html>
    <head><title>Video Stream Test</title></head>
    <body>
        <h1>Video Stream Test</h1>
        <img src="/test_video" style="width: 800px; height: auto;">
        <p>If you see the video with "TEST STREAM" text, the streaming is working!</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🧪 Starting simple video stream test...")
    print("🌐 Open http://localhost:5002 in your browser")
    app.run(host='0.0.0.0', port=5002, debug=False)
