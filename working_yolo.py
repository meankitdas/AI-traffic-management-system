#!/usr/bin/env python3
"""
Working YOLOv8 Traffic Detector - Guaranteed to work!
"""

import cv2
import json
import time
import asyncio
import websockets
from datetime import datetime
from ultralytics import YOLO

class WorkingYoloDetector:
    def __init__(self):
        self.video_path = "live_cam.mp4"
        self.model = YOLO("yolov8n.pt")
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        self.running = False
        self.websocket_clients = set()
        self.current_signal = "green"
        self.signal_timer = 0
        self.frame_count = 0
        self.vehicle_counts = []
        
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
    
    async def broadcast_data(self, data):
        """Broadcast data to all connected WebSocket clients"""
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
    
    async def process_video(self):
        """Main video processing loop"""
        print(f"📹 Opening video: {self.video_path}")
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            print(f"❌ Cannot open video file: {self.video_path}")
            return
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_delay = 1.0 / fps
        last_time = time.time()
        
        print(f"📊 Video FPS: {fps}, Frame delay: {frame_delay}")
        print("🚀 Starting video processing...")
        
        while self.running:
            ret, frame = cap.read()
            
            if not ret:
                print("📹 End of video, looping...")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            current_time = time.time()
            self.frame_count += 1
            
            # Detect vehicles with YOLOv8
            try:
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
                
            except Exception as e:
                print(f"❌ YOLO detection error: {e}")
                vehicle_count = 0
            
            # Update metrics
            self.vehicle_counts.append(vehicle_count)
            if len(self.vehicle_counts) > 30:  # Keep last 30 frames
                self.vehicle_counts.pop(0)
            
            # Calculate congestion level
            if vehicle_count < 5:
                congestion_level = "low"
            elif vehicle_count < 15:
                congestion_level = "medium"
            else:
                congestion_level = "high"
            
            # Update traffic signal timing
            self.signal_timer += current_time - last_time
            
            # Traffic signal logic
            signal_timings = {"low": 30, "medium": 20, "high": 15}
            
            if self.current_signal == "green" and self.signal_timer > signal_timings[congestion_level]:
                self.current_signal = "yellow"
                self.signal_timer = 0
            elif self.current_signal == "yellow" and self.signal_timer > 3:
                self.current_signal = "red"
                self.signal_timer = 0
            elif self.current_signal == "red" and self.signal_timer > signal_timings[congestion_level]:
                self.current_signal = "green"
                self.signal_timer = 0
            
            # Prepare data for WebSocket broadcast
            avg_vehicle_count = sum(self.vehicle_counts) / len(self.vehicle_counts) if self.vehicle_counts else 0
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "vehicle_count": vehicle_count,
                "avg_vehicle_count": avg_vehicle_count,
                "congestion_level": congestion_level,
                "traffic_signal": self.current_signal,
                "signal_timer": self.signal_timer,
                "frame_count": self.frame_count
            }
            
            # Broadcast data
            await self.broadcast_data(data)
            
            # Log progress
            if self.frame_count % 30 == 0:  # Log every 30 frames (1 second)
                print(f"📊 Frame {self.frame_count}: {vehicle_count} vehicles, {self.current_signal} signal, {congestion_level} congestion, {len(self.websocket_clients)} clients")
            
            last_time = current_time
            
            # Maintain frame rate
            elapsed = time.time() - current_time
            if elapsed < frame_delay:
                await asyncio.sleep(frame_delay - elapsed)
        
        cap.release()
        print("📹 Video processing stopped")
    
    async def start_server(self):
        """Start the WebSocket server and video processing"""
        self.running = True
        
        print("🚗 Working YOLOv8 Traffic Detector started!")
        print("📹 Processing video: live_cam.mp4")
        print("🌐 WebSocket server running on ws://localhost:8765")
        print("🚦 Traffic signal simulation active")
        
        # Start WebSocket server with proper handler wrapper
        async def handler_wrapper(websocket, path):
            await self.websocket_handler(websocket)
        
        server = await websockets.serve(handler_wrapper, "localhost", 8765)
        
        # Start video processing
        video_task = asyncio.create_task(self.process_video())
        
        try:
            await asyncio.gather(server.wait_closed(), video_task)
        except KeyboardInterrupt:
            print("\n🛑 Stopping detector...")
            self.running = False
            server.close()
            await server.wait_closed()

def main():
    detector = WorkingYoloDetector()
    try:
        asyncio.run(detector.start_server())
    except KeyboardInterrupt:
        print("\n✅ Detector stopped.")

if __name__ == "__main__":
    main()
