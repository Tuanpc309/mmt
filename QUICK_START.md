# Quick Start Guide - HD Video Streaming

## Prerequisites
- Python 3.7 or higher
- PIL/Pillow library: `pip install pillow`
- tkinter (usually comes with Python)
- Optional: matplotlib for analysis: `pip install matplotlib`

## Step 1: Generate Test Videos

Generate HD test videos for streaming:

```bash
# Generate a 720p test video (recommended for testing)
python HDVideoGenerator.py 720p

# Generate a 1080p test video (high bandwidth)
python HDVideoGenerator.py 1080p

# Generate full test suite (SD, 480p, 720p, 1080p)
python HDVideoGenerator.py suite
```

This will create `.Mjpeg` video files in the current directory.

## Step 2: Start the Server

Open a terminal and start the server:

```bash
python Server.py 8554
```

Expected output:
```
[Server listening on port 8554]
```

## Step 3: Start the Client

Open another terminal and start the client:

```bash
python ClientLauncher.py localhost 8554 25000 test_video_720p.Mjpeg
```

Parameters:
- `localhost`: Server IP address
- `8554`: Server RTSP port
- `25000`: RTP port for video data
- `test_video_720p.Mjpeg`: Video file name

## Step 4: Control Playback

In the client GUI:
1. Click **Setup** to establish connection
2. Click **Play** to start streaming
3. Click **Pause** to pause playback
4. Click **Teardown** to stop and disconnect

## Step 5: Monitor Performance

### Real-time Statistics (GUI)
The client shows live network statistics:
```
FPS: 28/10.0s | Loss: 2.1% | BW: 1850 Kbps | Latency: 45.2ms
```

### Console Output (Server)
Server prints statistics every 100 frames:
```
[Server] Frame 100 | Size: 52480 bytes | BW: 2048 Kbps | Fragments: 356
```

### Final Statistics
When streaming stops, both client and server print comprehensive statistics.

## Step 6: Run Network Analysis

Analyze network performance:

```bash
python NetworkAnalyzer.py
```

This generates:
- Console report with performance metrics
- JSON file with detailed results
- Visualization plots (if matplotlib installed)

## Testing Different Scenarios

### Test Low Bandwidth (SD)
```bash
# Server
python Server.py 8554

# Client
python ClientLauncher.py localhost 8554 25000 test_video_sd.Mjpeg
```
Expected: No fragmentation, smooth playback, low bandwidth

### Test HD 720p
```bash
# Server
python Server.py 8554

# Client
python ClientLauncher.py localhost 8554 25000 test_video_720p.Mjpeg
```
Expected: ~36 fragments/frame, moderate bandwidth (~1.5 Mbps)

### Test Full HD 1080p
```bash
# Server
python Server.py 8554

# Client
python ClientLauncher.py localhost 8554 25000 test_video_1080p.Mjpeg
```
Expected: ~87 fragments/frame, high bandwidth (~3.6 Mbps)

## Troubleshooting

### Issue: "Unable to Bind PORT=25000"
**Solution**: Port is in use. Try a different RTP port:
```bash
python ClientLauncher.py localhost 8554 25001 test_video_720p.Mjpeg
```

### Issue: High frame loss
**Solutions**:
- Check network bandwidth
- Reduce video resolution
- Close other network applications
- Check firewall settings

### Issue: Video not displaying
**Solutions**:
- Ensure PIL/Pillow is installed: `pip install pillow`
- Check video file exists and is valid
- Verify server is running and reachable

### Issue: "Connection Error"
**Solutions**:
- Verify server is running
- Check server IP and port are correct
- Ensure no firewall blocking UDP port

## Understanding the Output

### Fragmentation Messages
```
[Server] Fragmenting frame 50: 52480 bytes into 38 fragments
```
This is normal for HD video. Large frames are split into packets.

### Fragment Reassembly
```
[Client] Frame 50 reassembled from 38 fragments (52480 bytes)
```
Client successfully received and reassembled all fragments.

### Network Statistics
```
NETWORK STATISTICS
==================
Elapsed Time: 30.00 seconds
Packets:
  Sent: 11400
  Received: 11250
  Lost: 150
  Loss Rate: 1.32%
Frames:
  Sent: 300
  Received: 295
  Lost: 5
  Loss Rate: 1.67%
Bandwidth:
  Sent: 1850.50 Kbps
  Received: 1825.30 Kbps
Latency:
  Average: 45.20 ms
  Jitter: 5.30 ms
```

## Performance Expectations

### Standard Definition (SD)
- Frame size: ~8 KB
- No fragmentation
- Bandwidth: ~240 Kbps
- Latency: ~30 ms

### 720p HD
- Frame size: ~50 KB
- Fragments: ~36 per frame
- Bandwidth: ~1.5 Mbps
- Latency: ~60 ms

### 1080p Full HD
- Frame size: ~120 KB
- Fragments: ~87 per frame
- Bandwidth: ~3.6 Mbps
- Latency: ~100 ms

## Advanced Usage

### Custom Resolution Video
Generate custom resolution video:
```bash
python HDVideoGenerator.py 720p custom_video.Mjpeg 500 90
```
Parameters: resolution, filename, frames, quality

### Multiple Clients
Run multiple clients with different RTP ports:
```bash
# Client 1
python ClientLauncher.py localhost 8554 25000 test_video_720p.Mjpeg

# Client 2 (different RTP port)
python ClientLauncher.py localhost 8554 25001 test_video_720p.Mjpeg
```

### Remote Streaming
Stream over network (replace SERVER_IP with actual IP):
```bash
# Server (on machine A)
python Server.py 8554

# Client (on machine B)
python ClientLauncher.py SERVER_IP 8554 25000 test_video_720p.Mjpeg
```

## Key Features Demonstrated

✅ **Frame Fragmentation**: Automatic splitting of large frames
✅ **Fragment Reassembly**: Correct reconstruction of frames
✅ **Network Statistics**: Real-time bandwidth and loss tracking
✅ **Low Latency**: Optimized for smooth HD playback
✅ **Quality Metrics**: FPS, loss rate, latency, jitter
✅ **Adaptive Control**: Inter-fragment delay prevents congestion

## Next Steps

1. Experiment with different resolutions
2. Test on different network conditions
3. Compare performance metrics
4. Analyze fragmentation impact
5. Review network statistics

## Support

For issues or questions, refer to:
- HD_VIDEO_STREAMING_README.md - Comprehensive documentation
- NetworkAnalyzer.py - Performance analysis tool
- Source code comments - Implementation details
