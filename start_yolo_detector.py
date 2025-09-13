#!/usr/bin/env python3
"""
Startup script for YOLOv8 Traffic Detector
This script handles model download and starts the detection system
"""

import os
import sys
import subprocess
import urllib.request
from pathlib import Path


def check_video_file():
    """Check if the video file exists"""
    video_path = "live_cam.mp4"
    if not os.path.exists(video_path):
        print(f"❌ Video file '{video_path}' not found!")
        print(
            "📹 Please ensure your video file is named 'live_cam.mp4' and is in the current directory."
        )
        return False
    else:
        print(f"✅ Video file '{video_path}' found")
        return True


def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True,
        )
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        return False


def download_yolo_model():
    """Download YOLOv8 model if not present"""
    model_path = "yolov8n.pt"
    if os.path.exists(model_path):
        print(f"✅ YOLOv8 model '{model_path}' already exists")
        return True

    print("📥 Downloading YOLOv8 nano model (smallest, fastest)...")
    try:
        # The ultralytics package will automatically download the model
        # when we first use it, so we don't need to manually download
        print("✅ YOLOv8 model will be downloaded automatically on first run")
        return True
    except Exception as e:
        print(f"❌ Error preparing model: {e}")
        return False


def start_detector():
    """Start the YOLOv8 traffic detector"""
    print("\n🚀 Starting YOLOv8 Traffic Detector...")
    print("🌐 WebSocket server will start on ws://localhost:8765")
    print("📹 Processing video: live_cam.mp4")
    print("🚦 Traffic signal simulation will be active")
    print("\n💡 Open your web browser to see the live detection results!")
    print("🛑 Press Ctrl+C to stop the detector\n")

    try:
        subprocess.run([sys.executable, "yolo_traffic_detector.py"])
    except KeyboardInterrupt:
        print("\n✅ YOLOv8 Traffic Detector stopped.")
    except Exception as e:
        print(f"❌ Error running detector: {e}")


def main():
    """Main function"""
    print("🚗 YOLOv8 Traffic Detection System")
    print("=" * 40)

    # Check if we're in a virtual environment
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  No virtual environment detected. Consider using one:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print()

    # Check video file
    if not check_video_file():
        return 1

    # Install requirements
    if not install_requirements():
        return 1

    # Download model
    if not download_yolo_model():
        return 1

    # Start detector
    start_detector()

    return 0


if __name__ == "__main__":
    exit(main())
