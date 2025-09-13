#!/usr/bin/env python3
"""
Minimal WebSocket test server
"""

import asyncio
import websockets
import json
import time


async def handler(websocket, path):
    print("📱 Client connected")
    try:
        counter = 0
        while True:
            # Send test data every second
            data = {
                "timestamp": time.time(),
                "vehicle_count": counter % 20,
                "traffic_signal": ["green", "yellow", "red"][counter % 3],
                "congestion_level": ["low", "medium", "high"][counter % 3],
                "signal_timer": counter % 30,
                "test_counter": counter,
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
    print("🌐 Starting test WebSocket server on ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        print("✅ Server running! Connect from browser to test.")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
