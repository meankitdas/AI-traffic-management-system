#!/usr/bin/env python3
"""
Simplified YOLOv8 Traffic Detector that actually works
"""

import cv2
import json
import time
import asyncio
import websockets
from datetime import datetime
from ultralytics import YOLO
import threading
import queue


class WorkingTrafficDetector:
    def __init__(self):
        self.video_path = "live_cam.mp4"
        self.model = YOLO("yolov8n.pt")
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        self.running = False
        self.websocket_clients = set()
        self.data_queue = queue.Queue()
        self.current_signal = "green"
        self.signal_timer = 0
        self.frame_count = 0

    def process_video_thread(self):
        """Video processing in separate thread"""
        print(f"📹 Starting video processing: {self.video_path}")
        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            print(f"❌ Cannot open video file: {self.video_path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_delay = 1.0 / fps
        last_time = time.time()

        while self.running:
            ret, frame = cap.read()

            if not ret:
                print("📹 End of video, looping...")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            current_time = time.time()
            self.frame_count += 1

            # Detect vehicles with YOLOv8
            results = self.model(frame, verbose=False)
            vehicle_count = 0

            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        if cls in self.vehicle_classes and conf > 0.5:
                            vehicle_count += 1

            # Update traffic signal timing
            self.signal_timer += current_time - last_time

            # Simple traffic signal logic
            congestion_level = (
                "low"
                if vehicle_count < 5
                else "medium" if vehicle_count < 15 else "high"
            )
            signal_timings = {"low": 30, "medium": 20, "high": 15}

            if (
                self.current_signal == "green"
                and self.signal_timer > signal_timings[congestion_level]
            ):
                self.current_signal = "yellow"
                self.signal_timer = 0
            elif self.current_signal == "yellow" and self.signal_timer > 3:
                self.current_signal = "red"
                self.signal_timer = 0
            elif (
                self.current_signal == "red"
                and self.signal_timer > signal_timings[congestion_level]
            ):
                self.current_signal = "green"
                self.signal_timer = 0

            # Prepare data
            data = {
                "timestamp": datetime.now().isoformat(),
                "vehicle_count": vehicle_count,
                "avg_vehicle_count": vehicle_count * 0.9,  # Simple average simulation
                "congestion_level": congestion_level,
                "traffic_signal": self.current_signal,
                "signal_timer": self.signal_timer,
                "frame_count": self.frame_count,
            }

            # Put data in queue for WebSocket broadcasting
            try:
                self.data_queue.put_nowait(data)
            except queue.Full:
                pass  # Skip if queue is full

            if self.frame_count % 30 == 0:  # Log every 30 frames
                print(
                    f"📊 Frame {self.frame_count}: {vehicle_count} vehicles, {self.current_signal} signal, {congestion_level} congestion"
                )

            last_time = current_time

            # Maintain frame rate
            elapsed = time.time() - current_time
            if elapsed < frame_delay:
                time.sleep(frame_delay - elapsed)

        cap.release()
        print("📹 Video processing stopped")

    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections"""
        self.websocket_clients.add(websocket)
        print(f"📱 New client connected. Total clients: {len(self.websocket_clients)}")
        try:
            await websocket.wait_closed()
        except:
            pass
        finally:
            self.websocket_clients.discard(websocket)
            print(
                f"📱 Client disconnected. Total clients: {len(self.websocket_clients)}"
            )

    async def broadcast_loop(self):
        """Broadcast data from queue to WebSocket clients"""
        while self.running:
            try:
                # Get data from queue (non-blocking)
                data = self.data_queue.get_nowait()

                if self.websocket_clients:
                    message = json.dumps(data)
                    disconnected = set()

                    for client in self.websocket_clients:
                        try:
                            await client.send(message)
                        except:
                            disconnected.add(client)

                    # Remove disconnected clients
                    self.websocket_clients -= disconnected

            except queue.Empty:
                await asyncio.sleep(0.1)  # Wait a bit if no data
            except Exception as e:
                print(f"❌ Broadcast error: {e}")
                await asyncio.sleep(0.1)

    async def start_server(self):
        """Start the WebSocket server and video processing"""
        self.running = True

        print("🚗 Working YOLOv8 Traffic Detector started!")
        print("📹 Processing video: live_cam.mp4")
        print("🌐 WebSocket server running on ws://localhost:8765")
        print("🚦 Traffic signal simulation active")

        # Start video processing thread
        video_thread = threading.Thread(target=self.process_video_thread, daemon=True)
        video_thread.start()

        # Start WebSocket server
        server = await websockets.serve(self.websocket_handler, "localhost", 8765)

        # Start broadcast loop
        broadcast_task = asyncio.create_task(self.broadcast_loop())

        try:
            await asyncio.gather(server.wait_closed(), broadcast_task)
        except KeyboardInterrupt:
            print("\n🛑 Stopping detector...")
            self.running = False
            server.close()
            await server.wait_closed()


def main():
    detector = WorkingTrafficDetector()
    try:
        asyncio.run(detector.start_server())
    except KeyboardInterrupt:
        print("\n✅ Detector stopped.")


if __name__ == "__main__":
    main()
