#!/usr/bin/env python3
"""
YOLOv8 Web Video Streamer with Traffic Light Simulation
Streams video with detections to web browser via HTTP
"""

import cv2
import time
import asyncio
import websockets
import json
import threading
from flask import Flask, Response, render_template_string
from ultralytics import YOLO
import numpy as np


class YoloWebStreamer:
    def __init__(self, video_path="live_cam.mp4", model_path="yolov8n.pt"):
        self.video_path = video_path
        self.model = YOLO(model_path)

        # COCO dataset class IDs for vehicles (including bicycles)
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
        self.vehicle_history = []  # Track vehicle counts for congestion analysis

        # Traffic signal timing (seconds)
        self.signal_timings = {
            "green": {"low": 30, "medium": 20, "high": 15},
            "yellow": 3,
            "red": {"low": 15, "medium": 25, "high": 35},
        }

        # Flask app for video streaming
        self.app = Flask(__name__)
        self.setup_routes()

        # WebSocket clients
        self.websocket_clients = set()

        # Control flags
        self.streaming = False
        self.cap = None

    def setup_routes(self):
        @self.app.route("/video_feed")
        def video_feed():
            return Response(
                self.generate_frames(),
                mimetype="multipart/x-mixed-replace; boundary=frame",
            )

    def draw_detections(self, frame, results):
        """Draw bounding boxes and labels on frame"""
        vehicle_count = 0

        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])

                    if (
                        cls in self.vehicle_classes and conf > 0.3
                    ):  # Lower threshold for better detection
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

    def update_traffic_signal(self, vehicle_count):
        """Update traffic signal based on vehicle congestion"""
        current_time = time.time()
        elapsed = current_time - self.last_signal_time
        self.signal_timer = elapsed

        # Update vehicle history for congestion analysis
        self.vehicle_history.append(vehicle_count)
        if len(self.vehicle_history) > 30:  # Keep last 30 readings
            self.vehicle_history.pop(0)

        # Calculate congestion level
        avg_vehicles = (
            sum(self.vehicle_history) / len(self.vehicle_history)
            if self.vehicle_history
            else 0
        )

        if avg_vehicles < 5:
            congestion_level = "low"
        elif avg_vehicles < 15:
            congestion_level = "medium"
        else:
            congestion_level = "high"

        # Traffic signal logic
        if self.current_signal == "green":
            green_duration = self.signal_timings["green"][congestion_level]
            if elapsed > green_duration:
                self.current_signal = "yellow"
                self.last_signal_time = current_time
                self.signal_timer = 0
        elif self.current_signal == "yellow":
            if elapsed > self.signal_timings["yellow"]:
                self.current_signal = "red"
                self.last_signal_time = current_time
                self.signal_timer = 0
        else:  # red
            red_duration = self.signal_timings["red"][congestion_level]
            if elapsed > red_duration:
                self.current_signal = "green"
                self.last_signal_time = current_time
                self.signal_timer = 0

        return congestion_level

    def draw_traffic_light(self, frame):
        """Draw traffic light on the video"""
        height, width = frame.shape[:2]

        # Traffic light position (top right)
        light_x = width - 120
        light_y = 20
        light_width = 80
        light_height = 200

        # Draw traffic light housing (black background)
        cv2.rectangle(
            frame,
            (light_x, light_y),
            (light_x + light_width, light_y + light_height),
            (0, 0, 0),
            -1,
        )
        cv2.rectangle(
            frame,
            (light_x, light_y),
            (light_x + light_width, light_y + light_height),
            (255, 255, 255),
            3,
        )

        # Light positions
        red_center = (light_x + light_width // 2, light_y + 40)
        yellow_center = (light_x + light_width // 2, light_y + 100)
        green_center = (light_x + light_width // 2, light_y + 160)
        light_radius = 25

        # Draw lights (dim when not active)
        red_color = (0, 0, 255) if self.current_signal == "red" else (0, 0, 80)
        yellow_color = (0, 255, 255) if self.current_signal == "yellow" else (0, 80, 80)
        green_color = (0, 255, 0) if self.current_signal == "green" else (0, 80, 0)

        # Draw light circles
        cv2.circle(frame, red_center, light_radius, red_color, -1)
        cv2.circle(frame, red_center, light_radius, (255, 255, 255), 2)

        cv2.circle(frame, yellow_center, light_radius, yellow_color, -1)
        cv2.circle(frame, yellow_center, light_radius, (255, 255, 255), 2)

        cv2.circle(frame, green_center, light_radius, green_color, -1)
        cv2.circle(frame, green_center, light_radius, (255, 255, 255), 2)

        # Add glow effect for active light
        if self.current_signal == "red":
            cv2.circle(frame, red_center, light_radius + 5, (0, 0, 255), 2)
        elif self.current_signal == "yellow":
            cv2.circle(frame, yellow_center, light_radius + 5, (0, 255, 255), 2)
        elif self.current_signal == "green":
            cv2.circle(frame, green_center, light_radius + 5, (0, 255, 0), 2)

        # Add signal timer text
        timer_text = f"{self.signal_timer:.1f}s"
        cv2.putText(
            frame,
            timer_text,
            (light_x, light_y + light_height + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        return frame

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
            "🔴 LIVE",
            (live_x + 10, live_y + 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        return frame

    def add_info_overlay(self, frame, vehicle_count, fps, frame_num, congestion_level):
        """Add information overlay to frame"""
        height, width = frame.shape[:2]

        # Create semi-transparent overlay (moved down to avoid LIVE indicator)
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 80), (450, 230), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Add text information
        signal_emoji = {"red": "🔴", "yellow": "🟡", "green": "🟢"}
        congestion_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}

        info_text = [
            f"🚗 Vehicles Detected: {vehicle_count}",
            f"📊 FPS: {fps:.1f}",
            f"📹 Frame: {frame_num}",
            f"🚦 Signal: {signal_emoji.get(self.current_signal, '⚪')} {self.current_signal.upper()}",
            f"📈 Congestion: {congestion_emoji.get(congestion_level, '⚪')} {congestion_level.upper()}",
        ]

        y_offset = 105  # Adjusted for LIVE indicator
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

        # Add legend (moved down)
        legend_y = height - 100
        cv2.putText(
            frame,
            "Vehicle Types:",
            (20, legend_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        legend_items = [
            ("Bicycle", self.colors[1]),
            ("Car", self.colors[2]),
            ("Motorcycle", self.colors[3]),
            ("Bus", self.colors[5]),
            ("Truck", self.colors[7]),
        ]

        for i, (name, color) in enumerate(legend_items):
            x_pos = 20 + i * 120
            cv2.rectangle(
                frame, (x_pos, legend_y + 10), (x_pos + 15, legend_y + 25), color, -1
            )
            cv2.putText(
                frame,
                name,
                (x_pos + 20, legend_y + 22),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

        return frame

    def generate_frames(self):
        """Generate video frames for web streaming"""
        if not self.streaming:
            return

        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print(f"❌ Error: Cannot open video file {self.video_path}")
            return

        # Get video properties
        fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        frame_count = 0
        start_time = time.time()

        print(f"🚀 Starting web video stream at {fps} FPS")
        print(f"🔴 LIVE indicator active - streaming to web browser")

        while self.streaming:
            ret, frame = self.cap.read()

            if not ret:
                # Loop video
                print("📹 End of video, looping...")
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                frame_count = 0
                start_time = time.time()
                continue

            frame_count += 1

            # Run YOLOv8 detection
            results = self.model(frame, verbose=False)

            # Draw detections
            annotated_frame, vehicle_count = self.draw_detections(frame, results)

            # Update traffic signal simulation
            congestion_level = self.update_traffic_signal(vehicle_count)

            # Draw traffic light
            annotated_frame = self.draw_traffic_light(annotated_frame)

            # Add LIVE indicator
            annotated_frame = self.add_live_indicator(annotated_frame)

            # Calculate current FPS
            elapsed_time = time.time() - start_time
            current_fps = frame_count / elapsed_time if elapsed_time > 0 else 0

            # Add info overlay
            display_frame = self.add_info_overlay(
                annotated_frame,
                vehicle_count,
                current_fps,
                frame_count,
                congestion_level,
            )

            # Encode frame for web streaming
            ret, buffer = cv2.imencode(
                ".jpg", display_frame, [cv2.IMWRITE_JPEG_QUALITY, 80]
            )
            if ret:
                frame_bytes = buffer.tobytes()
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )

            # Send WebSocket data
            if self.websocket_clients:
                data = {
                    "timestamp": time.time(),
                    "vehicle_count": vehicle_count,
                    "avg_vehicle_count": (
                        sum(self.vehicle_history) / len(self.vehicle_history)
                        if self.vehicle_history
                        else 0
                    ),
                    "congestion_level": congestion_level,
                    "traffic_signal": self.current_signal,
                    "signal_timer": self.signal_timer,
                    "fps": current_fps,
                    "frame_number": frame_count,
                }
                asyncio.run(self.broadcast_data(data))

            # Control frame rate
            time.sleep(1 / 30)  # ~30 FPS

        if self.cap:
            self.cap.release()
            print("✅ Video stream stopped")

    async def broadcast_data(self, data):
        """Send data to all WebSocket clients"""
        if not self.websocket_clients:
            return

        message = json.dumps(data)
        disconnected_clients = set()

        for client in self.websocket_clients.copy():
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                print(f"❌ WebSocket send error: {e}")
                disconnected_clients.add(client)

        # Remove disconnected clients
        self.websocket_clients -= disconnected_clients

    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections"""
        print(f"🔗 New WebSocket client connected from {path}")
        self.websocket_clients.add(websocket)
        try:
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.websocket_clients.discard(websocket)
            print(f"🔌 WebSocket client disconnected")

    def start_streaming(self):
        """Start video streaming"""
        self.streaming = True
        print("🎬 YOLOv8 web streaming started")

    def stop_streaming(self):
        """Stop video streaming"""
        self.streaming = False
        print("⏹️ YOLOv8 web streaming stopped")

    def run_flask_app(self):
        """Run Flask app in a separate thread"""
        self.app.run(host="0.0.0.0", port=5001, debug=False, threaded=True)

    async def run_websocket_server(self):
        """Run WebSocket server"""
        print("🌐 Starting WebSocket server on ws://localhost:8765")
        server = await websockets.serve(self.websocket_handler, "localhost", 8765)
        await server.wait_closed()


def main():
    """Main function"""
    streamer = YoloWebStreamer()

    # Start Flask app in background thread
    flask_thread = threading.Thread(target=streamer.run_flask_app, daemon=True)
    flask_thread.start()

    print("🌐 Flask video server started on http://localhost:5001")
    print("📺 Video feed available at http://localhost:5001/video_feed")
    print("🔗 WebSocket server starting...")

    # Start streaming
    streamer.start_streaming()

    # Run WebSocket server
    try:
        asyncio.run(streamer.run_websocket_server())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        streamer.stop_streaming()


if __name__ == "__main__":
    main()
