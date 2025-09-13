#!/usr/bin/env python3
"""
Test script to see what classes YOLOv8 detects in the video
"""

import cv2
from ultralytics import YOLO
from collections import Counter


def test_yolo_detection():
    print("🔍 Testing YOLOv8 detection on live_cam.mp4...")

    # Load model and video
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture("live_cam.mp4")

    if not cap.isOpened():
        print("❌ Cannot open video file")
        return

    detected_classes = Counter()
    frame_count = 0
    max_frames = 300  # Test first 10 seconds (30 fps * 10)

    print(f"📹 Analyzing first {max_frames} frames...")

    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Run detection
        results = model(frame, verbose=False)

        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])

                    if conf > 0.3:  # Same threshold as main script
                        detected_classes[cls] += 1

        if frame_count % 60 == 0:  # Progress every 2 seconds
            print(f"📊 Processed {frame_count} frames...")

    cap.release()

    print(f"\n🎯 Detection Results from {frame_count} frames:")
    print("=" * 50)

    # COCO class names (relevant ones)
    coco_names = {
        0: "person",
        1: "bicycle",
        2: "car",
        3: "motorcycle",
        4: "airplane",
        5: "bus",
        6: "train",
        7: "truck",
        8: "boat",
        9: "traffic light",
        10: "fire hydrant",
        11: "stop sign",
        12: "parking meter",
        13: "bench",
    }

    if detected_classes:
        for cls_id, count in detected_classes.most_common():
            class_name = coco_names.get(cls_id, f"Unknown({cls_id})")
            print(f"Class {cls_id:2d} ({class_name:12s}): {count:4d} detections")

        print(f"\n🚗 Vehicle-related detections:")
        vehicle_classes = [1, 2, 3, 5, 7]  # bicycle, car, motorcycle, bus, truck
        total_vehicles = 0

        for cls_id in vehicle_classes:
            if cls_id in detected_classes:
                class_name = coco_names.get(cls_id, f"Unknown({cls_id})")
                count = detected_classes[cls_id]
                total_vehicles += count
                print(f"  {class_name:12s}: {count:4d} detections")

        print(f"\n📈 Total vehicle detections: {total_vehicles}")

        if 1 in detected_classes:
            print(f"✅ Bicycles detected: {detected_classes[1]} times")
        else:
            print("❌ No bicycles detected in the analyzed frames")

    else:
        print("❌ No objects detected at all!")


if __name__ == "__main__":
    test_yolo_detection()
