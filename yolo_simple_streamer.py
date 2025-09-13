#!/usr/bin/env python3
"""
Simplified YOLOv8 Web Streamer - Video Only (No WebSocket)
"""

import cv2
import time
import numpy as np
from flask import Flask, Response
from ultralytics import YOLO


class SimpleYoloStreamer:
    def __init__(self, video_path="live_cam.mp4", model_path="yolov8n.pt"):
        self.video_path = video_path
        self.model = YOLO(model_path)

        # COCO dataset class IDs for vehicles
        self.vehicle_classes = [1, 2, 3, 5, 7]  # bicycle, car, motorcycle, bus, truck

        # Class names for display
        self.class_names = {
            1: "Bicycle",
            2: "Car",
            3: "Motorcycle",
            5: "Bus",
            7: "Truck",
        }

        # Colors for different vehicle types (BGR format for OpenCV)
        self.colors = {
            1: (255, 255, 0),  # Bicycle - Cyan
            2: (0, 255, 0),  # Car - Green
            3: (255, 0, 0),  # Motorcycle - Blue
            5: (0, 0, 255),  # Bus - Red
            7: (0, 255, 255),  # Truck - Yellow
        }

        # Traffic light simulation
        self.current_signal = "green"
        self.signal_timer = 0
        self.last_signal_time = time.time()
        self.vehicle_history = []

        # Flask app
        self.app = Flask(__name__)
        self.setup_routes()

        # Control flags
        self.streaming = False

    def setup_routes(self):
        @self.app.route("/video_feed")
        def video_feed():
            return Response(
                self.generate_frames(),
                mimetype="multipart/x-mixed-replace; boundary=frame",
            )

        @self.app.route("/")
        def index():
            return """
            <html>
            <head><title>YOLOv8 Stream Test</title></head>
            <body>
                <h1>YOLOv8 Live Detection Stream</h1>
                <img src="/video_feed" style="width: 100%; max-width: 1200px; height: auto;">
                <p>🔴 LIVE YOLOv8 Vehicle Detection</p>
            </body>
            </html>
            """

    def draw_detections(self, frame, results):
        """Draw bounding boxes and labels on frame"""
        vehicle_count = 0

        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])

                    if cls in self.vehicle_classes and conf > 0.3:
                        vehicle_count += 1

                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                        # Get color for this vehicle type
                        color = self.colors.get(cls, (255, 255, 255))
                        class_name = self.class_names.get(cls, "Vehicle")

                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                        # Draw label background
                        label = f"{class_name}: {conf:.2f}"
                        label_size = cv2.getTextSize(
                            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                        )[0]
                        cv2.rectangle(
                            frame,
                            (x1, y1 - label_size[1] - 10),
                            (x1 + label_size[0], y1),
                            color,
                            -1,
                        )

                        # Draw label text
                        cv2.putText(
                            frame,
                            label,
                            (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 0, 0),
                            2,
                        )

        return frame, vehicle_count

    def add_live_indicator(self, frame):
        """Add LIVE indicator to frame"""
        height, width = frame.shape[:2]

        # Live indicator position (top left)
        live_x = 20
        live_y = 20
        live_width = 100
        live_height = 40

        # Create pulsing effect
        pulse = int(abs(np.sin(time.time() * 3) * 255))
        live_color = (0, 0, max(128, pulse))  # Pulsing red

        # Draw live indicator background
        cv2.rectangle(
            frame,
            (live_x, live_y),
            (live_x + live_width, live_y + live_height),
            live_color,
            -1,
        )
        cv2.rectangle(
            frame,
            (live_x, live_y),
            (live_x + live_width, live_y + live_height),
            (255, 255, 255),
            2,
        )

        # Add LIVE text
        cv2.putText(
            frame,
            "LIVE",
            (live_x + 25, live_y + 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        return frame

    def add_live_indicator_with_loop(self, frame, loop_count):
        """Add LIVE indicator with loop information"""
        height, width = frame.shape[:2]

        # Live indicator position (top left)
        live_x = 20
        live_y = 20
        live_width = 140
        live_height = 60

        # Create pulsing effect
        pulse = int(abs(np.sin(time.time() * 3) * 255))
        live_color = (0, 0, max(128, pulse))  # Pulsing red

        # Draw live indicator background
        cv2.rectangle(
            frame,
            (live_x, live_y),
            (live_x + live_width, live_y + live_height),
            live_color,
            -1,
        )
        cv2.rectangle(
            frame,
            (live_x, live_y),
            (live_x + live_width, live_y + live_height),
            (255, 255, 255),
            2,
        )

        # Add LIVE text
        cv2.putText(
            frame,
            "🔴 LIVE",
            (live_x + 10, live_y + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # Add loop information
        cv2.putText(
            frame,
            f"Loop #{loop_count}",
            (live_x + 10, live_y + 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1,
        )

        return frame

    def add_info_overlay(self, frame, vehicle_count, fps, frame_num):
        """Add information overlay to frame"""
        height, width = frame.shape[:2]

        # Create semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 80), (400, 180), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Add text information
        info_text = [
            f"Vehicles Detected: {vehicle_count}",
            f"FPS: {fps:.1f}",
            f"Frame: {frame_num}",
        ]

        y_offset = 105
        for i, text in enumerate(info_text):
            cv2.putText(
                frame,
                text,
                (20, y_offset + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

        return frame

    def generate_frames(self):
        """Generate video frames for web streaming with continuous looping"""
        cap = None
        frame_count = 0
        start_time = time.time()
        loop_count = 0

        print(f"✅ Starting YOLOv8 detection stream with continuous looping...")

        while True:
            # Initialize or reinitialize video capture
            if cap is None or not cap.isOpened():
                if cap is not None:
                    cap.release()

                cap = cv2.VideoCapture(self.video_path)
                if not cap.isOpened():
                    print(f"❌ Error: Cannot open video file {self.video_path}")
                    time.sleep(1)
                    continue

                loop_count += 1
                print(f"🔄 Video loop #{loop_count} - {self.video_path}")

            ret, frame = cap.read()

            if not ret:
                print(f"📹 End of video loop #{loop_count}, restarting...")
                cap.release()
                cap = None
                frame_count = 0
                start_time = time.time()
                continue

            frame_count += 1

            try:
                # Run YOLOv8 detection
                results = self.model(frame, verbose=False)

                # Draw detections
                annotated_frame, vehicle_count = self.draw_detections(frame, results)

                # Add LIVE indicator with loop info
                annotated_frame = self.add_live_indicator_with_loop(
                    annotated_frame, loop_count
                )

                # Calculate current FPS
                elapsed_time = time.time() - start_time
                current_fps = frame_count / elapsed_time if elapsed_time > 0 else 0

                # Add info overlay
                display_frame = self.add_info_overlay(
                    annotated_frame, vehicle_count, current_fps, frame_count
                )

                # Encode frame for web streaming
                ret, buffer = cv2.imencode(
                    ".jpg", display_frame, [cv2.IMWRITE_JPEG_QUALITY, 85]
                )
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                    )

            except Exception as e:
                print(f"⚠️ Frame processing error: {e}")
                continue

            # Control frame rate - 30 FPS
            time.sleep(1 / 30)

        # Cleanup
        if cap is not None:
            cap.release()

    def run(self):
        """Run the Flask streaming server"""
        print("🌐 Starting YOLOv8 streaming server...")
        print("📺 Video stream: http://localhost:5001/video_feed")
        print("🏠 Test page: http://localhost:5001/")
        print("🛑 Press Ctrl+C to stop")

        self.app.run(host="0.0.0.0", port=5001, debug=False, threaded=True)


def main():
    streamer = SimpleYoloStreamer()
    streamer.run()


if __name__ == "__main__":
    main()
