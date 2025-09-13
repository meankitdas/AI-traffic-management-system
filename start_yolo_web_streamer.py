#!/usr/bin/env python3
"""
Startup script for YOLOv8 Web Streamer
Sets up environment and runs the web streaming server
"""

import os
import sys
import subprocess
import time


def check_video_file():
    """Check if live_cam.mp4 exists"""
    if not os.path.exists("live_cam.mp4"):
        print("❌ live_cam.mp4 not found!")
        print("📹 Creating demo video...")

        # Run demo.py to create video if it exists
        if os.path.exists("demo.py"):
            subprocess.run([sys.executable, "demo.py"], check=True)
        else:
            print("❌ demo.py not found. Please ensure live_cam.mp4 exists.")
            return False

    print("✅ live_cam.mp4 found")
    return True


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True,
        )
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True


def download_yolo_model():
    """Download YOLOv8 model if not present"""
    if not os.path.exists("yolov8n.pt"):
        print("🤖 Downloading YOLOv8 model...")
        try:
            from ultralytics import YOLO

            model = YOLO("yolov8n.pt")  # This will download the model
            print("✅ YOLOv8 model downloaded successfully")
        except Exception as e:
            print(f"❌ Failed to download YOLOv8 model: {e}")
            return False
    else:
        print("✅ YOLOv8 model found")
    return True


def main():
    """Main function"""
    print("🚀 Starting YOLOv8 Web Streamer Setup")
    print("=" * 50)

    # Check video file
    if not check_video_file():
        return

    # Install dependencies
    if not install_dependencies():
        return

    # Download YOLO model
    if not download_yolo_model():
        return

    print("\n🌐 Starting YOLOv8 Web Streaming Server...")
    print("📺 Video will be available at: http://localhost:5001/video_feed")
    print("🔗 WebSocket server will run on: ws://localhost:8765")
    print("💡 Click 'Start Detection' in the web interface to begin streaming")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)

    try:
        # Import and run the web streamer
        from yolo_web_streamer import main as run_streamer

        run_streamer()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down YOLOv8 Web Streamer...")
        print("✅ Server stopped successfully")
    except Exception as e:
        print(f"❌ Error running web streamer: {e}")
        print("💡 Make sure all dependencies are installed correctly")


if __name__ == "__main__":
    main()
