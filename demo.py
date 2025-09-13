#!/usr/bin/env python3
"""
Demo script to show YOLOv8 Traffic Detection System
This creates a simple test video if live_cam.mp4 doesn't exist
"""

import cv2
import numpy as np
import os
from pathlib import Path


def create_demo_video():
    """Create a simple demo video with moving rectangles (cars)"""
    print("🎬 Creating demo video 'live_cam.mp4'...")

    # Video properties
    width, height = 640, 480
    fps = 30
    duration = 30  # seconds
    total_frames = fps * duration

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter("live_cam.mp4", fourcc, fps, (width, height))

    # Colors for different "vehicles"
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

    # Vehicle properties
    num_vehicles = 8
    vehicles = []
    for i in range(num_vehicles):
        vehicles.append(
            {
                "x": np.random.randint(0, width - 40),
                "y": np.random.randint(0, height - 20),
                "dx": np.random.randint(-3, 4),
                "dy": np.random.randint(-2, 3),
                "color": colors[i % len(colors)],
                "width": np.random.randint(30, 50),
                "height": np.random.randint(15, 25),
            }
        )

    for frame_num in range(total_frames):
        # Create black background
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Add road-like background
        cv2.rectangle(
            frame, (0, height // 3), (width, 2 * height // 3), (50, 50, 50), -1
        )

        # Add lane dividers
        for x in range(0, width, 40):
            cv2.rectangle(
                frame,
                (x, height // 2 - 2),
                (x + 20, height // 2 + 2),
                (255, 255, 255),
                -1,
            )

        # Update and draw vehicles
        for vehicle in vehicles:
            # Update position
            vehicle["x"] += vehicle["dx"]
            vehicle["y"] += vehicle["dy"]

            # Bounce off edges
            if vehicle["x"] <= 0 or vehicle["x"] >= width - vehicle["width"]:
                vehicle["dx"] *= -1
            if vehicle["y"] <= 0 or vehicle["y"] >= height - vehicle["height"]:
                vehicle["dy"] *= -1

            # Keep in bounds
            vehicle["x"] = max(0, min(width - vehicle["width"], vehicle["x"]))
            vehicle["y"] = max(0, min(height - vehicle["height"], vehicle["y"]))

            # Draw vehicle as rectangle
            cv2.rectangle(
                frame,
                (int(vehicle["x"]), int(vehicle["y"])),
                (
                    int(vehicle["x"] + vehicle["width"]),
                    int(vehicle["y"] + vehicle["height"]),
                ),
                vehicle["color"],
                -1,
            )

            # Add some detail (windows)
            cv2.rectangle(
                frame,
                (int(vehicle["x"] + 5), int(vehicle["y"] + 3)),
                (
                    int(vehicle["x"] + vehicle["width"] - 5),
                    int(vehicle["y"] + vehicle["height"] - 3),
                ),
                (200, 200, 200),
                1,
            )

        # Add frame info
        cv2.putText(
            frame,
            f"Demo Traffic Video - Frame {frame_num+1}/{total_frames}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
        )
        cv2.putText(
            frame,
            f"Vehicles: {num_vehicles}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
        )

        # Vary vehicle count over time to simulate traffic changes
        if frame_num % (fps * 5) == 0:  # Every 5 seconds
            # Randomly add or remove vehicles
            if len(vehicles) < 12 and np.random.random() > 0.5:
                vehicles.append(
                    {
                        "x": np.random.randint(0, width - 40),
                        "y": np.random.randint(0, height - 20),
                        "dx": np.random.randint(-3, 4),
                        "dy": np.random.randint(-2, 3),
                        "color": colors[len(vehicles) % len(colors)],
                        "width": np.random.randint(30, 50),
                        "height": np.random.randint(15, 25),
                    }
                )
            elif len(vehicles) > 3 and np.random.random() > 0.7:
                vehicles.pop()

        out.write(frame)

        # Show progress
        if frame_num % (fps * 2) == 0:
            progress = (frame_num / total_frames) * 100
            print(f"Progress: {progress:.1f}%")

    out.release()
    print("✅ Demo video created successfully!")
    print("📁 File: live_cam.mp4")
    print(f"📊 Duration: {duration}s, Resolution: {width}x{height}, FPS: {fps}")


def main():
    """Main function"""
    print("🚗 YOLOv8 Traffic Detection Demo Setup")
    print("=" * 40)

    # Check if video already exists
    if os.path.exists("live_cam.mp4"):
        print("✅ Video file 'live_cam.mp4' already exists")
        print(
            "🎬 If you want to recreate the demo video, delete the existing file first"
        )
        return

    try:
        create_demo_video()
        print("\n🚀 Demo setup complete!")
        print("\nNext steps:")
        print("1. Run: python start_yolo_detector.py")
        print("2. Open index.html in your browser")
        print("3. Click 'Start Detection' in the YOLOv8 section")
        print("4. Watch the real-time vehicle detection!")

    except Exception as e:
        print(f"❌ Error creating demo video: {e}")
        print("💡 Make sure OpenCV is installed: pip install opencv-python")


if __name__ == "__main__":
    main()
