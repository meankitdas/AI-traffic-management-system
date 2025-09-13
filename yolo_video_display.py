#!/usr/bin/env python3
"""
YOLOv8 Real-time Video Detection Display
Shows live_cam.mp4 with vehicle detection bounding boxes using OpenCV
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time


class YoloVideoDisplay:
    def __init__(self, video_path="live_cam.mp4", model_path="yolov8n.pt"):
        self.video_path = video_path
        self.model = YOLO(model_path)
        # COCO dataset class IDs for vehicles
        self.vehicle_classes = [1, 2, 3, 5, 7]  # bicycle, car, motorcycle, bus, truck

        # Class names for display
        self.class_names = {
            1: "Bicycle",
            2: "Car",
            3: "Motorcycle",
            5: "Bus",
            7: "Truck",
        }

        # Colors for different vehicle types (BGR format for OpenCV)
        self.colors = {
            1: (255, 255, 0),  # Bicycle - Cyan
            2: (0, 255, 0),  # Car - Green
            3: (255, 0, 0),  # Motorcycle - Blue
            5: (0, 0, 255),  # Bus - Red
            7: (0, 255, 255),  # Truck - Yellow
        }

        # Traffic light simulation
        self.current_signal = "green"
        self.signal_timer = 0
        self.last_signal_time = time.time()
        self.vehicle_history = []  # Track vehicle counts for congestion analysis

        # Traffic signal timing (seconds)
        self.signal_timings = {
            "green": {"low": 30, "medium": 20, "high": 15},
            "yellow": 3,
            "red": {"low": 15, "medium": 25, "high": 35},
        }

    def draw_detections(self, frame, results):
        """Draw bounding boxes and labels on frame"""
        vehicle_count = 0

        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])

                    if (
                        cls in self.vehicle_classes and conf > 0.3
                    ):  # Lower threshold for better detection
                        vehicle_count += 1

                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                        # Get color for this vehicle type
                        color = self.colors.get(cls, (255, 255, 255))
                        class_name = self.class_names.get(cls, "Vehicle")

                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                        # Draw label background
                        label = f"{class_name}: {conf:.2f}"
                        label_size = cv2.getTextSize(
                            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                        )[0]
                        cv2.rectangle(
                            frame,
                            (x1, y1 - label_size[1] - 10),
                            (x1 + label_size[0], y1),
                            color,
                            -1,
                        )

                        # Draw label text
                        cv2.putText(
                            frame,
                            label,
                            (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 0, 0),
                            2,
                        )

        return frame, vehicle_count

    def update_traffic_signal(self, vehicle_count):
        """Update traffic signal based on vehicle congestion"""
        current_time = time.time()
        elapsed = current_time - self.last_signal_time
        self.signal_timer = elapsed

        # Update vehicle history for congestion analysis
        self.vehicle_history.append(vehicle_count)
        if len(self.vehicle_history) > 30:  # Keep last 30 readings
            self.vehicle_history.pop(0)

        # Calculate congestion level
        avg_vehicles = (
            sum(self.vehicle_history) / len(self.vehicle_history)
            if self.vehicle_history
            else 0
        )
        if avg_vehicles < 5:
            congestion_level = "low"
        elif avg_vehicles < 15:
            congestion_level = "medium"
        else:
            congestion_level = "high"

        # Traffic signal logic
        if self.current_signal == "green":
            duration = self.signal_timings["green"][congestion_level]
            if elapsed >= duration:
                self.current_signal = "yellow"
                self.last_signal_time = current_time
                self.signal_timer = 0
        elif self.current_signal == "yellow":
            if elapsed >= self.signal_timings["yellow"]:
                self.current_signal = "red"
                self.last_signal_time = current_time
                self.signal_timer = 0
        elif self.current_signal == "red":
            duration = self.signal_timings["red"][congestion_level]
            if elapsed >= duration:
                self.current_signal = "green"
                self.last_signal_time = current_time
                self.signal_timer = 0

        return congestion_level

    def draw_traffic_light(self, frame):
        """Draw traffic light on the video"""
        height, width = frame.shape[:2]

        # Traffic light position (top right)
        light_x = width - 120
        light_y = 20
        light_width = 80
        light_height = 200

        # Draw traffic light housing (black background)
        cv2.rectangle(
            frame,
            (light_x, light_y),
            (light_x + light_width, light_y + light_height),
            (0, 0, 0),
            -1,
        )
        cv2.rectangle(
            frame,
            (light_x, light_y),
            (light_x + light_width, light_y + light_height),
            (255, 255, 255),
            3,
        )

        # Light positions
        red_center = (light_x + light_width // 2, light_y + 40)
        yellow_center = (light_x + light_width // 2, light_y + 100)
        green_center = (light_x + light_width // 2, light_y + 160)
        light_radius = 25

        # Draw lights (dim when not active)
        red_color = (0, 0, 255) if self.current_signal == "red" else (0, 0, 80)
        yellow_color = (0, 255, 255) if self.current_signal == "yellow" else (0, 80, 80)
        green_color = (0, 255, 0) if self.current_signal == "green" else (0, 80, 0)

        # Draw light circles
        cv2.circle(frame, red_center, light_radius, red_color, -1)
        cv2.circle(frame, red_center, light_radius, (255, 255, 255), 2)

        cv2.circle(frame, yellow_center, light_radius, yellow_color, -1)
        cv2.circle(frame, yellow_center, light_radius, (255, 255, 255), 2)

        cv2.circle(frame, green_center, light_radius, green_color, -1)
        cv2.circle(frame, green_center, light_radius, (255, 255, 255), 2)

        # Add glow effect for active light
        if self.current_signal == "red":
            cv2.circle(frame, red_center, light_radius + 5, (0, 0, 255), 2)
        elif self.current_signal == "yellow":
            cv2.circle(frame, yellow_center, light_radius + 5, (0, 255, 255), 2)
        elif self.current_signal == "green":
            cv2.circle(frame, green_center, light_radius + 5, (0, 255, 0), 2)

        # Add signal timer text
        timer_text = f"{self.signal_timer:.1f}s"
        cv2.putText(
            frame,
            timer_text,
            (light_x, light_y + light_height + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        return frame

    def add_info_overlay(self, frame, vehicle_count, fps, frame_num, congestion_level):
        """Add information overlay to frame"""
        height, width = frame.shape[:2]

        # Create semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (450, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Add text information
        signal_emoji = {"red": "🔴", "yellow": "🟡", "green": "🟢"}
        congestion_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}

        info_text = [
            f"🚗 Vehicles Detected: {vehicle_count}",
            f"📊 FPS: {fps:.1f}",
            f"📹 Frame: {frame_num}",
            f"🚦 Signal: {signal_emoji.get(self.current_signal, '⚪')} {self.current_signal.upper()}",
            f"📈 Congestion: {congestion_emoji.get(congestion_level, '⚪')} {congestion_level.upper()}",
        ]

        y_offset = 35
        for i, text in enumerate(info_text):
            cv2.putText(
                frame,
                text,
                (20, y_offset + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

        # Add legend
        legend_y = height - 100
        cv2.putText(
            frame,
            "Vehicle Types:",
            (20, legend_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        legend_items = [
            ("Bicycle", self.colors[1]),
            ("Car", self.colors[2]),
            ("Motorcycle", self.colors[3]),
            ("Bus", self.colors[5]),
            ("Truck", self.colors[7]),
        ]

        for i, (name, color) in enumerate(legend_items):
            x_pos = 20 + i * 120
            cv2.rectangle(
                frame, (x_pos, legend_y + 10), (x_pos + 15, legend_y + 25), color, -1
            )
            cv2.putText(
                frame,
                name,
                (x_pos + 20, legend_y + 22),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

        return frame

    def run(self):
        """Main display loop"""
        print("🚗 YOLOv8 Real-time Vehicle Detection Display")
        print("📹 Loading video and model...")

        # Open video
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print(f"❌ Error: Cannot open video file {self.video_path}")
            return

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"📊 Video Info: {width}x{height}, {fps} FPS, {total_frames} frames")
        print("🚀 Starting detection display with traffic light simulation...")
        print("💡 Press 'q' to quit, 'p' to pause/resume, 's' to save current frame")
        print("🚦 Traffic light adapts to vehicle congestion levels!")

        # Create window
        cv2.namedWindow("YOLOv8 Vehicle Detection", cv2.WINDOW_NORMAL)

        frame_count = 0
        paused = False
        start_time = time.time()

        while True:
            if not paused:
                ret, frame = cap.read()

                if not ret:
                    print("📹 End of video, looping...")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    frame_count = 0
                    start_time = time.time()
                    continue

                frame_count += 1

                # Run YOLOv8 detection
                results = self.model(frame, verbose=False)

                # Draw detections
                annotated_frame, vehicle_count = self.draw_detections(frame, results)

                # Update traffic signal simulation
                congestion_level = self.update_traffic_signal(vehicle_count)

                # Draw traffic light
                annotated_frame = self.draw_traffic_light(annotated_frame)

                # Calculate current FPS
                elapsed_time = time.time() - start_time
                current_fps = frame_count / elapsed_time if elapsed_time > 0 else 0

                # Add info overlay
                display_frame = self.add_info_overlay(
                    annotated_frame,
                    vehicle_count,
                    current_fps,
                    frame_count,
                    congestion_level,
                )

                # Display frame
                cv2.imshow("YOLOv8 Vehicle Detection", display_frame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                print("🛑 Stopping detection display...")
                break
            elif key == ord("p"):
                paused = not paused
                print(f"⏸️ {'Paused' if paused else 'Resumed'}")
            elif key == ord("s") and not paused:
                # Save current frame
                timestamp = int(time.time())
                filename = f"detection_frame_{timestamp}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"💾 Saved frame: {filename}")

        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Detection display stopped.")


def main():
    """Main function"""
    detector = YoloVideoDisplay()
    detector.run()


if __name__ == "__main__":
    main()
