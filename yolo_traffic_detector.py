#!/usr/bin/env python3
"""
YOLOv8 Traffic Detection System
Processes live_cam.mp4 video to detect vehicles and simulate traffic signals
"""

import cv2
import numpy as np
from ultralytics import YOLO
import json
import time
import threading
from collections import defaultdict, deque
import websockets
import asyncio
from datetime import datetime
import os


class TrafficDetector:
    def __init__(self, video_path="live_cam.mp4", model_path="yolov8n.pt"):
        self.video_path = video_path
        self.model = YOLO(model_path)
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        self.vehicle_counts = deque(maxlen=30)  # Store last 30 frames
        self.congestion_history = deque(maxlen=10)  # Store last 10 readings
        self.current_signal = "green"
        self.signal_timer = 0
        self.running = False
        self.websocket_clients = set()

        # Traffic signal timing (seconds)
        self.signal_timings = {
            "green": {"low": 30, "medium": 20, "high": 15},
            "yellow": 3,
            "red": {"low": 15, "medium": 25, "high": 35},
        }

    def detect_vehicles(self, frame):
        """Detect vehicles in frame using YOLOv8"""
        results = self.model(frame, verbose=False)
        vehicles = []

        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])

                    if cls in self.vehicle_classes and conf > 0.5:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        vehicles.append(
                            {
                                "class": cls,
                                "confidence": conf,
                                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                                "center": [(x1 + x2) / 2, (y1 + y2) / 2],
                            }
                        )

        return vehicles

    def calculate_congestion_level(self, vehicle_count):
        """Calculate congestion level based on vehicle count"""
        if vehicle_count < 5:
            return "low"
        elif vehicle_count < 15:
            return "medium"
        else:
            return "high"

    def update_traffic_signal(self, congestion_level):
        """Update traffic signal based on congestion"""
        current_time = time.time()

        # Simple traffic signal logic
        if self.current_signal == "green":
            duration = self.signal_timings["green"][congestion_level]
            if self.signal_timer > duration:
                self.current_signal = "yellow"
                self.signal_timer = 0
        elif self.current_signal == "yellow":
            if self.signal_timer > self.signal_timings["yellow"]:
                self.current_signal = "red"
                self.signal_timer = 0
        elif self.current_signal == "red":
            duration = self.signal_timings["red"][congestion_level]
            if self.signal_timer > duration:
                self.current_signal = "green"
                self.signal_timer = 0

    def draw_detections(self, frame, vehicles):
        """Draw bounding boxes and vehicle count on frame"""
        for vehicle in vehicles:
            x1, y1, x2, y2 = vehicle["bbox"]
            conf = vehicle["confidence"]

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw confidence
            label = f"Vehicle: {conf:.2f}"
            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

        # Draw vehicle count and signal status
        count_text = f"Vehicles: {len(vehicles)}"
        signal_text = f"Signal: {self.current_signal.upper()}"
        congestion_level = self.calculate_congestion_level(len(vehicles))
        congestion_text = f"Congestion: {congestion_level.upper()}"

        cv2.putText(
            frame, count_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
        )
        cv2.putText(
            frame,
            signal_text,
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            self.get_signal_color(),
            2,
        )
        cv2.putText(
            frame,
            congestion_text,
            (10, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

        return frame

    def get_signal_color(self):
        """Get BGR color for current signal"""
        colors = {"green": (0, 255, 0), "yellow": (0, 255, 255), "red": (0, 0, 255)}
        return colors.get(self.current_signal, (255, 255, 255))

    async def broadcast_data(self, data):
        """Broadcast data to all connected WebSocket clients"""
        if self.websocket_clients:
            message = json.dumps(data)
            disconnected = set()

            for client in self.websocket_clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)

            # Remove disconnected clients
            self.websocket_clients -= disconnected

    async def websocket_handler(self, websocket):
        """Handle WebSocket connections"""
        self.websocket_clients.add(websocket)
        print(f"📱 New client connected. Total clients: {len(self.websocket_clients)}")
        try:
            await websocket.wait_closed()
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
        finally:
            self.websocket_clients.discard(websocket)
            print(f"📱 Client disconnected. Total clients: {len(self.websocket_clients)}")

    async def process_video(self):
        """Main video processing loop"""
        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            print(f"Error: Could not open video file {self.video_path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_delay = 1.0 / fps
        last_time = time.time()

        while self.running and cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                # Loop video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            current_time = time.time()

            # Detect vehicles
            vehicles = self.detect_vehicles(frame)
            vehicle_count = len(vehicles)

            # Update metrics
            self.vehicle_counts.append(vehicle_count)
            congestion_level = self.calculate_congestion_level(vehicle_count)
            self.congestion_history.append(congestion_level)

            # Update traffic signal
            self.signal_timer += current_time - last_time
            self.update_traffic_signal(congestion_level)

            # Draw detections
            annotated_frame = self.draw_detections(frame.copy(), vehicles)

            # Prepare data for WebSocket broadcast
            data = {
                "timestamp": datetime.now().isoformat(),
                "vehicle_count": vehicle_count,
                "avg_vehicle_count": (
                    sum(self.vehicle_counts) / len(self.vehicle_counts)
                    if self.vehicle_counts
                    else 0
                ),
                "congestion_level": congestion_level,
                "traffic_signal": self.current_signal,
                "signal_timer": self.signal_timer,
                "vehicles": vehicles[:10],  # Send only first 10 vehicles to reduce data
            }

            # Broadcast data
            await self.broadcast_data(data)

            # Save annotated frame (optional - for debugging)
            # cv2.imwrite(f"debug_frame_{int(current_time)}.jpg", annotated_frame)

            last_time = current_time

            # Maintain frame rate
            elapsed = time.time() - current_time
            if elapsed < frame_delay:
                await asyncio.sleep(frame_delay - elapsed)

        cap.release()

    async def start_server(self):
        """Start the WebSocket server and video processing"""
        self.running = True

        # Start WebSocket server
        async def handler_wrapper(websocket, path):
            await self.websocket_handler(websocket)
        
        server = await websockets.serve(handler_wrapper, "localhost", 8765)

        print("🚗 YOLOv8 Traffic Detector started!")
        print("📹 Processing video: live_cam.mp4")
        print("🌐 WebSocket server running on ws://localhost:8765")
        print("🚦 Traffic signal simulation active")

        # Start video processing
        video_task = asyncio.create_task(self.process_video())

        try:
            await asyncio.gather(server.wait_closed(), video_task)
        except KeyboardInterrupt:
            print("\n🛑 Stopping traffic detector...")
            self.running = False
            server.close()
            await server.wait_closed()


def main():
    """Main function"""
    detector = TrafficDetector()

    try:
        asyncio.run(detector.start_server())
    except KeyboardInterrupt:
        print("\n✅ Traffic detector stopped.")


if __name__ == "__main__":
    main()
