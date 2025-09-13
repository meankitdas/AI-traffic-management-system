# AI Traffic Management System - Bhubaneswar

A comprehensive traffic management system that combines real-time traffic simulation with YOLOv8-powered vehicle detection and intelligent traffic signal control.

## Features

### 🗺️ Interactive Traffic Map

- Real-time traffic flow visualization on Bhubaneswar road network
- Dynamic congestion level indicators with color-coded roads
- Live vehicle tracking and analytics
- Interactive map controls and zoom functionality

### 🤖 YOLOv8 Vehicle Detection

- **Real-time vehicle detection** from live camera feed (`live_cam.mp4`)
- **Automatic vehicle counting** with running averages
- **AI-powered traffic signal simulation** based on congestion levels
- **WebSocket-based real-time updates** to the web interface

### 🚦 Intelligent Traffic Signal Control

- **Adaptive signal timing** based on vehicle density:
  - **Low congestion**: Green 30s, Red 15s
  - **Medium congestion**: Green 20s, Red 25s
  - **High congestion**: Green 15s, Red 35s
- **Visual signal display** with realistic traffic light colors
- **Real-time countdown timer** for signal changes

### 📊 Live Analytics Dashboard

- Vehicle count metrics and trends
- FPS performance monitoring
- Average speed calculations
- Road congestion statistics
- AI confidence indicators

## Setup Instructions

### 1. Environment Setup

```bash
# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Video File Preparation

- Place your traffic video file in the project directory
- **Rename it to `live_cam.mp4`** (this is required)
- Supported formats: MP4, AVI, MOV, etc.

### 3. Running the System

#### Option A: Quick Start (Recommended)

```bash
python start_yolo_detector.py
```

#### Option B: Manual Start

```bash
# Start the YOLOv8 detector backend
python yolo_traffic_detector.py

# Open index.html in your web browser
# Click "Start Detection" in the YOLOv8 section
```

### 4. Using the Web Interface

1. Open `index.html` in your web browser
2. Navigate to the **YOLOv8 Live Detection** panel (right sidebar)
3. Click **"Start Detection"** to connect to the backend
4. Watch real-time vehicle detection and traffic signal simulation

## System Components

### Backend Components

- **`yolo_traffic_detector.py`**: Main YOLOv8 detection engine
- **`start_yolo_detector.py`**: Easy startup script with dependency management
- **`parse_traffic.py`**: Traffic network data processor
- **`requirements.txt`**: Python dependencies

### Frontend Components

- **`index.html`**: Main web interface with integrated YOLOv8 controls
- **Interactive map**: Leaflet-based traffic visualization
- **Real-time dashboard**: Live metrics and analytics
- **WebSocket client**: Connects to YOLOv8 backend for live updates

### Data Files

- **`live_cam.mp4`**: Your traffic video file (you provide this)
- **`bhubaneswar_traffic_flow.geojson`**: Traffic network geometry
- **`roads.json`**, **`intersections.json`**, **`graph.json`**: Processed traffic data

## YOLOv8 Detection Features

### Vehicle Detection

- Detects: Cars, motorcycles, buses, trucks
- Confidence threshold: 50%
- Real-time bounding box visualization
- Vehicle count tracking with 30-frame history

### Traffic Signal Logic

The system simulates intelligent traffic signals that adapt to congestion:

```python
# Signal timing based on vehicle count
if vehicles < 5:     # Low congestion
    green_time = 30s, red_time = 15s
elif vehicles < 15:  # Medium congestion
    green_time = 20s, red_time = 25s
else:               # High congestion
    green_time = 15s, red_time = 35s
```

### WebSocket Communication

- **Server**: `ws://localhost:8765`
- **Data format**: JSON with vehicle counts, signal states, congestion levels
- **Auto-reconnection**: Automatically reconnects if connection is lost

## Troubleshooting

### Common Issues

#### "Video file not found"

- Ensure your video is named exactly `live_cam.mp4`
- Place it in the same directory as the Python scripts

#### "WebSocket connection failed"

- Make sure `yolo_traffic_detector.py` is running
- Check that port 8765 is not blocked by firewall
- Try restarting the backend script

#### "YOLOv8 model download error"

- Ensure stable internet connection
- The model (~6MB) downloads automatically on first run
- Check available disk space

#### Low performance

- Use YOLOv8n (nano) model for fastest inference
- Reduce video resolution if needed
- Close other resource-intensive applications

### System Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB for models and dependencies
- **GPU**: Optional (CUDA-compatible) for faster inference

## Technical Details

### Architecture

```
┌─────────────────┐    WebSocket     ┌──────────────────┐
│   Web Browser   │ ←──────────────→ │  YOLOv8 Backend  │
│   (index.html)  │    Port 8765     │   (Python)       │
└─────────────────┘                  └──────────────────┘
                                              │
                                              ▼
                                     ┌──────────────────┐
                                     │   live_cam.mp4   │
                                     │  (Video Input)   │
                                     └──────────────────┘
```

### Performance Metrics

- **Detection FPS**: ~15-30 FPS (depending on hardware)
- **WebSocket latency**: <50ms locally
- **Model size**: YOLOv8n (~6MB), YOLOv8s (~22MB)
- **Memory usage**: ~200-500MB

## License & Credits

- **YOLOv8**: Ultralytics (AGPL-3.0)
- **OpenCV**: Apache 2.0
- **Leaflet**: BSD-2-Clause
- **Tailwind CSS**: MIT

---

🚗 **Happy Traffic Monitoring!** 🚦

For issues or questions, check the console logs in both the Python backend and browser developer tools.
