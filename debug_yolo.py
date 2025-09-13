#!/usr/bin/env python3
"""
Debug version of YOLOv8 Traffic Detector
"""

import cv2
import json
import time
import asyncio
import websockets
from datetime import datetime


class SimpleTrafficDetector:
    def __init__(self):
        self.video_path = "live_cam.mp4"
        self.running = False
        self.websocket_clients = set()
        self.frame_count = 0

    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections"""
        self.websocket_clients.add(websocket)
        print(f"📱 New client connected. Total clients: {len(self.websocket_clients)}")
        try:
            await websocket.wait_closed()
        finally:
            self.websocket_clients.discard(websocket)
            print(
                f"📱 Client disconnected. Total clients: {len(self.websocket_clients)}"
            )

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

    async def process_video(self):
        """Simple video processing loop"""
        print(f"📹 Opening video: {self.video_path}")
        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            print(f"❌ Cannot open video file: {self.video_path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_delay = 1.0 / fps
        print(f"📊 Video FPS: {fps}, Frame delay: {frame_delay}")

        while self.running and cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                print("📹 End of video, looping...")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            self.frame_count += 1

            # Simulate vehicle detection (random count for testing)
            import random

            vehicle_count = random.randint(0, 20)

            # Simulate traffic signal
            signal_states = ["green", "yellow", "red"]
            current_signal = signal_states[(self.frame_count // 30) % 3]

            # Simulate congestion level
            if vehicle_count < 5:
                congestion = "low"
            elif vehicle_count < 15:
                congestion = "medium"
            else:
                congestion = "high"

            # Prepare data
            data = {
                "timestamp": datetime.now().isoformat(),
                "vehicle_count": vehicle_count,
                "avg_vehicle_count": vehicle_count * 0.8,
                "congestion_level": congestion,
                "traffic_signal": current_signal,
                "signal_timer": (self.frame_count % 30),
                "frame_count": self.frame_count,
            }

            # Broadcast data
            await self.broadcast_data(data)

            if self.frame_count % 30 == 0:  # Log every 30 frames (1 second)
                print(
                    f"📊 Frame {self.frame_count}: {vehicle_count} vehicles, {current_signal} signal, {congestion} congestion"
                )

            # Maintain frame rate
            await asyncio.sleep(frame_delay)

        cap.release()
        print("📹 Video processing stopped")

    async def start_server(self):
        """Start the WebSocket server and video processing"""
        self.running = True

        print("🚗 Debug YOLOv8 Traffic Detector started!")
        print("📹 Processing video: live_cam.mp4")
        print("🌐 WebSocket server running on ws://localhost:8765")

        # Start WebSocket server
        server = await websockets.serve(self.websocket_handler, "localhost", 8765)

        # Start video processing
        video_task = asyncio.create_task(self.process_video())

        try:
            await asyncio.gather(server.wait_closed(), video_task)
        except KeyboardInterrupt:
            print("\n🛑 Stopping debug detector...")
            self.running = False
            server.close()
            await server.wait_closed()


def main():
    detector = SimpleTrafficDetector()
    try:
        asyncio.run(detector.start_server())
    except KeyboardInterrupt:
        print("\n✅ Debug detector stopped.")


if __name__ == "__main__":
    main()
