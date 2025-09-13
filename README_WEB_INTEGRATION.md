# YOLOv8 Web Integration - Live Video Streaming

## 🎯 Overview

This integration allows you to view the YOLOv8 vehicle detection directly in your web browser with a **live video stream** featuring:

- **🔴 LIVE indicator** - Red pulsing indicator showing real-time status
- **Real-time vehicle detection** with colored bounding boxes
- **Adaptive traffic light simulation** overlaid on the video
- **Vehicle count and statistics** displayed on the video
- **Web-based controls** to start/stop detection from the HTML interface

## 🚀 Quick Start

### 1. Start the Web Streaming Server

```bash
# Option 1: Use the automated startup script
python start_yolo_web_streamer.py

# Option 2: Run the streamer directly
source venv/bin/activate
python yolo_web_streamer.py
```

### 2. Open the Web Interface

1. Open `index.html` in your browser
2. Look for the **"YOLOv8 Live Detection"** section in the right sidebar
3. Click the **"Start Detection"** button
4. The live video stream will appear with the red **🔴 LIVE** indicator

## 📺 What You'll See

### In the Video Stream:

- **🔴 LIVE indicator** (top-left, pulsing red)
- **Vehicle detection boxes** (colored by type):
  - 🚲 Bicycle - Cyan
  - 🚗 Car - Green
  - 🏍️ Motorcycle - Blue
  - 🚌 Bus - Red
  - 🚛 Truck - Yellow
- **Traffic light simulation** (top-right with timer)
- **Real-time statistics** overlay:
  - Vehicle count
  - FPS
  - Frame number
  - Current traffic signal
  - Congestion level
- **Vehicle type legend** (bottom of video)

### In the Web Interface:

- **Live connection status** indicator
- **Real-time vehicle counts** (current and 30-second average)
- **Traffic signal display** with timing
- **Congestion level** with color-coded progress bar
- **Start/Stop controls**

## 🔧 Technical Details

### Components Created:

1. **`yolo_web_streamer.py`** - Main streaming server with:

   - Flask HTTP server for video streaming (`http://localhost:5001`)
   - WebSocket server for real-time data (`ws://localhost:8765`)
   - YOLOv8 detection with traffic simulation
   - Live video encoding for web browsers

2. **Updated `index.html`** - Enhanced with:

   - Video stream display container
   - Live indicator overlay
   - Updated JavaScript for stream control
   - Improved button functionality

3. **`start_yolo_web_streamer.py`** - Automated setup script

### Ports Used:

- **5001** - Flask video streaming server
- **8765** - WebSocket data server (same as before)

### Video Features:

- **Aspect ratio**: 16:9 for responsive design
- **Quality**: Optimized JPEG streaming at 80% quality
- **Frame rate**: ~30 FPS for smooth playback
- **Auto-loop**: Video automatically restarts when finished

## 🎮 Controls

### Start Detection:

1. Click **"Start Detection"** button
2. Video stream appears with 🔴 LIVE indicator
3. Button changes to **"📺 Live Stream Active"**
4. Real-time data updates begin

### Stop Detection:

1. Click **"Stop Detection"** button
2. Video stream hides
3. All counters reset to zero
4. Button returns to **"Start Detection"**

## 🔍 Troubleshooting

### Video Not Showing:

- Ensure `live_cam.mp4` exists in the project directory
- Check that Flask server is running on port 5001
- Verify browser console for any errors

### Connection Issues:

- Make sure both servers are running:
  - Flask (port 5001) for video
  - WebSocket (port 8765) for data
- Check firewall settings for localhost connections

### Performance:

- Video streaming uses significant CPU/GPU resources
- Lower detection threshold if needed (currently 0.3)
- Close other resource-intensive applications

## 🎨 Customization

### Modify Detection Threshold:

In `yolo_web_streamer.py`, line ~145:

```python
if cls in self.vehicle_classes and conf > 0.3:  # Change 0.3 to desired threshold
```

### Change Video Quality:

In `yolo_web_streamer.py`, line ~340:

```python
ret, buffer = cv2.imencode('.jpg', display_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])  # Change 80 to desired quality (1-100)
```

### Adjust Traffic Light Timing:

In `yolo_web_streamer.py`, lines ~40-45:

```python
self.signal_timings = {
    "green": {"low": 30, "medium": 20, "high": 15},  # Adjust green light durations
    "yellow": 3,                                      # Adjust yellow duration
    "red": {"low": 15, "medium": 25, "high": 35},    # Adjust red light durations
}
```

## 🌟 Features Highlights

✅ **Live video streaming** directly in browser  
✅ **🔴 LIVE indicator** with pulsing animation  
✅ **Real-time vehicle detection** with colored boxes  
✅ **Traffic light simulation** with adaptive timing  
✅ **Comprehensive statistics** overlay  
✅ **Responsive design** that works on different screen sizes  
✅ **Easy start/stop controls** integrated into existing UI  
✅ **Auto-reconnection** for robust operation  
✅ **Performance optimized** for smooth streaming

## 🎯 Perfect Integration

The live video stream integrates seamlessly with your existing traffic management dashboard:

- **Same color scheme** and styling
- **Consistent UI elements** with the rest of the interface
- **Real-time data synchronization** with WebSocket updates
- **Professional appearance** with smooth animations and transitions

## 🔍 NEW: Click to Expand Video Feature

### Expand Video to Fullscreen:

- **Click on the video** to expand it to a fullscreen modal view
- **🔴 LIVE - EXPANDED VIEW** indicator shows it's still streaming live
- **Enhanced viewing experience** with larger video size for better detail visibility

### Close Expanded Video:

- **❌ Close button** (top-right corner)
- **Click outside video** (on the dark background)
- **Press ESC key** for quick close
- **Press F key** to toggle browser fullscreen mode

### Features in Expanded Mode:

✅ **Larger video display** for better detection visibility  
✅ **Same live stream** with all YOLOv8 detections  
✅ **Enhanced LIVE indicator** for expanded view  
✅ **Multiple close options** for user convenience  
✅ **Keyboard shortcuts** for power users  
✅ **Fullscreen browser mode** support

---

Click **"Start Detection"** and then **click on the video** to expand it for the ultimate YOLOv8 vehicle detection experience! 🚀🔍
