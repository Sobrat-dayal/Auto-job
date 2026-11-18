# Capture Session Management Specification (Stage 18)

## 1. Lifecycle & Session State Machine

Continuous visual automation requires bounded, resource-managed frame capture sessions. `CaptureSessionManager` (`app/visual/capture/sessions.py`) governs active capture streams with strict memory safeguards.

```
       [Created]
           │
           ▼
    [Starting / Active] ──(New Frame Request)──► [Frame Buffer Push]
           │                                            │
           │                                            ▼
           ├──────────────────────────────────► [Ring Buffer (Cap 10)]
           │
           ▼ (Stop / Close)
       [Stopped] ──► [Buffer Clear & Memory Free]
```

---

## 2. Ring Frame Buffering: `FrameBuffer`

To prevent unbounded RAM consumption from uncompressed raw bitmaps:
- `FrameBuffer` maintains an in-memory deque capped at `capacity=10` frames.
- When full, the oldest frame is evicted automatically.
- Each buffered element contains both the strongly-typed `CapturedFrame` (metadata + base64 PNG) and the active `Image.Image` instance.
- Explicit `buffer.clear()` is triggered upon session termination.

---

## 3. Session Identification & Telemetry

Each capture session is assigned a deterministic unique identifier with the standard visual prefix: `vsess_{10-char-hex}`.

Telemetry exposed per session includes:
- `target_type`: `DISPLAY`, `WINDOW`, or `REGION`.
- `target_id`: Specific display index (`display_0`) or window handle reference.
- `provider`: Active capture provider (`mss`, `gdi`, `wgc`).
- `frame_count`: Cumulative frames captured.
- `fps`: Rolling average frames captured per second.
- `created_at` & `last_frame_at`: ISO 8601 UTC timestamps.
