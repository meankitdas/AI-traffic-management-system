#!/usr/bin/env python3
"""
Minimal WebSocket test that definitely works
"""

import asyncio
import websockets
import json
import time

async def handler(websocket, path):
    print("📱 Client connected!")
    try:
        counter = 0
        while True:
            # Send test data
            data = {
                "timestamp": time.time(),
                "vehicle_count": counter % 20,
                "traffic_signal": ["green", "yellow", "red"][counter % 3],
                "congestion_level": ["low", "medium", "high"][counter % 3],
                "signal_timer": counter % 30,
                "frame_count": counter
            }
            
            message = json.dumps(data)
            await websocket.send(message)
            print(f"📤 Sent: {counter} vehicles, {data['traffic_signal']} signal")
            
            counter += 1
            await asyncio.sleep(1)
            
    except websockets.exceptions.ConnectionClosed:
        print("📱 Client disconnected")
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("🌐 Starting minimal WebSocket server on ws://localhost:8765")
    start_server = websockets.serve(handler, "localhost", 8765)
    await start_server
    print("✅ Server running!")
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
