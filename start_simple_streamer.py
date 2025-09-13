#!/usr/bin/env python3
"""
Start the simplified YOLOv8 streamer
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting Simplified YOLOv8 Streamer")
    print("=" * 50)
    
    # Check if video exists
    if not os.path.exists("live_cam.mp4"):
        print("❌ live_cam.mp4 not found!")
        print("🎬 Run: python demo.py to create a demo video")
        return
    
    print("✅ Video file found")
    print("🤖 Starting YOLOv8 streaming server...")
    print("📺 Video stream will be at: http://localhost:5001/video_feed")
    print("🌐 Test page at: http://localhost:5001/")
    print("💡 Open index.html and click 'Start Detection'")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Run the simplified streamer
        subprocess.run([sys.executable, "yolo_simple_streamer.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
