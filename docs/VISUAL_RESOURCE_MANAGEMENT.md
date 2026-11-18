# Visual Resource Management & Memory Protection (Stage 18)

## 1. Frame Buffer Limits & Memory Leak Prevention

Uncompressed high-resolution bitmaps consume substantial memory:
- A single 4K (3840x2160) 32-bit frame requires ~33 MB of RAM.
- Unbounded capture streaming would exhaust host system RAM within minutes.

To guarantee bounded memory usage:
- `FrameBuffer` enforces a fixed `capacity = 10` frames per capture session.
- Frames are stored as compressed PNG byte strings in memory, with uncompressed Pillow bitmaps discarded as soon as inference and differencing complete.
- Active capture sessions are capped at 5 concurrent sessions per desktop host.

---

## 2. Capture Frame Rate Throttling

Continuous observation loops are rate-limited via `frame_rate_limit`:
- Default: 5.0 FPS.
- Permitted range: 0.5 FPS to 30.0 FPS.
- Low-latency visual checks during static tasks drop to 1.0 FPS to conserve CPU and GPU utilization.

---

## 3. Database Frame Retention

Captured frames stored in persistent SQLite storage (`VisualFrameRecord`) are subjected to automated retention policies:
- High-resolution thumbnails are downscaled to 800px max side.
- Non-critical intermediate frames from completed tasks are purged after 72 hours.
- Failure diagnostic frames are retained for user inspection.
