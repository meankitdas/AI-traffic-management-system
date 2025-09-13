# 🔧 Video Loading Troubleshooting Guide

## 🎯 Issue: Video Not Loading in Browser

If you're experiencing issues with the video stream not loading, follow these steps:

## ✅ **SOLUTION 1: Use Simplified Streamer (Recommended)**

### Step 1: Start the Simplified Streamer
```bash
# Option 1: Use the startup script
python start_simple_streamer.py

# Option 2: Run directly
source venv/bin/activate
python yolo_simple_streamer.py
```

### Step 2: Verify Stream is Working
Open in browser: http://localhost:5001/
- You should see a test page with the video stream
- If this works, the server is running correctly

### Step 3: Use in Your Web Interface
1. Open `index.html` in your browser
2. Click **"Start Detection"** button
3. Video should appear with 🔴 LIVE indicator

---

## ✅ **SOLUTION 2: Manual Testing**

### Test 1: Check if Video File Exists
```bash
ls -la live_cam.mp4
# Should show the video file (~22MB)
```

### Test 2: Test Basic Video Streaming
```bash
python test_video_stream.py
```
Then open: http://localhost:5002/

### Test 3: Check YOLOv8 Model
```bash
python -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); print('✅ Model loaded')"
```

---

## 🔍 **Common Issues & Fixes**

### Issue 1: "Connection Failed" in Browser
**Symptoms**: Button shows "Retry Connection"
**Fix**: 
1. Make sure the streaming server is running
2. Check console for error messages
3. Try: `curl http://localhost:5001/video_feed`

### Issue 2: WebSocket Errors (in terminal)
**Symptoms**: `TypeError: handler_wrapper() missing 1 required positional argument`
**Fix**: Use the simplified streamer (no WebSocket dependency)

### Issue 3: Video Shows But No Detections
**Symptoms**: Video plays but no colored boxes
**Fix**: 
1. Check if YOLOv8 model downloaded: `ls -la yolov8n.pt`
2. Lower detection threshold in code (change 0.3 to 0.1)

### Issue 4: CORS Errors
**Symptoms**: Browser blocks video loading
**Fix**: The Flask server runs on `0.0.0.0` which should allow local access

### Issue 5: Port Already in Use
**Symptoms**: `Address already in use` error
**Fix**: 
```bash
# Kill existing processes
pkill -f yolo_simple_streamer
pkill -f yolo_web_streamer

# Then restart
python yolo_simple_streamer.py
```

---

## 🎬 **Video Stream URLs**

| Service | URL | Purpose |
|---------|-----|---------|
| **YOLOv8 Stream** | http://localhost:5001/video_feed | Main detection stream |
| **Test Page** | http://localhost:5001/ | Verify server working |
| **Test Stream** | http://localhost:5002/test_video | Basic video test |

---

## 🚀 **Quick Start (If Nothing Works)**

### 1. Clean Start
```bash
# Stop everything
pkill -f yolo
pkill -f test_video

# Activate environment
source venv/bin/activate

# Install dependencies
pip install flask ultralytics opencv-python

# Create demo video if needed
python demo.py

# Start simplified streamer
python yolo_simple_streamer.py
```

### 2. Test in Browser
1. Go to: http://localhost:5001/
2. You should see YOLOv8 detection video
3. If this works, your server is fine

### 3. Use in Web Interface
1. Open `index.html`
2. Click "Start Detection"
3. Video should appear with expand functionality

---

## 📊 **Success Indicators**

✅ **Server Running**: Terminal shows "Starting YOLOv8 detection stream..."
✅ **Video Loading**: Browser shows live video with detections
✅ **Detections Working**: Colored boxes around vehicles
✅ **LIVE Indicator**: Red pulsing "LIVE" indicator visible
✅ **Expand Works**: Click video to expand to fullscreen

---

## 🆘 **Still Not Working?**

### Check Browser Console
1. Press F12 in browser
2. Look for error messages
3. Common errors:
   - Network errors → Server not running
   - CORS errors → Try different browser
   - Loading errors → Check video file

### Check Terminal Output
Look for:
- ✅ "Video opened: live_cam.mp4"
- ✅ "Starting YOLOv8 detection stream..."
- ❌ Any error messages about OpenCV or YOLO

### Test with curl
```bash
curl -I http://localhost:5001/video_feed
# Should return: HTTP/1.1 200 OK
```

---

## 💡 **Pro Tips**

1. **Use Chrome/Firefox** - Better video streaming support
2. **Check firewall** - Make sure localhost:5001 is not blocked
3. **Close other video apps** - They might lock the video file
4. **Restart browser** - Clear any cached errors
5. **Use incognito mode** - Avoid extension conflicts

The simplified streamer should work reliably without WebSocket complications! 🎯
